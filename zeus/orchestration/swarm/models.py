# zeus/orchestration/swarm/models.py
"""Pydantic models + enums for the Argo swarm state machine.

A Run owns a DAG of TaskNodes (deps between them) and a set of Approval gates.
Statuses drive the coordinator; see docs/swarm-orchestration-plan.md.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class RunStatus(str, Enum):
    PENDING_PLAN_APPROVAL = "pending_plan_approval"  # gate 1: approve the plan
    RUNNING = "running"
    PENDING_FINAL_APPROVAL = "pending_final_approval"  # gate 3: approve the merge
    COMPLETED = "completed"
    COMPLETED_PARTIAL = "completed_partial"  # fail-open: some nodes failed/unreachable
    FAILED = "failed"  # nothing succeeded
    CANCELLED = "cancelled"
    PAUSED_BUDGET = "paused_budget"


class NodeStatus(str, Enum):
    BLOCKED = "blocked"  # deps not yet succeeded
    READY = "ready"  # deps met, awaiting dispatch
    PENDING_APPROVAL = "pending_approval"  # gate 2: approve a write/risky node
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"  # exhausted attempts
    SKIPPED = "skipped"  # write gate rejected
    UNREACHABLE = "unreachable"  # a dependency failed (fail-open)


class ApprovalKind(str, Enum):
    PLAN = "plan"
    NODE_WRITE = "node_write"
    BUDGET = "budget"  # run exceeded budget_usd; approve to continue
    FINAL = "final"


class ApprovalState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Input specs (POST /swarm/runs)
# ---------------------------------------------------------------------------


class TaskNodeSpec(BaseModel):
    """One node of the task DAG as submitted by the caller (or planner)."""

    id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=300)
    deps: list[str] = Field(default_factory=list)
    acceptance: str = ""  # human-readable acceptance note
    check: str = ""  # shell command run in the worktree to verify the node (exit 0 = pass)
    tool_scope: list[str] = Field(default_factory=list)  # min tools this node may use
    model: str = ""  # model hint (e.g. "haiku" for trivial nodes); "" = worker default
    requires_approval: bool = False  # gate 2 before this node runs
    max_attempts: int = Field(default=1, ge=1, le=5)  # verify-retry budget

    @field_validator("id")
    @classmethod
    def _no_self_dep_chars(cls, v: str) -> str:
        if any(c.isspace() for c in v):
            raise ValueError("node id must not contain whitespace")
        return v


class RunSpec(BaseModel):
    """A project run: a goal, a target repo, and the task DAG to execute."""

    goal: str = Field(..., min_length=1, max_length=4000)
    repo: str = Field(..., min_length=1)  # absolute path under ~/ (validated server-side)
    nodes: list[TaskNodeSpec] = Field(..., min_length=1)
    budget_usd: float = Field(default=10.0, ge=0)
    max_parallel: int = Field(default=3, ge=1, le=16)
    dry_run: bool = False  # execute the DAG against a stub (zero spend) to validate shape
    planner_cost_usd: float = 0.0  # what Metis spent producing this DAG (set by /plan)

    @model_validator(mode="after")
    def _validate_dag(self) -> RunSpec:
        ids = [n.id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate node ids")
        idset = set(ids)
        for n in self.nodes:
            for d in n.deps:
                if d == n.id:
                    raise ValueError(f"node {n.id!r} depends on itself")
                if d not in idset:
                    raise ValueError(f"node {n.id!r} depends on unknown node {d!r}")
        return self


# ---------------------------------------------------------------------------
# Stored / view models
# ---------------------------------------------------------------------------


class TaskNode(BaseModel):
    run_id: str
    id: str
    title: str
    deps: list[str] = Field(default_factory=list)
    acceptance: str = ""
    check: str = ""
    tool_scope: list[str] = Field(default_factory=list)
    model: str = ""
    requires_approval: bool = False
    max_attempts: int = 1
    status: NodeStatus = NodeStatus.BLOCKED
    attempts: int = 0
    worker_id: str | None = None
    output: str | None = None
    error: str | None = None
    cost_usd: float = 0.0
    session_id: str | None = None  # Claude Code session (for transcript + ledger)
    updated_at: str = ""


class Approval(BaseModel):
    id: str
    run_id: str
    kind: ApprovalKind
    node_id: str | None = None
    state: ApprovalState = ApprovalState.PENDING
    created_at: str = ""
    resolved_at: str | None = None


class Run(BaseModel):
    id: str
    goal: str
    repo: str
    status: RunStatus = RunStatus.PENDING_PLAN_APPROVAL
    budget_usd: float = 10.0
    max_parallel: int = 3
    dry_run: bool = False
    planner_cost_usd: float = 0.0
    created_at: str = ""
    updated_at: str = ""


class RunEstimate(BaseModel):
    """Projected cost, computed at request time (never stored)."""

    total_usd: float
    per_node: dict[str, float]


class RunView(BaseModel):
    """Full run snapshot for GET /swarm/runs/{id}."""

    run: Run
    nodes: list[TaskNode]
    approvals: list[Approval]
    estimate: RunEstimate | None = None  # populated by the API, not the store

    def pending_approval(self, kind: ApprovalKind, node_id: str | None = None) -> Approval | None:
        for a in self.approvals:
            if a.state == ApprovalState.PENDING and a.kind == kind and a.node_id == node_id:
                return a
        return None
