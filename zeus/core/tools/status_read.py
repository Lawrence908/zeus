# zeus/core/tools/status_read.py — Olympian status file reader
#
# Pulls the user-maintained status file (default ~/.zeus/status.md) via the
# /admin/status_file Core HTTP endpoint. cacheable=True with the default TTL
# is fine: the file changes on the order of minutes, and the cache TTL keeps
# us from hammering disk on chatty Telegram sessions.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.status_read")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="olympian_status_read",
    description=(
        "Read the user's status file (default ~/.zeus/status.md), which "
        "holds today's focus, current projects, and active blockers. Call "
        "this whenever the user asks 'what's on my plate?', 'what am I "
        "working on?', 'what's my status?', or anything else asking for a "
        "compact view of their current state. Quote relevant lines verbatim "
        "in your reply rather than paraphrasing. Returns the file contents "
        "as plain text. Zero argument; the path is server-configured."
    ),
    parameters={
        "type": "object",
        "properties": {},
    },
    aegis_policy="tool_arguments",
    timeout_seconds=5.0,
    cacheable=True,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{_core_url()}/admin/status_file")
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_status_read failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code == 404:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=(
                "No status file exists yet. The user can create one at "
                "~/.zeus/status.md, or set ZEUS_STATUS_AUTOCREATE=1 to "
                "treat a missing file as empty."
            ),
            is_error=True,
        )
    if r.status_code >= 400:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_status_read got HTTP {r.status_code}: {r.text[:200]!r}",
            is_error=True,
        )
    data = r.json() or {}
    content = str(data.get("content") or "").strip()
    path = str(data.get("path") or "")
    if not content:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"Status file at {path} is empty.",
        )
    return ToolResult(call_id="", name=_SPEC.name, content=content)


def register() -> None:
    """Register olympian_status_read. Always available; gracefully degrades if file is missing."""
    registry.register(_SPEC, _handler)
    logger.info("olympian_status_read registered")
