# zeus/pheme/cache.py - Per-run stage cache under zeus/data/pheme/.
#
# Every stage result is written as JSON keyed by run date + stage name so
# re-runs skip completed stages and deep-dive queries can inspect what each
# stage produced. Wall-clock on the local GPU is the real budget; the cache
# is what makes every stage skippable.
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("zeus.pheme.cache")


def pheme_data_dir() -> Path:
    return Path(os.getenv("PHEME_DATA_DIR", "zeus/data/pheme"))


def run_key(trigger: str, when: datetime | None = None) -> str:
    """Cache partition for one pipeline run: date for daily, timestamped for breaking."""
    now = when or datetime.now(timezone.utc)
    if trigger == "daily":
        return now.strftime("%Y-%m-%d")
    return now.strftime("%Y-%m-%d") + f"-breaking-{now.strftime('%H%M%S')}"


class StageCache:
    def __init__(self, run: str) -> None:
        self.dir = pheme_data_dir() / run
        self.dir.mkdir(parents=True, exist_ok=True)

    def path(self, stage: str) -> Path:
        return self.dir / f"{stage}.json"

    def get(self, stage: str, *, fingerprint: str | None = None) -> Any | None:
        """Read a stage result.

        When ``fingerprint`` is given (a hash of the run's item set), a cached
        entry only counts when it was written for the same item set. This is
        what keeps a same-day rerun after fresh ingest from reusing stale
        clusters or rankings. Entries without a stored fingerprint are treated
        as stale for fingerprinted reads.
        """
        p = self.path(stage)
        if not p.is_file():
            return None
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("corrupt stage cache %s: %s", p, exc)
            return None
        if fingerprint is None:
            return raw
        if isinstance(raw, dict) and raw.get("_fingerprint") == fingerprint:
            return raw.get("data")
        logger.info("stage cache %s stale (item set changed), recomputing", stage)
        return None

    def put(self, stage: str, data: Any, *, fingerprint: str | None = None) -> None:
        p = self.path(stage)
        payload = data if fingerprint is None else {"_fingerprint": fingerprint, "data": data}
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        tmp.replace(p)
