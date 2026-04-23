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
            "enum": ["iso", "human", "unix"],
            "description": (
                "Output format. 'iso' = ISO 8601 with offset (default), "
                "'human' = 'Thursday, April 23, 2026 at 2:37 PM PDT', "
                "'unix' = seconds since epoch."
            ),
        },
    },
}


_SPEC = ToolSpec(
    name="current_time",
    description=(
        "Get the current wall-clock date and time. Use whenever the user asks "
        "about now, today, this morning, 'what time is it', or needs a "
        "timestamp for a follow-up. Returns the time in the requested IANA "
        "timezone, or the server's default if none is given. Do not guess the "
        "time without calling this tool."
    ),
    parameters=_SCHEMA,
    aegis_policy="tool_arguments",
    timeout_seconds=1.0,
    cacheable=False,  # never cache: output changes every second by definition.
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    tz_name = str(args.get("timezone") or _default_timezone()).strip() or "UTC"
    fmt = str(args.get("format") or "iso").strip().lower()

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
    elif fmt == "human":
        # %-I / %-d are POSIX-only no-pad variants; if we ever run on Windows
        # this would need %#I / %#d. Docker Linux is the only target, so fine.
        body = now.strftime("%A, %B %-d, %Y at %-I:%M %p %Z")
    else:
        # ISO 8601 default. isoformat() on a tz-aware datetime includes offset.
        body = now.isoformat(timespec="seconds")

    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register() -> None:
    """Register current_time. Always available; no external dependency."""
    registry.register(_SPEC, _handler)
    logger.info("current_time registered (default tz=%s)", _default_timezone())
