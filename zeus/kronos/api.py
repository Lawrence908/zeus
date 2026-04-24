# zeus/kronos/api.py — FastAPI router at /kronos (Phase 1 subset).
#
# Phase 1 endpoints:
#   GET  /kronos/jobs              list, filter by category / enabled
#   GET  /kronos/jobs/{id}         single job + last 20 runs
#   POST /kronos/jobs/{id}/run     manual trigger (gated by ZEUS_KRONOS_ALLOW_WRITE)
#   GET  /kronos/runs              recent runs across jobs
#   GET  /kronos/runs/{id}         one run
#   GET  /kronos/health            scheduler liveness
#
# Phase 2 adds POST/PATCH/DELETE on /kronos/jobs, enable/disable, upcoming,
# executors, categories.
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from zeus.kronos.models import JobCategory, JobDefinition, JobRun, JobStatus
from zeus.kronos.registry import KronosRegistry

router = APIRouter(prefix="/kronos", tags=["kronos"])


def _registry(request: Request) -> KronosRegistry:
    reg: KronosRegistry | None = getattr(request.app.state, "kronos_registry", None)
    if reg is None:
        raise HTTPException(503, detail="Kronos is not enabled")
    return reg


def _write_allowed() -> bool:
    return os.getenv("ZEUS_KRONOS_ALLOW_WRITE", "0").strip().lower() in ("1", "true", "yes", "on")


class JobWithRuns(BaseModel):
    job: JobDefinition
    runs: list[JobRun]


class ManualRunResponse(BaseModel):
    job_id: str
    run_id: str
    correlation_id: str


@router.get("/health")
async def kronos_health(request: Request) -> dict[str, Any]:
    scheduler = getattr(request.app.state, "kronos_scheduler", None)
    if scheduler is None:
        return {"enabled": False, "reason": "scheduler not started"}
    return {"enabled": True, **scheduler.health}


@router.get("/jobs")
async def list_jobs(
    request: Request,
    category: JobCategory | None = Query(None),
    enabled: bool | None = Query(None),
) -> list[JobDefinition]:
    reg = _registry(request)
    jobs = await reg.list(enabled=enabled)
    if category is not None:
        jobs = [j for j in jobs if j.category == category]
    return jobs


@router.get("/jobs/{job_id}", response_model=JobWithRuns)
async def get_job(job_id: str, request: Request) -> JobWithRuns:
    reg = _registry(request)
    job = await reg.get(job_id)
    if job is None:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")
    runs = await reg.list_runs(job_id=job_id, limit=20)
    return JobWithRuns(job=job, runs=runs)


@router.post("/jobs/{job_id}/run", response_model=ManualRunResponse)
async def run_job_now(job_id: str, request: Request) -> ManualRunResponse:
    if not _write_allowed():
        raise HTTPException(403, detail="ZEUS_KRONOS_ALLOW_WRITE is not set")
    reg = _registry(request)
    job = await reg.get(job_id)
    if job is None:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")

    executor = getattr(request.app.state, "kronos_executor", None)
    if executor is None:
        raise HTTPException(503, detail="Kronos executor not initialised")

    import asyncio

    correlation_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    run = await reg.storage.claim_fire(job_id, now, correlation_id)

    recent = getattr(request.app.state, "kronos_recent_runs", None)

    async def _dispatch() -> None:
        try:
            result = await executor.run(job, run)
        except Exception:
            return
        if recent is not None:
            recent.appendleft(result.model_dump(mode="json"))

    asyncio.create_task(_dispatch())
    return ManualRunResponse(
        job_id=job_id, run_id=run.id, correlation_id=correlation_id
    )


@router.get("/runs")
async def list_runs(
    request: Request,
    job_id: str | None = Query(None),
    status: JobStatus | None = Query(None),
    since: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> list[JobRun]:
    reg = _registry(request)
    return await reg.list_runs(job_id=job_id, status=status, since=since, limit=limit)


@router.get("/runs/{run_id}", response_model=JobRun)
async def get_run(run_id: str, request: Request) -> JobRun:
    reg = _registry(request)
    run = await reg.get_run(run_id)
    if run is None:
        raise HTTPException(404, detail=f"Unknown run: {run_id!r}")
    return run
