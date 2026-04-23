# tests/test_chat_async.py — /chat/async endpoint + background worker tests
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from zeus.core.chat import (
    ChatJob,
    _CHAT_JOB_MAX,
    _run_chat_job_background,
    router,
)
from zeus.core.query import QueryResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _fake_query_result(
    *, session_id: str, message: str = "hi", reply: str = "a perfectly adequate reply"
) -> QueryResult:
    return QueryResult(
        session_id=session_id,
        assistant_message=reply,
        context_sources=[],
        latency_ms=42,
        model_used="test-model",
        token_estimate=10,
        topic="test",
        reflection_attempts=0,
        aegis_flags=[],
        tool_calls=[],
    )


def _fake_engine() -> MagicMock:
    engine = MagicMock()
    sessions = MagicMock()
    fake_sess = MagicMock()
    fake_sess.id = "sess-abc"
    sessions.get_or_create = AsyncMock(return_value=fake_sess)
    sessions.get = AsyncMock(return_value=fake_sess)
    engine.sessions = sessions

    async def _query(message, session_id=None, **kwargs):
        return _fake_query_result(session_id=session_id or fake_sess.id, message=message)

    engine.query = AsyncMock(side_effect=_query)
    return engine


@pytest.fixture
def app_with_engine():
    app = FastAPI()
    app.include_router(router)
    app.state.query_engine = _fake_engine()
    app.state.memory = MagicMock()  # required by _chat_use guards in chat.py
    app.state.session_manager = app.state.query_engine.sessions
    return app


@pytest.fixture
def client(app_with_engine):
    return TestClient(app_with_engine)


# ---------------------------------------------------------------------------
# POST /chat/async — create job
# ---------------------------------------------------------------------------


class TestChatAsyncCreate:
    def test_returns_job_id_immediately(self, client: TestClient) -> None:
        resp = client.post("/chat/async", json={"message": "hello"})
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["status"] == "queued"
        assert body["session_id"]

    def test_rejects_empty_message(self, client: TestClient) -> None:
        resp = client.post("/chat/async", json={"message": ""})
        assert resp.status_code == 422

    def test_accepts_callback_url(self, client: TestClient) -> None:
        resp = client.post(
            "/chat/async",
            json={"message": "hello", "callback_url": "https://example.invalid/hook"},
        )
        assert resp.status_code == 202

    def test_rejects_non_http_callback_url(self, client: TestClient) -> None:
        # Validator must block file://, javascript:, gopher://, etc. — any
        # scheme other than http/https is a foot-gun for SSRF.
        for bad in ("file:///etc/passwd", "javascript:alert(1)", "ftp://internal/x", "no-scheme"):
            r = client.post("/chat/async", json={"message": "hi", "callback_url": bad})
            assert r.status_code == 422, f"expected 422 for {bad!r}, got {r.status_code}"

    def test_normalizes_empty_callback_url_to_none(self, client: TestClient) -> None:
        # Empty string and whitespace-only must collapse to None so the job
        # never gets stuck in callback_status='pending' waiting on a callback
        # that will never fire. (Copilot review on LAB-401.)
        for empty in ("", "   ", "\n\t"):
            r = client.post("/chat/async", json={"message": "hi", "callback_url": empty})
            assert r.status_code == 202, f"expected 202 for {empty!r}"
            job_id = r.json()["job_id"]
            # Poll briefly for completion so callback_status settles.
            deadline = time.time() + 2.0
            while time.time() < deadline:
                j = client.get(f"/chat/async/{job_id}").json()
                if j["status"] in ("done", "error"):
                    break
                time.sleep(0.05)
            assert j["callback_status"] == "skipped", f"got {j['callback_status']} for {empty!r}"


# ---------------------------------------------------------------------------
# GET /chat/async/{job_id} — status + 404
# ---------------------------------------------------------------------------


class TestChatAsyncStatus:
    def test_unknown_job_404(self, client: TestClient) -> None:
        resp = client.get("/chat/async/nonexistent")
        assert resp.status_code == 404

    def test_poll_eventually_done(self, client: TestClient) -> None:
        create = client.post("/chat/async", json={"message": "hi"})
        job_id = create.json()["job_id"]
        # Background task runs on the event loop between sync TestClient calls.
        # A short wait should be enough for the fake engine to complete.
        deadline = time.monotonic() + 2.0
        status = None
        while time.monotonic() < deadline:
            resp = client.get(f"/chat/async/{job_id}")
            assert resp.status_code == 200
            status = resp.json()["status"]
            if status in ("done", "error"):
                break
            time.sleep(0.05)
        assert status == "done"
        assert resp.json()["result"]["assistant_message"] == "a perfectly adequate reply"


# ---------------------------------------------------------------------------
# _run_chat_job_background — direct unit test
# ---------------------------------------------------------------------------


class TestBackgroundWorker:
    def test_success_updates_job_to_done(self) -> None:
        from collections import OrderedDict

        jobs: OrderedDict[str, ChatJob] = OrderedDict()
        now = time.time()
        job = ChatJob(
            job_id="j1",
            session_id="s1",
            status="queued",
            created_at=now,
            updated_at=now,
            callback_url=None,
        )
        jobs[job.job_id] = job

        engine = _fake_engine()
        asyncio.run(
            _run_chat_job_background(
                jobs=jobs,
                job_id="j1",
                engine=engine,
                message="hi",
                session_id="s1",
                max_tokens=256,
                use_context=False,
                callback_url=None,
                http_client=None,
            )
        )
        assert jobs["j1"].status == "done"
        assert jobs["j1"].result is not None
        assert jobs["j1"].result.assistant_message == "a perfectly adequate reply"

    def test_engine_exception_marks_error(self) -> None:
        from collections import OrderedDict

        jobs: OrderedDict[str, ChatJob] = OrderedDict()
        now = time.time()
        job = ChatJob(
            job_id="j2",
            session_id="s1",
            status="queued",
            created_at=now,
            updated_at=now,
        )
        jobs[job.job_id] = job

        engine = _fake_engine()
        engine.query = AsyncMock(side_effect=RuntimeError("kaboom"))
        asyncio.run(
            _run_chat_job_background(
                jobs=jobs,
                job_id="j2",
                engine=engine,
                message="hi",
                session_id="s1",
                max_tokens=256,
                use_context=False,
                callback_url=None,
                http_client=None,
            )
        )
        assert jobs["j2"].status == "error"
        assert "kaboom" in (jobs["j2"].error or "")

    def test_callback_posts_payload(self) -> None:
        from collections import OrderedDict

        jobs: OrderedDict[str, ChatJob] = OrderedDict()
        now = time.time()
        job = ChatJob(
            job_id="j3",
            session_id="s1",
            status="queued",
            created_at=now,
            updated_at=now,
            callback_url="https://callback.invalid/hook",
            callback_status="pending",
        )
        jobs[job.job_id] = job

        engine = _fake_engine()

        fake_response = MagicMock()
        fake_response.raise_for_status = MagicMock()
        http_client = MagicMock()
        http_client.post = AsyncMock(return_value=fake_response)

        asyncio.run(
            _run_chat_job_background(
                jobs=jobs,
                job_id="j3",
                engine=engine,
                message="hi",
                session_id="s1",
                max_tokens=256,
                use_context=False,
                callback_url="https://callback.invalid/hook",
                http_client=http_client,
            )
        )
        assert jobs["j3"].status == "done"
        assert jobs["j3"].callback_status == "ok"
        http_client.post.assert_awaited_once()
        posted_url, posted_kwargs = http_client.post.call_args
        assert posted_url[0] == "https://callback.invalid/hook"
        payload = posted_kwargs["json"]
        assert payload["job_id"] == "j3"
        assert payload["status"] == "done"
        assert payload["result"]["assistant_message"] == "a perfectly adequate reply"

    def test_callback_failure_is_recorded(self) -> None:
        from collections import OrderedDict

        jobs: OrderedDict[str, ChatJob] = OrderedDict()
        now = time.time()
        jobs["j4"] = ChatJob(
            job_id="j4",
            session_id="s1",
            status="queued",
            created_at=now,
            updated_at=now,
            callback_url="https://bad.invalid/hook",
            callback_status="pending",
        )

        http_client = MagicMock()
        http_client.post = AsyncMock(side_effect=RuntimeError("network down"))

        asyncio.run(
            _run_chat_job_background(
                jobs=jobs,
                job_id="j4",
                engine=_fake_engine(),
                message="hi",
                session_id="s1",
                max_tokens=256,
                use_context=False,
                callback_url="https://bad.invalid/hook",
                http_client=http_client,
            )
        )
        # Job is still 'done' — the query succeeded; only the callback failed.
        assert jobs["j4"].status == "done"
        assert jobs["j4"].callback_status == "failed"


# ---------------------------------------------------------------------------
# Ring buffer
# ---------------------------------------------------------------------------


class TestJobRingBuffer:
    def test_eviction_caps_at_max(self, client: TestClient) -> None:
        # Create _CHAT_JOB_MAX + 5 jobs; oldest should be evicted.
        created: list[str] = []
        for _ in range(_CHAT_JOB_MAX + 5):
            r = client.post("/chat/async", json={"message": "hi"})
            created.append(r.json()["job_id"])

        # Oldest 5 should be 404 by now.
        missing = sum(1 for jid in created[:5] if client.get(f"/chat/async/{jid}").status_code == 404)
        assert missing == 5
        # Newest 5 should still be present.
        present = sum(1 for jid in created[-5:] if client.get(f"/chat/async/{jid}").status_code == 200)
        assert present == 5
