# zeus/kronos/jobs/aletheia_sweep.py — Nightly Aletheia documentation-drift sweep.
#
# Registered as a Kronos job (not a Kairos observation source): Aletheia is a
# scheduled batch job with a weekly digest, which is exactly Kronos's shape, and
# it inherits Kronos's enable gate, timeout, and runs feed for free.
#
# Scheduled runs are silent by design (findings persist; the weekly digest is the
# delivery). Gated by ZEUS_ALETHEIA_ENABLED so a seeded-but-off job never spends.
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("zeus.kronos.aletheia")


async def run_nightly_sweep(params: dict[str, Any]) -> dict[str, Any]:
    from zeus.orchestration.aletheia import config
    from zeus.orchestration.aletheia.models import RunMode
    from zeus.orchestration.aletheia.store import AletheiaStore
    from zeus.orchestration.aletheia.sweep import run_sweep

    if not config.enabled():
        return {"status": "skipped", "reason": "ZEUS_ALETHEIA_ENABLED is off"}

    store = AletheiaStore(config.db_path())
    report = await run_sweep(store, mode=RunMode.FULL)

    pruned = await store.prune(retention_days=config.findings_retention_days())

    r = report.run
    return {
        "status": "ok",
        "run_id": r.id,
        "run_status": r.status.value,
        "docs_total": r.docs_total,
        "docs_complete": r.docs_complete,
        "docs_incomplete": r.docs_incomplete,
        "findings_reportable": r.findings_reportable,
        "cost_usd": round(r.cost_usd, 4),
        "pruned_rows": pruned,
    }
