# zeus/core/tools/file_search.py — Olympian ripgrep search
#
# Wraps POST /vault/search. Not cacheable: the LLM may want to vary the
# pattern slightly, and the cost of re-running rg against a small set of
# allowlisted roots is low. Aegis policy `file_access` rejects shell
# metacharacters and traversal patterns.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.file_search")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="olympian_file_search",
    description=(
        "Full-text search the user's notes / vault using ripgrep across "
        "ZEUS_FILE_READ_ROOTS. Much faster and more exact than vector "
        "search for 'did I write about X?' or 'find my notes mentioning Y'. "
        "Returns up to 50 path/line/text matches by default. Pattern is a "
        "regex unless fixed_strings=true. Case-insensitive by default. "
        "After this returns, call olympian_file_read on a promising path "
        "to get the full file."
    ),
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regex pattern (or literal if fixed_strings=true).",
            },
            "root": {
                "type": "string",
                "description": "Optional single root from the allowlist; omit to search all.",
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 500,
                "description": "Default 50.",
            },
            "case_sensitive": {"type": "boolean", "description": "Default false."},
            "fixed_strings": {
                "type": "boolean",
                "description": "Treat pattern as a literal string. Default false.",
            },
        },
        "required": ["pattern"],
    },
    aegis_policy="file_access",
    timeout_seconds=15.0,
    cacheable=False,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    pattern = str(args.get("pattern") or "").strip()
    if not pattern:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="olympian_file_search requires a non-empty 'pattern'.",
            is_error=True,
        )
    payload: dict[str, Any] = {
        "pattern": pattern,
        "max_results": max(1, min(500, int(args.get("max_results") or 50))),
        "case_sensitive": bool(args.get("case_sensitive") or False),
        "fixed_strings": bool(args.get("fixed_strings") or False),
    }
    root = str(args.get("root") or "").strip()
    if root:
        payload["root"] = root

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(f"{_core_url()}/vault/search", json=payload)
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_file_search failed to reach Zeus core: {exc}",
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
            content=f"olympian_file_search HTTP {r.status_code}: {str(detail)[:300]}",
            is_error=True,
        )

    data = r.json() or {}
    matches = data.get("matches") or []
    if not matches:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"No matches for pattern {pattern!r} in allowlisted roots.",
        )
    lines = [f"{m.get('path')}:{m.get('line')}: {m.get('text')}" for m in matches]
    suffix = ""
    if data.get("truncated"):
        suffix = f"\n\n(truncated at {len(matches)} matches; refine the pattern for more)"
    return ToolResult(
        call_id="",
        name=_SPEC.name,
        content="\n".join(lines) + suffix,
    )


def register() -> None:
    """Register olympian_file_search."""
    registry.register(_SPEC, _handler)
    logger.info("olympian_file_search registered")
