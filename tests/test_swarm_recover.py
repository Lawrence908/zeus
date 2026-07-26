# tests/test_swarm_recover.py — P6 durable resume + reapers
import asyncio
import subprocess

from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import (
    NodeStatus,
    RunSpec,
    RunStatus,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.notifier import NullNotifier
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.verifier import NoopVerifier
from zeus.orchestration.swarm.worker import StubWorker
from zeus.orchestration.swarm.worktree import CodeWorkspace


def _git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(path):
    _git(["init", "-q", "-b", "main"], path)
    _git(["config", "user.email", "t@t"], path)
    _git(["config", "user.name", "t"], path)
    (path / "seed.txt").write_text("seed\n")
    _git(["add", "-A"], path)
    _git(["commit", "-q", "-m", "seed"], path)


def _branches(path):
    out = subprocess.run(["git", "branch", "--format=%(refname:short)"],
                         cwd=path, capture_output=True, text=True).stdout
    return {b.strip() for b in out.splitlines() if b.strip()}


# ---- branch parsing -------------------------------------------------------


def test_run_id_from_branch():
    f = CodeWorkspace.run_id_from_branch
    assert f("swarm/run-abc123def456") == "abc123def456"
    assert f("swarm/run-abc123def456-n-build") == "abc123def456"
    assert f("main") is None
    assert f(None) is None


# ---- reaper ---------------------------------------------------------------


def test_reap_orphans_removes_dead_runs(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    wt = tmp_path / "wt"

    async def scenario():
        a = CodeWorkspace(str(repo), "aaaaaaaaaaaa", base_dir=str(wt))
        b = CodeWorkspace(str(repo), "bbbbbbbbbbbb", base_dir=str(wt))
        await a.setup()
        await b.setup()
        assert {"swarm/run-aaaaaaaaaaaa", "swarm/run-bbbbbbbbbbbb"} <= _branches(repo)

        # only aaa is still live -> bbb is debris
        result = await CodeWorkspace.reap_orphans(str(repo), {"aaaaaaaaaaaa"}, base_dir=str(wt))

        branches = _branches(repo)
        assert "swarm/run-aaaaaaaaaaaa" in branches
        assert "swarm/run-bbbbbbbbbbbb" not in branches
        assert any("bbbbbbbbbbbb" in p for p in result["worktrees"])
        assert "swarm/run-bbbbbbbbbbbb" in result["branches"]

    asyncio.run(scenario())


# ---- re-attach ------------------------------------------------------------


def test_attach_reuses_existing_worktree(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    wt = tmp_path / "wt"

    async def scenario():
        ws = CodeWorkspace(str(repo), "cccccccccccc", base_dir=str(wt))
        path = await ws.setup()
        # land a commit on the integration branch (simulating merged work)
        (repo_path := __import__("pathlib").Path(path) / "work.txt").write_text("done\n")
        _git(["add", "-A"], path)
        _git(["-c", "user.email=s@s", "-c", "user.name=s", "commit", "-q", "-m", "work"], path)

        # "restart": a fresh object re-attaches without resetting the branch
        ws2 = await CodeWorkspace.attach(str(repo), "cccccccccccc", base_dir=str(wt))
        assert ws2.integration_path == path
        assert (__import__("pathlib").Path(ws2.integration_path) / "work.txt").exists()
        assert repo_path.exists()

    asyncio.run(scenario())


def test_attach_rechecks_out_branch_when_worktree_gone(tmp_path):
    from pathlib import Path

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    wt = tmp_path / "wt"

    async def scenario():
        ws = CodeWorkspace(str(repo), "dddddddddddd", base_dir=str(wt))
        path = await ws.setup()
        (Path(path) / "work.txt").write_text("done\n")
        _git(["add", "-A"], path)
        _git(["-c", "user.email=s@s", "-c", "user.name=s", "commit", "-q", "-m", "work"], path)
        # branch survives, worktree removed (e.g. cleaned tmp)
        _git(["worktree", "remove", "--force", path], repo)
        assert "swarm/run-dddddddddddd" in _branches(repo)

        ws2 = await CodeWorkspace.attach(str(repo), "dddddddddddd", base_dir=str(wt))
        assert ws2.integration_path is not None
        assert ws2.integration_path != path  # fresh worktree
        assert (Path(ws2.integration_path) / "work.txt").exists()  # branch tip preserved

    asyncio.run(scenario())


# ---- coordinator.recover --------------------------------------------------


def _coord(tmp_path):
    _init_repo(tmp_path)  # so the per-repo reaper has a real git repo to scan
    store = SwarmStore(str(tmp_path / "swarm.db"))
    return store, Coordinator(store, StubWorker(), None, NoopVerifier(), NullNotifier())


def test_recover_resets_interrupted_node_and_resumes(tmp_path):
    store, coord = _coord(tmp_path)

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo=str(tmp_path), nodes=[TaskNodeSpec(id="n1", title="t")],
        ))
        rid = view.run.id
        # simulate a crash mid-run: run RUNNING, node stuck RUNNING
        await store.set_run_status(rid, RunStatus.RUNNING)
        node = view.nodes[0]
        node.status = NodeStatus.RUNNING
        await store.update_node(node)

        res = await coord.recover(resume=True)
        assert res["reset_nodes"] == 1 and res["resumed"] == 1

        after = await store.get_view(rid)
        # stub node completed -> run reached the final gate
        assert after.run.status == RunStatus.PENDING_FINAL_APPROVAL
        assert after.nodes[0].status == NodeStatus.SUCCEEDED

    asyncio.run(scenario())


def test_recover_no_resume_only_resets(tmp_path):
    store, coord = _coord(tmp_path)

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo=str(tmp_path), nodes=[TaskNodeSpec(id="n1", title="t")],
        ))
        rid = view.run.id
        await store.set_run_status(rid, RunStatus.RUNNING)
        node = view.nodes[0]
        node.status = NodeStatus.RUNNING
        await store.update_node(node)

        res = await coord.recover(resume=False)
        assert res["reset_nodes"] == 1 and res["resumed"] == 0
        after = await store.get_view(rid)
        assert after.run.status == RunStatus.RUNNING  # untouched
        assert after.nodes[0].status == NodeStatus.READY

    asyncio.run(scenario())


def test_recover_ignores_terminal_runs(tmp_path):
    store, coord = _coord(tmp_path)

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo=str(tmp_path), nodes=[TaskNodeSpec(id="n1", title="t")],
        ))
        await store.set_run_status(view.run.id, RunStatus.COMPLETED)
        res = await coord.recover(resume=True)
        assert res == {"live": 0, "reattached": 0, "reset_nodes": 0, "resumed": 0}

    asyncio.run(scenario())
