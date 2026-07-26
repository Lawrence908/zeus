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

import asyncio
import logging
import os
from typing import Callable

from zeus.orchestration.swarm import config, dag
from zeus.orchestration.swarm.models import (
    Approval,
    ApprovalKind,
    ApprovalState,
    NodeStatus,
    Run,
    RunStatus,
    RunView,
    TaskNode,
)
from zeus.orchestration.swarm.notifier import ApprovalNotifier, NullNotifier
from zeus.orchestration.swarm.pr import PrResult, PullRequestOpener
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.verifier import NoopVerifier, Verifier
from zeus.orchestration.swarm.worker import Worker
from zeus.orchestration.swarm.worktree import CodeWorkspace

logger = logging.getLogger("zeus.swarm.coordinator")

_MAX_ITERS = 10_000  # safety bound on the drive loop

# Builds a per-run git workspace; None for the stub path (no worktree).
WorkspaceFactory = Callable[[str, str], CodeWorkspace]


class Coordinator:
    def __init__(
        self,
        store: SwarmStore,
        worker: Worker,
        workspace_factory: WorkspaceFactory | None = None,
        verifier: Verifier | None = None,
        notifier: ApprovalNotifier | None = None,
        pr_opener: PullRequestOpener | None = None,
    ) -> None:
        self._store = store
        self._worker = worker
        self._workspace_factory = workspace_factory
        self._verifier = verifier or NoopVerifier()
        self._notifier = notifier or NullNotifier()
        self._pr_opener = pr_opener or PullRequestOpener()
        self._workspaces: dict[str, CodeWorkspace] = {}

    async def _notify(self, run: Run, approval: Approval) -> None:
        try:
            await self._notifier.approval_opened(run, approval)
        except Exception:  # noqa: BLE001 - notification is best-effort
            logger.exception("swarm approval notify failed (run %s)", run.id)

    _TERMINAL_RUN_STATUSES = (
        RunStatus.COMPLETED,
        RunStatus.COMPLETED_PARTIAL,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
    )

    # ---- durable resume (P6) --------------------------------------------

    async def recover(self, *, resume: bool = True) -> dict[str, int]:
        """Reconcile persisted runs with on-disk git state after a restart.

        The coordinator's workspaces and in-flight asyncio tasks are in-memory, so
        a zeus-core restart mid-run orphans worktrees and strands non-terminal
        runs. On startup: reset interrupted RUNNING nodes to READY, re-attach the
        integration workspace for runs that had one, reap worktrees/branches whose
        run is no longer live, then (resume=True) re-drive RUNNING runs.
        """
        runs = await self._store.list_runs(limit=100_000)
        live = [r for r in runs if r.status not in self._TERMINAL_RUN_STATUSES]
        reattached = reset_nodes = resumed = 0

        for r in live:
            if r.status == RunStatus.RUNNING:
                view = await self._store.get_view(r.id)
                for n in (view.nodes if view else []):
                    if n.status == NodeStatus.RUNNING:  # interrupted mid-execution
                        n.status = NodeStatus.READY
                        n.error = None
                        await self._store.update_node(n)
                        reset_nodes += 1
            had_workspace = r.status in (
                RunStatus.RUNNING, RunStatus.PENDING_FINAL_APPROVAL, RunStatus.PAUSED_BUDGET
            )
            if (self._workspace_factory is not None and not r.dry_run
                    and had_workspace and r.id not in self._workspaces):
                try:
                    self._workspaces[r.id] = await CodeWorkspace.attach(r.repo, r.id)
                    reattached += 1
                except Exception:  # noqa: BLE001 - a run we can't re-attach still resolves
                    logger.exception("swarm recover: attach failed for run %s", r.id)

        # Reap debris per repo: worktrees/branches whose run is not live.
        live_by_repo: dict[str, set[str]] = {}
        for r in live:
            live_by_repo.setdefault(os.path.realpath(os.path.expanduser(r.repo)), set()).add(r.id)
        for repo in {os.path.realpath(os.path.expanduser(r.repo)) for r in runs}:
            try:
                await CodeWorkspace.reap_orphans(repo, live_by_repo.get(repo, set()))
            except Exception:  # noqa: BLE001 - reaping is best-effort
                logger.exception("swarm reaper failed for repo %s", repo)

        if resume:
            for r in live:
                if r.status == RunStatus.RUNNING:
                    try:
                        await self.advance(r.id)
                        resumed += 1
                    except Exception:  # noqa: BLE001
                        logger.exception("swarm resume failed for run %s", r.id)

        if live:
            logger.info(
                "swarm recover: %d live runs, re-attached %d, reset %d nodes, resumed %d",
                len(live), reattached, reset_nodes, resumed,
            )
        return {"live": len(live), "reattached": reattached,
                "reset_nodes": reset_nodes, "resumed": resumed}

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
                    # Keep the workspace (integration branch) until the final gate.
                    ap = await self._store.create_approval(run_id, ApprovalKind.FINAL)
                    await self._store.set_run_status(run_id, RunStatus.PENDING_FINAL_APPROVAL)
                    await self._notify(view.run, ap)
                elif dag.has_failure(view.nodes):
                    await self._store.set_run_status(run_id, RunStatus.FAILED)
                    logger.warning("swarm run %s failed (no node succeeded)", run_id)
                    await self._teardown_workspace(run_id)
                else:
                    await self._store.set_run_status(run_id, RunStatus.CANCELLED)
                    await self._teardown_workspace(run_id)
                break
            if self._over_budget(view.run, view.nodes):
                # Kill-switch: hold the run until the budget overrun is approved.
                if view.pending_approval(ApprovalKind.BUDGET) is None:
                    ap = await self._store.create_approval(run_id, ApprovalKind.BUDGET)
                    await self._notify(view.run, ap)
                await self._store.set_run_status(run_id, RunStatus.PAUSED_BUDGET)
                logger.warning("swarm run %s paused: over budget ($%.2f)", run_id, view.run.budget_usd)
                break
            if not progressed:
                break  # waiting on an approval gate (nothing else dispatchable)

        return await self._store.get_view(run_id)

    async def _step(self, run: Run, nodes: list[TaskNode]) -> bool:
        """One scheduling pass: unblock, gate, and dispatch a ready batch in parallel."""
        progressed = False

        # 1. Unblock nodes whose deps have all succeeded.
        for n in dag.newly_ready(nodes):
            n.status = NodeStatus.READY
            await self._store.update_node(n)
            progressed = True

        # 2. Select a batch of READY nodes up to max_parallel; gate the rest.
        batch: list[TaskNode] = []
        for n in dag.dispatchable(nodes):
            if len(batch) >= run.max_parallel:
                break
            if n.requires_approval:
                ap = await self._store.create_approval(run.id, ApprovalKind.NODE_WRITE, n.id)
                n.status = NodeStatus.PENDING_APPROVAL
                await self._store.update_node(n)
                await self._notify(run, ap)
                progressed = True
                continue
            n.status = NodeStatus.RUNNING
            await self._store.update_node(n)
            batch.append(n)

        # 3. Run the batch concurrently. Each node works in its own worktree; the
        #    denylist commit + merge into the integration branch are serialized by
        #    the workspace lock.
        if batch:
            progressed = True
            await asyncio.gather(*(self._execute_node(n, run, self._workspaces.get(run.id), nodes)
                                   for n in batch))

        return progressed

    @staticmethod
    def _over_budget(run: Run, nodes: list[TaskNode]) -> bool:
        return run.budget_usd > 0 and sum(n.cost_usd for n in nodes) > run.budget_usd

    async def _execute_node(
        self, n: TaskNode, run: Run, ws: CodeWorkspace | None, nodes: list[TaskNode]
    ) -> None:
        """Run the worker in a per-node worktree, verify, commit, and merge.

        Verification happens in the node worktree *before* the commit, and the
        commit is merged into the integration branch only if it applies cleanly,
        so only passing, conflict-free work lands. Failures (worker, verify,
        denylist, or merge conflict) fail the node fail-open. Retries up to
        n.max_attempts, feeding the failure back to the worker.
        """
        if run.dry_run:
            # C2: validate DAG shape + gates without spending; no worker, no worktree.
            n.status = NodeStatus.SUCCEEDED
            n.output = "[dry-run] would execute"
            n.attempts = 1
            await self._store.update_node(n)
            return
        node_path = await ws.new_node_worktree(n.id) if ws else None
        try:
            feedback: str | None = None
            for attempt in range(1, n.max_attempts + 1):
                n.attempts = attempt
                result = await self._worker.run(n, run, node_path, feedback=feedback)
                n.cost_usd += result.cost_usd  # accumulate across retries
                n.session_id = result.session_id or n.session_id

                if not result.success:
                    feedback = f"Worker error: {result.error}"
                    if attempt < n.max_attempts:
                        await self._store.update_node(n)
                        continue
                    await self._fail(n, nodes, result.error or "worker reported failure")
                    return

                vres = await self._verifier.verify(n, node_path) if node_path else None
                if vres is not None and not vres.passed:
                    feedback = f"Verification (`{n.check}`) failed:\n{vres.output}"
                    if node_path is not None:
                        await ws.discard_in(node_path)  # drop the failed attempt
                    if attempt < n.max_attempts:
                        await self._store.update_node(n)
                        continue
                    await self._fail(n, nodes, f"verification failed after {attempt} attempt(s)")
                    return

                # Passed (or no check): commit in the node worktree, then merge.
                if ws is not None and node_path is not None:
                    try:
                        commit = await ws.commit_in(n, node_path)
                    except Exception as exc:  # noqa: BLE001
                        await self._fail(n, nodes, f"commit failed: {exc}")
                        return
                    if commit.denied:
                        await self._fail(n, nodes, f"policy violation: denied paths {commit.denied}")
                        return
                    if commit.committed:
                        merge = await ws.merge_node(n.id)
                        if not merge.merged:
                            await self._fail(n, nodes, f"merge conflict: {merge.conflicts}")
                            return
                n.status = NodeStatus.SUCCEEDED
                n.output = result.output
                await self._store.update_node(n)
                return
        finally:
            if ws is not None and node_path is not None:
                await ws.teardown_node(node_path)

    async def _fail(self, node: TaskNode, nodes: list[TaskNode], error: str) -> None:
        node.status = NodeStatus.FAILED
        node.error = error
        await self._store.update_node(node)
        # Fail-open: strand everything downstream, keep the rest running.
        await self._mark_unreachable(node, nodes)

    # ---- gates -----------------------------------------------------------

    async def resolve(self, run_id: str, approval_id: str, approve: bool) -> RunView | None:
        state = ApprovalState.APPROVED if approve else ApprovalState.REJECTED
        ap = await self._store.resolve_approval(approval_id, state)
        if ap is None or ap.run_id != run_id:
            return await self._store.get_view(run_id)

        if ap.kind == ApprovalKind.PLAN:
            if approve:
                await self._store.set_run_status(run_id, RunStatus.RUNNING)
                view = await self._store.get_view(run_id)
                if view is not None:
                    await self._setup_workspace(view.run)
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

        elif ap.kind == ApprovalKind.BUDGET:
            if approve:
                # Grant another budget's worth of headroom above current spend so
                # the run makes real progress instead of re-pausing immediately.
                view = await self._store.get_view(run_id)
                if view is not None:
                    spent = sum(n.cost_usd for n in view.nodes)
                    await self._store.set_run_budget(run_id, spent + view.run.budget_usd)
                await self._store.set_run_status(run_id, RunStatus.RUNNING)
                return await self.advance(run_id)
            await self._store.set_run_status(run_id, RunStatus.CANCELLED)
            await self._teardown_workspace(run_id)

        elif ap.kind == ApprovalKind.FINAL:
            if approve:
                await self._finalize(run_id)
            else:
                await self._store.set_run_status(run_id, RunStatus.CANCELLED)
            # Integration branch stays for review; only the worktree is removed.
            await self._teardown_workspace(run_id)

        return await self._store.get_view(run_id)

    async def _finalize(self, run_id: str) -> None:
        """Final gate approved (P7): run a run-level project check on the integration
        branch, then (opt-in) open a PR. Must run before the workspace is torn down.

        A failing project check does not discard the merged work - the run settles
        COMPLETED_PARTIAL with the check output and no PR, so the branch is there to
        fix. A passing check (or none) with all nodes green settles COMPLETED.
        """
        view = await self._store.get_view(run_id)
        if view is None:
            return
        all_ok = all(n.status == NodeStatus.SUCCEEDED for n in view.nodes)
        ws = self._workspaces.get(run_id)

        # Run-level check on the assembled branch, reusing the (sandboxed) verifier.
        check_cmd = (view.run.project_check or config.project_check_default()).strip()
        passed: bool | None = None
        output: str | None = None
        if check_cmd and ws is not None and ws.integration_path is not None:
            synthetic = TaskNode(run_id=run_id, id="__project__",
                                 title="project check", check=check_cmd)
            vres = await self._verifier.verify(synthetic, ws.integration_path)
            passed, output = vres.passed, vres.output

        status = RunStatus.COMPLETED if (all_ok and passed is not False) else RunStatus.COMPLETED_PARTIAL

        pr_url: str | None = None
        if passed is not False and config.auto_pr() and ws is not None:
            nodes_summary = "\n".join(
                f"- {n.id}: {n.title} ({n.status.value})" for n in view.nodes
            )
            # Reflect the check result on the run so the PR body can read it.
            run_for_pr = view.run.model_copy(update={"project_check_passed": passed})
            pr: PrResult = await self._pr_opener.open(run_for_pr, ws.branch, nodes_summary)
            pr_url = pr.url
            if pr.error:
                logger.warning("swarm %s: PR not opened: %s", run_id, pr.error)

        await self._store.finalize_run(
            run_id, status, pr_url=pr_url,
            project_check_passed=passed, project_check_output=output,
        )

    async def kill(self, run_id: str) -> RunView | None:
        view = await self._store.get_view(run_id)
        if view is None:
            return None
        for n in view.nodes:
            if n.status not in self._TERMINAL:
                n.status = NodeStatus.SKIPPED
                await self._store.update_node(n)
        await self._store.set_run_status(run_id, RunStatus.CANCELLED)
        await self._teardown_workspace(run_id)
        return await self._store.get_view(run_id)

    _TERMINAL = (
        NodeStatus.SUCCEEDED,
        NodeStatus.FAILED,
        NodeStatus.SKIPPED,
        NodeStatus.UNREACHABLE,
    )

    # ---- workspace lifecycle --------------------------------------------

    async def _setup_workspace(self, run: Run) -> None:
        if self._workspace_factory is None or run.dry_run:
            return  # dry runs never touch git
        ws = self._workspace_factory(run.repo, run.id)
        await ws.setup()
        self._workspaces[run.id] = ws

    async def _teardown_workspace(self, run_id: str, *, keep_branch: bool = True) -> None:
        ws = self._workspaces.pop(run_id, None)
        if ws is not None:
            try:
                await ws.teardown(keep_branch=keep_branch)
            except Exception:  # best-effort; a dangling worktree is prunable
                logger.exception("workspace teardown failed for run %s", run_id)

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
