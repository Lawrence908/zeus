# zeus/ingest/scheduler.py — Iris scheduled ingest.
# Uses APScheduler to run Iris ingest on a timer inside the FastAPI process.
# Schedule is controlled by INGEST_SCHEDULE_HOURS / INGEST_INCREMENTAL env vars.
#
# (The memory-consolidation job was removed along with mem0. Idempotent
# re-ingest is now handled by MemoryStore.delete_by_source() per-source.)
import logging
import os
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler

if TYPE_CHECKING:
    from zeus.ingest.pipeline import IngestPipeline

logger = logging.getLogger("iris.scheduler")

INGEST_HOURS = float(os.getenv("INGEST_SCHEDULE_HOURS", "6"))
INGEST_INCREMENTAL = os.getenv("INGEST_INCREMENTAL", "true").lower() == "true"


async def _run_ingest(pipeline) -> None:
    logger.info("scheduler: starting periodic Iris ingest (incremental=%s)", INGEST_INCREMENTAL)
    try:
        results = await pipeline.run_all_sources(incremental=INGEST_INCREMENTAL)
        total_stored = sum(r.chunks_stored for r in results)
        logger.info("scheduler: ingest complete — %d chunks stored across %d source(s)", total_stored, len(results))
    except Exception as exc:
        logger.error("scheduler: ingest failed — %s", exc, exc_info=True)


def build_scheduler(pipeline) -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
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
    return scheduler
