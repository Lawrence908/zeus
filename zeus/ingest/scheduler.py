# zeus/ingest/scheduler.py — Iris scheduled ingest (Sprint 9d / LAB-148 extension)
# Uses APScheduler to run Iris ingest and memory consolidation on a timer
# inside the FastAPI process. Schedule is controlled by env vars.
import logging
import os
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler

if TYPE_CHECKING:
    from zeus.ingest.pipeline import IngestPipeline

logger = logging.getLogger("iris.scheduler")

INGEST_HOURS = float(os.getenv("INGEST_SCHEDULE_HOURS", "6"))
INGEST_INCREMENTAL = os.getenv("INGEST_INCREMENTAL", "true").lower() == "true"
CONSOLIDATE_HOURS = float(os.getenv("CONSOLIDATE_SCHEDULE_HOURS", "24"))


async def _run_ingest(pipeline) -> None:
    """Scheduled Iris ingest callback."""
    logger.info("scheduler: starting periodic Iris ingest (incremental=%s)", INGEST_INCREMENTAL)
    try:
        results = await pipeline.run_all_sources(incremental=INGEST_INCREMENTAL)
        total_stored = sum(r.chunks_stored for r in results)
        logger.info("scheduler: ingest complete — %d chunks stored across %d source(s)", total_stored, len(results))
    except Exception as exc:
        logger.error("scheduler: ingest failed — %s", exc, exc_info=True)


async def _run_consolidation(consolidator) -> None:
    """Scheduled memory consolidation callback."""
    logger.info("scheduler: starting memory consolidation")
    try:
        result = await consolidator.run()
        logger.info(
            "scheduler: consolidation complete — %d merged, %d deleted",
            result.get("merged", 0),
            result.get("deleted", 0),
        )
    except Exception as exc:
        logger.error("scheduler: consolidation failed — %s", exc, exc_info=True)


def build_scheduler(pipeline, consolidator=None) -> AsyncIOScheduler:
    """
    Create and configure the APScheduler instance.

    pipeline     — IngestPipeline (must have run_all_sources())
    consolidator — MemoryConsolidator (optional; skipped if None)
    """
    scheduler = AsyncIOScheduler(timezone="UTC")

    scheduler.add_job(
        _run_ingest,
        "interval",
        hours=INGEST_HOURS,
        id="iris_ingest",
        args=[pipeline],
        misfire_grace_time=300,
    )
    logger.info("scheduler: iris_ingest every %.1fh", INGEST_HOURS)

    if consolidator is not None:
        scheduler.add_job(
            _run_consolidation,
            "interval",
            hours=CONSOLIDATE_HOURS,
            id="memory_consolidate",
            args=[consolidator],
            misfire_grace_time=600,
        )
        logger.info("scheduler: memory_consolidate every %.1fh", CONSOLIDATE_HOURS)

    return scheduler
