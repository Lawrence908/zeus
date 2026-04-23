# zeus/orchestration/bus.py — Inter-agent request routing over the FastAPI bus
# All agent-to-agent calls go through here so agents stay decoupled from
# each other's concrete URLs.  The runtime is required to be on app.state.

from __future__ import annotations

import asyncio
import logging
import uuid
from collections import deque
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from zeus.orchestration.runtime import (
    AgentRuntime,
    AgentStatus,
    AgentStep,
    TaskRecord,
    TaskRunner,
    TaskStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

# Ring buffer capacity for task records
_MAX_TASK_RECORDS = 100


# ------------------------------------------------------------------
# Request / response models
# ------------------------------------------------------------------


class BusCallRequest(BaseModel):
    target_agent: str
    endpoint: str
    method: str = "POST"
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None  # LAB-335: auto-generated if absent
    idempotent: bool = False           # LAB-337: suppress non-500 errors


class BusCallResponse(BaseModel):
    agent: str
    endpoint: str
    status: str          # "ok" | "error"
    data: dict[str, Any] | None = None
    error: str | None = None
    correlation_id: str | None = None  # LAB-335


class AgentActionRequest(BaseModel):
    action: str          # "start" | "stop"


class TaskCreateRequest(BaseModel):
    agent: str
    task_description: str = ""
    steps: list[AgentStep] | None = None  # None → use agent's default steps


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _runtime(request: Request) -> AgentRuntime:
    runtime: AgentRuntime | None = getattr(request.app.state, "agent_runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Agent runtime not initialised")
    return runtime


def _task_records(request: Request) -> deque[TaskRecord]:
    """Get or create the task records ring buffer on app.state."""
    records: deque[TaskRecord] | None = getattr(request.app.state, "task_records", None)
    if records is None:
        records = deque(maxlen=_MAX_TASK_RECORDS)
        request.app.state.task_records = records
    return records


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------


@router.get("/status")
async def orchestration_status(request: Request) -> dict:
    """Return status of all agents in the olympian swarm."""
    return _runtime(request).get_status()


@router.post("/agents/{agent_name}/action")
async def agent_action(
    agent_name: str, body: AgentActionRequest, request: Request
) -> dict:
    """Start or stop a named agent."""
    rt = _runtime(request)
    try:
        if body.action == "start":
            await rt.start_agent(agent_name)
        elif body.action == "stop":
            await rt.stop_agent(agent_name)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {body.action!r}")
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_name!r}")
    return {"agent": agent_name, "action": body.action, "ok": True}


@router.post("/call", response_model=BusCallResponse)
async def bus_call(body: BusCallRequest, request: Request) -> BusCallResponse:
    """
    Route a call from one agent to another via the bus.

    The target agent must be RUNNING and the endpoint must be declared in its
    YAML definition (if it declares any endpoints at all).
    """
    rt = _runtime(request)
    correlation_id = body.correlation_id or uuid.uuid4().hex[:12]

    target = rt.get_agent(body.target_agent)
    if target is None:
        raise HTTPException(404, detail=f"Agent not found: {body.target_agent!r}")
    if target.status != AgentStatus.RUNNING:
        raise HTTPException(
            503,
            detail=(
                f"Agent {body.target_agent!r} is not running "
                f"(status: {target.status})"
            ),
        )

    # Validate against declared endpoints (skip if agent declares none)
    declared = {e["path"] for e in target.definition.endpoints}
    if declared and body.endpoint not in declared:
        raise HTTPException(
            400,
            detail=(
                f"Endpoint {body.endpoint!r} not declared for "
                f"agent {body.target_agent!r}"
            ),
        )

    # Per-agent timeout from YAML config, fallback to 30s (LAB-336)
    timeout_s: float = target.definition.config.get("timeout_seconds", 30.0)

    hooks = getattr(request.app.state, "orchestration_hooks", None)

    # Run pre-hooks (LAB-340) — mutate payload/context before dispatch
    pre_ctx: dict[str, Any] = {
        "source": "orchestration_bus",
        "target_agent": body.target_agent,
        "endpoint": body.endpoint,
        "method": body.method,
        "payload": body.payload,
        "correlation_id": correlation_id,
        "safety_policy": target.definition.safety_policy,
    }
    if hooks is not None:
        pre_ctx = await hooks.run_pre(pre_ctx)
        body.payload = pre_ctx.get("payload", body.payload)

    # Forward the call to the actual FastAPI route
    bus_base = getattr(request.app.state, "zeus_bus_url", "http://localhost:8000")
    url = f"{bus_base}{body.endpoint}"
    client: httpx.AsyncClient = request.app.state.http_client

    logger.info(
        "[bus:call correlation_id=%s] %s %s%s timeout=%.0fs",
        correlation_id, body.method, body.target_agent, body.endpoint, timeout_s,
    )

    import time as _time
    call_start = _time.monotonic()
    try:
        if body.method.upper() == "POST":
            resp = await client.post(url, json=body.payload, timeout=timeout_s)
        elif body.method.upper() == "GET":
            resp = await client.get(url, params=body.payload, timeout=timeout_s)
        else:
            raise HTTPException(400, detail=f"Unsupported method: {body.method!r}")

        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        latency_ms = (_time.monotonic() - call_start) * 1000

        # Run post-hooks
        if hooks is not None:
            post_ctx = await hooks.run_post(
                {
                    "source": "orchestration_bus",
                    "target": body.target_agent,
                    "target_agent": body.target_agent,
                    "endpoint": body.endpoint,
                    "response_data": data,
                    "safety_policy": target.definition.safety_policy,
                    "response_status": resp.status_code,
                    "latency_ms": latency_ms,
                    "correlation_id": correlation_id,
                }
            )
            data = post_ctx.get("response_data", data)
        return BusCallResponse(
            agent=body.target_agent,
            endpoint=body.endpoint,
            status="ok",
            data=data,
            correlation_id=correlation_id,
        )
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code if exc.response is not None else 500
        # LAB-337: idempotent requests suppress non-500 errors
        if body.idempotent and status_code < 500:
            logger.warning(
                "[bus:call correlation_id=%s] idempotent suppressed %d for %s%s: %s",
                correlation_id, status_code, body.target_agent, body.endpoint, exc,
            )
            return BusCallResponse(
                agent=body.target_agent,
                endpoint=body.endpoint,
                status="ok",
                data={"idempotent_suppressed": True, "original_status": status_code},
                correlation_id=correlation_id,
            )
        logger.error(
            "[bus:call correlation_id=%s] %s%s failed: %s",
            correlation_id, body.target_agent, body.endpoint, exc,
        )
        return BusCallResponse(
            agent=body.target_agent,
            endpoint=body.endpoint,
            status="error",
            error=str(exc),
            correlation_id=correlation_id,
        )
    except Exception as exc:
        logger.error(
            "[bus:call correlation_id=%s] %s%s error: %s",
            correlation_id, body.target_agent, body.endpoint, exc,
        )
        return BusCallResponse(
            agent=body.target_agent,
            endpoint=body.endpoint,
            status="error",
            error=str(exc),
            correlation_id=correlation_id,
        )


# ------------------------------------------------------------------
# Internal bus_call for TaskRunner (bypasses HTTP, reuses logic)
# ------------------------------------------------------------------


async def _internal_bus_call(
    request: Request,
    *,
    target_agent: str,
    endpoint: str,
    method: str = "POST",
    payload: dict[str, Any] | None = None,
) -> BusCallResponse:
    """Call bus_call programmatically for TaskRunner steps."""
    body = BusCallRequest(
        target_agent=target_agent,
        endpoint=endpoint,
        method=method,
        payload=payload or {},
    )
    return await bus_call(body, request)


# ------------------------------------------------------------------
# Task routes (LAB-333)
# ------------------------------------------------------------------


@router.post("/tasks")
async def create_task(body: TaskCreateRequest, request: Request) -> dict:
    """Dispatch a task to an agent. Returns task_id for polling."""
    rt = _runtime(request)
    agent_state = rt.get_agent(body.agent)
    if agent_state is None:
        raise HTTPException(404, detail=f"Agent not found: {body.agent!r}")

    steps = body.steps
    if steps is None:
        steps = agent_state.definition.steps
    if not steps:
        raise HTTPException(
            400, detail=f"No steps provided and agent {body.agent!r} has no default steps"
        )

    records = _task_records(request)
    runner = TaskRunner(
        bus_call_fn=lambda **kw: _internal_bus_call(request, **kw),
        task_records=records,
    )

    # Create the record synchronously so we can return the ID
    record = TaskRecord(
        agent_name=body.agent,
        description=body.task_description,
        steps=steps,
    )
    records.append(record)

    async def _run_task() -> None:
        record.status = TaskStatus.RUNNING
        import time as _time
        t0 = _time.monotonic()
        for step in record.steps:
            result = await runner._execute_step(body.agent, step)
            record.results.append(result)
            # Match TaskRunner.run: any terminal "failed" result stops the task.
            # "skipped" results (on_failure="skip") are not failures.
            if result.status == "failed":
                record.status = TaskStatus.FAILED
                record.elapsed_ms = (_time.monotonic() - t0) * 1000
                return
        record.status = TaskStatus.DONE
        record.elapsed_ms = (_time.monotonic() - t0) * 1000

    asyncio.create_task(_run_task())
    return {"task_id": record.id, "status": record.status.value}


@router.get("/tasks")
async def list_tasks(request: Request) -> list[dict]:
    """List recent tasks from the ring buffer."""
    records = _task_records(request)
    return [
        {
            "task_id": r.id,
            "agent": r.agent_name,
            "description": r.description,
            "status": r.status.value,
            "elapsed_ms": r.elapsed_ms,
            "step_count": len(r.steps),
            "results_count": len(r.results),
        }
        for r in records
    ]


@router.get("/tasks/{task_id}")
async def get_task(task_id: str, request: Request) -> dict:
    """Poll a task by ID."""
    records = _task_records(request)
    for r in records:
        if r.id == task_id:
            return r.model_dump()
    raise HTTPException(404, detail=f"Task not found: {task_id!r}")


@router.get("/kairos/status")
async def kairos_status(request: Request) -> dict:
    """Report current state of the KAIROS daemon (LAB-330)."""
    state = getattr(request.app.state, "kairos_state", None)
    if state is None:
        return {"enabled": False, "reason": "daemon not started"}
    return state.snapshot()
