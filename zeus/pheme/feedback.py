# zeus/pheme/feedback.py - Reader feedback store for Pheme ranking.
#
# Telegram digest messages carry per-story thumbs buttons; each press lands
# here as a reaction row (SQLite, stdlib). At rank time the reactions become
# per-token preference weights with exponential time decay, so the digest
# tunes itself to what Chris actually reads instead of a static profile.
#
# Two artifacts under PHEME_DATA_DIR:
#   feedback.db          - reactions table (append-only)
#   digest_context.json  - digest_id -> per-story meta, written at delivery
#                          so a button press can resolve index -> story
from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("zeus.pheme.feedback")

_KEEP_CONTEXTS = 15  # digests still accepting feedback


def _data_dir() -> Path:
    return Path(os.getenv("PHEME_DATA_DIR", "zeus/data/pheme"))


def _db_path() -> Path:
    return _data_dir() / "feedback.db"


def _halflife_days() -> float:
    try:
        return max(1.0, float(os.getenv("PHEME_FEEDBACK_HALFLIFE_DAYS", "30")))
    except ValueError:
        return 30.0


def feedback_weight() -> float:
    """Significance adjustment scale; 0 disables the term."""
    try:
        return max(0.0, min(0.5, float(os.getenv("PHEME_FEEDBACK_WEIGHT", "0.15"))))
    except ValueError:
        return 0.15


def _connect() -> sqlite3.Connection:
    _data_dir().mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            digest_id TEXT NOT NULL,
            cluster_key TEXT NOT NULL,
            cluster_name TEXT NOT NULL,
            reaction INTEGER NOT NULL,          -- +1 up / -1 down
            entities TEXT NOT NULL DEFAULT '[]',
            topics TEXT NOT NULL DEFAULT '[]',
            sources TEXT NOT NULL DEFAULT '[]'
        )
        """
    )
    # One reaction per (digest, story); a second press overwrites the first.
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_reactions_story "
        "ON reactions (digest_id, cluster_key)"
    )
    return conn


# ---------------------------------------------------------------------------
# Digest context (written at delivery, read by the button callback)
# ---------------------------------------------------------------------------

def _context_path() -> Path:
    return _data_dir() / "digest_context.json"


def save_digest_context(digest_id: str, clusters: list[dict[str, Any]]) -> None:
    """Persist per-story meta so `pheme:fb:<digest>:<idx>` can resolve later."""
    path = _context_path()
    data: dict[str, Any] = {}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data[digest_id] = {"ts": time.time(), "clusters": clusters}
    for stale in sorted(data, key=lambda k: data[k].get("ts", 0))[:-_KEEP_CONTEXTS]:
        data.pop(stale, None)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    tmp.replace(path)


def _load_digest_context(digest_id: str) -> list[dict[str, Any]] | None:
    path = _context_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    entry = data.get(digest_id)
    return entry.get("clusters") if entry else None


# ---------------------------------------------------------------------------
# Recording
# ---------------------------------------------------------------------------

def record_reaction(digest_id: str, story_index: int, reaction: int) -> dict[str, Any] | None:
    """Record a thumbs press. Returns the story meta, or None when unresolvable."""
    clusters = _load_digest_context(digest_id)
    if not clusters or not 0 <= story_index < len(clusters):
        logger.warning("feedback for unknown digest/story: %s[%s]", digest_id, story_index)
        return None
    story = clusters[story_index]
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO reactions (ts, digest_id, cluster_key, cluster_name,
                                   reaction, entities, topics, sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (digest_id, cluster_key) DO UPDATE SET
                ts = excluded.ts, reaction = excluded.reaction
            """,
            (
                time.time(),
                digest_id,
                str(story.get("key", story_index)),
                str(story.get("name", ""))[:200],
                1 if reaction > 0 else -1,
                json.dumps(story.get("entities") or []),
                json.dumps(story.get("topics") or []),
                json.dumps(story.get("sources") or []),
            ),
        )
    logger.info(
        "feedback %s on %r (%s)",
        "up" if reaction > 0 else "down",
        str(story.get("name", ""))[:60],
        digest_id,
    )
    return story


# ---------------------------------------------------------------------------
# Preference weights
# ---------------------------------------------------------------------------

def preference_weights() -> dict[str, float]:
    """Per-token weights in [-1, 1] from decayed reactions.

    Tokens come from reacted stories' entities and topics (topics prefixed
    ``topic:`` so a topic never collides with an entity name). Weight is
    tanh(sum of decayed +1/-1 signals / 2): three consistent reactions push a
    token near saturation, one reaction nudges it.
    """
    if not _db_path().is_file():
        return {}
    now = time.time()
    halflife_s = _halflife_days() * 86400.0
    sums: dict[str, float] = {}
    with _connect() as conn:
        rows = conn.execute(
            "SELECT ts, reaction, entities, topics FROM reactions"
        ).fetchall()
    for ts, reaction, entities_json, topics_json in rows:
        decay = math.pow(0.5, max(0.0, now - float(ts)) / halflife_s)
        signal = float(reaction) * decay
        try:
            entities = json.loads(entities_json) or []
            topics = json.loads(topics_json) or []
        except json.JSONDecodeError:
            continue
        for e in entities:
            key = str(e).strip().casefold()
            if key:
                sums[key] = sums.get(key, 0.0) + signal
        for t in topics:
            key = f"topic:{str(t).strip().casefold()}"
            if key != "topic:":
                sums[key] = sums.get(key, 0.0) + signal
    return {k: math.tanh(v / 2.0) for k, v in sums.items() if abs(v) > 0.01}


def cluster_feedback_score(
    entities: list[str], topics: list[str], weights: dict[str, float] | None = None
) -> float:
    """Score a cluster against preference weights. Returns [-1, 1] (0 = no signal)."""
    if weights is None:
        weights = preference_weights()
    if not weights:
        return 0.0
    matched = [
        weights[k]
        for k in (
            *(str(e).strip().casefold() for e in entities),
            *(f"topic:{str(t).strip().casefold()}" for t in topics),
        )
        if k in weights
    ]
    if not matched:
        return 0.0
    # Average of matched token weights: broad weak matches don't out-shout
    # one strongly liked entity.
    return max(-1.0, min(1.0, sum(matched) / len(matched)))


def recent_reaction_summary(limit: int = 6) -> tuple[list[str], list[str]]:
    """(liked story names, disliked story names), newest first - for the rank prompt."""
    if not _db_path().is_file():
        return [], []
    with _connect() as conn:
        rows = conn.execute(
            "SELECT cluster_name, reaction FROM reactions ORDER BY ts DESC LIMIT 40"
        ).fetchall()
    liked: list[str] = []
    disliked: list[str] = []
    for name, reaction in rows:
        bucket = liked if reaction > 0 else disliked
        if name and name not in bucket and len(bucket) < limit:
            bucket.append(name)
    return liked, disliked
