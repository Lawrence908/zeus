# zeus/core/zeus_os/vault_router.py — Obsidian vault tree + wikilink index.
#
# Operates on a single vault root configured by ZEUS_OS_OBSIDIAN_VAULT.
# Defaults to the same livesync mirror that the file manager already exposes.
# Read-only; writes go through the existing /zeus-os/fs/write surface when the
# vault root is also in ZEUS_OS_FS_WRITE_ROOTS.
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from zeus.core._fs import allowlisted_roots, resolve_in_allowlist

logger = logging.getLogger("zeus.zeus_os.vault")

router = APIRouter()

_DEFAULT_VAULT = "/home/chris/data/headless-obsidian-vault"


def _vault_root() -> Path:
    raw = os.getenv("ZEUS_OS_OBSIDIAN_VAULT", _DEFAULT_VAULT)
    p = Path(os.path.expanduser(raw)).resolve(strict=False)
    return p


def _check_vault_in_allowlist() -> Path:
    root = _vault_root()
    roots = allowlisted_roots("ZEUS_OS_FS_ROOTS", "")
    if not roots:
        raise HTTPException(status_code=503, detail="ZEUS_OS_FS_ROOTS is empty")
    # vault must be inside an allowlisted read root (we resolve the entire
    # vault path containment up front so subsequent file reads avoid the
    # symlink check overhead).
    for r in roots:
        try:
            root.relative_to(r)
        except ValueError:
            continue
        if not root.exists():
            raise HTTPException(
                status_code=503,
                detail=f"vault path {root} does not exist on disk",
            )
        return root
    raise HTTPException(
        status_code=403,
        detail=(
            f"vault {root} is not inside ZEUS_OS_FS_ROOTS — broaden the env "
            "var to include it before opening the Obsidian viewer."
        ),
    )


# Files we don't want surfaced in the tree even if they live under the vault.
_HIDDEN_PREFIXES = (".",)
_HIDDEN_DIRS = {
    ".obsidian",
    ".trash",
    "headless-obsidian-vault-fa1dd4bf-4a8c6eb0d7aad165-livesync-v2",
}
_DOC_EXTS = {".md", ".markdown"}
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
_OTHER_EXTS = {".pdf", ".canvas", ".excalidraw", ".css"}


def _kind_for(name: str) -> str:
    ext = Path(name).suffix.lower()
    if ext in _DOC_EXTS:
        return "doc"
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _OTHER_EXTS:
        return "asset"
    return "other"


def _walk_tree(root: Path) -> dict[str, Any]:
    """Return a recursive {name, kind, path, children?} dict rooted at `root`."""

    def rec(p: Path) -> dict[str, Any] | None:
        rel = p.relative_to(root).as_posix()
        name = p.name
        if any(name.startswith(prefix) for prefix in _HIDDEN_PREFIXES):
            return None
        if name in _HIDDEN_DIRS:
            return None
        if p.is_dir():
            children: list[dict[str, Any]] = []
            try:
                with os.scandir(p) as it:
                    items = list(it)
            except OSError:
                return None
            items.sort(key=lambda d: (not d.is_dir(follow_symlinks=False), d.name.lower()))
            for de in items:
                child = rec(Path(de.path))
                if child is not None:
                    children.append(child)
            if not children:
                return None
            return {"kind": "dir", "name": name, "path": rel or "", "children": children}
        if p.is_file():
            kind = _kind_for(name)
            if kind == "other":
                return None
            try:
                st = p.stat()
            except OSError:
                return None
            return {
                "kind": kind,
                "name": name,
                "path": rel,
                "size": st.st_size,
                "mtime": st.st_mtime,
            }
        return None

    out = rec(root) or {"kind": "dir", "name": root.name, "path": "", "children": []}
    out["path"] = ""
    return out


@router.get("/vault/tree")
def vault_tree() -> dict[str, Any]:
    root = _check_vault_in_allowlist()
    tree = _walk_tree(root)
    return {"root": str(root), "tree": tree}


@router.get("/vault/index")
def vault_index() -> dict[str, Any]:
    """Build a {title → [relative paths]} index for wikilink resolution.

    Title is the file stem; multiple matches are surfaced so the client can
    resolve `[[Foo]]` against the closest one when ambiguous.
    """
    root = _check_vault_in_allowlist()
    by_title: dict[str, list[str]] = {}
    paths: list[str] = []
    for dirpath, dirs, files in os.walk(root):
        # Prune hidden dirs in place.
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in _HIDDEN_DIRS]
        for fname in files:
            if Path(fname).suffix.lower() not in _DOC_EXTS:
                continue
            rel = Path(dirpath).joinpath(fname).resolve().relative_to(root).as_posix()
            stem = Path(fname).stem
            by_title.setdefault(stem, []).append(rel)
            paths.append(rel)
    return {"root": str(root), "by_title": by_title, "paths": sorted(paths)}


_WIKILINK_RE = re.compile(r"!?\[\[([^\[\]\|#]+)(?:#([^\[\]\|]+))?(?:\|([^\[\]]+))?\]\]")
_OBSIDIAN_IMG_RE = re.compile(r"!\[\[([^\[\]\|]+)\]\]")


def _rewrite_obsidian_links(content: str) -> str:
    """Convert Obsidian wikilinks to standard markdown.

    `[[Note]]` → `[Note](obsidian://Note)`     — SPA-intercepted, routes
                                                 through the title index.
    `[[Note|alias]]` → `[alias](obsidian://Note)`
    `![[image.png]]` → `![image.png](/zeus-os/vault/asset?path=image.png)`
                                                 — direct URL, browser fetches
                                                 the image via the asset
                                                 endpoint's basename fallback.

    Note links keep the synthetic `obsidian://` scheme so the SPA's click
    delegate can resolve `[[Foo]]` to the actual relative path; asset
    embeds get a real URL so the `<img>` tag works without any DOM
    post-processing.
    """
    from urllib.parse import quote as _q

    def repl(m: re.Match[str]) -> str:
        whole = m.group(0)
        target = m.group(1).strip()
        alias = m.group(3)
        if whole.startswith("!"):
            return f"![{target}](/zeus-os/vault/asset?path={_q(target, safe='/')})"
        label = (alias or target).strip()
        return f"[{label}](obsidian://{target})"

    return _WIKILINK_RE.sub(repl, content)


@router.get("/vault/file")
def vault_file(path: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Read a vault doc and pre-rewrite Obsidian wikilinks.

    Returns the rewritten markdown plus the original bytes so the client can
    show "raw" if it wants. Capped at ~1 MB.
    """
    root = _check_vault_in_allowlist()
    # Compose the absolute path from vault root + relative `path`.
    raw_path = (root / path).resolve(strict=False)
    try:
        raw_path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="path escapes vault root") from exc
    if not raw_path.is_file():
        raise HTTPException(status_code=404, detail="not a regular file")
    if raw_path.suffix.lower() not in _DOC_EXTS:
        raise HTTPException(status_code=400, detail="not a markdown file")
    try:
        size = raw_path.stat().st_size
        if size > 1_000_000:
            raise HTTPException(status_code=413, detail="file too large")
        raw = raw_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"read failed: {exc}") from exc
    # Confirm symlinked containment one more time via the shared resolver so
    # we use the same security stance as the rest of /zeus-os/fs/*.
    resolve_in_allowlist(str(raw_path), allowlisted_roots("ZEUS_OS_FS_ROOTS", ""))
    return {
        "path": path,
        "abs_path": str(raw_path),
        "content": raw,
        "rewritten": _rewrite_obsidian_links(raw),
        "size_bytes": size,
    }


_RAW_MAX_BYTES = 25 * 1024 * 1024  # generous for vault PDFs / canvas exports


@router.get("/vault/asset")
def vault_asset(path: str = Query(..., min_length=1)) -> FileResponse:
    """Serve a vault asset (image / pdf / etc.) by relative path.

    Backs the Obsidian Viewer's inline image rendering. Path must resolve
    inside the vault root. Returned via FileResponse so the browser gets
    a proper Content-Type from the filename.
    """
    root = _check_vault_in_allowlist()
    raw_path = (root / path).resolve(strict=False)
    try:
        raw_path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="path escapes vault root") from exc
    if not raw_path.is_file():
        # Best-effort fallback: maybe the user passed just a basename — scan
        # for the first match. Wikilink-style ![[image.png]] embeds usually
        # carry the bare name.
        for candidate in root.rglob(Path(path).name):
            if candidate.is_file():
                raw_path = candidate
                break
        else:
            raise HTTPException(status_code=404, detail="not a regular file")
    try:
        if raw_path.stat().st_size > _RAW_MAX_BYTES:
            raise HTTPException(status_code=413, detail="asset too large")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"stat failed: {exc}") from exc
    return FileResponse(str(raw_path))
