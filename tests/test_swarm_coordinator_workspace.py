# tests/test_swarm_coordinator_workspace.py — coordinator + git worktree + denylist
import asyncio
import os
import subprocess
import tempfile

from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import (
    ApprovalKind,
    NodeStatus,
    RunSpec,
    RunStatus,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.verifier import CommandVerifier
from zeus.orchestration.swarm.worker import WorkerResult
from zeus.orchestration.swarm.worktree import CodeWorkspace


def _run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def _init_repo(path):
    _run(["git", "init", "-q", "-b", "main"], path)
    _run(["git", "config", "user.email", "t@t"], path)
    _run(["git", "config", "user.name", "t"], path)
    with open(os.path.join(path, "README.md"), "w") as f:
        f.write("# repo\n")
    _run(["git", "add", "-A"], path)
    _run(["git", "commit", "-qm", "init"], path)


class FileWorker:
    """Writes a per-node file into the worktree, then reports success."""

    def __init__(self, files):
        self.files = files  # node_id -> (relpath, content)

    async def run(self, node, run, workspace, feedback=None) -> WorkerResult:
        rel, content = self.files[node.id]
        full = os.path.join(workspace, rel)
        os.makedirs(os.path.dirname(full) or workspace, exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        return WorkerResult(success=True, output=f"wrote {rel}", cost_usd=0.01, session_id=f"s-{node.id}")


class FlakyWorker:
    """Writes ok.txt only from the 2nd attempt on; always writes attempt.txt."""

    def __init__(self):
        self.calls = 0

    async def run(self, node, run, workspace, feedback=None) -> WorkerResult:
        self.calls += 1
        with open(os.path.join(workspace, "attempt.txt"), "w") as f:
            f.write(str(self.calls))
        if self.calls >= 2:
            with open(os.path.join(workspace, "ok.txt"), "w") as f:
                f.write("ok\n")
        return WorkerResult(success=True, output=f"attempt {self.calls}", cost_usd=0.01)


def _status(view, nid):
    return next(n for n in view.nodes if n.id == nid).status


def _mk(tmp_path, worker, verifier=None):
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    _init_repo(repo)
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SwarmStore(db)
    factory = lambda r, rid: CodeWorkspace(r, rid, base_dir=str(tmp_path / "wt"))  # noqa: E731
    return repo, store, Coordinator(store, worker, factory, verifier)


def test_parallel_independent_nodes_both_land(tmp_path):
    repo, store, coord = _mk(
        tmp_path, FileWorker({"a": ("out/a.txt", "A\n"), "b": ("out/b.txt", "B\n")}))

    async def scenario():
        spec = RunSpec(goal="g", repo=repo, max_parallel=2,
                       nodes=[TaskNodeSpec(id="a", title="a"), TaskNodeSpec(id="b", title="b")])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        assert _status(view, "a") == NodeStatus.SUCCEEDED
        assert _status(view, "b") == NodeStatus.SUCCEEDED
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL
        files = subprocess.run(["git", "ls-tree", "-r", "--name-only", f"swarm/run-{view.run.id}"],
                               cwd=repo, capture_output=True, text=True).stdout
        assert "out/a.txt" in files and "out/b.txt" in files  # both merges landed

    asyncio.run(scenario())


def test_parallel_merge_conflict_auto_rebase_recovers(tmp_path, monkeypatch):
    # Both nodes edit README.md from the same base tip -> one merges, the other
    # conflicts. P9a: the loser re-cuts from the new tip and redoes, so both land.
    monkeypatch.setenv("ZEUS_SWARM_MERGE_CONFLICT_RETRIES", "1")
    repo, store, coord = _mk(
        tmp_path, FileWorker({"a": ("README.md", "from a\n"), "b": ("README.md", "from b\n")}))

    async def scenario():
        spec = RunSpec(goal="g", repo=repo, max_parallel=2,
                       nodes=[TaskNodeSpec(id="a", title="a"), TaskNodeSpec(id="b", title="b")])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        assert sorted(n.status.value for n in view.nodes) == ["succeeded", "succeeded"]
        # the rebased node ran twice (initial conflict + redo)
        assert max(n.attempts for n in view.nodes) == 2
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL

    asyncio.run(scenario())


def test_parallel_merge_conflict_no_retry_fails_one(tmp_path, monkeypatch):
    # With auto-rebase disabled, the classic behaviour: one node fails fail-open.
    monkeypatch.setenv("ZEUS_SWARM_MERGE_CONFLICT_RETRIES", "0")
    repo, store, coord = _mk(
        tmp_path, FileWorker({"a": ("README.md", "from a\n"), "b": ("README.md", "from b\n")}))

    async def scenario():
        spec = RunSpec(goal="g", repo=repo, max_parallel=2,
                       nodes=[TaskNodeSpec(id="a", title="a"), TaskNodeSpec(id="b", title="b")])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        statuses = sorted(n.status.value for n in view.nodes)
        assert statuses == ["failed", "succeeded"]  # exactly one lost the merge race
        failed = next(n for n in view.nodes if n.status == NodeStatus.FAILED)
        assert "merge conflict" in (failed.error or "")
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL  # fail-open

    asyncio.run(scenario())


def test_verify_retry_then_succeed(tmp_path):
    repo, store, coord = _mk(tmp_path, FlakyWorker(), CommandVerifier())

    async def scenario():
        spec = RunSpec(goal="g", repo=repo, nodes=[
            TaskNodeSpec(id="a", title="make ok", check="test -f ok.txt", max_attempts=2)])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        a = next(n for n in view.nodes if n.id == "a")
        assert a.status == NodeStatus.SUCCEEDED
        assert a.attempts == 2  # first attempt failed the check, second passed
        # committed the passing attempt only
        files = subprocess.run(["git", "ls-tree", "-r", "--name-only", f"swarm/run-{view.run.id}"],
                               cwd=repo, capture_output=True, text=True).stdout
        assert "ok.txt" in files

    asyncio.run(scenario())


def test_verify_exhausted_fails_node(tmp_path):
    class NeverPasses:
        async def run(self, node, run, workspace, feedback=None):
            with open(os.path.join(workspace, "junk.txt"), "w") as f:
                f.write("x")
            return WorkerResult(success=True, output="wrote junk")

    repo, store, coord = _mk(tmp_path, NeverPasses(), CommandVerifier())

    async def scenario():
        spec = RunSpec(goal="g", repo=repo, nodes=[
            TaskNodeSpec(id="a", title="never", check="test -f ok.txt", max_attempts=2)])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        a = next(n for n in view.nodes if n.id == "a")
        assert a.status == NodeStatus.FAILED
        assert "verification failed" in (a.error or "")
        # nothing committed; the failed attempt was discarded
        files = subprocess.run(["git", "ls-tree", "-r", "--name-only", f"swarm/run-{view.run.id}"],
                               cwd=repo, capture_output=True, text=True).stdout
        assert "junk.txt" not in files

    asyncio.run(scenario())


def test_commit_per_node_and_denylist_rejection(tmp_path):
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    _init_repo(repo)

    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SwarmStore(db)
    worker = FileWorker({
        "a": ("generated/a.txt", "hello from a\n"),
        "b": ("zeus/orchestration/evil.py", "# tamper\n"),  # denied path
    })
    factory = lambda r, rid: CodeWorkspace(r, rid, base_dir=str(tmp_path / "wt"))  # noqa: E731
    coord = Coordinator(store, worker, factory)

    async def scenario():
        spec = RunSpec(
            goal="two independent edits",
            repo=repo,
            nodes=[TaskNodeSpec(id="a", title="write a"), TaskNodeSpec(id="b", title="tamper")],
        )
        view = await store.create_run(spec)
        plan = view.pending_approval(ApprovalKind.PLAN)
        view = await coord.resolve(view.run.id, plan.id, approve=True)

        # a committed + succeeded; b hit the denylist -> failed (policy), not committed.
        assert _status(view, "a") == NodeStatus.SUCCEEDED
        assert _status(view, "b") == NodeStatus.FAILED
        b = next(n for n in view.nodes if n.id == "b")
        assert "policy violation" in (b.error or "")
        # cost/session captured on the succeeded node
        a = next(n for n in view.nodes if n.id == "a")
        assert a.session_id == "s-a" and a.cost_usd == 0.01

        # any succeeded -> final gate (fail-open partial delivery)
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL
        final = view.pending_approval(ApprovalKind.FINAL)
        view = await coord.resolve(view.run.id, final.id, approve=True)
        assert view.run.status == RunStatus.COMPLETED_PARTIAL

        # Integration branch has a's commit only; evil never landed. Worktree gone.
        branch = f"swarm/run-{view.run.id}"
        log = subprocess.run(
            ["git", "log", "--oneline", branch], cwd=repo, capture_output=True, text=True
        ).stdout
        assert "swarm node a" in log
        assert "swarm node b" not in log
        files = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", branch], cwd=repo, capture_output=True, text=True
        ).stdout
        assert "generated/a.txt" in files
        assert "zeus/orchestration/evil.py" not in files

    asyncio.run(scenario())
