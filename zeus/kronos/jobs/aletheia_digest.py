# zeus/kronos/jobs/aletheia_digest.py — Weekly Aletheia drift digest.
#
# Renders the week's findings into a markdown report (new vs carried-over vs
# resolved), writes it under zeus/data/research/aletheia/, ingests it into the
# Knowledge layer (idempotent by iso-week), and pushes a Telegram headline.
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("zeus.kronos.aletheia")


async def run_weekly_digest(params: dict[str, Any]) -> dict[str, Any]:
    from zeus.orchestration.aletheia import config, notifier
    from zeus.orchestration.aletheia.digest import generate_digest
    from zeus.orchestration.aletheia.store import AletheiaStore

    if not config.enabled():
        return {"status": "skipped", "reason": "ZEUS_ALETHEIA_ENABLED is off"}

    week = str(params.get("week") or "").strip() or None
    store = AletheiaStore(config.db_path())
    result = await generate_digest(store, week=week, ingest=True)

    notified = await notifier.notify_digest(result)

    return {
        "status": "ok",
        "iso_week": result.iso_week,
        "total": result.total,
        "new": result.new,
        "carried": result.carried,
        "resolved": result.resolved,
        "path": result.path,
        "ingested": result.ingested,
        "notified": notified,
    }
