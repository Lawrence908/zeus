# tests/test_swarm_questions.py — P10 question gates + Telegram /answer
import asyncio

from zeus.orchestration.swarm.claude_worker import build_prompt
from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import (
    ApprovalKind,
    ApprovalState,
    NodeStatus,
    Run,
    RunSpec,
    RunStatus,
    TaskNode,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.notifier import build_message
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.worker import StubWorker


def _mk(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))
    return store, Coordinator(store, StubWorker())


async def _to_running(store, coord, question=""):
    view = await store.create_run(RunSpec(
        goal="g", repo="/repo",
        nodes=[TaskNodeSpec(id="n1", title="do it", question=question)]))
    plan = next(a for a in view.approvals if a.kind == ApprovalKind.PLAN)
    return view.run.id, await coord.resolve(view.run.id, plan.id, True)


def test_question_opens_gate_and_blocks(tmp_path):
    store, coord = _mk(tmp_path)

    async def scenario():
        rid, view = await _to_running(store, coord, question="Which DB — sqlite or postgres?")
        # The node did not run; it opened a QUESTION gate instead.
        node = view.nodes[0]
        assert node.status == NodeStatus.PENDING_APPROVAL
        q = next(a for a in view.approvals if a.kind == ApprovalKind.QUESTION)
        assert q.state == ApprovalState.PENDING and q.detail == "Which DB — sqlite or postgres?"
        assert view.run.status == RunStatus.RUNNING  # waiting on the human

    asyncio.run(scenario())


def test_answer_unblocks_and_completes(tmp_path):
    store, coord = _mk(tmp_path)

    async def scenario():
        rid, _ = await _to_running(store, coord, question="Which DB?")
        view = await coord.answer(rid, "sqlite")
        node = view.nodes[0]
        assert node.answer == "sqlite" and node.status == NodeStatus.SUCCEEDED
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL
        q = next(a for a in view.approvals if a.kind == ApprovalKind.QUESTION)
        assert q.state == ApprovalState.APPROVED

    asyncio.run(scenario())


def test_answer_defaults_to_oldest_pending(tmp_path):
    store, coord = _mk(tmp_path)

    async def scenario():
        rid, _ = await _to_running(store, coord, question="Which DB?")
        # No approval_id passed -> resolves the run's pending question.
        view = await coord.answer(rid, "postgres")
        assert view.nodes[0].answer == "postgres"

    asyncio.run(scenario())


def test_reject_question_skips_node(tmp_path):
    store, coord = _mk(tmp_path)

    async def scenario():
        rid, view = await _to_running(store, coord, question="Which DB?")
        q = next(a for a in view.approvals if a.kind == ApprovalKind.QUESTION)
        view = await coord.resolve(rid, q.id, False)  # reject -> skip the node
        assert view.nodes[0].status == NodeStatus.SKIPPED
        # nothing succeeded -> the run is cancelled (all work rejected away)
        assert view.run.status == RunStatus.CANCELLED

    asyncio.run(scenario())


def test_no_question_runs_normally(tmp_path):
    store, coord = _mk(tmp_path)

    async def scenario():
        rid, view = await _to_running(store, coord, question="")
        assert view.nodes[0].status == NodeStatus.SUCCEEDED
        assert view.run.status == RunStatus.PENDING_FINAL_APPROVAL

    asyncio.run(scenario())


def test_answer_injected_into_worker_prompt():
    node = TaskNode(run_id="r", id="n", title="build", question="Which DB?", answer="sqlite")
    run = Run(id="r", goal="g", repo="/repo")
    prompt = build_prompt(node, run)
    assert "Which DB?" in prompt and "sqlite" in prompt


def test_notifier_question_message_shows_question_and_answer_hint():
    from zeus.orchestration.swarm.models import Approval
    run = Run(id="abc123", goal="ship it", repo="/repo", status=RunStatus.RUNNING)
    ap = Approval(id="a1", run_id="abc123", kind=ApprovalKind.QUESTION,
                  node_id="n1", detail="Which DB?")
    msg = build_message(run, ap)
    assert "Which DB?" in msg and "/answer abc123" in msg


# ---- Telegram /answer command --------------------------------------------


def test_telegram_answer_command_parses_and_dispatches():
    import types

    from zeus.integrations.telegram.bot import TelegramBot

    calls = []

    async def fake_answer(run_id, text):
        calls.append((run_id, text))
        return f"Answer recorded for run {run_id}."

    bot = TelegramBot("tok", query_engine=object(), allowed_chat_ids=[42],
                      swarm_answer=fake_answer)

    replies = []

    async def scenario():
        msg = types.SimpleNamespace(
            text="/answer run9 use sqlite please",
            reply_text=lambda t, **k: replies.append(t) or _acoro(),
        )
        update = types.SimpleNamespace(
            effective_message=msg,
            effective_chat=types.SimpleNamespace(id=42),
        )
        await bot._on_answer(update, None)
        assert calls == [("run9", "use sqlite please")]
        assert replies and "recorded" in replies[0]

    async def _acoro():
        return None

    asyncio.run(scenario())


def test_telegram_answer_rejects_disallowed_chat():
    import types

    from zeus.integrations.telegram.bot import TelegramBot

    calls = []

    async def fake_answer(run_id, text):
        calls.append((run_id, text))
        return "ok"

    bot = TelegramBot("tok", query_engine=object(), allowed_chat_ids=[42],
                      swarm_answer=fake_answer)

    async def scenario():
        msg = types.SimpleNamespace(text="/answer run9 hi", reply_text=lambda *a, **k: _acoro())
        update = types.SimpleNamespace(
            effective_message=msg,
            effective_chat=types.SimpleNamespace(id=999),  # not allowlisted
        )
        await bot._on_answer(update, None)
        assert calls == []  # never dispatched

    async def _acoro():
        return None

    asyncio.run(scenario())
