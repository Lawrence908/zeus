# tests/test_pheme_dedup_tickers.py - Syndication dedup + ticker resolution units.
from __future__ import annotations

from zeus.pheme.pipeline import _dedupe_syndicated, _Item, _url_domain
from zeus.pheme.tickers import resolve_tickers


def _item(key: str, title: str, text: str = "body", published: str = "2026-07-27") -> _Item:
    return _Item(
        key=key, point_id=f"pid-{key}", source="canary", source_id=key,
        title=title, text=text, url=f"https://{key}.example.com/story",
        published_at=published,
    )


def test_dedupe_groups_near_copies_and_picks_clean_canonical():
    items = [
        _item("a", "article 29079025 64b2.html", text="wire text short"),
        _item("b", "Berlin attack suspect shot", text="wire text much longer body here"),
        _item("c", "Unrelated story", text="different"),
    ]
    neighbors = {
        "a": [("b", 0.97)],
        "b": [("a", 0.97)],
        "c": [("a", 0.60)],
    }
    groups = _dedupe_syndicated(items, neighbors, 0.95)
    assert set(groups) == {"b", "c"}          # clean-titled copy is canonical
    assert [m.key for m in groups["b"]] == ["b", "a"]
    assert len(groups["c"]) == 1


def test_dedupe_threshold_respected():
    items = [_item("a", "Story A"), _item("b", "Story B")]
    groups = _dedupe_syndicated(items, {"a": [("b", 0.90)], "b": []}, 0.95)
    assert len(groups) == 2                   # 0.90 similar = related, not copies


def test_url_domain():
    assert _url_domain("https://www.salisburyjournal.co.uk/news/x") == "salisburyjournal.co.uk"
    assert _url_domain("") == ""


def test_ticker_from_name_in_entities():
    extras = resolve_tickers(["Nvidia", "berlin"], "")
    assert "nvda" in extras and "nvidia" not in extras  # nvidia already present


def test_ticker_from_text_scan():
    extras = resolve_tickers([], "Congress is scrutinizing Microsoft and Taiwan Semiconductor.")
    assert "msft" in extras and "tsm" in extras


def test_name_from_bare_ticker():
    extras = resolve_tickers(["MSFT"], "")
    assert "microsoft" in extras


def test_no_false_positive_on_unrelated():
    assert resolve_tickers(["gatwick airport"], "water outage at the terminal") == []


def test_audio_summary_dict_shape():
    from zeus.pheme.models import ClusterSummary
    from zeus.pheme.pipeline import _audio_summary_dict

    clusters = [
        ClusterSummary(key="a", name="Berlin Pride Attack", claim="Suspect shot dead",
                       thread_status="development", thread_days=2),
        ClusterSummary(key="b", name="Gatwick outage", claim="Water restored"),
    ]
    d = _audio_summary_dict("Lead paragraph.", ["Insight one."], clusters)
    assert d["summary"] == "Lead paragraph."
    assert d["bullets"][0].startswith("Day 2 of Berlin Pride Attack")
    assert d["bullets"][1].startswith("Gatwick outage")
    assert d["advice"] == "Insight one."
    assert "http" not in " ".join(d["bullets"])
