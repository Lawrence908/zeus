# zeus/core/_fs.py — Shared filesystem helpers used by /vault and /zeus-os/fs
#
# Two consumers, two allowlists, one resolver:
#   - vault.py uses ZEUS_FILE_READ_ROOTS for the LLM tool pack.
#   - zeus_os/fs_router.py uses ZEUS_OS_FS_ROOTS for the user-facing WM file
#     manager. Both call resolve_in_allowlist() and ripgrep_search() here.
#
# Symlink escape is the typical attack vector here; targets are fully resolved
# (strict=True) and then re-checked against the resolved roots.
from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Any

from fastapi import HTTPException

logger = logging.getLogger("zeus.fs")

_RG_BIN = "rg"
_RG_TIMEOUT_SEC = 10.0


def allowlisted_roots(env_var: str, default: str = "") -> list[Path]:
    """Parse a comma-separated env var into a list of resolved Path roots.

    Non-existent roots are still included (resolve(strict=False)) so the caller
    can distinguish "misconfigured" (empty) from "configured but root missing".
    """
    raw = os.getenv(env_var, default)
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


def resolve_in_allowlist(target_str: str, roots: list[Path]) -> Path:
    """Resolve target into a real path inside one of the allowlist roots.

    Raises HTTPException on missing target, escape attempt, or empty allowlist.
    """
    if not target_str or len(target_str) > 4096:
        raise HTTPException(status_code=400, detail="path is required and must be reasonable length")
    if not roots:
        raise HTTPException(status_code=503, detail="filesystem allowlist is empty")
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


def resolve_for_write(target_str: str, write_roots: list[Path]) -> Path:
    """Resolve a target whose parent must already exist inside a writable root.

    Unlike resolve_in_allowlist, the target itself may not exist yet (we're
    about to create it). The *parent directory* is resolved strictly and must
    sit inside one of the write roots.
    """
    if not target_str or len(target_str) > 4096:
        raise HTTPException(status_code=400, detail="path is required and must be reasonable length")
    if not write_roots:
        raise HTTPException(status_code=503, detail="filesystem write allowlist is empty")
    candidate = Path(os.path.expanduser(target_str))
    parent = candidate.parent
    try:
        parent_resolved = parent.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="parent directory does not exist") from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=f"invalid path: {exc}") from exc
    for root in write_roots:
        try:
            parent_resolved.relative_to(root)
        except ValueError:
            continue
        return parent_resolved / candidate.name
    raise HTTPException(status_code=400, detail="path is outside the writable roots")


async def ripgrep_search(
    pattern: str,
    search_paths: list[str],
    *,
    max_results: int = 50,
    case_sensitive: bool = False,
    fixed_strings: bool = False,
    timeout: float = _RG_TIMEOUT_SEC,
) -> dict[str, Any]:
    """Run ripgrep across one or more roots; return {match_count, matches, truncated}.

    Raises HTTPException on missing rg binary, timeout, or non-trivial rg error.
    Match dicts: {path, line, column, text} (text capped at 300 chars).
    """
    if shutil.which(_RG_BIN) is None:
        raise HTTPException(
            status_code=503,
            detail="ripgrep (rg) is not installed in this Zeus container.",
        )
    if not search_paths:
        raise HTTPException(status_code=503, detail="no allowlisted roots exist on disk")

    args = [
        _RG_BIN,
        "--vimgrep",
        "--no-heading",
        "--max-count", str(max_results),
        "--max-filesize", "5M",
    ]
    if not case_sensitive:
        args.append("--ignore-case")
    if fixed_strings:
        args.append("--fixed-strings")
    args.append("--")
    args.append(pattern)
    args.extend(search_paths)

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=504, detail="ripgrep timed out") from exc
    except (FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=500, detail=f"ripgrep failed: {exc}") from exc

    rc = proc.returncode
    # 0 = matches, 1 = no matches, 2 = error
    if rc not in (0, 1):
        msg = stderr.decode("utf-8", errors="replace").strip()[:300]
        raise HTTPException(status_code=500, detail=f"ripgrep error (rc={rc}): {msg}")

    matches: list[dict[str, Any]] = []
    for line in stdout.decode("utf-8", errors="replace").splitlines():
        if not line:
            continue
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
        if len(matches) >= max_results:
            break

    return {
        "match_count": len(matches),
        "matches": matches,
        "truncated": len(matches) >= max_results,
    }
