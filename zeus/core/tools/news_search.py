# zeus/core/tools/news_search.py - Chat-path mirror of the zeus_news_search MCP tool.
#
# Searches the Pheme news layer (zeus_news) in-process. Read-only, cacheable
# within the default TTL - the collection only changes when ingest runs.
from __future__ import annotations

import asyncio
import logging
from typing import Any

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.news_search")

_SPEC = ToolSpec(
    name="zeus_news_search",
    description=(
        "Search the Pheme news layer: consolidated Canary OSINT articles and "
        "CapitolScope congressional-trading signals stored over time. Use for "
        "'what has the news said about X', topic deep-dives, or connecting "
        "congressional trades to events. Supports source (canary|capitolscope), "
        "topic, entity (person/org/ticker), and since (ISO date) filters."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for"},
            "source": {"type": "string", "enum": ["canary", "capitolscope"]},
            "topic": {"type": "string"},
            "entity": {"type": "string"},
            "since": {"type": "string", "description": "ISO-8601 lower bound on published_at"},
            "top_k": {"type": "integer", "minimum": 1, "maximum": 20},
        },
        "required": ["query"],
    },
    aegis_policy="tool_arguments",
    timeout_seconds=20.0,
    cacheable=True,
)


def _format_hits(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No news items matched."
    lines: list[str] = []
    for r in results:
        md = r.get("metadata", {}) or {}
        head = f"[{md.get('source', 'news')} | {str(md.get('published_at', ''))[:10]} | score={float(r.get('score', 0)):.3f}]"
        lines.append(head)
        lines.append(str(r.get("memory", ""))[:500])
        url = md.get("url", "")
        if url:
            lines.append(f"  {url}")
    return "\n".join(lines)


async def _handler(args: dict[str, Any]) -> ToolResult:
    from zeus.memory.search import search_news

    try:
        results = await asyncio.to_thread(
            search_news,
            str(args.get("query", "")),
            top_k=int(args.get("top_k") or 8),
            source=args.get("source"),
            topic=args.get("topic"),
            entity=args.get("entity"),
            since=args.get("since"),
        )
    except Exception as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"zeus_news_search failed: {exc}",
            is_error=True,
        )
    return ToolResult(call_id="", name=_SPEC.name, content=_format_hits(results))


def register() -> None:
    """Register zeus_news_search."""
    registry.register(_SPEC, _handler)
    logger.info("zeus_news_search registered")
