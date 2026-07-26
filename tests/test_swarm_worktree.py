# tests/test_swarm_worktree.py — per-node worktrees + integration merge
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
        f.write("base\n")
    _run(["git", "add", "-A"], path)
    _run(["git", "commit", "-qm", "init"], path)


def _node(nid, title="t"):
    return TaskNode(run_id="r", id=nid, title=title, status=NodeStatus.RUNNING)


def _write(path, rel, content):
    full = os.path.join(path, rel)
    os.makedirs(os.path.dirname(full) or path, exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


def _mkrepo(tmp_path):
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    _init_repo(repo)
    return repo


def _ls(repo, branch):
    return subprocess.run(["git", "ls-tree", "-r", "--name-only", branch],
                          cwd=repo, capture_output=True, text=True).stdout


def test_node_commit_and_merge(tmp_path):
    repo = _mkrepo(tmp_path)

    async def scenario():
        ws = CodeWorkspace(repo, "run1", base_dir=str(tmp_path / "wt"))
        await ws.setup()
        p = await ws.new_node_worktree("a")
        _write(p, "zeus/core/new.py", "x = 1\n")
        c = await ws.commit_in(_node("a"), p)
        assert c.committed and not c.denied
        m = await ws.merge_node("a")
        assert m.merged
        assert "zeus/core/new.py" in _ls(repo, "swarm/run-run1")
        await ws.teardown()

    asyncio.run(scenario())


def test_denied_path_rejected(tmp_path):
    repo = _mkrepo(tmp_path)

    async def scenario():
        ws = CodeWorkspace(repo, "run2", base_dir=str(tmp_path / "wt"))
        await ws.setup()
        p = await ws.new_node_worktree("evil")
        _write(p, "zeus/orchestration/bus.py", "# tamper\n")
        _write(p, ".env", "SECRET=1\n")
        c = await ws.commit_in(_node("evil"), p)
        assert not c.committed
        assert "zeus/orchestration/bus.py" in c.denied and ".env" in c.denied
        assert await ws.changed_paths(p) == []  # discarded
        await ws.teardown()

    asyncio.run(scenario())


def test_commit_bypasses_precommit_hook(tmp_path):
    repo = _mkrepo(tmp_path)
    hook = os.path.join(repo, ".git", "hooks", "pre-commit")
    with open(hook, "w") as f:
        f.write("#!/bin/sh\nexit 1\n")
    os.chmod(hook, 0o755)

    async def scenario():
        ws = CodeWorkspace(repo, "run3", base_dir=str(tmp_path / "wt"))
        await ws.setup()
        p = await ws.new_node_worktree("a")
        _write(p, "note.txt", "hi\n")
        assert (await ws.commit_in(_node("a"), p)).committed
        await ws.teardown()

    asyncio.run(scenario())


def test_merge_conflict_fails_open(tmp_path):
    repo = _mkrepo(tmp_path)

    async def scenario():
        ws = CodeWorkspace(repo, "run4", base_dir=str(tmp_path / "wt"))
        await ws.setup()
        # Two nodes edit the same line of README.md from the same base tip.
        pa = await ws.new_node_worktree("a")
        _write(pa, "README.md", "from a\n")
        await ws.commit_in(_node("a"), pa)
        pb = await ws.new_node_worktree("b")
        _write(pb, "README.md", "from b\n")
        await ws.commit_in(_node("b"), pb)

        assert (await ws.merge_node("a")).merged  # first lands
        mb = await ws.merge_node("b")             # second conflicts
        assert not mb.merged and "README.md" in mb.conflicts

        # Integration branch is intact with a's change (merge aborted cleanly).
        head = subprocess.run(["git", "show", "swarm/run-run4:README.md"],
                              cwd=repo, capture_output=True, text=True).stdout
        assert head == "from a\n"
        await ws.teardown()

    asyncio.run(scenario())


def test_noop_node_commits_nothing(tmp_path):
    repo = _mkrepo(tmp_path)

    async def scenario():
        ws = CodeWorkspace(repo, "run5", base_dir=str(tmp_path / "wt"))
        await ws.setup()
        p = await ws.new_node_worktree("noop")
        assert not (await ws.commit_in(_node("noop"), p)).committed
        await ws.teardown()

    asyncio.run(scenario())
