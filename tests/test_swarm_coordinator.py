# tests/test_swarm_coordinator.py — Argo swarm P0 state-machine tests
import asyncio
import os
import tempfile

from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import (
    ApprovalKind,
    ApprovalState,
    NodeStatus,
    RunSpec,
    RunStatus,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.worker import StubWorker, Worker, WorkerResult


def _fresh():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SwarmStore(path)
    return store, Coordinator(store, StubWorker()), path


def _node(nid, deps=None, requires_approval=False):
    return TaskNodeSpec(id=nid, title=f"do {nid}", deps=deps or [], requires_approval=requires_approval)


def _status(view, nid):
    return next(n for n in view.nodes if n.id == nid).status


class FailingWorker:
    async def run(self, node, run, workspace=None, feedback=None) -> WorkerResult:
        return WorkerResult(success=False, error="boom")


class SelectiveFailWorker:
    def __init__(self, fail_ids):
        self.fail_ids = set(fail_ids)

    async def run(self, node, run, workspace=None, feedback=None) -> WorkerResult:
        if node.id in self.fail_ids:
            return WorkerResult(success=False, error=f"{node.id} boom")
        return WorkerResult(success=True, output="ok")


# ---------------------------------------------------------------------------
# Happy path with a node-write gate
# ---------------------------------------------------------------------------


def test_full_run_through_all_gates():
    store, coord, _ = _fresh()

    async def scenario():
        spec = RunSpec(
            goal="ship it",
            repo=os.path.expanduser("~"),
            nodes=[
                _node("a"),
                _node("b", deps=["a"], requires_approval=True),  # gate 2
                _node("c", deps=["b"]),
            ],
        )
        view = await store.create_run(spec)

        # Gate 1: created pending, a is ready, b/c blocked, one PLAN approval.
        assert view.run.status == RunStatus.PENDING_PLAN_APPROVAL
        assert _status(view, "a") == NodeStatus.READY
        assert _status(view, "b") == NodeStatus.BLOCKED
        plan = view.pending_approval(ApprovalKind.PLAN)
        assert plan is not None

        # Approve plan -> a runs & succeeds -> b unblocks but hits its write gate.
        view = await coord.resolve(view.run.id, plan.id, approve=True)
        assert view.run.status == RunStatus.RUNNING
        assert _status(view, "a") == NodeStatus.SUCCEEDED
        assert _status(view, "b") == NodeStatus.PENDING_APPROVAL
        assert _status(view, "c") == NodeStatus.BLOCKED
        gate2 = view.pending_approval(ApprovalKind.NODE_WRITE, node_id="b")
        assert gate2 is not None

        # Approve b's write gate -> b runs -> c unblocks, runs -> final gate.
        view = await coord.resolve(view.run.id, gate2.id, approve=True)
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL
        assert _status(view, "b") == NodeStatus.SUCCEEDED
        assert _status(view, "c") == NodeStatus.SUCCEEDED
        final = view.pending_approval(ApprovalKind.FINAL)
        assert final is not None

        # Approve final -> completed.
        view = await coord.resolve(view.run.id, final.id, approve=True)
        assert view.run.status == RunStatus.COMPLETED

    asyncio.run(scenario())


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


def test_reject_plan_cancels_run():
    store, coord, _ = _fresh()

    async def scenario():
        view = await store.create_run(
            RunSpec(goal="x", repo=os.path.expanduser("~"), nodes=[_node("a")])
        )
        plan = view.pending_approval(ApprovalKind.PLAN)
        view = await coord.resolve(view.run.id, plan.id, approve=False)
        assert view.run.status == RunStatus.CANCELLED

    asyncio.run(scenario())


def test_reject_node_write_cascade_skips_descendants():
    store, coord, _ = _fresh()

    async def scenario():
        spec = RunSpec(
            goal="x",
            repo=os.path.expanduser("~"),
            nodes=[
                _node("a", requires_approval=True),  # gated at the root
                _node("b", deps=["a"]),
            ],
        )
        view = await store.create_run(spec)
        plan = view.pending_approval(ApprovalKind.PLAN)
        view = await coord.resolve(view.run.id, plan.id, approve=True)
        gate = view.pending_approval(ApprovalKind.NODE_WRITE, node_id="a")

        # Reject a -> a skipped, b (its descendant) skipped. Nothing succeeded and
        # nothing failed, so the run is cancelled (no subgraph to deliver).
        view = await coord.resolve(view.run.id, gate.id, approve=False)
        assert _status(view, "a") == NodeStatus.SKIPPED
        assert _status(view, "b") == NodeStatus.SKIPPED
        assert view.run.status == RunStatus.CANCELLED

    asyncio.run(scenario())


# ---------------------------------------------------------------------------
# Failure + parallelism budget
# ---------------------------------------------------------------------------


def test_worker_failure_with_no_survivors_fails_run():
    store, _, path = _fresh()
    coord = Coordinator(store, FailingWorker())

    async def scenario():
        view = await store.create_run(
            RunSpec(goal="x", repo=os.path.expanduser("~"), nodes=[_node("a")])
        )
        plan = view.pending_approval(ApprovalKind.PLAN)
        view = await coord.resolve(view.run.id, plan.id, approve=True)
        assert _status(view, "a") == NodeStatus.FAILED
        assert view.run.status == RunStatus.FAILED  # nothing succeeded

    asyncio.run(scenario())


def test_fail_open_delivers_passing_subgraph():
    store, _, _ = _fresh()
    coord = Coordinator(store, SelectiveFailWorker({"b"}))

    async def scenario():
        # a is an independent root; b fails and strands its dependent c.
        spec = RunSpec(
            goal="x",
            repo=os.path.expanduser("~"),
            nodes=[_node("a"), _node("b"), _node("c", deps=["b"])],
        )
        view = await store.create_run(spec)
        plan = view.pending_approval(ApprovalKind.PLAN)
        view = await coord.resolve(view.run.id, plan.id, approve=True)

        assert _status(view, "a") == NodeStatus.SUCCEEDED
        assert _status(view, "b") == NodeStatus.FAILED
        assert _status(view, "c") == NodeStatus.UNREACHABLE  # fail-open, not a run failure
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL

        final = view.pending_approval(ApprovalKind.FINAL)
        view = await coord.resolve(view.run.id, final.id, approve=True)
        assert view.run.status == RunStatus.COMPLETED_PARTIAL

    asyncio.run(scenario())


class CostWorker:
    def __init__(self, per_node=0.6):
        self.per = per_node

    async def run(self, node, run, workspace=None, feedback=None) -> WorkerResult:
        return WorkerResult(success=True, output="ok", cost_usd=self.per)


def test_budget_kill_switch_pauses_then_resumes():
    store, _, _ = _fresh()
    coord = Coordinator(store, CostWorker(0.6))  # 3 nodes x $0.60 vs $1.00 budget

    async def scenario():
        spec = RunSpec(goal="x", repo=os.path.expanduser("~"), budget_usd=1.0,
                       nodes=[_node("a"), _node("b"), _node("c")])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)

        # a ($0.60) ok; b takes it to $1.20 > $1.00 -> paused before c runs.
        assert view.run.status == RunStatus.PAUSED_BUDGET
        assert _status(view, "c") == NodeStatus.READY
        budget = view.pending_approval(ApprovalKind.BUDGET)
        assert budget is not None

        # Approve the overrun -> headroom granted, c runs, run settles.
        view = await coord.resolve(view.run.id, budget.id, approve=True)
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL
        assert _status(view, "c") == NodeStatus.SUCCEEDED

    asyncio.run(scenario())


def test_kill_skips_open_nodes():
    store, coord, _ = _fresh()

    async def scenario():
        spec = RunSpec(
            goal="x",
            repo=os.path.expanduser("~"),
            nodes=[_node("a"), _node("b", deps=["a"])],
        )
        view = await store.create_run(spec)
        view = await coord.kill(view.run.id)
        assert view.run.status == RunStatus.CANCELLED
        assert all(n.status == NodeStatus.SKIPPED for n in view.nodes)

    asyncio.run(scenario())


# keep the Worker protocol referenced so imports stay honest
_ = Worker
