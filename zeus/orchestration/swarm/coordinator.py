# zeus/orchestration/swarm/coordinator.py
"""Argo coordinator: drives a run through the checkpoint-approval state machine.

Flow (P0, synchronous against the stub worker):

    create -> PENDING_PLAN_APPROVAL
      approve(plan)      -> RUNNING
        schedule ready DAG nodes (deps met), <= max_parallel
          node.requires_approval -> NODE_WRITE gate (PENDING_APPROVAL)
            approve(node_write) -> node runs
          else -> dispatch to worker
        all nodes terminal & none failed -> PENDING_FINAL_APPROVAL
          approve(final) -> COMPLETED
        any node FAILED -> FAILED

Parallel/async dispatch and a real verifier arrive in P3; here dispatch is
awaited inline (the stub returns instantly), which keeps the machine
deterministic and easy to test.
"""

from __future__ import annotations

import logging

from zeus.orchestration.swarm import dag
from zeus.orchestration.swarm.models import (
    ApprovalKind,
    ApprovalState,
    NodeStatus,
    Run,
    RunStatus,
    RunView,
    TaskNode,
)
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.worker import Worker

logger = logging.getLogger("zeus.swarm.coordinator")

_MAX_ITERS = 10_000  # safety bound on the drive loop


class Coordinator:
    def __init__(self, store: SwarmStore, worker: Worker) -> None:
        self._store = store
        self._worker = worker

    # ---- driver ----------------------------------------------------------

    async def advance(self, run_id: str) -> RunView | None:
        """Drive a RUNNING run until it completes, fails, or blocks on a gate."""
        view = await self._store.get_view(run_id)
        if view is None:
            return None
        if view.run.status != RunStatus.RUNNING:
            return view

        for _ in range(_MAX_ITERS):
            progressed = await self._step(view.run, view.nodes)
            view = await self._store.get_view(run_id)
            assert view is not None

            if dag.all_settled(view.nodes):
                # Fail-open: if anything succeeded, deliver that subgraph through the
                # final gate. Otherwise distinguish a real failure from a run whose
                # work was all rejected away (nothing failed, nothing to deliver).
                if dag.any_succeeded(view.nodes):
                    await self._store.create_approval(run_id, ApprovalKind.FINAL)
                    await self._store.set_run_status(run_id, RunStatus.PENDING_FINAL_APPROVAL)
                elif dag.has_failure(view.nodes):
                    await self._store.set_run_status(run_id, RunStatus.FAILED)
                    logger.warning("swarm run %s failed (no node succeeded)", run_id)
                else:
                    await self._store.set_run_status(run_id, RunStatus.CANCELLED)
                break
            if not progressed:
                break  # waiting on an approval gate (nothing else dispatchable)

        return await self._store.get_view(run_id)

    async def _step(self, run: Run, nodes: list[TaskNode]) -> bool:
        """One scheduling pass. Returns True if it changed any state."""
        progressed = False

        # 1. Unblock nodes whose deps have all succeeded.
        for n in dag.newly_ready(nodes):
            n.status = NodeStatus.READY
            await self._store.update_node(n)
            progressed = True

        # 2. Dispatch READY nodes up to the parallelism budget.
        capacity = run.max_parallel - dag.running_count(nodes)
        for n in dag.dispatchable(nodes):
            if capacity <= 0:
                break
            if n.requires_approval:
                # Gate 2: hold this node until a NODE_WRITE approval is granted.
                await self._store.create_approval(run.id, ApprovalKind.NODE_WRITE, n.id)
                n.status = NodeStatus.PENDING_APPROVAL
                await self._store.update_node(n)
                progressed = True
                continue

            n.status = NodeStatus.RUNNING
            n.attempts += 1
            await self._store.update_node(n)
            capacity -= 1
            progressed = True

            result = await self._worker.run(n, run)
            n.cost_usd = result.cost_usd
            n.session_id = result.session_id
            if result.success:
                n.status = NodeStatus.SUCCEEDED
                n.output = result.output
                await self._store.update_node(n)
            else:
                # TODO(P1): retry up to n.max_attempts before giving up.
                n.status = NodeStatus.FAILED
                n.error = result.error or "worker reported failure"
                await self._store.update_node(n)
                # Fail-open: strand everything downstream, keep the rest running.
                await self._mark_unreachable(n, nodes)

        return progressed

    # ---- gates -----------------------------------------------------------

    async def resolve(self, run_id: str, approval_id: str, approve: bool) -> RunView | None:
        state = ApprovalState.APPROVED if approve else ApprovalState.REJECTED
        ap = await self._store.resolve_approval(approval_id, state)
        if ap is None or ap.run_id != run_id:
            return await self._store.get_view(run_id)

        if ap.kind == ApprovalKind.PLAN:
            if approve:
                await self._store.set_run_status(run_id, RunStatus.RUNNING)
                return await self.advance(run_id)
            await self._store.set_run_status(run_id, RunStatus.CANCELLED)

        elif ap.kind == ApprovalKind.NODE_WRITE:
            view = await self._store.get_view(run_id)
            if view is None:
                return None
            node = next((n for n in view.nodes if n.id == ap.node_id), None)
            if node is not None:
                if approve:
                    node.requires_approval = False  # cleared so it won't re-gate
                    node.status = NodeStatus.READY
                    await self._store.update_node(node)
                else:
                    await self._skip_cascade(node, view.nodes)
            return await self.advance(run_id)

        elif ap.kind == ApprovalKind.FINAL:
            if approve:
                view = await self._store.get_view(run_id)
                all_ok = view is not None and all(
                    n.status == NodeStatus.SUCCEEDED for n in view.nodes
                )
                await self._store.set_run_status(
                    run_id, RunStatus.COMPLETED if all_ok else RunStatus.COMPLETED_PARTIAL
                )
            else:
                await self._store.set_run_status(run_id, RunStatus.CANCELLED)

        return await self._store.get_view(run_id)

    async def kill(self, run_id: str) -> RunView | None:
        view = await self._store.get_view(run_id)
        if view is None:
            return None
        for n in view.nodes:
            if n.status not in (NodeStatus.SUCCEEDED, NodeStatus.FAILED, NodeStatus.SKIPPED):
                n.status = NodeStatus.SKIPPED
                await self._store.update_node(n)
        await self._store.set_run_status(run_id, RunStatus.CANCELLED)
        return await self._store.get_view(run_id)

    _TERMINAL = (
        NodeStatus.SUCCEEDED,
        NodeStatus.FAILED,
        NodeStatus.SKIPPED,
        NodeStatus.UNREACHABLE,
    )

    async def _skip_cascade(self, node: TaskNode, nodes: list[TaskNode]) -> None:
        """Reject a node: skip it and every node that (transitively) depends on it."""
        node.status = NodeStatus.SKIPPED
        await self._store.update_node(node)
        for d in dag.descendants(node.id, nodes):
            if d.status not in self._TERMINAL:
                d.status = NodeStatus.SKIPPED
                await self._store.update_node(d)

    async def _mark_unreachable(self, node: TaskNode, nodes: list[TaskNode]) -> None:
        """Fail-open: a node failed, so its transitive dependents can never run."""
        for d in dag.descendants(node.id, nodes):
            if d.status not in self._TERMINAL:
                d.status = NodeStatus.UNREACHABLE
                await self._store.update_node(d)
