# zeus/core/tools/newsletter_latest.py — Most recent newsletter digest
#
# Wraps GET /api/newsletter/digests?limit=1. Cacheable=True with the default
# TTL keeps repeat queries cheap; the underlying digest only updates when
# the newsletter pipeline runs.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.newsletter_latest")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="zeus_newsletter_latest",
    description=(
        "Return the most recent newsletter digest entry (TLDR, etc.) in "
        "compact form. Use when the user asks 'what's in today's "
        "newsletter?', 'summarize the latest digest', or similar. Reads "
        "from the digest manifest, not the live mailbox; freshness depends "
        "on the newsletter ingest pipeline."
    ),
    parameters={
        "type": "object",
        "properties": {},
    },
    aegis_policy="tool_arguments",
    timeout_seconds=10.0,
    cacheable=True,
)


def _format_digest(d: dict[str, Any]) -> str:
    title = str(d.get("title") or d.get("source") or "newsletter").strip()
    generated = str(d.get("generated_at") or "").strip()
    summary = str(d.get("summary") or "").strip()
    advice = d.get("advice") or []
    lines = [f"# {title}", f"generated: {generated}"]
    if summary:
        lines.append("")
        lines.append(summary)
    if advice:
        lines.append("")
        lines.append("Advice:")
        for a in advice[:8]:
            lines.append(f"- {str(a)[:200]}")
    return "\n".join(lines)


async def _handler(args: dict[str, Any]) -> ToolResult:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{_core_url()}/api/newsletter/digests",
                params={"limit": 1},
            )
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"zeus_newsletter_latest failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code >= 400:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"zeus_newsletter_latest HTTP {r.status_code}: {r.text[:200]!r}",
            is_error=True,
        )
    data = r.json() or {}
    digests = data.get("digests") or []
    if not digests:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="No newsletter digests have been generated yet.",
        )
    return ToolResult(call_id="", name=_SPEC.name, content=_format_digest(digests[0]))


def register() -> None:
    """Register zeus_newsletter_latest."""
    registry.register(_SPEC, _handler)
    logger.info("zeus_newsletter_latest registered")
