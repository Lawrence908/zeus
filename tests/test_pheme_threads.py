# tests/test_pheme_threads.py - Story-thread registry: match, day counts, idempotency.
from __future__ import annotations

import pytest

from zeus.pheme.threads import match_and_update


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PHEME_DATA_DIR", str(tmp_path))


BERLIN = {"berlin", "pride", "attack", "suspect"}
GATWICK = {"gatwick", "airport", "water"}


def test_new_then_development_across_days():
    day1 = match_and_update(
        [("c1", BERLIN, "Berlin Pride Attack", "Suspect at large.")], today="2026-07-26"
    )
    assert day1["c1"].is_new and day1["c1"].days_seen == 1

    day2 = match_and_update(
        [("c9", BERLIN | {"police"}, "Berlin Suspect Shot", "Suspect shot dead.")],
        today="2026-07-27",
    )
    m = day2["c9"]
    assert not m.is_new
    assert m.days_seen == 2
    assert m.thread_id == day1["c1"].thread_id
    assert m.prior_history[-1]["claim"] == "Suspect at large."


def test_same_day_rerun_does_not_inflate_days():
    match_and_update([("c1", BERLIN, "Berlin", "v1")], today="2026-07-26")
    rerun = match_and_update([("c2", BERLIN, "Berlin", "v2")], today="2026-07-26")
    assert rerun["c2"].days_seen == 1
    assert rerun["c2"].is_new  # created today, still day one


def test_unrelated_clusters_get_distinct_threads():
    out = match_and_update(
        [("a", BERLIN, "Berlin", "x"), ("b", GATWICK, "Gatwick", "y")],
        today="2026-07-26",
    )
    assert out["a"].thread_id != out["b"].thread_id


def test_single_shared_token_is_not_a_match():
    match_and_update([("a", BERLIN, "Berlin", "x")], today="2026-07-26")
    out = match_and_update(
        [("b", {"berlin", "film", "festival"}, "Berlin Film Festival", "y")],
        today="2026-07-27",
    )
    assert out["b"].is_new  # only "berlin" shared


def test_one_thread_cannot_be_claimed_twice():
    match_and_update([("a", BERLIN, "Berlin", "x")], today="2026-07-26")
    out = match_and_update(
        [
            ("strong", BERLIN, "Berlin update", "z"),
            ("weak", {"berlin", "attack"}, "Other berlin attack piece", "w"),
        ],
        today="2026-07-27",
    )
    assert not out["strong"].is_new
    assert out["weak"].is_new  # thread already claimed by the stronger overlap


def test_stale_threads_pruned():
    old = match_and_update([("a", BERLIN, "Berlin", "x")], today="2026-07-01")
    out = match_and_update([("b", BERLIN, "Berlin again", "y")], today="2026-07-26")
    assert out["b"].is_new
    assert out["b"].thread_id != old["a"].thread_id
