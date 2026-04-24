# zeus/core/tools/file_read.py — Olympian single-file read
#
# Wraps GET /vault/file. Not cacheable: the file may have changed since the
# last call (it is the user's notes / status / config), and the LLM needs
# the freshest contents.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.file_read")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="olympian_file_read",
    description=(
        "Read one file from the user's allowlisted vault roots (notes, "
        "status, configs). Use after olympian_file_search has identified a "
        "promising path, or when the user names a specific file. Path must "
        "resolve inside ZEUS_FILE_READ_ROOTS; traversal and symlink escapes "
        "are rejected. Returns the file's full text (1 MB cap)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or ~-expanded path inside an allowlisted root.",
            },
        },
        "required": ["path"],
    },
    aegis_policy="file_access",
    timeout_seconds=10.0,
    cacheable=False,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    path = str(args.get("path") or "").strip()
    if not path:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="olympian_file_read requires a non-empty 'path'.",
            is_error=True,
        )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{_core_url()}/vault/file",
                params={"path": path},
            )
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_file_read failed to reach Zeus core: {exc}",
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
            content=f"olympian_file_read HTTP {r.status_code}: {str(detail)[:300]}",
            is_error=True,
        )
    data = r.json() or {}
    content = str(data.get("content") or "")
    resolved = str(data.get("path") or path)
    body = f"# {resolved}\n\n{content}"
    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register() -> None:
    """Register olympian_file_read."""
    registry.register(_SPEC, _handler)
    logger.info("olympian_file_read registered")
