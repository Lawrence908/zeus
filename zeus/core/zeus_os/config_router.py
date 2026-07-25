# zeus/core/zeus_os/config_router.py — User preferences persistence.
#
# Stored at $ZEUS_OS_CONFIG_DIR/config.json (default ~/.zeus/zeus-os/config.json).
# `~/.zeus` is already bind-mounted writable into zeus-core in compose.
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException

router = APIRouter()


_DEFAULT_CONFIG: dict[str, Any] = {
    "theme": "catppuccin-mocha",
    "modifier": "Meta",  # or "Alt"
    "gap_px": 8,
    "pinned": {
        # workspace_id (1-10) → default app id when empty
        "1": "chat",
    },
    "keybinds": {},  # user overrides, merged on top of defaults in the client
}


def _config_path() -> Path:
    base = os.getenv("ZEUS_OS_CONFIG_DIR", os.path.expanduser("~/.zeus/zeus-os"))
    p = Path(base)
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return p / "config.json"


@router.get("/config")
def get_config() -> dict[str, Any]:
    p = _config_path()
    if not p.is_file():
        return _DEFAULT_CONFIG
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return _DEFAULT_CONFIG
        # Merge over defaults so newly-added keys appear with sensible values.
        merged = {**_DEFAULT_CONFIG, **data}
        return merged
    except (OSError, json.JSONDecodeError):
        return _DEFAULT_CONFIG


@router.put("/config")
def put_config(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="body must be an object")
    p = _config_path()
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=p.parent, delete=False, suffix=".tmp"
        ) as fh:
            json.dump(body, fh, indent=2, sort_keys=True)
            tmp_name = fh.name
        os.replace(tmp_name, p)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"write failed: {exc}") from exc
    return {"ok": True, "path": str(p)}
