# zeus/core/tools/cache.py — In-memory TTL+LRU cache for tool results
#
# Scope: a short-TTL dedup cache so a model that re-asks the same thing twice
# (or two near-simultaneous chat requests that need the same Brave query)
# don't both burn through the Brave free-tier quota. NOT a persistence layer:
# cache is lost on process restart, which is correct — stale results leaking
# across restarts is worse than a cold miss.
#
# Keyed on (tool_name, canonical_args). Errors are never cached. Opt-in per
# tool via ToolSpec.cacheable.
from __future__ import annotations

import json
import logging
import os
import time
from collections import OrderedDict
from typing import Any

from zeus.core.tools.base import ToolResult

logger = logging.getLogger("zeus.tools.cache")


def _ttl_seconds() -> int:
    try:
        return max(0, int(os.getenv("ZEUS_TOOL_CACHE_TTL_SECONDS", "300")))
    except (TypeError, ValueError):
        return 300


def _max_entries() -> int:
    try:
        return max(1, int(os.getenv("ZEUS_TOOL_CACHE_MAX_ENTRIES", "256")))
    except (TypeError, ValueError):
        return 256


class ToolCache:
    """LRU cache with per-entry TTL. Thread-unsafe (single-process asyncio only)."""

    def __init__(self) -> None:
        self._store: OrderedDict[str, tuple[float, ToolResult]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _key(name: str, args: dict[str, Any]) -> str:
        # default=str keeps datetimes / paths from breaking the key build.
        return f"{name}:{json.dumps(args, sort_keys=True, default=str)}"

    def get(self, name: str, args: dict[str, Any]) -> ToolResult | None:
        ttl = _ttl_seconds()
        if ttl <= 0:
            return None
        key = self._key(name, args)
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        ts, result = entry
        if time.monotonic() - ts > ttl:
            # Expired — drop and miss.
            self._store.pop(key, None)
            self._misses += 1
            return None
        self._store.move_to_end(key)
        self._hits += 1
        return result

    def set(self, name: str, args: dict[str, Any], result: ToolResult) -> None:
        ttl = _ttl_seconds()
        if ttl <= 0:
            return
        if result.is_error:
            # Transient errors would poison the cache; never store them.
            return
        key = self._key(name, args)
        self._store[key] = (time.monotonic(), result)
        self._store.move_to_end(key)
        limit = _max_entries()
        while len(self._store) > limit:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, int]:
        return {"size": len(self._store), "hits": self._hits, "misses": self._misses}


_CACHE = ToolCache()


def get_cache() -> ToolCache:
    return _CACHE
