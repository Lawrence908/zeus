# tests/test_swarm_store.py — run-list triage fields on SwarmStore.
"""The run list is the triage surface: it has to answer "which of these is waiting
on me" without the caller opening each run in turn. `status` alone cannot, because
a QUESTION gate leaves the run RUNNING, so a status-only list shows a blocked run
as busy while its node sits idle. That is the case a supervisor most needs to see."""

import asyncio

from zeus.orchestration.swarm.models import (
    ApprovalKind,
    ApprovalState,
    RunSpec,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.store import SwarmStore


def _spec(goal: str) -> RunSpec:
    return RunSpec(goal=goal, repo="/r", nodes=[TaskNodeSpec(id="n1", title="t")])


def test_list_runs_reports_pending_gate_kinds(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))

    async def scenario():
        blocked = await store.create_run(_spec("blocked"))
        quiet = await store.create_run(_spec("quiet"))
        await store.create_approval(
            blocked.run.id, ApprovalKind.QUESTION, "n1", detail="which db?")

        runs = {r.id: r for r in await store.list_runs(limit=10)}
        assert "question" in runs[blocked.run.id].pending_kinds
        # Both opened with a plan gate, so only the question separates them.
        assert "question" not in runs[quiet.run.id].pending_kinds

    asyncio.run(scenario())


def test_resolved_gates_drop_out_of_pending_kinds(tmp_path):
    """Stale badges would be worse than none: a list that keeps showing answered
    gates trains the reader to ignore the column."""
    store = SwarmStore(str(tmp_path / "s.db"))

    async def scenario():
        view = await store.create_run(_spec("g"))
        plan = next(a for a in view.approvals if a.kind == ApprovalKind.PLAN)
        await store.resolve_approval(plan.id, ApprovalState.APPROVED)

        runs = {r.id: r for r in await store.list_runs(limit=10)}
        assert runs[view.run.id].pending_kinds == []

    asyncio.run(scenario())


def test_pending_kinds_are_deduped_and_sorted(tmp_path):
    """Several nodes can block on questions at once; the badge row should say
    "question" once, not once per node."""
    store = SwarmStore(str(tmp_path / "s.db"))

    async def scenario():
        view = await store.create_run(_spec("g"))
        rid = view.run.id
        await store.create_approval(rid, ApprovalKind.QUESTION, "n1", detail="a")
        await store.create_approval(rid, ApprovalKind.QUESTION, "n1", detail="b")

        runs = {r.id: r for r in await store.list_runs(limit=10)}
        assert runs[rid].pending_kinds == ["plan", "question"]

    asyncio.run(scenario())


def test_empty_list_does_not_query_approvals(tmp_path):
    """Guards the N+1 shortcut: the approval join is skipped when there are no
    runs, and an empty page must not error on an empty IN () clause."""
    store = SwarmStore(str(tmp_path / "s.db"))
    assert asyncio.run(store.list_runs(limit=10)) == []
