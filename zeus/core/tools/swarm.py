# zeus/core/tools/swarm.py — chat-path tools to drive & watch Argo swarm runs.
#
# Organic swarm use from chat: propose a run, check status, approve a gate, or
# answer a question - all wrapping the /swarm/* HTTP surface via loopback, so the
# same server-side gates (ZEUS_SWARM_PROPOSE_ENABLED, Aegis, budget caps) apply.
# The rich DAG/gates view lives in the Zeus OS Swarm app; these tools are for
# quick drive-and-watch in conversation.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.swarm")

_OS_HINT = "Open the Swarm app in Zeus OS (/os/) to watch or approve."


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


def _err(name: str, msg: str) -> ToolResult:
    return ToolResult(call_id="", name=name, content=msg, is_error=True)


async def _get(path: str, params: dict | None = None) -> Any:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{_core_url()}{path}", params=params)
        r.raise_for_status()
        return r.json()


async def _post(path: str, payload: dict) -> httpx.Response:
    async with httpx.AsyncClient(timeout=30.0) as client:
        return await client.post(f"{_core_url()}{path}", json=payload)


def _pending(view: dict) -> list[dict]:
    return [a for a in view.get("approvals", []) if a.get("state") == "pending"]


def _summarize_run(view: dict) -> str:
    run = view["run"]
    nodes = view.get("nodes", [])
    spent = sum(n.get("cost_usd", 0) for n in nodes) + (run.get("planner_cost_usd") or 0)
    lines = [
        f"run {run['id']} · {run['status']} · spent ${spent:.2f} of ${run['budget_usd']:.2f}",
        f"goal: {run['goal'][:160]}",
    ]
    for n in nodes:
        deps = f" <- {','.join(n['deps'])}" if n.get("deps") else ""
        lines.append(f"  [{n['status']}] {n['id']}{deps}: {n['title'][:80]}")
    gates = _pending(view)
    if gates:
        lines.append("pending gates: " + ", ".join(
            f"{a['kind']}{('/' + a['node_id']) if a.get('node_id') else ''}" for a in gates))
    if run.get("pr_url"):
        lines.append(f"PR: {run['pr_url']}")
    return "\n".join(lines)


# ---- swarm_status ---------------------------------------------------------

_STATUS_SPEC = ToolSpec(
    name="swarm_status",
    description=(
        "Report Argo swarm run status. With no run_id, lists recent runs (id, "
        "status, goal). With a run_id, shows that run's DAG (per-node status), "
        "spend vs budget, any pending approval gates, and the PR link. Use when "
        "the user asks about swarm/orchestration runs, what's in progress, or "
        "whether a run needs approval. Read-only."
    ),
    parameters={
        "type": "object",
        "properties": {
            "run_id": {"type": "string", "description": "A specific run to detail; omit to list recent runs."},
            "limit": {"type": "integer", "description": "Max runs to list (default 10)."},
        },
    },
)


async def _status_handler(args: dict[str, Any]) -> ToolResult:
    run_id = str(args.get("run_id") or "").strip()
    try:
        if run_id:
            view = await _get(f"/swarm/runs/{run_id}")
            return ToolResult(call_id="", name="swarm_status", content=_summarize_run(view))
        limit = max(1, min(50, int(args.get("limit") or 10)))
        runs = await _get("/swarm/runs", {"limit": limit})
        if not runs:
            return ToolResult(call_id="", name="swarm_status", content="No swarm runs yet.")
        lines = [f"{r['id']} · {r['status']} · {r['goal'][:80]}" for r in runs]
        return ToolResult(call_id="", name="swarm_status", content="\n".join(lines))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 503:
            return _err("swarm_status", "Swarm is not enabled (ZEUS_SWARM_ENABLED).")
        return _err("swarm_status", f"swarm_status HTTP {exc.response.status_code}")
    except httpx.HTTPError as exc:
        return _err("swarm_status", f"swarm_status failed: {exc}")


# ---- swarm_propose --------------------------------------------------------

_PROPOSE_SPEC = ToolSpec(
    name="swarm_propose",
    description=(
        "Scope a software goal into an Argo swarm run (a DAG of coding tasks) "
        "that WAITS for the user's plan approval before any work runs. Use when "
        "the user asks to have the swarm build/implement/fix something. The run "
        "never spends until approved (in the Swarm app, or via swarm_approve). "
        "Budget is capped server-side. Returns the run id + node count."
    ),
    parameters={
        "type": "object",
        "properties": {
            "goal": {"type": "string", "description": "What the swarm should accomplish."},
            "repo": {"type": "string", "description": "Target repo path (must be on the allowlist); omit for the default."},
            "budget_usd": {"type": "number", "description": "Requested budget; capped server-side."},
        },
        "required": ["goal"],
    },
)


async def _propose_handler(args: dict[str, Any]) -> ToolResult:
    goal = str(args.get("goal") or "").strip()
    if not goal:
        return _err("swarm_propose", "swarm_propose requires a 'goal'.")
    payload: dict[str, Any] = {"goal": goal}
    if args.get("repo"):
        payload["repo"] = str(args["repo"])
    if args.get("budget_usd") is not None:
        payload["budget_usd"] = float(args["budget_usd"])
    try:
        r = await _post("/swarm/propose", payload)
    except httpx.HTTPError as exc:
        return _err("swarm_propose", f"swarm_propose failed: {exc}")
    if r.status_code == 403:
        return _err("swarm_propose", "Proposing runs is disabled (set ZEUS_SWARM_PROPOSE_ENABLED=1).")
    if r.status_code >= 400:
        return _err("swarm_propose", f"swarm_propose HTTP {r.status_code}: {r.text[:160]}")
    view = r.json()
    run = view["run"]
    est = view.get("estimate") or {}
    est_s = f", est ${est['total_usd']:.2f}" if est.get("total_usd") is not None else ""
    body = (
        f"Proposed run {run['id']} — {len(view.get('nodes', []))} nodes{est_s}, "
        f"budget ${run['budget_usd']:.2f}. Waiting for plan approval.\n{_OS_HINT}"
    )
    return ToolResult(call_id="", name="swarm_propose", content=body)


# ---- swarm_approve --------------------------------------------------------

_APPROVE_SPEC = ToolSpec(
    name="swarm_approve",
    description=(
        "Approve or reject a pending Argo swarm gate for a run. ONLY call this "
        "when the user explicitly asks to approve/reject (approving the plan gate "
        "starts real, paid work). `kind` picks which gate (plan/final/node_write/"
        "budget); defaults to the run's plan gate. Set approve=false to reject."
    ),
    parameters={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"},
            "kind": {"type": "string", "enum": ["plan", "final", "node_write", "budget"],
                     "description": "Which gate to resolve (default plan)."},
            "node_id": {"type": "string", "description": "For node_write gates."},
            "approve": {"type": "boolean", "description": "True to approve (default), false to reject."},
        },
        "required": ["run_id"],
    },
)


async def _approve_handler(args: dict[str, Any]) -> ToolResult:
    run_id = str(args.get("run_id") or "").strip()
    if not run_id:
        return _err("swarm_approve", "swarm_approve requires 'run_id'.")
    kind = str(args.get("kind") or "plan")
    node_id = args.get("node_id")
    approve = args.get("approve", True)
    try:
        view = await _get(f"/swarm/runs/{run_id}")
        gate = next((a for a in _pending(view)
                     if a["kind"] == kind and (node_id is None or a.get("node_id") == node_id)), None)
        if gate is None:
            return _err("swarm_approve", f"No pending {kind} gate on run {run_id}.")
        r = await _post(f"/swarm/runs/{run_id}/approve",
                        {"approval_id": gate["id"], "approve": bool(approve)})
        if r.status_code >= 400:
            return _err("swarm_approve", f"swarm_approve HTTP {r.status_code}: {r.text[:160]}")
        verb = "approved" if approve else "rejected"
        return ToolResult(call_id="", name="swarm_approve",
                          content=f"{verb} {kind} gate on run {run_id}.\n" + _summarize_run(r.json()))
    except httpx.HTTPError as exc:
        return _err("swarm_approve", f"swarm_approve failed: {exc}")


# ---- swarm_answer ---------------------------------------------------------

_ANSWER_SPEC = ToolSpec(
    name="swarm_answer",
    description=(
        "Answer a swarm node's QUESTION gate (a clarification the run is paused "
        "on) with free text, so the node can proceed. Use when the user provides "
        "the answer to a swarm question. Defaults to the run's oldest pending "
        "question."
    ),
    parameters={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"},
            "answer": {"type": "string", "description": "The clarification text."},
        },
        "required": ["run_id", "answer"],
    },
)


async def _answer_handler(args: dict[str, Any]) -> ToolResult:
    run_id = str(args.get("run_id") or "").strip()
    answer = str(args.get("answer") or "").strip()
    if not run_id or not answer:
        return _err("swarm_answer", "swarm_answer requires 'run_id' and 'answer'.")
    try:
        r = await _post(f"/swarm/runs/{run_id}/answer", {"answer": answer})
    except httpx.HTTPError as exc:
        return _err("swarm_answer", f"swarm_answer failed: {exc}")
    if r.status_code >= 400:
        return _err("swarm_answer", f"swarm_answer HTTP {r.status_code}: {r.text[:160]}")
    return ToolResult(call_id="", name="swarm_answer",
                      content=f"Answered the question on run {run_id}.\n" + _summarize_run(r.json()))


def register() -> None:
    """Register the swarm chat tools when the swarm is enabled."""
    if os.getenv("ZEUS_SWARM_ENABLED", "0").strip().lower() not in ("1", "true", "yes", "on"):
        return
    registry.register(_STATUS_SPEC, _status_handler)
    registry.register(_PROPOSE_SPEC, _propose_handler)
    registry.register(_APPROVE_SPEC, _approve_handler)
    registry.register(_ANSWER_SPEC, _answer_handler)
    logger.info("swarm chat tools registered (status, propose, approve, answer)")
