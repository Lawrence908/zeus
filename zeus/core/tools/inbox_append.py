# zeus/core/tools/inbox_append.py — Olympian capture tool
#
# Wraps POST /inbox/append. Write side: gated server-side by
# ZEUS_MCP_ALLOW_WRITE. cacheable=False is the only correct setting for any
# tool with side effects.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.inbox_append")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="olympian_inbox_append",
    description=(
        "Capture a one-line note to the user's inbox file (default "
        "~/.zeus/inbox.md). Use for 'remember this for later', 'add to my "
        "inbox', 'note that X', or anytime the user wants something captured "
        "without interrupting the conversation. Optional tags become #tag "
        "tokens at the end of the line. Each entry is timestamped and "
        "atomically appended. The inbox is the user's own; do not summarise "
        "or re-phrase the captured text unless they explicitly ask."
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The captured note (one line; newlines collapsed).",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags (no leading #, no whitespace).",
            },
        },
        "required": ["text"],
    },
    aegis_policy="file_access",
    timeout_seconds=10.0,
    cacheable=False,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    text = str(args.get("text") or "").strip()
    if not text:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="olympian_inbox_append requires non-empty 'text'.",
            is_error=True,
        )
    tags = args.get("tags") or []
    if not isinstance(tags, list):
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="olympian_inbox_append: 'tags' must be a list of strings.",
            is_error=True,
        )
    payload: dict[str, Any] = {"text": text}
    if tags:
        payload["tags"] = [str(t) for t in tags]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{_core_url()}/inbox/append", json=payload)
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_inbox_append failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code >= 400:
        try:
            detail = (r.json() or {}).get("detail", r.text)
        except ValueError:
            detail = r.text
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_inbox_append HTTP {r.status_code}: {str(detail)[:300]}",
            is_error=True,
        )
    data = r.json() or {}
    line = str(data.get("appended_line") or "").strip()
    path = str(data.get("path") or "")
    return ToolResult(
        call_id="",
        name=_SPEC.name,
        content=f"Appended to {path}:\n{line}",
    )


def register() -> None:
    """Register olympian_inbox_append. Server-side write gate enforces ZEUS_MCP_ALLOW_WRITE."""
    registry.register(_SPEC, _handler)
    logger.info("olympian_inbox_append registered")
