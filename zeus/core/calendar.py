# zeus/core/calendar.py — Today's calendar events from ingested gcal facts
#
# GET /calendar/today  →  compact list of today's events
#
# gcal events land in the MemoryStore via Iris with source = "gcal:<id>".
# Each event is run through fact extraction, so the stored text is one or
# more atomic facts ("Chris has a meeting with X at 14:00 on YYYY-MM-DD").
# We use vector search with today's date as a query, then filter to gcal
# sources. Not perfect recall, but matches how the chat path already
# surfaces these items, and keeps the implementation small.
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger("zeus.calendar")

router = APIRouter(tags=["calendar"])


def _user_id() -> str:
    return os.getenv("ZEUS_USER_ID", "user")


def _default_tz() -> str:
    return (os.getenv("ZEUS_DEFAULT_TIMEZONE", "") or "UTC").strip() or "UTC"


def _today_iso() -> str:
    try:
        tz = ZoneInfo(_default_tz())
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    return datetime.now(tz=tz).date().isoformat()


def _limit() -> int:
    try:
        return max(1, min(50, int(os.getenv("ZEUS_CALENDAR_TODAY_LIMIT", "10"))))
    except (TypeError, ValueError):
        return 10


@router.get("/calendar/today")
async def calendar_today() -> dict[str, Any]:
    """List today's calendar events from ingested gcal facts. Backs zeus_calendar_today."""
    today = _today_iso()
    query = f"calendar events on {today} today's schedule meetings appointments"

    try:
        from zeus.memory.search import search_memories
    except ImportError as exc:
        return {"date": today, "events": [], "error": f"memory search unavailable: {exc}"}

    try:
        hits = await asyncio.to_thread(
            search_memories,
            query=query,
            user_id=_user_id(),
            top_k=20,
        )
    except Exception as exc:
        logger.warning("calendar_today: memory search failed: %s", exc)
        return {"date": today, "events": [], "error": str(exc)}

    events: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for hit in hits or []:
        md = (hit or {}).get("metadata") or {}
        source = str(md.get("source") or "")
        if not source.startswith("gcal:"):
            continue
        # Filter to events that mention today's date (in valid_from or in text).
        valid_from = str(md.get("valid_from") or "")
        if valid_from and valid_from != today and today not in str(hit.get("memory", "")):
            continue
        eid = str(md.get("event_id") or md.get("source_id") or hit.get("id") or "")
        if eid and eid in seen_ids:
            continue
        seen_ids.add(eid)
        events.append({
            "summary": md.get("summary") or "",
            "text": str(hit.get("memory") or "")[:400],
            "valid_from": valid_from,
            "source_id": str(md.get("source_id") or ""),
            "score": float(hit.get("score") or 0.0),
        })
        if len(events) >= _limit():
            break

    return {
        "date": today,
        "event_count": len(events),
        "events": events,
    }
