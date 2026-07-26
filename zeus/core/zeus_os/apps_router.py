# zeus/core/zeus_os/apps_router.py — Registry of launchable apps for the WM launcher.
#
# Phase 1 is a static list. Phase 2 layers an optional ~/.zeus/zeus-os/apps.json
# override so the user can pin custom iframe targets.
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter()


# Phase 1 default registry. The "kind" field tells the frontend which Svelte
# component to mount; "Placeholder" renders a "Not implemented yet" window so
# the launcher feels populated from day one.
_DEFAULT_APPS: list[dict[str, Any]] = [
    # Phase 1 + 1.5 — shell + core surfaces.
    {"id": "terminal", "title": "Terminal", "icon": "terminal", "kind": "Terminal"},
    {"id": "chat", "title": "Zeus Chat", "icon": "message-square", "kind": "Chat", "default_workspace": 1},
    {"id": "files", "title": "File Manager", "icon": "folder", "kind": "FileManager"},
    {"id": "sysmon", "title": "System Monitor", "icon": "activity", "kind": "SystemMonitor"},
    # Phase A — voice.
    {"id": "voice", "title": "Voice", "icon": "mic", "kind": "VoiceOrb", "default_workspace": 1},
    # Phase 2a — ported from the React frontend's data-dense surfaces.
    {"id": "tools", "title": "Tools", "icon": "tool", "kind": "Tools"},
    {"id": "jobs", "title": "Jobs", "icon": "clock", "kind": "Jobs"},
    {"id": "usage", "title": "Token Usage", "icon": "bar-chart", "kind": "TokenUsage"},
    {"id": "settings", "title": "Settings", "icon": "settings", "kind": "Settings"},
    # Phase 2b / 3 — still placeholders.
    {"id": "obsidian", "title": "Obsidian Vault", "icon": "book", "kind": "Obsidian"},
    {"id": "editor", "title": "Code Editor", "icon": "code", "kind": "Editor"},
    {"id": "ha", "title": "Home Assistant", "icon": "home", "kind": "HomeAssistant"},
    {"id": "linear", "title": "Linear", "icon": "kanban", "kind": "Linear"},
    {"id": "memories", "title": "Memories", "icon": "database", "kind": "Memories"},
    {"id": "knowledge", "title": "Knowledge", "icon": "library", "kind": "Knowledge"},
    {"id": "agents", "title": "Agents", "icon": "users", "kind": "Agents"},
    {"id": "swarm", "title": "Swarm", "icon": "git-merge", "kind": "Swarm"},
    {"id": "ingest", "title": "Ingest", "icon": "download", "kind": "Ingest"},
    {"id": "images", "title": "Image Viewer", "icon": "image", "kind": "Images"},
    {"id": "procs", "title": "Process Manager", "icon": "cpu", "kind": "Processes"},
    {"id": "network", "title": "Network", "icon": "wifi", "kind": "Network"},
    {"id": "notepad", "title": "Notepad", "icon": "edit-3", "kind": "Notepad"},
    {"id": "calendar", "title": "Calendar", "icon": "calendar", "kind": "Calendar"},
]


def _override_path() -> Path:
    base = os.getenv("ZEUS_OS_CONFIG_DIR", os.path.expanduser("~/.zeus/zeus-os"))
    return Path(base) / "apps.json"


@router.get("/apps")
def list_apps() -> dict[str, Any]:
    apps = list(_DEFAULT_APPS)
    override = _override_path()
    if override.is_file():
        try:
            extra = json.loads(override.read_text(encoding="utf-8"))
            if isinstance(extra, list):
                apps.extend(a for a in extra if isinstance(a, dict) and "id" in a)
        except (OSError, json.JSONDecodeError):
            pass
    return {"apps": apps}
