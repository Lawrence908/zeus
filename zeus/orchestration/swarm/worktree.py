# zeus/orchestration/swarm/worktree.py
"""Per-run integration branch + per-node git worktrees for parallel argonauts.

Model (P3b):
  - A run owns branch `swarm/run-<id>` (the integration branch) and one
    integration worktree used only for merges.
  - Each node gets its own ephemeral worktree on `swarm/run-<id>/n-<node>`,
    branched from the *current* integration tip, so it sees prior merged work.
  - Independent nodes run concurrently in separate worktrees. When a node passes
    verification its work is committed on its node branch and then merged into
    the integration branch under a per-run lock (git can only merge one thing at
    a time). A merge conflict aborts and fails the node fail-open.

Before each commit the node's diff is checked against the self-edit denylist.
Worktrees check out tracked files only, so `zeus/data/` never enters a workspace.
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
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout


async def _git(args: list[str], cwd: str) -> str:
    return await asyncio.to_thread(_git_sync, args, cwd)


class CommitResult:
    def __init__(self, committed: bool, denied: list[str], commit: str | None = None) -> None:
        self.committed = committed
        self.denied = denied  # denylisted paths the node touched (non-empty -> rejected)
        self.commit = commit


class MergeResult:
    def __init__(self, merged: bool, conflicts: list[str] | None = None) -> None:
        self.merged = merged
        self.conflicts = conflicts or []


class CodeWorkspace:
    """Owns a run's integration branch and mints per-node worktrees off its tip."""

    def __init__(self, repo: str, run_id: str, *, base_dir: str | None = None) -> None:
        self.repo = os.path.realpath(os.path.expanduser(repo))
        self.run_id = run_id
        self.branch = f"swarm/run-{run_id}"
        self._base_dir = base_dir
        self.integration_path: str | None = None
        self._merge_lock = asyncio.Lock()
        self._node_branches: list[str] = []

    # ---- lifecycle -------------------------------------------------------

    def _root(self) -> str:
        root = self._base_dir or os.path.expanduser(
            os.getenv("ZEUS_SWARM_WORKTREE_DIR", "~/.zeus/swarm/worktrees")
        )
        os.makedirs(root, exist_ok=True)
        return root

    async def setup(self) -> str:
        base = (await _git(["rev-parse", "HEAD"], self.repo)).strip()
        self.integration_path = tempfile.mkdtemp(prefix=f"{self.run_id}-int-", dir=self._root())
        await _git(["worktree", "add", "-B", self.branch, self.integration_path, base], self.repo)
        logger.info("swarm %s: integration worktree %s on %s", self.run_id, self.integration_path, self.branch)
        return self.integration_path

    @classmethod
    async def attach(cls, repo: str, run_id: str, *, base_dir: str | None = None) -> "CodeWorkspace":
        """Re-bind to a run's existing integration branch/worktree after a restart.

        Never resets the branch (that would discard merged work): re-uses the
        on-disk integration worktree if present, else re-checks-out the surviving
        branch into a fresh worktree, else falls back to a clean setup(). Node
        branches are re-listed so teardown still cleans them.
        """
        ws = cls(repo, run_id, base_dir=base_dir)
        path = await ws._find_worktree(ws.branch)
        if path and os.path.isdir(path):
            ws.integration_path = path
            logger.info("swarm %s: re-attached integration worktree %s", run_id, path)
        elif await ws._branch_exists(ws.branch):
            ip = tempfile.mkdtemp(prefix=f"{run_id}-int-", dir=ws._root())
            try:
                await _git(["worktree", "add", ip, ws.branch], ws.repo)  # existing branch, no -B
                ws.integration_path = ip
                logger.info("swarm %s: re-checked-out branch %s into %s", run_id, ws.branch, ip)
            except GitError:
                shutil.rmtree(ip, ignore_errors=True)
                await ws.setup()
        else:
            await ws.setup()  # nothing survived; start the integration branch clean
        ws._node_branches = await ws._list_node_branches()
        return ws

    async def new_node_worktree(self, node_id: str) -> str:
        """A worktree on a node branch cut from the current integration tip.

        Serialized with merges: `git worktree add` takes a repo lock, and we want
        a consistent tip read even while another node is merging.
        """
        assert self.integration_path is not None
        node_branch = f"{self.branch}-n-{node_id}"
        path = tempfile.mkdtemp(prefix=f"{self.run_id}-{node_id}-", dir=self._root())
        async with self._merge_lock:
            tip = (await _git(["rev-parse", self.branch], self.repo)).strip()
            await _git(["worktree", "add", "-B", node_branch, path, tip], self.repo)
        self._node_branches.append(node_branch)
        return path

    # ---- per-node commit + merge ----------------------------------------

    async def changed_paths(self, node_path: str) -> list[str]:
        out = await _git(["status", "--porcelain=1", "-z", "-uall"], node_path)
        return [e[3:] if len(e) > 3 else e for e in out.split("\0") if e]

    async def commit_in(self, node: TaskNode, node_path: str) -> CommitResult:
        changed = await self.changed_paths(node_path)
        if not changed:
            return CommitResult(committed=False, denied=[])
        denied = config.denied_paths(changed)
        if denied:
            await self.discard_in(node_path)
            logger.warning("swarm %s node %s rejected: denied %s", self.run_id, node.id, denied)
            return CommitResult(committed=False, denied=denied)
        await _git(["add", "-A"], node_path)
        # --no-verify: swarm commits are mechanical; repo hooks run on the final PR.
        await _git(
            ["-c", "user.name=zeus-swarm", "-c", "user.email=swarm@zeus.local",
             "commit", "--no-verify", "-m", f"swarm node {node.id}: {node.title}"],
            node_path,
        )
        sha = (await _git(["rev-parse", "HEAD"], node_path)).strip()
        return CommitResult(committed=True, denied=[], commit=sha)

    async def merge_node(self, node_id: str) -> MergeResult:
        """Merge the node branch into the integration branch (serialized)."""
        assert self.integration_path is not None
        node_branch = f"{self.branch}-n-{node_id}"
        async with self._merge_lock:
            try:
                await _git(
                    ["-c", "user.name=zeus-swarm", "-c", "user.email=swarm@zeus.local",
                     "merge", "--no-ff", "-m", f"merge node {node_id}", node_branch],
                    self.integration_path,
                )
                return MergeResult(merged=True)
            except GitError:
                conflicts: list[str] = []
                try:
                    out = await _git(["diff", "--name-only", "--diff-filter=U"], self.integration_path)
                    conflicts = [p for p in out.splitlines() if p]
                    await _git(["merge", "--abort"], self.integration_path)
                except GitError:
                    pass
                logger.warning("swarm %s node %s merge conflict: %s", self.run_id, node_id, conflicts)
                return MergeResult(merged=False, conflicts=conflicts)

    async def discard_in(self, node_path: str) -> None:
        await _git(["reset", "--hard", "HEAD"], node_path)
        await _git(["clean", "-fd"], node_path)

    async def teardown_node(self, node_path: str) -> None:
        try:
            await _git(["worktree", "remove", "--force", node_path], self.repo)
        except GitError:
            shutil.rmtree(node_path, ignore_errors=True)
            await _git(["worktree", "prune"], self.repo)

    async def teardown(self, *, keep_branch: bool = True) -> None:
        """Remove all worktrees. The integration branch is kept for the PR."""
        if self.integration_path is None:
            return
        try:
            await _git(["worktree", "remove", "--force", self.integration_path], self.repo)
        except GitError:
            shutil.rmtree(self.integration_path, ignore_errors=True)
        await _git(["worktree", "prune"], self.repo)
        # Node branches are throwaway; the integration branch carries the merges.
        for nb in self._node_branches:
            try:
                await _git(["branch", "-D", nb], self.repo)
            except GitError:
                pass
        if not keep_branch:
            try:
                await _git(["branch", "-D", self.branch], self.repo)
            except GitError:
                pass
        self.integration_path = None

    # ---- introspection + reaping (P6) -----------------------------------

    async def _worktree_list(self) -> list[tuple[str, str | None]]:
        """(path, branch-name-or-None) for every worktree registered in the repo."""
        out = await _git(["worktree", "list", "--porcelain"], self.repo)
        entries: list[tuple[str, str | None]] = []
        path: str | None = None
        branch: str | None = None
        for line in out.splitlines() + [""]:
            if line.startswith("worktree "):
                if path is not None:
                    entries.append((path, branch))
                path, branch = line[len("worktree "):], None
            elif line.startswith("branch "):
                ref = line[len("branch "):]
                branch = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
            elif line == "" and path is not None:
                entries.append((path, branch))
                path, branch = None, None
        return entries

    async def _find_worktree(self, branch: str) -> str | None:
        for path, br in await self._worktree_list():
            if br == branch:
                return path
        return None

    async def _branch_exists(self, branch: str) -> bool:
        try:
            await _git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], self.repo)
            return True
        except GitError:
            return False

    async def _list_node_branches(self) -> list[str]:
        out = await _git(
            ["for-each-ref", "--format=%(refname:short)", f"refs/heads/{self.branch}-n-*"],
            self.repo,
        )
        return [b for b in out.splitlines() if b]

    @staticmethod
    def run_id_from_branch(branch: str | None) -> str | None:
        """`swarm/run-<id>` and `swarm/run-<id>-n-<node>` -> `<id>` (12 hex, no '-')."""
        if not branch or not branch.startswith("swarm/run-"):
            return None
        return branch[len("swarm/run-"):].split("-n-", 1)[0] or None

    @classmethod
    async def reap_orphans(
        cls, repo: str, live_run_ids: set[str], *, base_dir: str | None = None
    ) -> dict[str, list[str]]:
        """Remove swarm worktrees/branches whose run is no longer live.

        A run is live iff it is still non-terminal in the store. Everything else
        under `swarm/run-*` is debris from a completed/failed/dead run and is
        pruned so the repo doesn't accumulate stale worktrees and branches.
        """
        ws = cls(repo, "reaper", base_dir=base_dir)
        repo = ws.repo  # resolved
        removed_worktrees: list[str] = []
        deleted_branches: list[str] = []
        for path, branch in await ws._worktree_list():
            rid = cls.run_id_from_branch(branch)
            if rid is not None and rid not in live_run_ids:
                try:
                    await _git(["worktree", "remove", "--force", path], repo)
                except GitError:
                    shutil.rmtree(path, ignore_errors=True)
                removed_worktrees.append(path)
        await _git(["worktree", "prune"], repo)
        out = await _git(
            ["for-each-ref", "--format=%(refname:short)", "refs/heads/swarm/run-*"], repo
        )
        for branch in (b for b in out.splitlines() if b):
            rid = cls.run_id_from_branch(branch)
            if rid is not None and rid not in live_run_ids:
                try:
                    await _git(["branch", "-D", branch], repo)
                    deleted_branches.append(branch)
                except GitError:
                    pass
        if removed_worktrees or deleted_branches:
            logger.info(
                "swarm reaper (%s): removed %d worktrees, %d branches",
                repo, len(removed_worktrees), len(deleted_branches),
            )
        return {"worktrees": removed_worktrees, "branches": deleted_branches}
