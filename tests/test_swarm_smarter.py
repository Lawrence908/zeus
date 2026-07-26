# tests/test_swarm_smarter.py — P9 critical-path scheduling + auto-rebase redo
import asyncio

from zeus.orchestration.swarm import dag
from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import NodeStatus, Run, RunStatus, TaskNode
from zeus.orchestration.swarm.notifier import NullNotifier
from zeus.orchestration.swarm.verifier import NoopVerifier
from zeus.orchestration.swarm.worker import StubWorker, WorkerResult
from zeus.orchestration.swarm.worktree import CommitResult, MergeResult


def _n(nid, deps=(), status=NodeStatus.READY):
    return TaskNode(run_id="r", id=nid, title=nid, deps=list(deps), status=status)


# ---- P9b critical-path scheduling ----------------------------------------


def test_critical_path_depth():
    # chain a->b->c (c deep), plus a leaf x. depth = longest downstream chain.
    nodes = [_n("a"), _n("b", ["a"]), _n("c", ["b"]), _n("x")]
    depth = dag.critical_path_depth(nodes)
    assert depth["a"] == 3 and depth["b"] == 2 and depth["c"] == 1 and depth["x"] == 1


def test_dispatchable_orders_by_critical_path():
    # Two ready roots: 'deep' gates a 2-node chain, 'shallow' gates nothing.
    nodes = [
        _n("shallow"),
        _n("deep"),
        _n("mid", ["deep"], status=NodeStatus.BLOCKED),
        _n("leaf", ["mid"], status=NodeStatus.BLOCKED),
    ]
    order = [n.id for n in dag.dispatchable(nodes)]
    assert order == ["deep", "shallow"]  # longest critical path first


def test_dispatchable_stable_on_ties():
    nodes = [_n("a"), _n("b"), _n("c")]  # all depth 1
    assert [n.id for n in dag.dispatchable(nodes)] == ["a", "b", "c"]  # original order


# ---- P9a auto-rebase by redo ----------------------------------------------


class _ConflictWorkspace:
    """Fake workspace: merge_node conflicts the first N times, then succeeds."""

    def __init__(self, conflicts: int) -> None:
        self._conflicts = conflicts
        self.merge_calls = 0
        self.worktrees_cut = 0
        self.branch = "swarm/run-r"
        self.integration_path = "/tmp/int"

    async def new_node_worktree(self, node_id):
        self.worktrees_cut += 1
        return f"/tmp/wt/{node_id}/{self.worktrees_cut}"

    async def commit_in(self, node, node_path):
        return CommitResult(committed=True, denied=[], commit="deadbeef")

    async def merge_node(self, node_id):
        self.merge_calls += 1
        if self.merge_calls <= self._conflicts:
            return MergeResult(merged=False, conflicts=["README.md"])
        return MergeResult(merged=True)

    async def discard_in(self, node_path):
        pass

    async def teardown_node(self, node_path):
        pass


def _exec(monkeypatch, retries, ws):
    """Persist a single-node run, then drive _execute_node directly with `ws`."""
    monkeypatch.setenv("ZEUS_SWARM_MERGE_CONFLICT_RETRIES", str(retries))
    import tempfile

    from zeus.orchestration.swarm.models import RunSpec, TaskNodeSpec
    from zeus.orchestration.swarm.store import SwarmStore

    store = SwarmStore(tempfile.mktemp(suffix=".db"))
    coord = Coordinator(store, StubWorker(), None, NoopVerifier(), NullNotifier())

    async def go():
        v = await store.create_run(RunSpec(goal="g", repo="/repo",
                                           nodes=[TaskNodeSpec(id="n1", title="t")]))
        node = v.nodes[0]
        run = v.run.model_copy(update={"status": RunStatus.RUNNING})
        await coord._execute_node(node, run, ws, v.nodes)
        return node

    return go


def test_merge_conflict_redo_recovers(monkeypatch):
    ws = _ConflictWorkspace(conflicts=1)

    async def scenario():
        node = await _exec(monkeypatch, 1, ws)()
        assert node.status == NodeStatus.SUCCEEDED
        assert ws.merge_calls == 2 and ws.worktrees_cut == 2  # initial + one redo
        assert node.attempts == 2

    asyncio.run(scenario())


def test_merge_conflict_exhausts_budget_fails(monkeypatch):
    ws = _ConflictWorkspace(conflicts=5)  # never resolves

    async def scenario():
        node = await _exec(monkeypatch, 1, ws)()
        assert node.status == NodeStatus.FAILED
        assert "merge conflict" in (node.error or "")
        assert ws.merge_calls == 2  # initial + one redo, then gives up (retries=1)

    asyncio.run(scenario())
