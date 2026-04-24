# zeus/core/vault.py — Read-side filesystem access for the Olympian tool pack
#
# Two endpoints back olympian_file_read and olympian_file_search:
#   GET  /vault/file?path=<...>            single-file read
#   POST /vault/search   {pattern, ...}    ripgrep across allowlist roots
#
# Allowlist enforcement is non-negotiable: every path must canonicalise into
# one of the ZEUS_FILE_READ_ROOTS entries after symlink resolution. Symlink
# escape is the typical attack here; we resolve to a real path and re-check
# containment.
from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from zeus.safety.policy_engine import AegisPolicyEngine, aegis_enabled

logger = logging.getLogger("zeus.vault")

router = APIRouter(tags=["vault"])

_DEFAULT_ROOTS = "~/.zeus,~/notes"
_MAX_FILE_BYTES = 1 * 1024 * 1024  # 1 MB read cap; status / inbox / notes only
_RG_BIN = "rg"
_RG_TIMEOUT_SEC = 10.0
_DEFAULT_MAX_RESULTS = 50
_HARD_MAX_RESULTS = 500


def _allowlisted_roots() -> list[Path]:
    raw = os.getenv("ZEUS_FILE_READ_ROOTS", _DEFAULT_ROOTS)
    out: list[Path] = []
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        try:
            p = Path(os.path.expanduser(entry)).resolve(strict=False)
        except (OSError, RuntimeError):
            continue
        out.append(p)
    return out


def _resolve_in_allowlist(target_str: str) -> Path:
    """Resolve target into a real path that is contained within one of the
    allowlist roots. Raises HTTPException on any escape attempt or on a
    non-existent target.
    """
    if not target_str or len(target_str) > 4096:
        raise HTTPException(status_code=400, detail="path is required and must be reasonable length")
    roots = _allowlisted_roots()
    if not roots:
        raise HTTPException(status_code=503, detail="ZEUS_FILE_READ_ROOTS is empty")
    try:
        candidate = Path(os.path.expanduser(target_str)).resolve(strict=True)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="path not found") from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=f"invalid path: {exc}") from exc
    for root in roots:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        return candidate
    raise HTTPException(status_code=400, detail="path is outside the allowlisted roots")


def _aegis_check(policy: str, payload: dict[str, Any]) -> None:
    if not aegis_enabled() or not payload:
        return
    engine = AegisPolicyEngine(policy=policy)
    outcome = engine.evaluate_payload(payload, policy_name=policy)
    if outcome.status == "rejected":
        raise HTTPException(status_code=400, detail=outcome.message or "Aegis blocked payload.")


@router.get("/vault/file")
async def vault_file_read(path: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Read a file from the allowlisted vault roots. Backs olympian_file_read."""
    _aegis_check("file_access", {"path": path})
    resolved = _resolve_in_allowlist(path)
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="path is not a regular file")
    try:
        size = resolved.stat().st_size
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"stat failed: {exc}") from exc
    if size > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"file is {size} bytes; cap is {_MAX_FILE_BYTES}",
        )
    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
        mtime = resolved.stat().st_mtime
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"read failed: {exc}") from exc
    return {
        "path": str(resolved),
        "content": content,
        "size_bytes": size,
        "mtime": mtime,
    }


class VaultSearchRequest(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=512)
    root: str | None = Field(default=None, description="Optional single root from the allowlist; omit to search all.")
    max_results: int = Field(default=_DEFAULT_MAX_RESULTS, ge=1, le=_HARD_MAX_RESULTS)
    case_sensitive: bool = Field(default=False)
    fixed_strings: bool = Field(default=False, description="If True, treat pattern as a literal string, not a regex.")


@router.post("/vault/search")
async def vault_search(req: VaultSearchRequest) -> dict[str, Any]:
    """ripgrep across allowlist roots. Backs olympian_file_search."""
    _aegis_check("file_access", {"pattern": req.pattern, "root": req.root or ""})

    if shutil.which(_RG_BIN) is None:
        raise HTTPException(
            status_code=503,
            detail="ripgrep (rg) is not installed in this Zeus container. "
                   "Add it to the image or set ZEUS_FILE_SEARCH_DISABLED=1.",
        )

    roots = _allowlisted_roots()
    if not roots:
        raise HTTPException(status_code=503, detail="ZEUS_FILE_READ_ROOTS is empty")

    if req.root:
        chosen = _resolve_in_allowlist(req.root)
        if not chosen.is_dir():
            raise HTTPException(status_code=400, detail="root must be a directory")
        search_paths = [str(chosen)]
    else:
        search_paths = [str(r) for r in roots if r.exists() and r.is_dir()]
        if not search_paths:
            raise HTTPException(status_code=503, detail="no allowlisted roots exist on disk")

    args = [
        _RG_BIN,
        "--vimgrep",
        "--no-heading",
        "--max-count", str(req.max_results),
        "--max-filesize", "5M",
    ]
    if not req.case_sensitive:
        args.append("--ignore-case")
    if req.fixed_strings:
        args.append("--fixed-strings")
    args.append("--")
    args.append(req.pattern)
    args.extend(search_paths)

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=_RG_TIMEOUT_SEC)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=504, detail="ripgrep timed out") from exc
    except (FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=500, detail=f"ripgrep failed: {exc}") from exc

    rc = proc.returncode
    # ripgrep exit codes: 0 = matches, 1 = no matches, 2 = error.
    if rc not in (0, 1):
        msg = stderr.decode("utf-8", errors="replace").strip()[:300]
        raise HTTPException(status_code=500, detail=f"ripgrep error (rc={rc}): {msg}")

    matches: list[dict[str, Any]] = []
    for line in stdout.decode("utf-8", errors="replace").splitlines():
        if not line:
            continue
        # vimgrep format: path:line:col:text
        parts = line.split(":", 3)
        if len(parts) != 4:
            continue
        try:
            matches.append({
                "path": parts[0],
                "line": int(parts[1]),
                "column": int(parts[2]),
                "text": parts[3][:300],
            })
        except ValueError:
            continue
        if len(matches) >= req.max_results:
            break

    return {
        "pattern": req.pattern,
        "match_count": len(matches),
        "matches": matches,
        "truncated": len(matches) >= req.max_results,
    }
