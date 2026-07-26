# zeus/orchestration/swarm/__init__.py
"""Argo swarm orchestration: scope + complete software projects.

Phase 0 substrate: a durable run/task-graph state machine with checkpoint
approval gates, dispatching to a pluggable worker (a stub in P0; sandboxed
Claude Code workers in P1). See docs/swarm-orchestration-plan.md.
"""

from zeus.orchestration.swarm.models import (
    Approval,
    ApprovalKind,
    ApprovalState,
    NodeStatus,
    Run,
    RunSpec,
    RunStatus,
    RunView,
    TaskNode,
    TaskNodeSpec,
)

__all__ = [
    "Approval",
    "ApprovalKind",
    "ApprovalState",
    "NodeStatus",
    "Run",
    "RunSpec",
    "RunStatus",
    "RunView",
    "TaskNode",
    "TaskNodeSpec",
]
