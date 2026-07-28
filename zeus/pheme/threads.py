# zeus/pheme/threads.py - Persistent story-thread registry for Pheme.
#
# Clusters are per-run; threads survive across days. Each run's clusters are
# matched against recent threads by salient entity-token overlap: a match
# means today's cluster is a development of an ongoing story (with the
# thread's dated claim history available for a "what changed" note), a miss
# starts a new thread. This replaces vector-lookup guessing in stage 3 with
# actual story identity - the thing that makes "day 3 of the Berlin story"
# possible.
#
# Storage: zeus/data/pheme/threads.db (stdlib sqlite). Threads unseen for
# PHEME_THREAD_MAX_AGE_DAYS are pruned on each run.
from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger("zeus.pheme.threads")

_HISTORY_CAP = 14  # dated claims kept per thread
_MIN_SHARED_TOKENS = 2


def _db_path() -> Path:
    return Path(os.getenv("PHEME_DATA_DIR", "zeus/data/pheme")) / "threads.db"


def _max_age_days() -> int:
    try:
        return max(2, int(os.getenv("PHEME_THREAD_MAX_AGE_DAYS", "10")))
    except ValueError:
        return 10


def _connect() -> sqlite3.Connection:
    _db_path().parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS threads (
            id TEXT PRIMARY KEY,
            created_date TEXT NOT NULL,     -- YYYY-MM-DD first seen
            last_seen_date TEXT NOT NULL,   -- YYYY-MM-DD
            days_seen INTEGER NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            tokens TEXT NOT NULL,           -- json list of salient entity tokens
            last_claim TEXT NOT NULL DEFAULT '',
            history TEXT NOT NULL DEFAULT '[]'  -- json [{date, name, claim}]
        )
        """
    )
    return conn


@dataclass
class ThreadMatch:
    thread_id: str
    days_seen: int                 # including today
    is_new: bool
    first_seen: str = ""
    prior_history: list[dict] = field(default_factory=list)  # before today


def match_and_update(
    clusters: list[tuple[str, set[str], str, str]],
    *,
    today: str | None = None,
    generic_tokens: set[str] | None = None,
) -> dict[str, ThreadMatch]:
    """Match this run's clusters to threads and update the registry.

    ``clusters`` rows are (cluster_key, salient_tokens, name, claim); the
    caller computes tokens with the same collapse rules it clusters with.
    ``generic_tokens`` are run-frequent tokens ("earnings", "election") that
    may support a match but never carry it: a match needs >= 2 shared tokens
    of which at least one is distinctive, so Franklin Electric earnings
    cannot steal the Nvidia/Microsoft thread on "tech" + "earnings" alone.
    Returns cluster_key -> ThreadMatch. Same-day reruns are idempotent:
    a thread already seen today is updated in place without inflating
    days_seen, and stays "new" only if today is its first day.
    """
    generic_tokens = generic_tokens or set()
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = (
        datetime.strptime(today, "%Y-%m-%d") - timedelta(days=_max_age_days())
    ).strftime("%Y-%m-%d")

    out: dict[str, ThreadMatch] = {}
    with _connect() as conn:
        conn.execute("DELETE FROM threads WHERE last_seen_date < ?", (cutoff,))
        rows = conn.execute(
            "SELECT id, created_date, last_seen_date, days_seen, name, tokens, last_claim, history "
            "FROM threads"
        ).fetchall()
        threads = [
            {
                "id": r[0], "created_date": r[1], "last_seen_date": r[2],
                "days_seen": int(r[3]), "name": r[4],
                "tokens": set(json.loads(r[5]) or []),
                "last_claim": r[6], "history": json.loads(r[7]) or [],
            }
            for r in rows
        ]
        claimed: set[str] = set()

        # Strongest overlaps claim first so two clusters can't grab one thread.
        scored: list[tuple[int, int, tuple]] = []
        for pos, (key, tokens, name, claim) in enumerate(clusters):
            best, best_shared = None, 0
            for t in threads:
                overlap = tokens & t["tokens"]
                if len(overlap) > best_shared and overlap - generic_tokens:
                    best, best_shared = t, len(overlap)
            scored.append((best_shared, pos, (key, tokens, name, claim, best)))
        scored.sort(key=lambda s: (-s[0], s[1]))

        for shared, _pos, (key, tokens, name, claim, best) in scored:
            thread = best if (best and shared >= _MIN_SHARED_TOKENS and best["id"] not in claimed) else None
            if thread is None:
                tid = uuid.uuid4().hex[:12]
                conn.execute(
                    "INSERT INTO threads (id, created_date, last_seen_date, days_seen, name, tokens, last_claim, history) "
                    "VALUES (?, ?, ?, 1, ?, ?, ?, ?)",
                    (
                        tid, today, today, name,
                        json.dumps(sorted(tokens)), claim,
                        json.dumps([{"date": today, "name": name, "claim": claim}]),
                    ),
                )
                out[key] = ThreadMatch(thread_id=tid, days_seen=1, is_new=True, first_seen=today)
                continue

            claimed.add(thread["id"])
            seen_today = thread["last_seen_date"] == today
            days_seen = thread["days_seen"] if seen_today else thread["days_seen"] + 1
            prior_history = [h for h in thread["history"] if h.get("date") != today]
            history = (prior_history + [{"date": today, "name": name, "claim": claim}])[-_HISTORY_CAP:]
            merged_tokens = sorted(thread["tokens"] | tokens)[:40]
            conn.execute(
                "UPDATE threads SET last_seen_date = ?, days_seen = ?, name = ?, tokens = ?, last_claim = ?, history = ? "
                "WHERE id = ?",
                (
                    today, days_seen, name, json.dumps(merged_tokens),
                    claim, json.dumps(history), thread["id"],
                ),
            )
            out[key] = ThreadMatch(
                thread_id=thread["id"],
                days_seen=days_seen,
                is_new=(thread["created_date"] == today),
                first_seen=thread["created_date"],
                prior_history=prior_history[-5:],
            )
    return out
