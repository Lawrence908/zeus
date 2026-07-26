# tests/test_swarm_local_worker.py — C4 local Ollama worker tier
import asyncio
import json

from zeus.orchestration.swarm import config, estimate
from zeus.orchestration.swarm import local_worker as lw
from zeus.orchestration.swarm.models import Run, RunStatus, TaskNode
from zeus.orchestration.swarm.worker import WorkerResult


def _node(model: str = "local", **kw) -> TaskNode:
    return TaskNode(run_id="r1", id="n1", title="Write a README", model=model, **kw)


def _run() -> Run:
    return Run(id="r1", goal="ship X", repo="/repo", status=RunStatus.RUNNING)


class _FakeResp:
    def __init__(self, content: str) -> None:
        self._content = content

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return {"message": {"content": self._content}}


class _FakeClient:
    def __init__(self, content: str) -> None:
        self._content = content

    def __call__(self, *a, **k):  # AsyncClient(timeout=...) -> self
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, json=None):  # noqa: A002
        return _FakeResp(self._content)


def _patch_ollama(monkeypatch, content: str) -> None:
    monkeypatch.setattr(lw.httpx, "AsyncClient", _FakeClient(content))


# ---- config helpers -------------------------------------------------------


def test_is_local_model():
    assert config.is_local_model("local")
    assert config.is_local_model("ollama")
    assert config.is_local_model("qwen2.5:7b-instruct")  # concrete tag
    assert not config.is_local_model("haiku")
    assert not config.is_local_model("sonnet")
    assert not config.is_local_model("")


def test_resolve_local_model():
    assert config.resolve_local_model("local") == config.local_model()
    assert config.resolve_local_model("ollama") == config.local_model()
    assert config.resolve_local_model("qwen3:8b") == "qwen3:8b"  # concrete tag kept


def test_local_node_estimates_zero():
    assert estimate.estimate_node(_node("local")) == 0.0
    assert estimate.estimate_node(_node("qwen2.5:7b-instruct")) == 0.0
    assert estimate.estimate_node(_node("haiku")) > 0.0


# ---- LocalWorker ----------------------------------------------------------


def test_local_worker_writes_files(monkeypatch, tmp_path):
    payload = json.dumps({
        "files": [{"path": "docs/README.md", "content": "# Hello\n"}],
        "summary": "added readme",
    })
    _patch_ollama(monkeypatch, payload)

    async def scenario():
        res = await lw.LocalWorker().run(_node(), _run(), str(tmp_path))
        assert res.success and res.cost_usd == 0.0
        assert (tmp_path / "docs" / "README.md").read_text() == "# Hello\n"

    asyncio.run(scenario())


def test_local_worker_parses_prose_wrapped_json(monkeypatch, tmp_path):
    payload = 'Sure!\n```json\n{"files":[{"path":"a.txt","content":"x"}]}\n```\n'
    _patch_ollama(monkeypatch, payload)

    async def scenario():
        res = await lw.LocalWorker().run(_node(), _run(), str(tmp_path))
        assert res.success
        assert (tmp_path / "a.txt").read_text() == "x"

    asyncio.run(scenario())


def test_local_worker_rejects_path_escape(monkeypatch, tmp_path):
    payload = json.dumps({"files": [{"path": "../evil.txt", "content": "x"}]})
    _patch_ollama(monkeypatch, payload)

    async def scenario():
        res = await lw.LocalWorker().run(_node(), _run(), str(tmp_path))
        assert not res.success and "escapes worktree" in (res.error or "")
        assert not (tmp_path.parent / "evil.txt").exists()

    asyncio.run(scenario())


def test_local_worker_bad_json_fails(monkeypatch, tmp_path):
    _patch_ollama(monkeypatch, "I could not do that.")

    async def scenario():
        res = await lw.LocalWorker().run(_node(), _run(), str(tmp_path))
        assert not res.success and "files" in (res.error or "")

    asyncio.run(scenario())


def test_local_worker_requires_workspace(monkeypatch, tmp_path):
    _patch_ollama(monkeypatch, "{}")

    async def scenario():
        res = await lw.LocalWorker().run(_node(), _run(), None)
        assert not res.success and "worktree" in (res.error or "")

    asyncio.run(scenario())


# ---- RoutingWorker --------------------------------------------------------


class _Recorder:
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.calls = 0

    async def run(self, node, run, workspace, feedback=None) -> WorkerResult:
        self.calls += 1
        return WorkerResult(success=True, output=self.tag)


def test_routing_worker_dispatch():
    paid, local = _Recorder("paid"), _Recorder("local")
    router = lw.RoutingWorker(paid, local)

    async def scenario():
        r1 = await router.run(_node("sonnet"), _run(), "/ws")
        r2 = await router.run(_node("local"), _run(), "/ws")
        r3 = await router.run(_node("qwen2.5:7b-instruct"), _run(), "/ws")
        assert r1.output == "paid" and paid.calls == 1
        assert r2.output == "local" and r3.output == "local" and local.calls == 2

    asyncio.run(scenario())
