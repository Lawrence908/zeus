# tests/test_swarm_chat_tools.py — chat-path swarm tools (status/propose/approve/answer)
import asyncio

from zeus.core.tools import registry
from zeus.core.tools import swarm as swarm_tools


class _Resp:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text

    def json(self):
        return self._payload


_VIEW = {
    "run": {"id": "run123", "status": "running", "goal": "add a health endpoint",
            "budget_usd": 1.0, "planner_cost_usd": 0.02, "pr_url": None},
    "nodes": [
        {"id": "implement", "title": "implement it", "deps": [], "status": "succeeded", "cost_usd": 0.03},
        {"id": "verify", "title": "test it", "deps": ["implement"], "status": "running", "cost_usd": 0.0},
    ],
    "approvals": [{"id": "ap1", "kind": "plan", "node_id": None, "state": "pending"}],
    "estimate": {"total_usd": 0.06, "per_node": {}},
}


# ---- registration gating --------------------------------------------------


def test_register_gated_on_swarm_enabled(monkeypatch):
    registry.clear()
    monkeypatch.delenv("ZEUS_SWARM_ENABLED", raising=False)
    swarm_tools.register()
    assert registry.list_specs() == []  # not registered when swarm off

    monkeypatch.setenv("ZEUS_SWARM_ENABLED", "1")
    swarm_tools.register()
    names = {s.name for s in registry.list_specs()}
    assert names == {"swarm_status", "swarm_propose", "swarm_approve", "swarm_answer"}
    registry.clear()


# ---- swarm_status ---------------------------------------------------------


def test_status_lists_runs(monkeypatch):
    async def fake_get(path, params=None):
        assert path == "/swarm/runs"
        return [{"id": "run123", "status": "running", "goal": "add a health endpoint"}]
    monkeypatch.setattr(swarm_tools, "_get", fake_get)

    async def scenario():
        res = await swarm_tools._status_handler({})
        assert not res.is_error and "run123" in res.content and "running" in res.content
    asyncio.run(scenario())


def test_status_details_a_run(monkeypatch):
    async def fake_get(path, params=None):
        assert path == "/swarm/runs/run123"
        return _VIEW
    monkeypatch.setattr(swarm_tools, "_get", fake_get)

    async def scenario():
        res = await swarm_tools._status_handler({"run_id": "run123"})
        assert "implement" in res.content and "verify" in res.content
        assert "pending gates: plan" in res.content
        assert "spent $0.05" in res.content  # 0.03 node + 0.02 planner
    asyncio.run(scenario())


# ---- swarm_propose --------------------------------------------------------


def test_propose_reports_run(monkeypatch):
    async def fake_post(path, payload):
        assert path == "/swarm/propose" and payload["goal"] == "build X"
        return _Resp(200, _VIEW)
    monkeypatch.setattr(swarm_tools, "_post", fake_post)

    async def scenario():
        res = await swarm_tools._propose_handler({"goal": "build X"})
        assert not res.is_error
        assert "run123" in res.content and "2 nodes" in res.content
        assert "plan approval" in res.content and "/os/" in res.content
    asyncio.run(scenario())


def test_propose_disabled_reports_flag(monkeypatch):
    async def fake_post(path, payload):
        return _Resp(403, text="disabled")
    monkeypatch.setattr(swarm_tools, "_post", fake_post)

    async def scenario():
        res = await swarm_tools._propose_handler({"goal": "x"})
        assert res.is_error and "ZEUS_SWARM_PROPOSE_ENABLED" in res.content
    asyncio.run(scenario())


def test_propose_requires_goal():
    async def scenario():
        res = await swarm_tools._propose_handler({})
        assert res.is_error and "goal" in res.content
    asyncio.run(scenario())


# ---- swarm_approve --------------------------------------------------------


def test_approve_resolves_pending_gate(monkeypatch):
    posted = {}

    async def fake_get(path, params=None):
        return _VIEW

    async def fake_post(path, payload):
        posted.update({"path": path, "payload": payload})
        return _Resp(200, _VIEW)

    monkeypatch.setattr(swarm_tools, "_get", fake_get)
    monkeypatch.setattr(swarm_tools, "_post", fake_post)

    async def scenario():
        res = await swarm_tools._approve_handler({"run_id": "run123"})
        assert not res.is_error and "approved plan gate" in res.content
        assert posted["path"] == "/swarm/runs/run123/approve"
        assert posted["payload"] == {"approval_id": "ap1", "approve": True}
    asyncio.run(scenario())


def test_approve_no_matching_gate(monkeypatch):
    async def fake_get(path, params=None):
        return {**_VIEW, "approvals": []}
    monkeypatch.setattr(swarm_tools, "_get", fake_get)

    async def scenario():
        res = await swarm_tools._approve_handler({"run_id": "run123", "kind": "final"})
        assert res.is_error and "No pending final gate" in res.content
    asyncio.run(scenario())


# ---- swarm_answer ---------------------------------------------------------


def test_answer_posts_and_summarizes(monkeypatch):
    async def fake_post(path, payload):
        assert path == "/swarm/runs/run123/answer" and payload == {"answer": "use sqlite"}
        return _Resp(200, _VIEW)
    monkeypatch.setattr(swarm_tools, "_post", fake_post)

    async def scenario():
        res = await swarm_tools._answer_handler({"run_id": "run123", "answer": "use sqlite"})
        assert not res.is_error and "Answered the question" in res.content
    asyncio.run(scenario())


def test_answer_requires_fields():
    async def scenario():
        res = await swarm_tools._answer_handler({"run_id": "run123"})
        assert res.is_error
    asyncio.run(scenario())
