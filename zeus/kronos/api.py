# zeus/kronos/api.py — FastAPI router at /kronos.
#
# Read endpoints:
#   GET  /kronos/jobs              list, filter by category / enabled
#   GET  /kronos/jobs/{id}         single job + last 20 runs
#   GET  /kronos/runs              recent runs across jobs
#   GET  /kronos/runs/{id}         one run
#   GET  /kronos/schedule/upcoming next N fire times across enabled jobs
#   GET  /kronos/executors         known built-in executor dotted paths
#   GET  /kronos/categories        JobCategory enum values
#   GET  /kronos/health            scheduler liveness
#
# Write endpoints (gated by ZEUS_KRONOS_ALLOW_WRITE=1):
#   POST   /kronos/jobs            create
#   PATCH  /kronos/jobs/{id}       partial update (schedule, params, safety, etc.)
#   DELETE /kronos/jobs/{id}       remove
#   POST   /kronos/jobs/{id}/run      manual trigger
#   POST   /kronos/jobs/{id}/enable
#   POST   /kronos/jobs/{id}/disable
from __future__ import annotations

import asyncio
import importlib
import inspect
import os
import pkgutil
import uuid
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import croniter
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from zeus.kronos.models import (
    JobCategory,
    JobDefinition,
    JobRun,
    JobSchedule,
    JobStatus,
)
from zeus.kronos.registry import KronosRegistry

router = APIRouter(prefix="/kronos", tags=["kronos"])


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _registry(request: Request) -> KronosRegistry:
    reg: KronosRegistry | None = getattr(request.app.state, "kronos_registry", None)
    if reg is None:
        raise HTTPException(503, detail="Kronos is not enabled")
    return reg


def _require_write() -> None:
    if os.getenv("ZEUS_KRONOS_ALLOW_WRITE", "0").strip().lower() not in (
        "1", "true", "yes", "on"
    ):
        raise HTTPException(403, detail="ZEUS_KRONOS_ALLOW_WRITE is not set")


def _resolve_tz(name: str):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return timezone.utc


# ------------------------------------------------------------------
# Response models
# ------------------------------------------------------------------


class JobWithRuns(BaseModel):
    job: JobDefinition
    runs: list[JobRun]


class ManualRunResponse(BaseModel):
    job_id: str
    run_id: str
    correlation_id: str


class UpcomingFire(BaseModel):
    job_id: str
    name: str
    next_fire: datetime
    timezone: str


class ExecutorInfo(BaseModel):
    dotted_path: str
    module: str
    function: str
    docstring: str | None = None


class JobPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    category: JobCategory | None = None
    schedule: JobSchedule | None = None
    executor: str | None = None
    agent: str | None = None
    endpoint: str | None = None
    params: dict[str, Any] | None = None
    safety_policy: str | None = None
    timeout_seconds: int | None = None
    max_retries: int | None = None
    tags: list[str] | None = None
    enabled: bool | None = None


# ------------------------------------------------------------------
# Read endpoints
# ------------------------------------------------------------------


@router.get("/health")
async def kronos_health(request: Request) -> dict[str, Any]:
    scheduler = getattr(request.app.state, "kronos_scheduler", None)
    if scheduler is None:
        return {"enabled": False, "reason": "scheduler not started"}
    return {"enabled": True, **scheduler.health}


@router.get("/categories")
async def list_categories() -> list[str]:
    return [c.value for c in JobCategory]


@router.get("/executors", response_model=list[ExecutorInfo])
async def list_executors() -> list[ExecutorInfo]:
    """Enumerate built-in executor callables under zeus.kronos.jobs.*."""
    return _discover_executors()


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


@router.get("/schedule/upcoming", response_model=list[UpcomingFire])
async def upcoming(
    request: Request, limit: int = Query(20, ge=1, le=200)
) -> list[UpcomingFire]:
    reg = _registry(request)
    jobs = await reg.list(enabled=True)
    now = datetime.now(timezone.utc)
    out: list[UpcomingFire] = []
    for job in jobs:
        next_fire = _compute_next_fire(job, now, await reg.last_fired_at(job.id))
        if next_fire is None:
            continue
        out.append(
            UpcomingFire(
                job_id=job.id,
                name=job.name,
                next_fire=next_fire,
                timezone=job.schedule.timezone,
            )
        )
    out.sort(key=lambda x: x.next_fire)
    return out[:limit]


# ------------------------------------------------------------------
# Write endpoints (gated)
# ------------------------------------------------------------------


@router.post("/jobs", response_model=JobDefinition, status_code=201)
async def create_job(job: JobDefinition, request: Request) -> JobDefinition:
    _require_write()
    reg = _registry(request)
    existing = await reg.get(job.id)
    if existing is not None:
        raise HTTPException(
            409, detail=f"Job id {job.id!r} already exists; use PATCH"
        )
    await reg.add(job)
    return job


@router.patch("/jobs/{job_id}", response_model=JobDefinition)
async def patch_job(job_id: str, body: JobPatch, request: Request) -> JobDefinition:
    _require_write()
    reg = _registry(request)
    current = await reg.get(job_id)
    if current is None:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return current

    # Pydantic v2 doesn't support mutating validators on frozen models, so
    # rebuild via dict round-trip. This re-runs the cross-field validators
    # (exactly-one-of-cron/run_at, executor-xor-agent).
    merged = current.model_dump()
    merged.update(updates)
    try:
        new_job = JobDefinition.model_validate(merged)
    except Exception as exc:
        raise HTTPException(422, detail=f"invalid update: {exc}")

    await reg.add(new_job)  # upsert preserves last_fired_at via _upsert_job_sync
    return new_job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, request: Request) -> dict[str, bool]:
    _require_write()
    reg = _registry(request)
    ok = await reg.delete(job_id)
    if not ok:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")
    return {"deleted": True}


@router.post("/jobs/{job_id}/enable", response_model=JobDefinition)
async def enable_job(job_id: str, request: Request) -> JobDefinition:
    _require_write()
    reg = _registry(request)
    ok = await reg.set_enabled(job_id, True)
    if not ok:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")
    job = await reg.get(job_id)
    assert job is not None
    return job


@router.post("/jobs/{job_id}/disable", response_model=JobDefinition)
async def disable_job(job_id: str, request: Request) -> JobDefinition:
    _require_write()
    reg = _registry(request)
    ok = await reg.set_enabled(job_id, False)
    if not ok:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")
    job = await reg.get(job_id)
    assert job is not None
    return job


@router.post("/jobs/{job_id}/run", response_model=ManualRunResponse)
async def run_job_now(job_id: str, request: Request) -> ManualRunResponse:
    _require_write()
    reg = _registry(request)
    job = await reg.get(job_id)
    if job is None:
        raise HTTPException(404, detail=f"Unknown job: {job_id!r}")

    executor = getattr(request.app.state, "kronos_executor", None)
    if executor is None:
        raise HTTPException(503, detail="Kronos executor not initialised")

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


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _compute_next_fire(
    job: JobDefinition, now: datetime, last_fired: datetime | None
) -> datetime | None:
    if job.schedule.run_at is not None:
        run_at = job.schedule.run_at
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=timezone.utc)
        return run_at if run_at > now else None
    if not job.schedule.cron:
        return None
    tz = _resolve_tz(job.schedule.timezone)
    base = (last_fired or now).astimezone(tz)
    try:
        nf = croniter(job.schedule.cron, base).get_next(datetime)
    except Exception:
        return None
    if nf.tzinfo is None:
        nf = nf.replace(tzinfo=tz)
    return nf.astimezone(timezone.utc)


_executor_cache: list[ExecutorInfo] | None = None


def _discover_executors() -> list[ExecutorInfo]:
    """Walk zeus.kronos.jobs for async callables named run_*. Cached per process."""
    global _executor_cache
    if _executor_cache is not None:
        return _executor_cache

    import zeus.kronos.jobs as jobs_pkg

    out: list[ExecutorInfo] = []
    for mod_info in pkgutil.iter_modules(jobs_pkg.__path__):
        if mod_info.ispkg or mod_info.name.startswith("_"):
            continue
        module_name = f"{jobs_pkg.__name__}.{mod_info.name}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for attr_name, attr in inspect.getmembers(module):
            if not attr_name.startswith("run_"):
                continue
            if not (inspect.iscoroutinefunction(attr) or inspect.isfunction(attr)):
                continue
            if getattr(attr, "__module__", "") != module_name:
                continue  # skip re-exports
            out.append(
                ExecutorInfo(
                    dotted_path=f"{module_name}.{attr_name}",
                    module=module_name,
                    function=attr_name,
                    docstring=inspect.getdoc(attr),
                )
            )
    out.sort(key=lambda e: e.dotted_path)
    _executor_cache = out
    return out
