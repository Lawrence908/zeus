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

    async def run(self, node, run, workspace) -> WorkerResult:
        rel, content = self.files[node.id]
        full = os.path.join(workspace, rel)
        os.makedirs(os.path.dirname(full) or workspace, exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        return WorkerResult(success=True, output=f"wrote {rel}", cost_usd=0.01, session_id=f"s-{node.id}")


def _status(view, nid):
    return next(n for n in view.nodes if n.id == nid).status


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
