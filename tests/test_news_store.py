# tests/test_news_store.py - NewsStore round-trip, idempotency, retention sweep.
#
# Runs against the live Qdrant + Ollama embed stack (like retrieval_eval.py)
# but on a throwaway collection so zeus_news is never touched. Skips cleanly
# when Qdrant is unreachable.
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from dotenv import load_dotenv

load_dotenv()  # ZEUS_EMBED_MODEL / OLLAMA_URL / QDRANT_URL for the live stack

from zeus.memory.news import NewsItem, NewsStore  # noqa: E402


@pytest.fixture()
def store():
    s = NewsStore(collection="zeus_news_test")
    try:
        s.ensure_collection()
    except Exception as exc:  # pragma: no cover - environment guard
        pytest.skip(f"qdrant unavailable: {exc}")
    yield s
    try:
        s._client.delete_collection("zeus_news_test")
    except Exception:
        pass


def _item(source_id: str, *, days_old: int = 0, pinned: bool = False) -> NewsItem:
    ts = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    return NewsItem(
        text=f"Body text for {source_id} about congressional semiconductor trades.",
        title=f"Title {source_id}",
        source="canary",
        source_id=source_id,
        url="https://example.com/a",
        published_at=ts,
        ingested_at=ts,
        topics=["markets"],
        entities=["NVDA"],
        pinned=pinned,
    )


def test_round_trip_and_idempotent_reingest(store: NewsStore):
    res = store.add_items([_item("a1")])
    assert res.added == 1 and not res.errors

    hits = store.search("semiconductor congressional trades", top_k=3)
    assert hits and hits[0].payload["source_id"] == "a1"
    assert hits[0].payload["entities"] == ["NVDA"]

    # Re-ingest of the same (source, source_id) upserts in place: count stays 1.
    store.add_items([_item("a1")])
    assert store.count(source="canary") == 1

    # Filters: entity match hits, wrong source misses.
    assert store.search("trades", filters={"entity": "NVDA"})
    assert not store.search("trades", filters={"source": "capitolscope"})


def test_set_analysis_writes_back(store: NewsStore):
    store.add_items([_item("a2")])
    assert store.set_analysis(
        "canary", "a2", topics=["chips"], significance=0.9
    )
    hits = store.search("semiconductor", filters={"topic": "chips"})
    assert hits and hits[0].payload["significance"] == 0.9


def test_sweep_expired_respects_pinned(store: NewsStore):
    store.add_items(
        [
            _item("old", days_old=60),
            _item("old-pinned", days_old=60, pinned=True),
            _item("fresh", days_old=1),
        ]
    )
    removed = store.sweep_expired(older_than_days=45)
    assert removed == 1
    assert store.count() == 2
    ids = {h.payload["source_id"] for h in store.scroll_recent(since="1970-01-01T00:00:00+00:00")}
    assert ids == {"old-pinned", "fresh"}
