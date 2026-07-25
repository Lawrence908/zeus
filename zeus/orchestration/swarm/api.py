# zeus/orchestration/swarm/api.py
"""FastAPI surface for the Argo swarm: /swarm/*.

Enabled by ZEUS_SWARM_ENABLED (wired in zeus/core/main.py). P0 dispatches to a
stub worker, so no real repo/tool access happens yet; repo paths are still
validated to be under the home directory to lock the contract in early.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ValidationError

from zeus.orchestration.swarm import config, dag
from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import Run, RunSpec, RunView
from zeus.orchestration.swarm.store import SwarmStore

router = APIRouter(prefix="/swarm", tags=["swarm"])


class ApproveBody(BaseModel):
    approval_id: str
    approve: bool = True


class PlanBody(BaseModel):
    goal: str
    repo: str
    budget_usd: float = 10.0
    max_parallel: int = 3


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


@router.post("/runs", response_model=RunView)
async def create_run(spec: RunSpec, request: Request) -> RunView:
    # RunSpec already rejects dup ids, self-deps, and unknown deps; also reject cycles.
    try:
        dag.assert_acyclic(spec.nodes)  # type: ignore[arg-type]  # structural: .id/.deps
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    spec = spec.model_copy(update={"repo": _validate_repo(spec.repo)})
    return await _store(request).create_run(spec)


@router.post("/plan", response_model=RunView)
async def plan_run(body: PlanBody, request: Request) -> RunView:
    """Metis: scope a goal into a task DAG, then create a run awaiting plan approval."""
    repo = _validate_repo(body.repo)
    try:
        specs = await _planner(request).plan(body.goal, repo)
    except Exception as exc:  # noqa: BLE001 - planner (LLM) failures surface as 502
        raise HTTPException(502, detail=f"planner failed: {exc}") from exc
    try:
        dag.assert_acyclic(specs)  # type: ignore[arg-type]
        spec = RunSpec(
            goal=body.goal, repo=repo, nodes=specs,
            budget_usd=body.budget_usd, max_parallel=body.max_parallel,
        )
    except (ValueError, ValidationError) as exc:
        raise HTTPException(422, detail=f"planner produced an invalid DAG: {exc}") from exc
    return await _store(request).create_run(spec)


@router.get("/runs", response_model=list[Run])
async def list_runs(request: Request, limit: int = 50) -> list[Run]:
    return await _store(request).list_runs(limit=limit)


@router.get("/runs/{run_id}", response_model=RunView)
async def get_run(run_id: str, request: Request) -> RunView:
    view = await _store(request).get_view(run_id)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return view


@router.post("/runs/{run_id}/approve", response_model=RunView)
async def approve(run_id: str, body: ApproveBody, request: Request) -> RunView:
    view = await _coordinator(request).resolve(run_id, body.approval_id, body.approve)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return view


@router.post("/runs/{run_id}/kill", response_model=RunView)
async def kill(run_id: str, request: Request) -> RunView:
    view = await _coordinator(request).kill(run_id)
    if view is None:
        raise HTTPException(404, detail=f"run not found: {run_id!r}")
    return view
