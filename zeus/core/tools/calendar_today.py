# zeus/core/tools/calendar_today.py — Today's calendar events
#
# Wraps GET /calendar/today. Cacheable=True with the default short TTL keeps
# rapid follow-up queries cheap; freshness is bounded by the underlying
# gcal ingest cadence anyway.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.calendar_today")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="zeus_calendar_today",
    description=(
        "List today's calendar events from already-ingested Google Calendar "
        "data. Use when the user asks 'what's on my calendar?', 'what "
        "meetings today?', 'what's my schedule?', or anything similar. "
        "Reads from MemoryStore via vector search; freshness depends on "
        "the latest Iris ingest cycle. Returns a compact list with summary, "
        "timing hints, and the underlying fact text."
    ),
    parameters={
        "type": "object",
        "properties": {},
    },
    aegis_policy="tool_arguments",
    timeout_seconds=15.0,
    cacheable=True,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(f"{_core_url()}/calendar/today")
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"zeus_calendar_today failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code >= 400:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"zeus_calendar_today HTTP {r.status_code}: {r.text[:200]!r}",
            is_error=True,
        )
    data = r.json() or {}
    events = data.get("events") or []
    today = str(data.get("date") or "")
    if not events:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=(
                f"No calendar events found for {today}. Either nothing is "
                "scheduled or the gcal source has not been re-ingested "
                "recently. Run `python -m zeus.ingest.run --source gcal` "
                "to refresh."
            ),
        )
    lines = [f"Calendar for {today}:"]
    for ev in events:
        summary = str(ev.get("summary") or "(no title)").strip()
        text = str(ev.get("text") or "").strip()
        line = f"- {summary}"
        if text and text != summary:
            line += f"\n  {text[:280]}"
        lines.append(line)
    return ToolResult(call_id="", name=_SPEC.name, content="\n".join(lines))


def register() -> None:
    """Register zeus_calendar_today."""
    registry.register(_SPEC, _handler)
    logger.info("zeus_calendar_today registered")
