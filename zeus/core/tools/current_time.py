# zeus/core/tools/current_time.py — Report the current wall-clock time
#
# Fixes the "it's currently 14:37" hallucination: without this tool the chat
# LLM has no clock access and will happily invent a time. cacheable=False
# is not negotiable — the result changes every second by definition.
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.current_time")


def _default_timezone() -> str:
    # ZEUS_DEFAULT_TIMEZONE lets ops pin the "local" interpretation without
    # relying on the container TZ env. Falls back to UTC which is always safe.
    return (os.getenv("ZEUS_DEFAULT_TIMEZONE", "") or "UTC").strip() or "UTC"


_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "timezone": {
            "type": "string",
            "description": (
                "IANA timezone name (e.g. 'America/Vancouver', 'UTC'). "
                "Defaults to the deployment's configured local timezone."
            ),
        },
        "format": {
            "type": "string",
            "enum": ["human", "iso", "unix"],
            "description": (
                "Output format. 'human' (default) = 24-hour clock with "
                "timezone abbreviation and weekday, e.g. "
                "'17:58:34 PDT on Thursday, April 23, 2026'. "
                "'iso' = ISO 8601 with UTC offset (e.g. '2026-04-23T17:58:34-07:00'). "
                "'unix' = seconds since the epoch. Prefer 'human' unless the "
                "caller specifically needs a machine-parseable format."
            ),
        },
    },
}


_SPEC = ToolSpec(
    name="current_time",
    description=(
        "Returns the current wall-clock date and time. You MUST call this "
        "tool whenever the user asks about the current time, date, day of "
        "the week, 'now', 'today', 'tonight', 'this morning', 'what time is "
        "it', or anything similar. Do NOT answer from memory, retrieval, or "
        "training data — the clock changes every second and only this tool "
        "has the real value. Timestamps you see in the context blocks are "
        "historical, not current. Call this first, then answer. The default "
        "output is human-friendly 24-hour format with timezone abbreviation "
        "(e.g. '17:58:34 PDT on Thursday, April 23, 2026') — quote it "
        "verbatim in your reply. Pass `timezone` as an IANA name when the "
        "user asks about a specific place (e.g. 'Asia/Tokyo', "
        "'Europe/London'); otherwise the server's default timezone is used."
    ),
    parameters=_SCHEMA,
    aegis_policy="tool_arguments",
    timeout_seconds=1.0,
    cacheable=False,  # never cache: output changes every second by definition.
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    tz_name = str(args.get("timezone") or _default_timezone()).strip() or "UTC"
    fmt = str(args.get("format") or "human").strip().lower()

    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=(
                f"Unknown timezone {tz_name!r}. Use an IANA name like "
                "'America/Vancouver', 'Europe/London', or 'UTC'."
            ),
            is_error=True,
        )

    now = datetime.now(tz=timezone.utc).astimezone(tz)

    if fmt == "unix":
        body = f"{int(now.timestamp())}"
    elif fmt == "iso":
        # ISO 8601 with offset — machine-parseable fallback.
        body = now.isoformat(timespec="seconds")
    else:
        # Default: 24-hour clock + timezone abbreviation + weekday + full date.
        # %-d is POSIX-only no-pad; Docker Linux is the only target.
        # %Z on a ZoneInfo-aware datetime yields PDT / PST / UTC / JST / etc.
        # Falls back to the IANA name if the tz has no abbreviation.
        tz_abbr = now.strftime("%Z") or tz_name
        body = now.strftime(f"%H:%M:%S {tz_abbr} on %A, %B %-d, %Y")

    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register() -> None:
    """Register current_time. Always available; no external dependency."""
    registry.register(_SPEC, _handler)
    logger.info("current_time registered (default tz=%s)", _default_timezone())
