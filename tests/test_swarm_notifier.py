# tests/test_swarm_notifier.py — approval notifier seam
import asyncio
import os
import tempfile

from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.models import ApprovalKind, RunSpec, TaskNodeSpec
from zeus.orchestration.swarm.notifier import TelegramNotifier, build_message
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.worker import StubWorker


class RecordingNotifier:
    def __init__(self):
        self.events = []

    async def approval_opened(self, run, approval):
        self.events.append(approval.kind)


def _fresh(notifier):
    fd, p = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SwarmStore(p)
    return store, Coordinator(store, StubWorker(), notifier=notifier)


def test_notifier_fires_on_node_write_and_final_gates():
    rec = RecordingNotifier()
    store, coord = _fresh(rec)

    async def scenario():
        spec = RunSpec(goal="g", repo=os.path.expanduser("~"), nodes=[
            TaskNodeSpec(id="a", title="a", requires_approval=True),  # node_write gate
        ])
        view = await store.create_run(spec)
        await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        # a hits its write gate
        assert ApprovalKind.NODE_WRITE in rec.events
        view = await store.get_view(view.run.id)
        await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.NODE_WRITE, "a").id, True)
        # a runs -> final gate
        assert ApprovalKind.FINAL in rec.events

    asyncio.run(scenario())


def test_notifier_failure_does_not_break_run():
    class Boom:
        async def approval_opened(self, run, approval):
            raise RuntimeError("telegram down")

    store, coord = _fresh(Boom())

    async def scenario():
        spec = RunSpec(goal="g", repo=os.path.expanduser("~"),
                       nodes=[TaskNodeSpec(id="a", title="a")])
        view = await store.create_run(spec)
        view = await coord.resolve(view.run.id, view.pending_approval(ApprovalKind.PLAN).id, True)
        # final gate still reached despite the notifier raising
        assert view.run.status.value == "pending_final_approval"

    asyncio.run(scenario())


def test_telegram_from_env(monkeypatch):
    monkeypatch.delenv("ZEUS_SWARM_TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "123,456")
    n = TelegramNotifier.from_env()
    assert n is not None and n._chat_id == "123"
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN")
    assert TelegramNotifier.from_env() is None


def test_build_message():
    from zeus.orchestration.swarm.models import Approval, Run, RunStatus
    run = Run(id="r1", goal="do the thing", repo="/r", status=RunStatus.PENDING_FINAL_APPROVAL)
    ap = Approval(id="a1", run_id="r1", kind=ApprovalKind.FINAL)
    msg = build_message(run, ap)
    assert "do the thing" in msg and "r1" in msg and "final" in msg.lower()
