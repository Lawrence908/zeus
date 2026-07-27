# zeus/kronos/jobs/pheme.py - Kronos built-in for the Pheme daily news digest.
#
# Ingest both news sources -> retention sweep -> staged pipeline -> delivery
# (Telegram push, Twitter autopost or pending approval). Each phase degrades
# gracefully: a dead source still lets the pipeline run over what's stored.
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("zeus.kronos.pheme")


async def run_daily_digest(params: dict[str, Any]) -> dict[str, Any]:
    """
    Params:
      news_days_back: source fetch window in days (default 2)
      skip_ingest:    true to run the pipeline over already-stored items only
    """
    from zeus.memory.news import get_news_store
    from zeus.pheme.delivery import deliver_digest
    from zeus.pheme.pipeline import run_pheme_pipeline

    days_back = max(1, int(params.get("news_days_back") or 2))
    ingest_summary: dict[str, Any] = {}

    if not params.get("skip_ingest"):
        from zeus.ingest.pipeline import run_ingest

        sources = []
        try:
            from zeus.ingest.sources.canary import CanaryNewsSource

            sources.append(CanaryNewsSource(days_back=days_back))
        except Exception as exc:
            logger.warning("pheme: canary source unavailable - %s", exc)
        try:
            from zeus.ingest.sources.capitolscope import CapitolScopeNewsSource

            sources.append(CapitolScopeNewsSource(days_back=days_back))
        except Exception as exc:
            logger.warning("pheme: capitolscope source unavailable - %s", exc)

        if sources:
            results = await run_ingest(sources, ingest_ui="plain")
            ingest_summary = {
                r.source: {"stored": r.chunks_stored, "errors": len(r.errors)}
                for r in results
            }

    store = get_news_store()
    swept = store.sweep_expired()

    digest = await run_pheme_pipeline("daily")
    delivery = await deliver_digest(digest)

    return {
        "status": "ok" if digest.clusters else "empty",
        "digest_id": digest.id,
        "ingest": ingest_summary,
        "swept": swept,
        "stats": digest.stats,
        "delivery": delivery,
        "summary": digest.lead[:400],
    }
