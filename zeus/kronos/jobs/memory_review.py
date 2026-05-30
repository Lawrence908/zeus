# zeus/kronos/jobs/memory_review.py — Weekly memory review built-in.
#
# Surveys MemoryStore additions in the last N days, groups by category, and
# returns counts plus a small sample of texts. No LLM call here — Phase 3 can
# layer a synthesiser on top via small_llm_call(min_privacy_tier=1).
#
# Reaches through MemoryStore._client for a Qdrant scroll filtered by
# created_at, the same admin-only-reach-through pattern used by
# /admin/ingest/stats. Memory writes carry ISO-8601 created_at strings.
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("zeus.kronos.memory_review")

_DEFAULT_DAYS = 7
_MAX_SAMPLES_PER_CATEGORY = 3
_SCROLL_PAGE = 256
_SCROLL_HARD_CAP = 5000  # safety: don't scan an unbounded collection


async def run_weekly_review(params: dict[str, Any]) -> dict[str, Any]:
    days = int(params.get("days") or _DEFAULT_DAYS)
    max_samples = int(params.get("max_samples_per_category") or _MAX_SAMPLES_PER_CATEGORY)
    user_id = str(params.get("user_id") or "user")

    return await asyncio.to_thread(_review_sync, days, max_samples, user_id)


def _review_sync(days: int, max_samples: int, user_id: str) -> dict[str, Any]:
    from qdrant_client.http import models as qmodels

    from zeus.memory.store import get_memory_store

    store = get_memory_store()
    store.ensure_collection()
    client = store._client  # noqa: SLF001 — admin-only reach-through, see CLAUDE.md
    collection = store.collection

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    qfilter = qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="user_id", match=qmodels.MatchValue(value=user_id)
            ),
            qmodels.FieldCondition(
                key="created_at",
                range=qmodels.DatetimeRange(gte=cutoff),
            ),
        ]
    )

    by_category: dict[str, dict[str, Any]] = {}
    by_source: dict[str, int] = {}
    total = 0
    pii_count = 0
    offset = None
    while True:
        records, offset = client.scroll(
            collection_name=collection,
            scroll_filter=qfilter,
            limit=_SCROLL_PAGE,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        if not records:
            break
        for rec in records:
            payload = dict(rec.payload or {})
            cat = str(payload.get("category") or "uncategorised")
            src = str(payload.get("source") or "unknown")
            text = str(payload.get("text") or "")
            entry = by_category.setdefault(cat, {"count": 0, "samples": []})
            entry["count"] += 1
            if len(entry["samples"]) < max_samples and text:
                entry["samples"].append(text[:240])
            by_source[src] = by_source.get(src, 0) + 1
            if payload.get("contains_pii") is True:
                pii_count += 1
            total += 1
        if offset is None or total >= _SCROLL_HARD_CAP:
            break

    sorted_cats = sorted(by_category.items(), key=lambda kv: kv[1]["count"], reverse=True)
    sorted_srcs = sorted(by_source.items(), key=lambda kv: kv[1], reverse=True)

    return {
        "status": "ok",
        "window_days": days,
        "user_id": user_id,
        "total_additions": total,
        "pii_additions": pii_count,
        "by_category": [
            {"category": cat, "count": data["count"], "samples": data["samples"]}
            for cat, data in sorted_cats
        ],
        "top_sources": [
            {"source": src, "count": cnt} for src, cnt in sorted_srcs[:10]
        ],
        "scan_capped": total >= _SCROLL_HARD_CAP,
    }
