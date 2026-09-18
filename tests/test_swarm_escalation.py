# tests/test_swarm_escalation.py — denial-streak escalation (Anthropic auto-mode pattern)
"""Anthropic report users approving 93% of permission prompts by default, so the
lesson copied here is NOT "gate more". The run stays silent while denials are
isolated and interrupts once a pattern emerges, so the interruption still carries
information. These tests pin the counting rules that make that true."""

import asyncio

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import ApprovalKind, RunStatus
from zeus.orchestration.swarm.notifier import NullNotifier
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.verifier import NoopVerifier
from zeus.orchestration.swarm.worker import StubWorker


def _coord(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))
    return store, Coordinator(store, StubWorker(), None, NoopVerifier(), NullNotifier())


def test_defaults_match_the_borrowed_thresholds(monkeypatch):
    monkeypatch.delenv("ZEUS_SWARM_ESCALATE_CONSECUTIVE_DENIALS", raising=False)
    monkeypatch.delenv("ZEUS_SWARM_ESCALATE_TOTAL_DENIALS", raising=False)
    assert config.escalate_consecutive_denials() == 3
    assert config.escalate_total_denials() == 20


def test_isolated_denials_do_not_escalate(tmp_path):
    """One denial is ordinary: the node fails open and the run carries on. If this
    escalated, every run would interrupt and the human would start rubber-stamping."""
    _, c = _coord(tmp_path)
    c._record_denial("r")
    c._clear_denial_streak("r")
    c._record_denial("r")
    assert c._should_escalate("r") is None


def test_consecutive_denials_escalate(tmp_path):
    _, c = _coord(tmp_path)
    for _ in range(3):
        c._record_denial("r")
    assert "3 safety denials in a row" in c._should_escalate("r")


def test_success_clears_the_streak_but_not_the_total(tmp_path):
    """The total is what catches the slow burn: denials scattered across many nodes,
    never three in a row, but a run plainly fighting the policy."""
    _, c = _coord(tmp_path)
    for _ in range(2):
        c._record_denial("r")
    c._clear_denial_streak("r")
    assert c._denials["r"] == [0, 2]


def test_total_denials_escalate_without_a_streak(tmp_path, monkeypatch):
    monkeypatch.setenv("ZEUS_SWARM_ESCALATE_TOTAL_DENIALS", "5")
    _, c = _coord(tmp_path)
    for _ in range(5):
        c._record_denial("r")
        c._clear_denial_streak("r")  # never two in a row
    assert "5 safety denials in this run" in c._should_escalate("r")


def test_approving_an_escalation_clears_both_counters(tmp_path):
    """Leaving the total in place would re-trip on the very next denial and turn the
    escalation back into the per-action prompt it exists to replace."""
    store, c = _coord(tmp_path)
    from zeus.orchestration.swarm.models import RunSpec, TaskNodeSpec

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo="/repo", nodes=[TaskNodeSpec(id="n1", title="t")]))
        rid = view.run.id
        c._denials[rid] = [3, 3]
        ap = await store.create_approval(rid, ApprovalKind.ESCALATION, detail="3 in a row")
        await c.resolve(rid, ap.id, True)
        assert c._denials[rid] == [0, 0]

    asyncio.run(scenario())


def test_rejecting_an_escalation_cancels_the_run(tmp_path):
    store, c = _coord(tmp_path)
    from zeus.orchestration.swarm.models import RunSpec, TaskNodeSpec

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo="/repo", nodes=[TaskNodeSpec(id="n1", title="t")]))
        rid = view.run.id
        ap = await store.create_approval(rid, ApprovalKind.ESCALATION, detail="3 in a row")
        out = await c.resolve(rid, ap.id, False)
        assert out.run.status == RunStatus.CANCELLED

    asyncio.run(scenario())
