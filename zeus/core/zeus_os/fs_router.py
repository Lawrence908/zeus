# zeus/core/zeus_os/fs_router.py — WM file manager filesystem access.
#
# Uses a SEPARATE allowlist (ZEUS_OS_FS_ROOTS) from the LLM-facing vault router
# so the user can broaden Zeus OS's filesystem view without widening what tools
# called from the chat model can read. Shared resolver + ripgrep wrapper live
# in zeus.core._fs.
from __future__ import annotations

import logging
import os
import stat as stat_mod
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from zeus.core._fs import (
    allowlisted_roots,
    resolve_for_write,
    resolve_in_allowlist,
    ripgrep_search,
)

logger = logging.getLogger("zeus.zeus_os.fs")

router = APIRouter()

_ROOTS_ENV = "ZEUS_OS_FS_ROOTS"
_WRITE_ROOTS_ENV = "ZEUS_OS_FS_WRITE_ROOTS"
_DEFAULT_ROOTS = "/app/zeus,/app/zeus/data,/root/.zeus"
_DEFAULT_WRITE_ROOTS = "/root/.zeus"
_MAX_READ_BYTES = 1 * 1024 * 1024  # 1 MB
_MAX_RAW_BYTES = 20 * 1024 * 1024  # 20 MB for image / binary previews
_MAX_WRITE_BYTES = 5 * 1024 * 1024  # 5 MB


def _read_roots() -> list[Path]:
    return allowlisted_roots(_ROOTS_ENV, _DEFAULT_ROOTS)


def _write_roots() -> list[Path]:
    return allowlisted_roots(_WRITE_ROOTS_ENV, _DEFAULT_WRITE_ROOTS)


def _write_enabled() -> bool:
    return os.getenv("ZEUS_OS_FS_WRITE_ENABLED", "0").strip().lower() in ("1", "true", "yes", "on")


def _entry_kind(p: Path) -> str:
    try:
        st = p.lstat()
    except OSError:
        return "unknown"
    mode = st.st_mode
    if stat_mod.S_ISLNK(mode):
        return "link"
    if stat_mod.S_ISDIR(mode):
        return "dir"
    if stat_mod.S_ISREG(mode):
        return "file"
    return "other"


@router.get("/fs/roots")
def fs_roots() -> dict[str, Any]:
    """List configured filesystem roots so the WM can show top-level mountpoints."""
    return {
        "read_roots": [str(r) for r in _read_roots() if r.exists()],
        "write_roots": [str(r) for r in _write_roots() if r.exists()],
        "write_enabled": _write_enabled(),
    }


@router.get("/fs/list")
def fs_list(path: str = Query(..., min_length=1)) -> dict[str, Any]:
    resolved = resolve_in_allowlist(path, _read_roots())
    if not resolved.is_dir():
        raise HTTPException(status_code=400, detail="path is not a directory")
    entries: list[dict[str, Any]] = []
    try:
        with os.scandir(resolved) as it:
            for de in it:
                try:
                    st = de.stat(follow_symlinks=False)
                except OSError:
                    continue
                kind = "dir" if de.is_dir(follow_symlinks=False) else (
                    "link" if de.is_symlink() else (
                        "file" if de.is_file(follow_symlinks=False) else "other"
                    )
                )
                entries.append({
                    "name": de.name,
                    "kind": kind,
                    "size": st.st_size,
                    "mtime": st.st_mtime,
                })
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"listdir failed: {exc}") from exc
    entries.sort(key=lambda e: (e["kind"] != "dir", e["name"].lower()))
    return {"path": str(resolved), "entries": entries}


@router.get("/fs/file")
def fs_read(path: str = Query(..., min_length=1)) -> dict[str, Any]:
    resolved = resolve_in_allowlist(path, _read_roots())
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="path is not a regular file")
    try:
        size = resolved.stat().st_size
        mtime = resolved.stat().st_mtime
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"stat failed: {exc}") from exc
    truncated = size > _MAX_READ_BYTES
    try:
        with open(resolved, "rb") as fh:
            raw = fh.read(_MAX_READ_BYTES)
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


@router.get("/fs/raw")
def fs_raw(path: str = Query(..., min_length=1)) -> FileResponse:
    """Serve a file's raw bytes (no UTF-8 round-trip). Backs the WM File Manager
    image preview. Capped at _MAX_RAW_BYTES to keep the browser from chewing
    on something unexpectedly enormous; for normal images and assets this is
    far above what we'd ever serve.
    """
    resolved = resolve_in_allowlist(path, _read_roots())
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="path is not a regular file")
    try:
        size = resolved.stat().st_size
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"stat failed: {exc}") from exc
    if size > _MAX_RAW_BYTES:
        raise HTTPException(status_code=413, detail="file too large for raw preview")
    return FileResponse(str(resolved))


class FsWriteRequest(BaseModel):
    path: str = Field(..., min_length=1)
    content: str = Field(..., max_length=_MAX_WRITE_BYTES)


@router.post("/fs/write")
def fs_write(body: FsWriteRequest) -> dict[str, Any]:
    if not _write_enabled():
        raise HTTPException(status_code=403, detail="ZEUS_OS_FS_WRITE_ENABLED is off")
    target = resolve_for_write(body.path, _write_roots())
    parent = target.parent
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=parent, delete=False, suffix=".tmp"
        ) as fh:
            fh.write(body.content)
            tmp_name = fh.name
        os.replace(tmp_name, target)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"write failed: {exc}") from exc
    try:
        size = target.stat().st_size
    except OSError:
        size = len(body.content)
    return {"ok": True, "path": str(target), "size_bytes": size}


class FsSearchRequest(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=512)
    root: str | None = Field(default=None)
    max_results: int = Field(default=50, ge=1, le=500)
    case_sensitive: bool = False
    fixed_strings: bool = False


@router.post("/fs/search")
async def fs_search(req: FsSearchRequest) -> dict[str, Any]:
    roots = _read_roots()
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
