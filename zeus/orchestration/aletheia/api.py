# zeus/orchestration/aletheia/api.py
"""FastAPI surface for Aletheia: /aletheia/*.

Enabled by ZEUS_ALETHEIA_ENABLED (wired in zeus/core/main.py).

Trust boundary note: unlike the coding swarm's /swarm/runs (which spends money
and edits repos), every path here can only trigger a *read-only* investigation.
There is no worker-type field to assert and no write/merge gate to bypass - the
router only ever runs the Aletheia sweep, so a push hook posting here cannot
escalate to a writing run. Read scope is still bounded by
ZEUS_ALETHEIA_OBSERVE_ROOTS and the enforced exclusion globs.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from zeus.orchestration.aletheia import config, notifier
from zeus.orchestration.aletheia.digest import generate_digest
from zeus.orchestration.aletheia.models import RunMode
from zeus.orchestration.aletheia.store import AletheiaStore
from zeus.orchestration.aletheia.sweep import run_sweep

logger = logging.getLogger("zeus.aletheia.api")

router = APIRouter(prefix="/aletheia", tags=["aletheia"])

# Keep strong refs to background sweep tasks so they are not GC'd mid-run.
_TASKS: set[asyncio.Task] = set()


def _store() -> AletheiaStore:
    return AletheiaStore(config.db_path())


def _require_enabled() -> None:
    if not config.enabled():
        raise HTTPException(status_code=403, detail="Aletheia is disabled (ZEUS_ALETHEIA_ENABLED)")


class RunBody(BaseModel):
    mode: str = "incremental"          # "full" or "incremental"
    changed_paths: list[str] = []      # repo-relative paths that changed (incremental)


class DigestBody(BaseModel):
    week: str | None = None            # ISO week "YYYY-Www"; default = current


@router.post("/runs", status_code=202)
async def create_run(body: RunBody) -> dict:
    _require_enabled()
    try:
        mode = RunMode(body.mode)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"invalid mode {body.mode!r}")

    store = _store()

    async def _bg() -> None:
        try:
            report = await run_sweep(store, mode=mode, changed_paths=body.changed_paths or None)
            if mode == RunMode.INCREMENTAL and config.notify_incremental():
                await notifier.notify_incremental(report)
        except Exception as exc:  # a background sweep crash must not go unlogged
            logger.exception("aletheia background sweep failed: %s", exc)

    task = asyncio.create_task(_bg())
    _TASKS.add(task)
    task.add_done_callback(_TASKS.discard)
    return {"status": "accepted", "mode": mode.value}


@router.get("/runs")
async def list_runs(limit: int = 50) -> dict:
    runs = await _store().list_runs(limit=limit)
    return {"runs": [r.model_dump() for r in runs]}


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    run = await _store().get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run.model_dump()


@router.get("/findings")
async def findings(week: str | None = None, reportable_only: bool = True) -> dict:
    from zeus.orchestration.aletheia.models import iso_week
    wk = week or iso_week()
    rows = await _store().findings_for_week(wk, reportable_only=reportable_only)
    return {"iso_week": wk, "count": len(rows), "findings": [f.model_dump() for f in rows]}


@router.post("/digest")
async def digest(body: DigestBody) -> dict:
    _require_enabled()
    result = await generate_digest(_store(), week=body.week, ingest=True)
    return result.model_dump(exclude={"markdown"})
