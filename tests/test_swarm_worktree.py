# tests/test_swarm_worktree.py — CodeWorkspace git worktree + denylist commit
import asyncio
import os
import subprocess

from zeus.orchestration.swarm.models import NodeStatus, TaskNode
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


def _node(nid, title="t"):
    return TaskNode(run_id="r", id=nid, title=title, status=NodeStatus.RUNNING)


def test_worktree_setup_commit_teardown(tmp_path):
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    _init_repo(repo)
    wt_root = str(tmp_path / "wt")

    async def scenario():
        ws = CodeWorkspace(repo, "run1", base_dir=wt_root)
        path = await ws.setup()
        assert os.path.isdir(path)

        # Worker writes a legit source file.
        os.makedirs(os.path.join(path, "zeus", "core"), exist_ok=True)
        with open(os.path.join(path, "zeus", "core", "new.py"), "w") as f:
            f.write("x = 1\n")

        res = await ws.commit_node(_node("a"))
        assert res.committed and not res.denied and res.commit

        # The commit is on the integration branch.
        log = subprocess.run(
            ["git", "log", "--oneline", "swarm/run-run1"],
            cwd=repo, capture_output=True, text=True,
        ).stdout
        assert "swarm node a" in log

        await ws.teardown()
        assert not os.path.isdir(path)

    asyncio.run(scenario())


def test_denied_path_is_rejected_and_discarded(tmp_path):
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    _init_repo(repo)
    wt_root = str(tmp_path / "wt")

    async def scenario():
        ws = CodeWorkspace(repo, "run2", base_dir=wt_root)
        path = await ws.setup()

        # Worker tries to weaken its own supervision + drop a secret.
        os.makedirs(os.path.join(path, "zeus", "orchestration"), exist_ok=True)
        with open(os.path.join(path, "zeus", "orchestration", "bus.py"), "w") as f:
            f.write("# tampered\n")
        with open(os.path.join(path, ".env"), "w") as f:
            f.write("SECRET=1\n")

        res = await ws.commit_node(_node("evil"))
        assert not res.committed
        assert "zeus/orchestration/bus.py" in res.denied
        assert ".env" in res.denied

        # Changes were discarded, nothing committed on the branch.
        assert await ws.changed_paths() == []
        log = subprocess.run(
            ["git", "log", "--oneline", "swarm/run-run2"],
            cwd=repo, capture_output=True, text=True,
        ).stdout.strip()
        assert log.count("\n") == 0  # only the initial commit

        await ws.teardown()

    asyncio.run(scenario())


def test_noop_node_commits_nothing(tmp_path):
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    _init_repo(repo)

    async def scenario():
        ws = CodeWorkspace(repo, "run3", base_dir=str(tmp_path / "wt"))
        await ws.setup()
        res = await ws.commit_node(_node("noop"))
        assert not res.committed and not res.denied
        await ws.teardown()

    asyncio.run(scenario())
