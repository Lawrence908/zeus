# zeus/pheme/observer.py - KAIROS observation source for breaking news events.
#
# Watches freshly ingested zeus_news items for an entity burst (one entity
# carried by several fresh items, ideally across both sources) and, when a
# burst clears the bar, runs the scoped breaking pipeline and delivers an
# alert. Hard-capped by PHEME_MAX_ALERTS_PER_DAY; entities alerted once are
# not re-alerted the same day. Gated by PHEME_BREAKING_ENABLED - the observer
# is only registered with the daemon when the flag is on, and it re-checks
# the flag every cycle so it can be disabled at runtime.
#
# This observer acts inside observe() (LAB-354 pattern): the Observation it
# returns is a report of the alert it already sent, not a request for the
# KAIROS planner - no tools are involved, so the KAIROS allowlist stays intact.
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

from zeus.orchestration.daemon import Observation

logger = logging.getLogger("zeus.pheme.observer")


def breaking_enabled() -> bool:
    return os.getenv("PHEME_BREAKING_ENABLED", "0").strip() in ("1", "true", "yes", "on")


def _min_burst_items() -> int:
    try:
        return max(2, int(os.getenv("PHEME_BREAKING_MIN_ITEMS", "3")))
    except ValueError:
        return 3


class PhemeBreakingObserver:
    """Fires a scoped Pheme breaking run when an entity burst clears the bar."""

    def __init__(self) -> None:
        self._watermark: str = datetime.now(timezone.utc).isoformat()
        self._alerted_entities: dict[str, str] = {}  # entity -> YYYY-MM-DD alerted

    async def observe(self) -> Observation | None:
        if not breaking_enabled():
            return None

        from zeus.pheme.delivery import (
            alerts_sent_today,
            deliver_digest,
            max_alerts_per_day,
            record_alert,
        )

        if alerts_sent_today() >= max_alerts_per_day():
            return None

        import asyncio

        from zeus.memory.news import get_news_store
        from zeus.pheme.pipeline import NEWS_SOURCES, run_pheme_pipeline

        store = get_news_store()
        window_start = min(
            self._watermark,
            (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
        )
        try:
            fresh = await asyncio.to_thread(
                store.scroll_recent, since=window_start, sources=NEWS_SOURCES, limit=300
            )
        except Exception as exc:
            logger.warning("pheme breaking observer scan failed: %s", exc)
            return None
        self._watermark = datetime.now(timezone.utc).isoformat()
        if not fresh:
            return None

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        by_entity: dict[str, list] = {}
        for hit in fresh:
            for entity in hit.payload.get("entities") or []:
                key = str(entity).strip().casefold()
                if key and self._alerted_entities.get(key) != today:
                    by_entity.setdefault(key, []).append(hit)

        burst_entity: str | None = None
        burst_hits: list = []
        for entity, hits in sorted(by_entity.items(), key=lambda kv: -len(kv[1])):
            sources = {h.source for h in hits}
            if len(hits) >= _min_burst_items() and (
                len(sources) > 1 or len(hits) >= _min_burst_items() + 1
            ):
                burst_entity, burst_hits = entity, hits
                break
        if burst_entity is None:
            return None

        scope_keys = [f"{h.source}:{h.payload.get('source_id')}" for h in burst_hits]
        logger.info(
            "pheme breaking burst on %r (%d items, sources=%s)",
            burst_entity,
            len(burst_hits),
            sorted({h.source for h in burst_hits}),
        )
        digest = await run_pheme_pipeline(
            "breaking", since=window_start, scope_item_keys=scope_keys
        )
        if not digest.clusters:
            return None
        delivery = await deliver_digest(digest, breaking=True)
        record_alert()
        self._alerted_entities[burst_entity] = today

        return Observation(
            source="pheme_breaking",
            summary=(
                f"Breaking alert sent for {burst_entity!r}: "
                f"{len(burst_hits)} fresh items, digest {digest.id}"
            ),
            raw={"digest_id": digest.id, "entity": burst_entity, "delivery": delivery},
        )
