# zeus/orchestration/swarm/worktree.py
"""Per-run git worktree + integration branch for code argonauts.

Each run gets a worktree of the target repo on branch `swarm/run-<id>`, cut
from the repo's current HEAD. A single sequential worker accumulates one commit
per node on that branch (dependent nodes see prior nodes' changes for free,
since it is the same working tree). Before each commit the coordinator checks
the diff against the self-edit denylist; a node that touched a denied path is
rejected and its changes discarded, never committed.

Worktrees check out tracked files only, so `zeus/data/` (gitignored) never
enters a worker's workspace - a privacy boundary for free.

Git runs as a subprocess in asyncio.to_thread (no libgit2 dependency).
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import tempfile

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.models import TaskNode

logger = logging.getLogger("zeus.swarm.worktree")


class GitError(RuntimeError):
    pass


def _git_sync(args: list[str], cwd: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout


async def _git(args: list[str], cwd: str) -> str:
    return await asyncio.to_thread(_git_sync, args, cwd)


class CommitResult:
    """Outcome of committing a node's work onto the integration branch."""

    def __init__(self, committed: bool, denied: list[str], commit: str | None = None) -> None:
        self.committed = committed
        self.denied = denied  # denylisted paths the node touched (non-empty -> rejected)
        self.commit = commit


class CodeWorkspace:
    """A git worktree of `repo` on `swarm/run-<run_id>`, one commit per node."""

    def __init__(self, repo: str, run_id: str, *, base_dir: str | None = None) -> None:
        self.repo = os.path.realpath(os.path.expanduser(repo))
        self.run_id = run_id
        self.branch = f"swarm/run-{run_id}"
        self._base_dir = base_dir
        self.path: str | None = None  # worktree checkout path, set by setup()

    async def setup(self) -> str:
        """Create the integration branch + worktree; return the worktree path."""
        base = (await _git(["rev-parse", "HEAD"], self.repo)).strip()
        root = self._base_dir or os.path.join(
            os.path.expanduser(os.getenv("ZEUS_SWARM_WORKTREE_DIR", "~/.zeus/swarm/worktrees"))
        )
        os.makedirs(root, exist_ok=True)
        self.path = tempfile.mkdtemp(prefix=f"{self.run_id}-", dir=root)
        # Fresh branch from base; -B so a re-run reuses the path cleanly.
        await _git(["worktree", "add", "-B", self.branch, self.path, base], self.repo)
        logger.info("swarm workspace %s: worktree %s on %s", self.run_id, self.path, self.branch)
        return self.path

    async def changed_paths(self) -> list[str]:
        assert self.path is not None
        # -uall expands untracked directories to individual files, so the denylist
        # sees `zeus/orchestration/bus.py`, not a collapsed `zeus/`.
        out = await _git(["status", "--porcelain=1", "-z", "-uall"], self.path)
        paths: list[str] = []
        for entry in out.split("\0"):
            if not entry:
                continue
            # porcelain: "XY <path>" (renames use "XY <old>\0<new>" but -z splits those;
            # good enough for the denylist check, which only needs the touched paths).
            paths.append(entry[3:] if len(entry) > 3 else entry)
        return paths

    async def commit_node(self, node: TaskNode) -> CommitResult:
        """Denylist-check the node's diff, then commit it (or reject + discard)."""
        assert self.path is not None
        changed = await self.changed_paths()
        if not changed:
            return CommitResult(committed=False, denied=[])  # no-op node

        denied = config.denied_paths(changed)
        if denied:
            # An argonaut touched supervisory / secret paths: discard, do not commit.
            await self._discard()
            logger.warning("swarm %s node %s rejected: denied paths %s", self.run_id, node.id, denied)
            return CommitResult(committed=False, denied=denied)

        await _git(["add", "-A"], self.path)
        # --no-verify: swarm integration commits are mechanical; the repo's own
        # pre-commit hooks (e.g. docs-index checks) run on the final PR / CI, not
        # on every per-node commit, so a hook must not stall or crash a run.
        await _git(
            ["-c", "user.name=zeus-swarm", "-c", "user.email=swarm@zeus.local",
             "commit", "--no-verify", "-m", f"swarm node {node.id}: {node.title}"],
            self.path,
        )
        sha = (await _git(["rev-parse", "HEAD"], self.path)).strip()
        return CommitResult(committed=True, denied=[], commit=sha)

    async def discard(self) -> None:
        """Throw away uncommitted changes in the worktree (e.g. a failed attempt)."""
        await self._discard()

    async def _discard(self) -> None:
        assert self.path is not None
        await _git(["reset", "--hard", "HEAD"], self.path)
        await _git(["clean", "-fd"], self.path)

    async def teardown(self, *, keep_branch: bool = True) -> None:
        """Remove the worktree. The integration branch is kept for the PR."""
        if self.path is None:
            return
        try:
            await _git(["worktree", "remove", "--force", self.path], self.repo)
        except GitError:
            shutil.rmtree(self.path, ignore_errors=True)
            await _git(["worktree", "prune"], self.repo)
        if not keep_branch:
            try:
                await _git(["branch", "-D", self.branch], self.repo)
            except GitError:
                pass
        self.path = None
