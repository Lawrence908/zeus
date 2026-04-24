# zeus/core/actions.py — Allowlisted custom action runner
#
# GET  /actions/list                  enumerate scripts in ZEUS_ACTIONS_DIR
# POST /actions/run  {name, args?}    execute one named script
#
# The allowlist is the directory: any executable script the operator drops in
# ZEUS_ACTIONS_DIR (default ~/.zeus/actions/) becomes callable. Names are
# alphanumeric + dash + underscore only — no path separators, no traversal.
#
# Three independent gates:
#   1. ZEUS_ACTIONS_ENABLED       master switch, default OFF
#   2. ZEUS_MCP_ALLOW_WRITE       global write gate (mirrors MCP)
#   3. directory contents         the operator's curated allowlist
#
# Subprocess args are passed positionally with no shell interpretation, so a
# malicious arg cannot inject another command. Stdout/stderr are size-capped
# so a runaway script cannot fill memory.
from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from zeus.safety.policy_engine import AegisPolicyEngine, aegis_enabled

logger = logging.getLogger("zeus.actions")

router = APIRouter(tags=["actions"])

_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_ARG_MAX_LEN = 256
_ARG_MAX_COUNT = 16
_OUTPUT_CAP_BYTES = 64 * 1024


def _actions_enabled() -> bool:
    return os.getenv("ZEUS_ACTIONS_ENABLED", "0").strip().lower() in (
        "1", "true", "yes", "on",
    )


def _write_enabled() -> bool:
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in (
        "1", "true", "yes", "y", "on",
    )


def _actions_dir() -> Path:
    raw = os.getenv("ZEUS_ACTIONS_DIR", "~/.zeus/actions")
    return Path(os.path.expanduser(raw)).resolve(strict=False)


def _action_timeout() -> float:
    try:
        return max(1.0, float(os.getenv("ZEUS_ACTIONS_TIMEOUT", "30")))
    except (TypeError, ValueError):
        return 30.0


def _resolve_action(name: str) -> Path:
    if not _NAME_RE.match(name):
        raise HTTPException(
            status_code=400,
            detail="action name must match [A-Za-z0-9][A-Za-z0-9_-]{0,63}",
        )
    base = _actions_dir()
    if not base.is_dir():
        raise HTTPException(
            status_code=503,
            detail=f"actions directory does not exist: {base}",
        )
    candidate = (base / f"{name}.sh").resolve(strict=False)
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="action name escapes the actions directory") from exc
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"no such action: {name}.sh")
    if not os.access(candidate, os.X_OK):
        raise HTTPException(status_code=400, detail=f"{name}.sh is not executable")
    return candidate


def _aegis_check(payload: dict[str, Any]) -> None:
    if not aegis_enabled() or not payload:
        return
    engine = AegisPolicyEngine(policy="file_access")
    outcome = engine.evaluate_payload(payload, policy_name="file_access")
    if outcome.status == "rejected":
        raise HTTPException(status_code=400, detail=outcome.message or "Aegis blocked payload.")


def _read_first_desc_comment(path: Path) -> str | None:
    """Return the first `# desc: ...` line in the script, if present."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 20:
                    break
                stripped = line.strip()
                if stripped.lower().startswith("# desc:"):
                    return stripped[len("# desc:"):].strip()
    except OSError:
        return None
    return None


@router.get("/actions/list")
async def actions_list() -> dict[str, Any]:
    """Enumerate every *.sh in ZEUS_ACTIONS_DIR. Backs olympian_action_list."""
    if not _actions_enabled():
        # Listing is fine when disabled — it is a no-write read; but it is
        # cleaner to treat the whole subsystem as off so callers get one
        # consistent error.
        raise HTTPException(
            status_code=403,
            detail="ZEUS_ACTIONS_ENABLED is off; the action runner is disabled.",
        )
    base = _actions_dir()
    if not base.is_dir():
        return {"directory": str(base), "actions": [], "exists": False}
    entries: list[dict[str, Any]] = []
    for child in sorted(base.iterdir()):
        if child.suffix != ".sh" or not child.is_file():
            continue
        executable = os.access(child, os.X_OK)
        try:
            mtime = child.stat().st_mtime
        except OSError:
            mtime = 0.0
        entries.append({
            "name": child.stem,
            "path": str(child),
            "mtime": mtime,
            "executable": executable,
            "description": _read_first_desc_comment(child),
        })
    return {"directory": str(base), "actions": entries, "exists": True}


class ActionRunRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    args: list[str] | None = Field(default=None)


@router.post("/actions/run")
async def actions_run(req: ActionRunRequest) -> dict[str, Any]:
    """Execute one allowlisted script. Backs olympian_action_run.

    Gates: ZEUS_ACTIONS_ENABLED AND ZEUS_MCP_ALLOW_WRITE must both be true.
    Args are passed positionally with no shell interpretation. Stdout/stderr
    are capped at 64 KB each.
    """
    if not _actions_enabled():
        raise HTTPException(
            status_code=403,
            detail="ZEUS_ACTIONS_ENABLED is off; the action runner is disabled.",
        )
    if not _write_enabled():
        raise HTTPException(
            status_code=403,
            detail="ZEUS_MCP_ALLOW_WRITE is off; action execution is disabled.",
        )

    args = list(req.args or [])
    if len(args) > _ARG_MAX_COUNT:
        raise HTTPException(status_code=400, detail=f"too many args (max {_ARG_MAX_COUNT})")
    for a in args:
        if not isinstance(a, str):
            raise HTTPException(status_code=400, detail="all args must be strings")
        if len(a) > _ARG_MAX_LEN:
            raise HTTPException(status_code=400, detail=f"arg too long (max {_ARG_MAX_LEN} chars)")

    _aegis_check({"name": req.name, "args": " ".join(args)})

    script = _resolve_action(req.name)

    started = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            str(script),
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(_actions_dir()),
            env=os.environ.copy(),
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=_action_timeout(),
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        raise HTTPException(status_code=504, detail=f"action '{req.name}' timed out")
    except (FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=500, detail=f"action launch failed: {exc}") from exc

    duration_ms = int((time.monotonic() - started) * 1000)
    return {
        "name": req.name,
        "exit_code": proc.returncode,
        "duration_ms": duration_ms,
        "stdout": stdout.decode("utf-8", errors="replace")[:_OUTPUT_CAP_BYTES],
        "stderr": stderr.decode("utf-8", errors="replace")[:_OUTPUT_CAP_BYTES],
        "stdout_truncated": len(stdout) > _OUTPUT_CAP_BYTES,
        "stderr_truncated": len(stderr) > _OUTPUT_CAP_BYTES,
    }
