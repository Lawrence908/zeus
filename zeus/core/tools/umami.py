# zeus/core/tools/umami.py: Umami web analytics (read-only)
#
# Two chat tools over /analytics/umami/* (zeus/core/analytics.py):
#   umami_stats   pageviews, visitors, top pages/referrers/events, change vs
#                 the previous period, for one site or all of them
#   umami_events  server-side homelab events (backup_completed etc.) from the
#                 "Homelab events" website
# Registered only when UMAMI_DB_URL is set, so the model is never offered a
# tool whose backing database is not configured.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.config import core_base_url
from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.umami")


def _core_url() -> str:
    return core_base_url()


_STATS_SPEC = ToolSpec(
    name="umami_stats",
    description=(
        "Website analytics from the self-hosted Umami instance: pageviews, "
        "visitors (distinct sessions), visits, top pages, top referrers, top "
        "custom events, and percent change vs the previous period of the same "
        "length. Sites include Portfolio, Landing (chrislawrence.ca), Econ, "
        "SchedShare, CapitolScope, MagicPages, EventSphere and Gravity. Use "
        "when the user asks about traffic, visitors, page views, or how a site "
        "is doing. Read-only."
    ),
    parameters={
        "type": "object",
        "properties": {
            "site": {
                "type": "string",
                "default": "all",
                "description": "Website name or domain (e.g. 'Portfolio'), or 'all'.",
            },
            "period": {
                "type": "string",
                "default": "7d",
                "description": "Rolling window ending now: e.g. 24h, 7d, 30d, 4w.",
            },
        },
    },
    aegis_policy="tool_arguments",
    timeout_seconds=20.0,
)

_EVENTS_SPEC = ToolSpec(
    name="umami_events",
    description=(
        "Server-side homelab events recorded in Umami's 'Homelab events' site "
        "(e.g. backup_completed, backup_failed), with counts, last occurrence "
        "and the most recent events with their key=value data. Use when the "
        "user asks whether a backup or scheduled job ran, or what happened on "
        "the homelab recently. Read-only."
    ),
    parameters={
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "default": "7d",
                "description": "Rolling window ending now: e.g. 24h, 7d, 30d.",
            },
            "event": {
                "type": "string",
                "default": "",
                "description": "Optional exact event name to filter on, e.g. 'backup_failed'.",
            },
        },
    },
    aegis_policy="tool_arguments",
    timeout_seconds=20.0,
)


async def _get(name: str, path: str, params: dict[str, Any]) -> ToolResult:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"{_core_url()}{path}", params=params)
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="", name=name, content=f"{name} failed to reach Zeus core: {exc}", is_error=True
        )
    if r.status_code >= 400:
        try:
            detail = (r.json() or {}).get("detail") or r.text
        except ValueError:
            detail = r.text
        return ToolResult(
            call_id="", name=name, content=f"{name} HTTP {r.status_code}: {str(detail)[:300]}", is_error=True
        )
    data = r.json() or {}
    return ToolResult(call_id="", name=name, content=str(data.get("summary") or "No data."))


async def _stats_handler(args: dict[str, Any]) -> ToolResult:
    params = {
        "site": str(args.get("site") or "all"),
        "period": str(args.get("period") or "7d"),
    }
    return await _get(_STATS_SPEC.name, "/analytics/umami/stats", params)


async def _events_handler(args: dict[str, Any]) -> ToolResult:
    params = {
        "period": str(args.get("period") or "7d"),
        "event": str(args.get("event") or ""),
    }
    return await _get(_EVENTS_SPEC.name, "/analytics/umami/events", params)


def register_if_configured() -> bool:
    """Register umami_stats + umami_events iff UMAMI_DB_URL is set."""
    if not os.getenv("UMAMI_DB_URL", "").strip():
        logger.info("umami tools not registered: UMAMI_DB_URL not set")
        return False
    registry.register(_STATS_SPEC, _stats_handler)
    registry.register(_EVENTS_SPEC, _events_handler)
    logger.info("umami_stats, umami_events registered")
    return True
