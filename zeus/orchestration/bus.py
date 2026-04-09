# zeus/orchestration/bus.py — Inter-agent request routing over the FastAPI bus
# All agent-to-agent calls go through here so agents stay decoupled from
# each other's concrete URLs.  The runtime is required to be on app.state.

import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from zeus.orchestration.runtime import AgentRuntime, AgentStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


# ------------------------------------------------------------------
# Request / response models
# ------------------------------------------------------------------


class BusCallRequest(BaseModel):
    target_agent: str
    endpoint: str
    method: str = "POST"
    payload: dict[str, Any] = {}


class BusCallResponse(BaseModel):
    agent: str
    endpoint: str
    status: str          # "ok" | "error"
    data: dict[str, Any] | None = None
    error: str | None = None


class AgentActionRequest(BaseModel):
    action: str          # "start" | "stop"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _runtime(request: Request) -> AgentRuntime:
    runtime: AgentRuntime | None = getattr(request.app.state, "agent_runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Agent runtime not initialised")
    return runtime


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

    # Forward the call to the actual FastAPI route
    bus_base = getattr(request.app.state, "zeus_bus_url", "http://localhost:8000")
    url = f"{bus_base}{body.endpoint}"
    client: httpx.AsyncClient = request.app.state.http_client

    try:
        if body.method.upper() == "POST":
            resp = await client.post(url, json=body.payload, timeout=30.0)
        elif body.method.upper() == "GET":
            resp = await client.get(url, params=body.payload, timeout=30.0)
        else:
            raise HTTPException(400, detail=f"Unsupported method: {body.method!r}")

        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        hooks = getattr(request.app.state, "orchestration_hooks", None)
        if hooks is not None:
            ctx = await hooks.run_post(
                {
                    "source": "orchestration_bus",
                    "target": body.target_agent,
                    "target_agent": body.target_agent,
                    "endpoint": body.endpoint,
                    "response_data": data,
                    "safety_policy": target.definition.safety_policy,
                    "response_status": resp.status_code,
                }
            )
            data = ctx.get("response_data", data)
        return BusCallResponse(
            agent=body.target_agent,
            endpoint=body.endpoint,
            status="ok",
            data=data,
        )
    except httpx.HTTPStatusError as exc:
        logger.error("Bus call %s%s failed: %s", body.target_agent, body.endpoint, exc)
        return BusCallResponse(
            agent=body.target_agent,
            endpoint=body.endpoint,
            status="error",
            error=str(exc),
        )
    except Exception as exc:
        logger.error("Bus call %s%s error: %s", body.target_agent, body.endpoint, exc)
        return BusCallResponse(
            agent=body.target_agent,
            endpoint=body.endpoint,
            status="error",
            error=str(exc),
        )
