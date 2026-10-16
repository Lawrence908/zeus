# tests/test_canary_source.py - Canary news source: GDELT balancing and total-limit semantics.
from __future__ import annotations

from zeus.ingest.sources.canary import CanaryNewsSource


def _src(**kw) -> CanaryNewsSource:
    return CanaryNewsSource(api_url="http://canary", email="e", password="p", **kw)


def test_total_limit_is_not_capped_at_page_size():
    # Canary caps each PAGE at 200; the total used to be capped there too,
    # which kept only the newest 200 articles (all GDELT).
    assert _src(limit=5000).limit == 5000


def test_balance_keeps_every_feed_article_and_trims_gdelt():
    gdelt = [{"id": f"g{i}", "source_name": "GDELT Project"} for i in range(10)]
    feeds = [{"id": "a", "source_name": "The Guardian World"}, {"id": "b", "source_name": "UN News"}]
    out = _src(gdelt_max=3)._balance(gdelt[:5] + feeds + gdelt[5:])
    assert [a["id"] for a in out] == ["a", "b", "g0", "g1", "g2"]  # newest GDELT kept


def test_gdelt_max_from_env(monkeypatch):
    monkeypatch.setenv("CANARY_GDELT_MAX", "7")
    assert _src().gdelt_max == 7
