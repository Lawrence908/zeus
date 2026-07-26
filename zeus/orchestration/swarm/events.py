# zeus/orchestration/swarm/events.py
"""In-process pub/sub for live swarm updates (P8 streaming).

The coordinator publishes a small event whenever a run's state changes; the SSE
endpoint (`GET /swarm/events`) subscribes and forwards each event to connected
Swarm apps, so the UI can refresh on change instead of polling every 4s. This is
ephemeral and best-effort - the durable record is the store's audit log; the bus
is only for liveness. A slow bounded queue per subscriber drops rather than
blocks a stuck client.
"""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger("zeus.swarm.events")

_QUEUE_MAX = 256


class SwarmEventBus:
    def __init__(self) -> None:
        self._subs: set[asyncio.Queue[dict]] = set()

    def subscribe(self) -> asyncio.Queue[dict]:
        q: asyncio.Queue[dict] = asyncio.Queue(maxsize=_QUEUE_MAX)
        self._subs.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[dict]) -> None:
        self._subs.discard(q)

    async def publish(self, event: dict) -> None:
        """Fan out to every subscriber; never block on a slow one."""
        for q in list(self._subs):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                logger.debug("swarm event dropped for a slow subscriber")

    @property
    def subscriber_count(self) -> int:
        return len(self._subs)
