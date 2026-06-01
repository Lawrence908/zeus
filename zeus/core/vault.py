# zeus/core/vault.py — Read-side filesystem access for the Olympian tool pack
#
# Two endpoints back olympian_file_read and olympian_file_search:
#   GET  /vault/file?path=<...>            single-file read
#   POST /vault/search   {pattern, ...}    ripgrep across allowlist roots
#
# Allowlist enforcement is non-negotiable: every path must canonicalise into
# one of the ZEUS_FILE_READ_ROOTS entries after symlink resolution. The
# resolver and ripgrep wrapper live in zeus.core._fs so the user-facing
# /zeus-os/fs/* router shares the same implementation with a different
# (broader) allowlist.
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from zeus.core._fs import allowlisted_roots, resolve_in_allowlist, ripgrep_search
from zeus.safety.policy_engine import AegisPolicyEngine, aegis_enabled

logger = logging.getLogger("zeus.vault")

router = APIRouter(tags=["vault"])

_ROOTS_ENV = "ZEUS_FILE_READ_ROOTS"
_DEFAULT_ROOTS = "~/.zeus,~/notes"
# 64 KB ≈ 16k tokens — fits comfortably in an 8k-ctx Ollama call and still
# covers any reasonable note. Larger files are truncated server-side with a
# `truncated: true` flag in the response so the LLM knows it didn't see the
# whole thing.
_MAX_FILE_BYTES = 64 * 1024
_DEFAULT_MAX_RESULTS = 50
_HARD_MAX_RESULTS = 500


def _vault_roots():
    return allowlisted_roots(_ROOTS_ENV, _DEFAULT_ROOTS)


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
    resolved = resolve_in_allowlist(path, _vault_roots())
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="path is not a regular file")
    try:
        size = resolved.stat().st_size
        mtime = resolved.stat().st_mtime
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"stat failed: {exc}") from exc
    truncated = size > _MAX_FILE_BYTES
    try:
        with open(resolved, "rb") as fh:
            raw = fh.read(_MAX_FILE_BYTES)
        content = raw.decode("utf-8", errors="replace")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"read failed: {exc}") from exc
    return {
        "path": str(resolved),
        "content": content,
        "size_bytes": size,
        "bytes_returned": len(raw),
        "truncated": truncated,
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

    roots = _vault_roots()
    if not roots:
        raise HTTPException(status_code=503, detail=f"{_ROOTS_ENV} is empty")

    if req.root:
        chosen = resolve_in_allowlist(req.root, roots)
        if not chosen.is_dir():
            raise HTTPException(status_code=400, detail="root must be a directory")
        search_paths = [str(chosen)]
    else:
        search_paths = [str(r) for r in roots if r.exists() and r.is_dir()]

    result = await ripgrep_search(
        req.pattern,
        search_paths,
        max_results=req.max_results,
        case_sensitive=req.case_sensitive,
        fixed_strings=req.fixed_strings,
    )
    return {"pattern": req.pattern, **result}
