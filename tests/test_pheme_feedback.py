# tests/test_pheme_feedback.py - Pheme feedback store: record, weights, decay, scoring.
from __future__ import annotations

import time

import pytest

from zeus.pheme import feedback


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PHEME_DATA_DIR", str(tmp_path))


def _context(digest_id: str = "d1") -> None:
    feedback.save_digest_context(
        digest_id,
        [
            {"key": "k-nvda", "name": "Nvidia earnings", "entities": ["nvda", "nvidia"],
             "topics": ["semiconductors"], "sources": ["canary"]},
            {"key": "k-gossip", "name": "Celebrity story", "entities": ["some celebrity"],
             "topics": ["entertainment"], "sources": ["canary"]},
        ],
    )


def test_record_and_weights():
    _context()
    assert feedback.record_reaction("d1", 0, +1)["key"] == "k-nvda"
    assert feedback.record_reaction("d1", 1, -1)["key"] == "k-gossip"

    weights = feedback.preference_weights()
    assert weights["nvda"] > 0
    assert weights["topic:semiconductors"] > 0
    assert weights["topic:entertainment"] < 0

    # Re-pressing flips the stored reaction instead of stacking a new row.
    feedback.record_reaction("d1", 1, +1)
    assert feedback.preference_weights()["topic:entertainment"] > 0


def test_unknown_digest_or_index():
    assert feedback.record_reaction("nope", 0, 1) is None
    _context()
    assert feedback.record_reaction("d1", 99, 1) is None


def test_cluster_score_and_neutrality():
    _context()
    feedback.record_reaction("d1", 0, +1)
    weights = feedback.preference_weights()
    up = feedback.cluster_feedback_score(["NVDA"], ["semiconductors"], weights)
    neutral = feedback.cluster_feedback_score(["unrelated"], ["politics"], weights)
    assert up > 0
    assert neutral == 0.0


def test_decay_reduces_weight(monkeypatch):
    _context()
    feedback.record_reaction("d1", 0, +1)
    fresh = feedback.preference_weights()["nvda"]
    # Same reaction viewed 90 days later (3 half-lives) is much weaker.
    real_time = time.time
    monkeypatch.setattr(feedback.time, "time", lambda: real_time() + 90 * 86400)
    aged = feedback.preference_weights()["nvda"]
    assert 0 < aged < fresh / 2


def test_recent_summary():
    _context()
    feedback.record_reaction("d1", 0, +1)
    feedback.record_reaction("d1", 1, -1)
    liked, disliked = feedback.recent_reaction_summary()
    assert liked == ["Nvidia earnings"]
    assert disliked == ["Celebrity story"]
