# zeus/memory/config.py — Mnemosyne configuration and token-usage tracker.
#
# mem0 has been removed (April 2026). This module used to construct the mem0
# client; it's now reduced to the thread-safe TokenUsage accumulator that
# `zeus/ingest/run.py` still imports for the summary table.
#
# Ingest-time extraction tokens are now written to the SQLite usage log by
# `zeus/core/small_llm.py`. The TokenUsage tracker here is a per-run counter
# rebuilt from the small_llm usage rows stamped during the ingest window.
from __future__ import annotations

import os
import sqlite3
import threading
import time
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TokenUsage:
    """Thread-safe accumulator for LLM token usage during ingest."""

    input_tokens: int = 0
    output_tokens: int = 0
    llm_calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record(self, input_tok: int, output_tok: int) -> None:
        with self._lock:
            self.input_tokens += input_tok
            self.output_tokens += output_tok
            self.llm_calls += 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


_token_usage = TokenUsage()
_run_started_at: float = time.time()


def get_token_usage() -> TokenUsage:
    """Return a TokenUsage snapshot summed from small_llm usage rows since the
    last reset. Falls back to an empty counter if the usage DB is unavailable."""
    since_iso = datetime.fromtimestamp(_run_started_at, tz=timezone.utc).isoformat()
    usage_db = Path(os.getenv("ZEUS_SMALL_LLM_USAGE_DB", "zeus/data/small_llm_usage.db"))
    snapshot = TokenUsage()
    if not usage_db.exists():
        return snapshot
    try:
        with closing(sqlite3.connect(str(usage_db))) as conn:
            cur = conn.execute(
                "SELECT COALESCE(SUM(tokens_in), 0), COALESCE(SUM(tokens_out), 0), COUNT(*) "
                "FROM usage WHERE ts >= ?",
                (since_iso,),
            )
            row = cur.fetchone() or (0, 0, 0)
    except sqlite3.Error:
        return snapshot
    snapshot.input_tokens = int(row[0] or 0)
    snapshot.output_tokens = int(row[1] or 0)
    snapshot.llm_calls = int(row[2] or 0)
    return snapshot


def reset_token_usage() -> None:
    """Mark a new ingest window. get_token_usage() sums rows logged after this."""
    global _run_started_at
    _run_started_at = time.time()
