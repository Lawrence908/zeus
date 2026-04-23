# zeus/core/tools/web_search.py — Brave Search reference tool
#
# Registered at package import time (zeus/core/tools/__init__.py does not
# import this automatically; main.py wires it in during startup so missing
# BRAVE_API_KEY becomes a runtime-visible condition instead of a silent
# import-time side effect). Free tier is 1 qps and 2000 queries/month, so
# concurrent chat requests need a module-level semaphore + pacing.
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.web_search")

_BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
_TIMEOUT_SEC = 10.0
_RATE_LIMIT_QPS = 1.0  # free tier

_sem = asyncio.Semaphore(1)
_last_call_ts: float = 0.0

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "What to search for. Be specific and concise; this is sent to Brave Search verbatim.",
        },
        "count": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "description": "Number of results to return. Defaults to 5.",
        },
    },
    "required": ["query"],
}


_SPEC = ToolSpec(
    name="web_search",
    description=(
        "Search the public web for current, up-to-date information. Call "
        "this tool whenever the user asks about news, current events, "
        "recent releases, live prices, weather, scores, or anything whose "
        "correct answer has likely changed since your training data. "
        "Ground your reply in the returned snippets — do NOT blend them "
        "with prior training knowledge, which may be stale or contradict "
        "the live results. Returns a short list of title + URL + snippet. "
        "When calling this tool more than once with the same topic, keep "
        "the arguments identical (including optional `count`) so cached "
        "results can be reused."
    ),
    parameters=_SCHEMA,
    aegis_policy="tool_arguments",
    timeout_seconds=_TIMEOUT_SEC,
    cacheable=True,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    global _last_call_ts

    query = str(args.get("query") or "").strip()
    if not query:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="web_search requires a non-empty 'query'.",
            is_error=True,
        )
    count = args.get("count", 5)
    try:
        count = max(1, min(10, int(count)))
    except (TypeError, ValueError):
        count = 5

    api_key = os.getenv("BRAVE_API_KEY", "").strip()
    if not api_key:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="web_search is unavailable: BRAVE_API_KEY is not set.",
            is_error=True,
        )

    async with _sem:
        # Pace to 1 qps across concurrent callers.
        now = time.monotonic()
        wait = (1.0 / _RATE_LIMIT_QPS) - (now - _last_call_ts)
        if wait > 0:
            await asyncio.sleep(wait)

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SEC) as client:
                r = await client.get(
                    _BRAVE_URL,
                    params={"q": query, "count": count},
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": api_key,
                    },
                )
        finally:
            _last_call_ts = time.monotonic()

    if r.status_code == 429:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content="web_search rate-limited (429) by Brave. Try again shortly.",
            is_error=True,
        )
    if r.status_code >= 400:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"web_search failed: Brave returned {r.status_code} {r.text[:200]!r}",
            is_error=True,
        )

    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    results = ((data.get("web") or {}).get("results") or [])[:count]
    if not results:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"No web results for {query!r}.",
        )

    lines: list[str] = []
    for hit in results:
        title = str(hit.get("title") or "").strip()
        url = str(hit.get("url") or "").strip()
        desc = str(hit.get("description") or "").strip()
        if not (title and url):
            continue
        lines.append(f"- {title}\n  {url}\n  {desc}")
    body = "\n".join(lines) or f"No usable results for {query!r}."
    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register_if_configured() -> bool:
    """Register web_search iff BRAVE_API_KEY is present. Returns True on register.

    Called by zeus/core/main.py at startup. Idempotent — a second call replaces
    the prior registration, which matters for ZEUS_PROMPT_RELOAD-style workflows.
    """
    if not os.getenv("BRAVE_API_KEY", "").strip():
        logger.info("web_search not registered: BRAVE_API_KEY not set")
        return False
    registry.register(_SPEC, _handler)
    logger.info("web_search registered")
    return True
