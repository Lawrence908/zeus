# zeus/kronos/scheduler.py — asyncio tick loop that dispatches due jobs.
#
# On each tick:
#   1. List enabled jobs.
#   2. For each, compute next_fire = croniter(job.schedule.cron).get_next()
#      starting from last_fired_at (or created_at if never fired).
#   3. If next_fire <= now:
#        a. storage.claim_fire() — atomically insert PENDING JobRun and bump
#           last_fired_at. This is the crash-recovery anchor.
#        b. Spawn asyncio.create_task(executor.run(job, run)) under a semaphore.
#        c. If the schedule was a one-off (run_at), disable the job.
#   4. Sleep until next tick OR stop_event.set().
from __future__ import annotations

import asyncio
import logging
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import croniter

from zeus.kronos.executor import KronosExecutor
from zeus.kronos.models import JobDefinition
from zeus.kronos.registry import KronosRegistry

logger = logging.getLogger("zeus.kronos")


class KronosScheduler:
    def __init__(
        self,
        registry: KronosRegistry,
        executor: KronosExecutor,
        *,
        tick_seconds: float,
        max_concurrent: int,
        recent_runs_buffer: deque | None = None,
    ) -> None:
        self._registry = registry
        self._executor = executor
        self._tick_seconds = max(1.0, float(tick_seconds))
        self._sem = asyncio.Semaphore(max(1, max_concurrent))
        self._recent = recent_runs_buffer
        self.stop_event = asyncio.Event()
        self.health: dict[str, Any] = {
            "tick_count": 0,
            "last_tick_at": None,
            "error_count": 0,
            "queue_depth": 0,
            "enabled_jobs": 0,
        }

    async def run_forever(self) -> None:
        # Reap any PENDING/RUNNING rows left over from a previous process
        # (crash recovery). max_age = 2 ticks is a conservative cutoff;
        # anything older can't still be running in this fresh process.
        try:
            await self._registry.reap_orphans(max_age_seconds=self._tick_seconds * 2)
        except Exception as exc:
            logger.warning("kronos: reap_orphans failed at boot: %s", exc)

        logger.info(
            "kronos: scheduler started (tick=%.0fs, max_concurrent=%d)",
            self._tick_seconds, self._sem._value,  # type: ignore[attr-defined]
        )
        while not self.stop_event.is_set():
            try:
                await self._tick()
            except Exception as exc:
                self.health["error_count"] += 1
                logger.exception("kronos tick failed: %s", exc)
            # Sleep until next tick, but wake immediately on shutdown.
            try:
                await asyncio.wait_for(
                    self.stop_event.wait(), timeout=self._tick_seconds
                )
            except asyncio.TimeoutError:
                pass
        logger.info("kronos: scheduler stopped")

    async def _tick(self) -> None:
        now = datetime.now(timezone.utc)
        self.health["tick_count"] += 1
        self.health["last_tick_at"] = now.isoformat()
        jobs = await self._registry.list(enabled=True)
        self.health["enabled_jobs"] = len(jobs)

        for job in jobs:
            due = await self._is_due(job, now)
            if not due:
                continue
            # Atomic intent + last_fired_at update happens inside claim_fire.
            correlation_id = uuid.uuid4().hex[:12]
            try:
                run = await self._registry.storage.claim_fire(
                    job.id, now, correlation_id
                )
            except Exception as exc:
                logger.error("kronos: claim_fire failed for %s: %s", job.id, exc)
                self.health["error_count"] += 1
                continue

            # One-offs auto-disable after firing (before dispatch so a slow
            # dispatch can't cause a second claim).
            if job.schedule.run_at is not None:
                try:
                    await self._registry.set_enabled(job.id, False)
                except Exception as exc:
                    logger.warning("kronos: could not disable one-off %s: %s", job.id, exc)

            asyncio.create_task(self._dispatch_with_semaphore(job, run))

        self.health["queue_depth"] = max(
            0, self._sem._bound_value - self._sem._value  # type: ignore[attr-defined]
        ) if hasattr(self._sem, "_bound_value") else 0

    async def _is_due(self, job: JobDefinition, now: datetime) -> bool:
        # One-off: fire when run_at has passed.
        if job.schedule.run_at is not None:
            run_at = job.schedule.run_at
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=timezone.utc)
            return run_at <= now

        # Cron: compute next fire time from last_fired_at (or created_at if never fired).
        cron = job.schedule.cron
        if not cron:
            return False
        tz = _resolve_tz(job.schedule.timezone)
        now_local = now.astimezone(tz)
        last_fired = await self._registry.last_fired_at(job.id)
        base = last_fired.astimezone(tz) if last_fired else now_local
        try:
            itr = croniter(cron, base)
            next_fire = itr.get_next(datetime)
        except Exception as exc:
            logger.error("kronos: invalid cron %r on job %s: %s", cron, job.id, exc)
            return False
        # croniter may return naive in some versions; normalize.
        if next_fire.tzinfo is None:
            next_fire = next_fire.replace(tzinfo=tz)
        return next_fire <= now_local

    async def _dispatch_with_semaphore(self, job: JobDefinition, run) -> None:
        async with self._sem:
            try:
                result = await self._executor.run(job, run)
            except Exception as exc:
                logger.exception("kronos: executor raised for %s: %s", job.id, exc)
                return
            if self._recent is not None:
                self._recent.appendleft(result.model_dump(mode="json"))


def _resolve_tz(name: str):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        logger.warning("kronos: unknown timezone %r, falling back to UTC", name)
        return timezone.utc
