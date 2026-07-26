# zeus/orchestration/swarm/api.py
"""FastAPI surface for the Argo swarm: /swarm/*.

Enabled by ZEUS_SWARM_ENABLED (wired in zeus/core/main.py). P0 dispatches to a
stub worker, so no real repo/tool access happens yet; repo paths are still
validated to be under the home directory to lock the contract in early.
"""

from __future__ import annotations

import asyncio
import json
import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError

from zeus.orchestration.swarm import config, dag
from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.estimate import estimate_run
from zeus.orchestration.swarm.events import SwarmEventBus
from zeus.orchestration.swarm.models import (
    Run,
    RunSpec,
    RunView,
    SwarmEvent,
    SwarmMetrics,
)
from zeus.orchestration.swarm.store import SwarmStore

router = APIRouter(prefix="/swarm", tags=["swarm"])


class ApproveBody(BaseModel):
    approval_id: str
    approve: bool = True


class AnswerBody(BaseModel):
    answer: str
    approval_id: str | None = None  # optional; defaults to the oldest pending question


class PlanBody(BaseModel):
    goal: str
    repo: str
    budget_usd: float = 10.0
    max_parallel: int = 3
    dry_run: bool = False
    project_check: str | None = None  # override the planner's run-level check (P7)


class ProposeBody(BaseModel):
    goal: str
    repo: str | None = None  # defaults to the first allowlisted repo
    budget_usd: float = 1.0  # capped at ZEUS_SWARM_PROPOSE_BUDGET_USD server-side


def _with_estimate(view: RunView) -> RunView:
    view.estimate = estimate_run(view.nodes)
    return view


def _store(request: Request) -> SwarmStore:
    s: SwarmStore | None = getattr(request.app.state, "swarm_store", None)
    if s is None:
        raise HTTPException(503, detail="Swarm is not enabled (ZEUS_SWARM_ENABLED)")
    return s


def _coordinator(request: Request) -> Coordinator:
    c: Coordinator | None = getattr(request.app.state, "swarm_coordinator", None)
    if c is None:
        raise HTTPException(503, detail="Swarm is not enabled (ZEUS_SWARM_ENABLED)")
    return c


def _planner(request: Request):
    p = getattr(request.app.state, "swarm_planner", None)
    if p is None:
        raise HTTPException(503, detail="Swarm planner is not configured")
    return p


def _bus(request: Request) -> SwarmEventBus:
    b: SwarmEventBus | None = getattr(request.app.state, "swarm_bus", None)
    if b is None:
        raise HTTPException(503, detail="Swarm is not enabled (ZEUS_SWARM_ENABLED)")
    return b


def _validate_repo(repo: str) -> str:
    """Repo must be on the configured allowlist (ships with just the zeus repo)."""
    if not config.repo_allowed(repo):
        raise HTTPException(
            422,
            detail=f"repo not on the swarm allowlist (ZEUS_SWARM_REPO_ALLOWLIST): {repo!r}",
        )
    return os.path.realpath(os.path.expanduser(repo))


@router.get("/health")
async def swarm_health(request: Request) -> dict:
    enabled = getattr(request.app.state, "swarm_store", None) is not None
    return {"enabled": enabled}


@router.get("/repos")
async def repos() -> dict:
    """The configured repo allowlist (P11), so the UI can offer a picker."""
    return {"repos": config.repo_allowlist(), "propose_enabled": config.propose_enabled()}


@router.post("/propose", response_model=RunView)
async def propose(body: ProposeBody, request: Request) -> RunView:
    """Autonomously scope a goal into a plan-gated run (P11 - e.g. Kairos).

    Gated by ZEUS_SWARM_PROPOSE_ENABLED. The run always stops at the plan gate (a
    human must approve before any spend), and its budget is hard-capped at
    ZEUS_SWARM_PROPOSE_BUDGET_USD - an initiator cannot exceed it.
    """
    if not config.propose_enabled():
        raise HTTPException(403, detail="proposing runs is disabled (ZEUS_SWARM_PROPOSE_ENABLED)")
    allow = config.repo_allowlist()
    repo = _validate_repo(body.repo) if body.repo else (allow[0] if allow else None)
    if repo is None:
        raise HTTPException(422, detail="no repo on the swarm allowlist to propose against")
    budget = min(body.budget_usd, config.propose_budget_usd())
    try:
        result = await _planner(request).plan(body.goal, repo)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"planner failed: {exc}") from exc
    try:
        dag.assert_acyclic(result.nodes)  # type: ignore[arg-type]
        spec = RunSpec(
            goal=body.goal, repo=repo, nodes=result.nodes, budget_usd=budget,
            planner_cost_usd=result.cost_usd, project_check=result.project_check,
        )
    except (ValueError, ValidationError) as exc:
        raise HTTPException(422, detail=f"planner produced an invalid DAG: {exc}") from exc
    view = await _store(request).create_run(spec)
    await _coordinator(request).notify_pending(view.run.id)  # ping the human to approve
    return _with_estimate(view)


@router.post("/runs", response_model=RunView)
async def create_run(spec: RunSpec, request: Request) -> RunView:
    # RunSpec already rejects dup ids, self-deps, and unknown deps; also reject cycles.
    try:
        dag.assert_acyclic(spec.nodes)  # type: ignore[arg-type]  # structural: .id/.deps
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    spec = spec.model_copy(update={"repo": _validate_repo(spec.repo)})
    return _with_estimate(await _store(request).create_run(spec))


@router.post("/plan", response_model=RunView)
async def plan_run(body: PlanBody, request: Request) -> RunView:
    """Metis: scope a goal into a task DAG, then create a run awaiting plan approval."""
    repo = _validate_repo(body.repo)
    try:
        result = await _planner(request).plan(body.goal, repo)
    except Exception as exc:  # noqa: BLE001 - planner (LLM) failures surface as 502
        raise HTTPException(502, detail=f"planner failed: {exc}") from exc
    try:
        dag.assert_acyclic(result.nodes)  # type: ignore[arg-type]
        # Run-level check: explicit override > planner's suggestion > config default.
        project_check = (
            body.project_check if body.project_check is not None
            else (result.project_check or config.project_check_default())
        )
        spec = RunSpec(
            goal=body.goal, repo=repo, nodes=result.nodes,
            budget_usd=body.budget_usd, max_parallel=body.max_parallel, dry_run=body.dry_run,
            planner_cost_usd=result.cost_usd, project_check=project_check,
        )
    except (ValueError, ValidationError) as exc:
        raise HTTPException(422, detail=f"planner produced an invalid DAG: {exc}") from exc
    return _with_estimate(await _store(request).create_run(spec))


@router.get("/metrics", response_model=SwarmMetrics)
async def metrics(request: Request) -> SwarmMetrics:
    return await _store(request).metrics()


@router.get("/events", include_in_schema=False)
async def events_stream(request: Request) -> StreamingResponse:
    """SSE stream of run updates (P8), so the Swarm app refreshes on change."""
    bus = _bus(request)
    queue = bus.subscribe()

    async def gen():
        try:
            yield ": connected\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    evt = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(evt)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"  # keep the connection warm through proxies
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/runs", response_model=list[Run])
async def list_runs(request: Request, limit: int = 50) -> list[Run]:
    return await _store(request).list_runs(limit=limit)


@router.get("/runs/{run_id}/events", response_model=list[SwarmEvent])
async def run_events(run_id: str, request: Request, limit: int = 200) -> list[SwarmEvent]:
    return await _store(request).list_events(run_id, limit=limit)


@router.get("/runs/{run_id}", response_model=RunView)
async def get_run(run_id: str, request: Request) -> RunView:
    view = await _store(request).get_view(run_id)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return _with_estimate(view)


@router.post("/runs/{run_id}/approve", response_model=RunView)
async def approve(run_id: str, body: ApproveBody, request: Request) -> RunView:
    view = await _coordinator(request).resolve(run_id, body.approval_id, body.approve)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return view


@router.post("/runs/{run_id}/answer", response_model=RunView)
async def answer(run_id: str, body: AnswerBody, request: Request) -> RunView:
    """Answer a node's QUESTION gate (P10) and let the node run."""
    if not body.answer.strip():
        raise HTTPException(422, detail="answer must not be empty")
    view = await _coordinator(request).answer(run_id, body.answer.strip(), approval_id=body.approval_id)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return view


@router.post("/runs/{run_id}/kill", response_model=RunView)
async def kill(run_id: str, request: Request) -> RunView:
    view = await _coordinator(request).kill(run_id)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return view
