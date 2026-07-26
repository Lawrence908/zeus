# tests/test_swarm_observability.py — P8 metrics, audit events, event bus
import asyncio

from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.events import SwarmEventBus
from zeus.orchestration.swarm.models import (
    ApprovalKind,
    NodeStatus,
    RunSpec,
    RunStatus,
    TaskNodeSpec,
)
from zeus.orchestration.swarm.notifier import NullNotifier
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.verifier import NoopVerifier
from zeus.orchestration.swarm.worker import StubWorker


# ---- event bus ------------------------------------------------------------


def test_event_bus_fanout():
    async def scenario():
        bus = SwarmEventBus()
        a, b = bus.subscribe(), bus.subscribe()
        assert bus.subscriber_count == 2
        await bus.publish({"run_id": "r", "type": "update"})
        assert (await a.get())["run_id"] == "r"
        assert (await b.get())["run_id"] == "r"
        bus.unsubscribe(a)
        assert bus.subscriber_count == 1

    asyncio.run(scenario())


def test_event_bus_drops_for_full_slow_subscriber():
    async def scenario():
        bus = SwarmEventBus()
        q = bus.subscribe()
        # Fill beyond capacity; publish must not raise.
        for i in range(500):
            await bus.publish({"n": i})
        assert not q.empty()

    asyncio.run(scenario())


# ---- audit log ------------------------------------------------------------


def test_store_logs_run_status_and_approval_events(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo="/repo", nodes=[TaskNodeSpec(id="n1", title="t")]))
        rid = view.run.id
        # create_run opened the plan approval -> one approval event already
        await store.set_run_status(rid, RunStatus.RUNNING)
        await store.append_event(rid, "node_status", "succeeded", "n1")

        events = await store.list_events(rid)
        kinds = [e.kind for e in events]
        assert "run_status" in kinds and "approval" in kinds and "node_status" in kinds
        # newest first
        assert events[0].detail == "succeeded" and events[0].node_id == "n1"

    asyncio.run(scenario())


# ---- metrics --------------------------------------------------------------


def test_metrics_aggregate(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))

    async def scenario():
        view = await store.create_run(RunSpec(
            goal="g", repo="/repo",
            nodes=[TaskNodeSpec(id="n1", title="t", model="haiku"),
                   TaskNodeSpec(id="n2", title="u", model="sonnet", deps=["n1"])],
            planner_cost_usd=0.05,
        ))
        rid = view.run.id
        n1, n2 = view.nodes
        n1.status, n1.attempts, n1.cost_usd = NodeStatus.SUCCEEDED, 2, 0.03  # retried
        await store.update_node(n1)
        n2.status, n2.attempts, n2.cost_usd = NodeStatus.SUCCEEDED, 1, 0.20
        await store.update_node(n2)
        await store.set_run_status(rid, RunStatus.COMPLETED)

        m = await store.metrics()
        assert m.runs_total == 1 and m.runs_by_status["completed"] == 1
        assert m.nodes_total == 2 and m.nodes_by_status["succeeded"] == 2
        assert m.retry_rate == 0.5  # 1 of 2 executed nodes retried
        assert abs(m.cost_total_usd - (0.03 + 0.20 + 0.05)) < 1e-6
        assert m.planner_cost_usd == 0.05
        assert m.cost_by_model["haiku"] == 0.03 and m.cost_by_model["sonnet"] == 0.20

    asyncio.run(scenario())


def test_metrics_empty(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))

    async def scenario():
        m = await store.metrics()
        assert m.runs_total == 0 and m.retry_rate == 0.0 and m.avg_cost_per_run_usd == 0.0

    asyncio.run(scenario())


# ---- coordinator publishes to the bus -------------------------------------


def test_coordinator_publishes_on_advance(tmp_path):
    store = SwarmStore(str(tmp_path / "s.db"))
    bus = SwarmEventBus()
    coord = Coordinator(store, StubWorker(), None, NoopVerifier(), NullNotifier(),
                        event_bus=bus)

    async def scenario():
        q = bus.subscribe()
        view = await store.create_run(RunSpec(
            goal="g", repo="/repo", nodes=[TaskNodeSpec(id="n1", title="t")]))
        plan = next(a for a in view.approvals if a.kind == ApprovalKind.PLAN)
        await coord.resolve(view.run.id, plan.id, True)  # -> running -> final gate
        # at least one update event was published for this run
        evt = await asyncio.wait_for(q.get(), timeout=1.0)
        assert evt["run_id"] == view.run.id and evt["type"] == "update"

    asyncio.run(scenario())
