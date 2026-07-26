# tests/test_swarm_finalize.py — P7 project check + auto-PR at the final gate
import asyncio

from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import (
    ApprovalKind,
    NodeStatus,
    Run,
    RunSpec,
    RunStatus,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.notifier import NullNotifier
from zeus.orchestration.swarm.planner import (
    parse_plan,
    parse_project_check,
)
from zeus.orchestration.swarm.pr import PrResult, PullRequestOpener, build_pr_body
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.verifier import NoopVerifier, VerifyResult
from zeus.orchestration.swarm.worker import StubWorker


# ---- planner: project_check ----------------------------------------------


def test_parse_project_check():
    raw = '{"nodes":[{"id":"a","title":"t"}],"project_check":"pytest -q"}'
    assert parse_project_check(raw) == "pytest -q"
    assert [s.id for s in parse_plan(raw)] == ["a"]


def test_parse_project_check_absent_or_bad():
    assert parse_project_check('{"nodes":[{"id":"a","title":"t"}]}') == ""
    assert parse_project_check("not json") == ""


# ---- PR body --------------------------------------------------------------


def test_build_pr_body_mentions_goal_and_check():
    run = Run(id="r1", goal="add health endpoint", repo="/repo",
              project_check="pytest -q", project_check_passed=True)
    body = build_pr_body(run, "- a: do a (succeeded)")
    assert "add health endpoint" in body
    assert "pytest -q" in body and "passed" in body
    assert "- a: do a (succeeded)" in body


# ---- finalize flow --------------------------------------------------------


class _StubVerifier:
    """Deterministic project-check result."""

    def __init__(self, passed: bool) -> None:
        self._passed = passed

    async def verify(self, node, workspace) -> VerifyResult:
        return VerifyResult(passed=self._passed, output=f"check {'ok' if self._passed else 'red'}")


class _FakeOpener:
    def __init__(self) -> None:
        self.calls = 0

    async def open(self, run, branch, nodes_summary="") -> PrResult:
        self.calls += 1
        return PrResult(url=f"https://github.com/x/y/pull/1?{branch}")


class _FakeWorkspace:
    """Enough surface for _finalize: a branch + an integration path."""

    def __init__(self) -> None:
        self.branch = "swarm/run-x"
        self.integration_path = "/tmp/int"

    async def teardown(self, *, keep_branch: bool = True) -> None:
        pass


async def _run_to_final(store, coord, *, project_check="") -> str:
    view = await store.create_run(RunSpec(
        goal="ship", repo="/repo", nodes=[TaskNodeSpec(id="n1", title="t")],
        project_check=project_check,
    ))
    rid = view.run.id
    # Drive plan -> node succeeds (no workspace: stub node runs with node_path=None)
    # -> final gate.
    plan = next(a for a in view.approvals if a.kind == ApprovalKind.PLAN)
    v = await coord.resolve(rid, plan.id, True)
    assert v.run.status == RunStatus.PENDING_FINAL_APPROVAL
    # Now pretend the run had a real integration workspace for the finalize step.
    coord._workspaces[rid] = _FakeWorkspace()
    return rid


def _final_approval_id(view):
    return next(a.id for a in view.approvals
               if a.kind == ApprovalKind.FINAL and a.state.value == "pending")


def test_finalize_check_pass_opens_pr(tmp_path, monkeypatch):
    monkeypatch.setenv("ZEUS_SWARM_AUTO_PR", "1")
    store = SwarmStore(str(tmp_path / "s.db"))
    opener = _FakeOpener()
    coord = Coordinator(store, StubWorker(), None, _StubVerifier(True), NullNotifier(), opener)

    async def scenario():
        rid = await _run_to_final(store, coord, project_check="pytest -q")
        view = await store.get_view(rid)
        out = await coord.resolve(rid, _final_approval_id(view), True)
        assert out.run.status == RunStatus.COMPLETED
        assert out.run.project_check_passed is True
        assert out.run.pr_url and "pull/1" in out.run.pr_url
        assert opener.calls == 1

    asyncio.run(scenario())


def test_finalize_check_fail_no_pr_partial(tmp_path, monkeypatch):
    monkeypatch.setenv("ZEUS_SWARM_AUTO_PR", "1")
    store = SwarmStore(str(tmp_path / "s.db"))
    opener = _FakeOpener()
    coord = Coordinator(store, StubWorker(), None, _StubVerifier(False), NullNotifier(), opener)

    async def scenario():
        rid = await _run_to_final(store, coord, project_check="pytest -q")
        view = await store.get_view(rid)
        out = await coord.resolve(rid, _final_approval_id(view), True)
        assert out.run.status == RunStatus.COMPLETED_PARTIAL  # merged but suite red
        assert out.run.project_check_passed is False
        assert out.run.pr_url is None
        assert opener.calls == 0  # no PR on a failing check

    asyncio.run(scenario())


def test_finalize_auto_pr_off_by_default(tmp_path):
    # No ZEUS_SWARM_AUTO_PR set -> no PR even when the check passes.
    store = SwarmStore(str(tmp_path / "s.db"))
    opener = _FakeOpener()
    coord = Coordinator(store, StubWorker(), None, _StubVerifier(True), NullNotifier(), opener)

    async def scenario():
        rid = await _run_to_final(store, coord, project_check="pytest -q")
        view = await store.get_view(rid)
        out = await coord.resolve(rid, _final_approval_id(view), True)
        assert out.run.status == RunStatus.COMPLETED
        assert out.run.project_check_passed is True
        assert out.run.pr_url is None and opener.calls == 0

    asyncio.run(scenario())


def test_finalize_no_check_completes(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))
    coord = Coordinator(store, StubWorker(), None, NoopVerifier(), NullNotifier(), _FakeOpener())

    async def scenario():
        rid = await _run_to_final(store, coord, project_check="")  # no run-level check
        view = await store.get_view(rid)
        out = await coord.resolve(rid, _final_approval_id(view), True)
        assert out.run.status == RunStatus.COMPLETED
        assert out.run.project_check_passed is None  # never ran

    asyncio.run(scenario())


def test_pr_opener_without_gh(monkeypatch):
    from zeus.orchestration.swarm import pr as prmod

    monkeypatch.setattr(prmod.shutil, "which", lambda name: None if name == "gh" else "/usr/bin/git")

    async def scenario():
        run = Run(id="r", goal="g", repo="/repo")
        res = await PullRequestOpener().open(run, "swarm/run-r")
        assert res.url is None and "gh" in res.error

    asyncio.run(scenario())
