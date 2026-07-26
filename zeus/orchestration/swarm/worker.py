# zeus/orchestration/swarm/worker.py
"""Worker abstraction: the coordinator dispatches a TaskNode to a Worker.

Phase 0 ships StubWorker (instant no-op) so the state machine can be exercised
without a sandbox. Phase 1 adds a sandboxed Claude Code worker implementing the
same protocol (spawn `claude -p` in an OpenShell/NemoClaw container on a git
worktree, stream results back).
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel

from zeus.orchestration.swarm.models import Run, TaskNode


class WorkerResult(BaseModel):
    success: bool
    output: str = ""
    error: str | None = None
    # From `claude -p` result JSON: feeds the usage ledger + kill-switch budget.
    cost_usd: float = 0.0
    session_id: str | None = None


class Worker(Protocol):
    # `workspace` is the git worktree path a code worker acts in (None for the stub);
    # `feedback` carries a prior verify/worker failure on a retry.
    async def run(
        self, node: TaskNode, run: Run, workspace: str | None, feedback: str | None = None
    ) -> WorkerResult: ...


class StubWorker:
    """No-op worker: marks every node succeeded. For P0 state-machine tests."""

    async def run(
        self, node: TaskNode, run: Run, workspace: str | None = None, feedback: str | None = None
    ) -> WorkerResult:
        return WorkerResult(
            success=True,
            output=f"[stub] would complete {node.id!r}: {node.title}",
        )
