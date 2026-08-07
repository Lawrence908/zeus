# tests/test_epstein.py — Epstein reference client + chat tools (offline, mocked).
#
# No live service dependency: an httpx.MockTransport stands in for the epstein
# API so the client's parsing, error handling, base-URL probing, and the six
# chat-path tools can be tested deterministically in CI.
from __future__ import annotations

import asyncio

import httpx
import pytest

from zeus.memory import epstein as ep


# --------------------------------------------------------------------------
# Mock transport
# --------------------------------------------------------------------------
_CAPABILITIES = {
    "service": "epstein-research",
    "graph_available": True,
    "auth": "open",
    "doc_types": {"": 100, "court-filing": 50, "foia": 10},
    "filter_fields": ["doc_type", "date_mentioned", "entity"],
    "endpoints": {"POST /api/research/search": "..."},
    "safety_rules": "1. Mention is not involvement. 2. Allegations stay labeled.",
}

_SEARCH = {
    "results": [
        {
            "text": "Box of flight logs delivered.",
            "source_label": "primary",
            "document_id": "DOC1",
            "chunk_index": "0",
            "doc_type": "primary",
            "score": 0.71,
        }
    ],
    "entities": {"Person A": {}},
}

_DOC = {
    "document_id": "DOC1",
    "source_label": "primary",
    "doc_type": "primary",
    "num_chunks": 1,
    "text": "From: A To: B Subject: logs",
    "metadata": {},
}

_ENTITY = {
    "entity": "Jane Doe",
    "subgraph": {
        "nodes": [
            {"name": "Jane Doe", "type": "Person"},
            {"name": "Acme Corp", "type": "Org"},
            {"event_id": "abc123", "event_type": "other"},
        ],
        "edges": [{"a": 1}, {"a": 2}],
    },
}

_JOB_DONE = {
    "job_id": "JOB1",
    "question": "q",
    "status": "done",
    "steps": ["Decomposing", "Retrieving", "Synthesizing", "Done"],
    "report": "# Research\n\nSynthesis failed: timed out",
    "citations": [
        {"source_label": "foia", "document_id": "DOC9", "chunk_index": "3", "doc_type": "foia"}
    ],
    "error": None,
}


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.endswith("/capabilities"):
        return httpx.Response(200, json=_CAPABILITIES)
    if path.endswith("/search"):
        return httpx.Response(200, json=_SEARCH)
    if "/document/" in path:
        return httpx.Response(200, json=_DOC)
    if "/entity/" in path:
        if "Downed" in path:  # sentinel name to simulate graph outage
            return httpx.Response(503, text="graph down")
        return httpx.Response(200, json=_ENTITY)
    if path.endswith("/jobs") and request.method == "POST":
        return httpx.Response(200, json={"job_id": "JOB1", "status": "queued"})
    if "/jobs/" in path:
        return httpx.Response(200, json=_JOB_DONE)
    return httpx.Response(404, text="not found")


@pytest.fixture
def mock_epstein(monkeypatch):
    """Patch httpx.AsyncClient so every client in ep.* uses the mock transport."""
    transport = httpx.MockTransport(_handler)
    orig = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = transport
        return orig(*args, **kwargs)

    monkeypatch.setattr(ep.httpx, "AsyncClient", factory)
    ep.reset_epstein_client()
    monkeypatch.setenv("ZEUS_EPSTEIN_ENABLED", "1")
    monkeypatch.setenv("ZEUS_EPSTEIN_BASE_URL", "http://epstein-test:9999")
    yield
    ep.reset_epstein_client()


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------
def test_client_endpoints(mock_epstein):
    async def _run():
        c = ep.get_epstein_client()
        assert c is not None

        cap = await c.capabilities()
        assert cap["graph_available"] is True
        assert "court-filing" in cap["doc_types"]

        s = await c.search("flight logs", n_results=2)
        hit = ep.EpsteinHit.from_api(s["results"][0])
        assert hit.document_id == "DOC1"
        assert "DOC1" in hit.citation() and "primary" in hit.citation()

        doc = await c.document("DOC1")
        assert doc["num_chunks"] == 1

        ent = await c.entity("Jane Doe")
        assert ent["entity"] == "Jane Doe"

        job = await c.start_job("q", depth=2)
        assert job["job_id"] == "JOB1"
        res = await c.get_job("JOB1")
        assert res["status"] == "done"
        assert len(res["citations"]) == 1

    asyncio.run(_run())


def test_entity_graph_down_raises_503(mock_epstein):
    async def _run():
        c = ep.get_epstein_client()
        with pytest.raises(ep.EpsteinError) as exc:
            await c.entity("Downed Entity")
        assert exc.value.status == 503

    asyncio.run(_run())


def test_base_url_probe(monkeypatch):
    """With no explicit base URL, the client probes candidates and caches the winner."""
    transport = httpx.MockTransport(_handler)
    orig = httpx.AsyncClient
    monkeypatch.setattr(
        ep.httpx,
        "AsyncClient",
        lambda *a, **k: orig(*a, **{**k, "transport": transport}),
    )

    async def _run():
        c = ep.EpsteinClient(candidates=("http://cand-a:1", "http://cand-b:2"))
        cap = await c.capabilities()
        assert cap["service"] == "epstein-research"
        assert c.resolved_base == "http://cand-a:1"  # first 200 wins

    asyncio.run(_run())


def test_client_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ZEUS_EPSTEIN_ENABLED", raising=False)
    ep.reset_epstein_client()
    assert ep.get_epstein_client() is None


# --------------------------------------------------------------------------
# Chat tools
# --------------------------------------------------------------------------
_SAFETY_TOKEN = "Mention"  # from the safety banner echoed into every result


def test_tools_register_only_when_enabled(monkeypatch):
    from zeus.core.tools import registry
    from zeus.core.tools.epstein import register

    registry.clear()
    monkeypatch.setenv("ZEUS_EPSTEIN_ENABLED", "0")
    register()
    assert not [s for s in registry.list_specs() if s.name.startswith("epstein_")]

    monkeypatch.setenv("ZEUS_EPSTEIN_ENABLED", "1")
    register()
    names = {s.name for s in registry.list_specs() if s.name.startswith("epstein_")}
    assert names == {
        "epstein_capabilities",
        "epstein_search",
        "epstein_document",
        "epstein_entity",
        "epstein_entity_dossier",
        "epstein_connection_map",
        "epstein_research_start",
        "epstein_research_result",
        "epstein_research",
    }
    registry.clear()


def test_tool_handlers_format_with_safety(mock_epstein):
    from zeus.core.tools import registry
    from zeus.core.tools.epstein import register

    registry.clear()
    register()

    async def call(name, args):
        spec, handler = registry.get(name)
        return await handler(args)

    async def _run():
        cap = await call("epstein_capabilities", {})
        assert not cap.is_error and _SAFETY_TOKEN in cap.content
        assert "safety_rules" in cap.content

        s = await call("epstein_search", {"query": "flight logs"})
        assert not s.is_error
        assert "DOC1" in s.content and "cite:" in s.content

        ent = await call("epstein_entity", {"name": "Jane Doe"})
        assert not ent.is_error
        # named nodes surfaced, event node counted separately
        assert "Acme Corp" in ent.content and "event node" in ent.content

        res = await call("epstein_research_result", {"job_id": "JOB1"})
        assert not res.is_error
        # citations surfaced even though the report prose is a timeout stub
        assert "DOC9" in res.content

    asyncio.run(_run())
    registry.clear()


def test_tools_graceful_when_disabled(monkeypatch):
    from zeus.core.tools.epstein import _cap_handler

    monkeypatch.delenv("ZEUS_EPSTEIN_ENABLED", raising=False)
    ep.reset_epstein_client()
    res = asyncio.run(_cap_handler({}))
    assert res.is_error and "disabled" in res.content


def test_mcp_server_lists_epstein_tools():
    import asyncio

    from zeus.mcp.server import mcp

    async def _run():
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert {"epstein_search", "epstein_research_start", "epstein_research"} <= names

    asyncio.run(_run())


# --------------------------------------------------------------------------
# Research workflow
# --------------------------------------------------------------------------
def _mock_client():
    transport = httpx.MockTransport(_handler)
    orig = httpx.AsyncClient

    class _C(ep.EpsteinClient):
        pass

    c = _C(base_url="http://epstein-test:9999")
    # Patch the module so this client's internal AsyncClients use the transport.
    ep.httpx.AsyncClient = lambda *a, **k: orig(*a, **{**k, "transport": transport})
    return c, orig


def test_workflow_assembles_cited_result():
    from zeus.orchestration.epstein_research import run_research

    c, orig = _mock_client()
    try:

        async def _run():
            r = await run_research("what about the logs", client=c, poll_budget_seconds=0)
            assert r.error is None
            # fast evidence + citation from the mock search
            assert any(h.document_id == "DOC1" for h in r.evidence)
            assert {"document_id": "DOC1", "source_label": "primary"} in r.citations()
            # job was started
            assert r.job_id == "JOB1"
            # entity path fired on the plausible name "Person A" -> Jane Doe graph
            assert any("Jane Doe" in e["names"] for e in r.entities)
            md = r.to_markdown()
            assert "Citations" in md and "Confidence" in md
            assert "co-occurrence" in md.lower()
            # standing caveat always present
            assert any("co-occurrence" in g for g in r.gaps)

        asyncio.run(_run())
    finally:
        ep.httpx.AsyncClient = orig


def test_workflow_poll_surfaces_job_citations():
    from zeus.orchestration.epstein_research import run_research

    c, orig = _mock_client()
    try:

        async def _run():
            # Mock get_job returns done immediately with a timeout-stub report
            r = await run_research(
                "logs", client=c, poll_budget_seconds=5, poll_interval_seconds=0.01
            )
            assert r.job_status == "done"
            # citations from the job merge in even though prose is a timeout stub
            assert any(x["document_id"] == "DOC9" for x in r.citations())

        asyncio.run(_run())
    finally:
        ep.httpx.AsyncClient = orig


def test_plausible_entity_filters_source_labels():
    from zeus.orchestration.epstein_research import _plausible_entity

    keys = {"", "court-filing", "foia", "2025-dec-DOJ-release"}
    assert _plausible_entity("Ghislaine Maxwell", keys)
    assert not _plausible_entity("primary", keys)
    assert not _plausible_entity("2025-dec-DOJ-release", keys)
    assert not _plausible_entity("court-filing", keys)


def test_workflow_disabled_returns_error(monkeypatch):
    from zeus.orchestration.epstein_research import run_research

    # Hermetic: an earlier test may leave ZEUS_EPSTEIN_ENABLED set in the
    # environment, so clear it and drop the cached singleton before asserting
    # the disabled path.
    monkeypatch.delenv("ZEUS_EPSTEIN_ENABLED", raising=False)
    ep.reset_epstein_client()
    r = asyncio.run(run_research("q", client=None))
    assert r.error and "disabled" in r.error


# --------------------------------------------------------------------------
# Phase 3 — persistence write-gate
# --------------------------------------------------------------------------
def _mk_result(**kw):
    from zeus.orchestration.epstein_research import ResearchResult

    defaults = dict(
        question="q",
        safety_rules="r",
        base_url="http://x",
        graph_available=True,
    )
    defaults.update(kw)
    return ResearchResult(**defaults)


def test_persist_findings_gated_off_by_default(monkeypatch):
    from zeus.memory.epstein import EpsteinHit
    from zeus.orchestration.epstein_research import persist_findings

    monkeypatch.delenv("ZEUS_MCP_ALLOW_WRITE", raising=False)
    r = _mk_result(
        evidence=[EpsteinHit("t", "DOC1", "primary", "primary", "0", 0.7)]
    )
    out = asyncio.run(persist_findings(r))
    assert out["persisted"] is False and "ALLOW_WRITE" in out["reason"]


def test_persist_findings_skips_on_error(monkeypatch):
    from zeus.orchestration.epstein_research import persist_findings

    monkeypatch.setenv("ZEUS_MCP_ALLOW_WRITE", "1")
    out = asyncio.run(persist_findings(_mk_result(error="boom")))
    assert out["persisted"] is False and "error" in out["reason"]


# --------------------------------------------------------------------------
# Phase 4 — overnight Kronos job fan-out
# --------------------------------------------------------------------------
def test_kronos_job_fans_out(monkeypatch):
    import zeus.orchestration.epstein_research as wf
    from zeus.kronos.jobs.epstein_research import run_epstein_research
    from zeus.memory.epstein import EpsteinHit

    async def fake_run_research(question, **kw):
        return _mk_result(
            question=question,
            evidence=[EpsteinHit("t", "DOC1", "primary", "primary", "0", 0.7)],
            job_id="J",
            job_status="done",
            confidence="medium",
        )

    monkeypatch.setattr(wf, "run_research", fake_run_research)

    out = asyncio.run(
        run_epstein_research(
            {
                "questions": ["q1", "q2", "q3"],
                "write_report": False,
                "persist": False,
            }
        )
    )
    assert out["subjects"] == 3
    assert len(out["results"]) == 3
    assert all(r["confidence"] == "medium" for r in out["results"])


def test_kronos_job_requires_question():
    from zeus.kronos.jobs.epstein_research import run_epstein_research

    with pytest.raises(ValueError):
        asyncio.run(run_epstein_research({}))
