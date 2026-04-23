# tests/test_classify.py — /classify endpoint tests
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from zeus.core.chat import ChatClassification, router
from zeus.core.small_llm import SmallLLMResult


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _small_llm_success(parsed: ChatClassification) -> SmallLLMResult:
    return SmallLLMResult(
        text=parsed.model_dump_json(),
        parsed=parsed,
        provider_used="test",
        model_used="test-model",
        latency_ms=50,
        tokens_in=100,
        tokens_out=40,
        cost_usd=0.0,
        attempts=1,
        errors=[],
    )


def _small_llm_unparsed() -> SmallLLMResult:
    return SmallLLMResult(
        text="garbage text not matching schema",
        parsed=None,
        provider_used="test",
        model_used="test-model",
        latency_ms=50,
        tokens_in=100,
        tokens_out=20,
        cost_usd=0.0,
        attempts=2,
        errors=["tier1: ValidationError"],
    )


class TestClassify:
    def test_happy_path_search(self, client: TestClient) -> None:
        parsed = ChatClassification(
            intent="search",
            estimated_ms=15000,
            tool_hint="web_search",
            reasoning="asks about current events",
        )
        with patch(
            "zeus.core.small_llm.small_llm_call",
            new=AsyncMock(return_value=_small_llm_success(parsed)),
        ):
            r = client.post("/classify", json={"message": "who won the F1 race yesterday?"})
        assert r.status_code == 200
        body = r.json()
        assert body["intent"] == "search"
        assert body["tool_hint"] == "web_search"
        assert body["estimated_ms"] == 15000

    def test_happy_path_chat(self, client: TestClient) -> None:
        parsed = ChatClassification(
            intent="chat",
            estimated_ms=3000,
            tool_hint=None,
            reasoning="small talk",
        )
        with patch(
            "zeus.core.small_llm.small_llm_call",
            new=AsyncMock(return_value=_small_llm_success(parsed)),
        ):
            r = client.post("/classify", json={"message": "hey how's it going"})
        assert r.status_code == 200
        assert r.json()["intent"] == "chat"

    def test_rejects_empty_message(self, client: TestClient) -> None:
        r = client.post("/classify", json={"message": ""})
        assert r.status_code == 422

    def test_fallback_on_llm_exception(self, client: TestClient) -> None:
        with patch(
            "zeus.core.small_llm.small_llm_call",
            new=AsyncMock(side_effect=RuntimeError("all providers down")),
        ):
            r = client.post("/classify", json={"message": "hello"})
        assert r.status_code == 200
        body = r.json()
        assert body["intent"] == "chat"  # safe default
        assert body["estimated_ms"] == 3000
        assert "unavailable" in (body["reasoning"] or "")

    def test_fallback_on_unparseable_output(self, client: TestClient) -> None:
        with patch(
            "zeus.core.small_llm.small_llm_call",
            new=AsyncMock(return_value=_small_llm_unparsed()),
        ):
            r = client.post("/classify", json={"message": "hello"})
        assert r.status_code == 200
        body = r.json()
        assert body["intent"] == "chat"

    def test_accepts_session_id(self, client: TestClient) -> None:
        parsed = ChatClassification(intent="chat", estimated_ms=2000)
        with patch(
            "zeus.core.small_llm.small_llm_call",
            new=AsyncMock(return_value=_small_llm_success(parsed)),
        ):
            r = client.post(
                "/classify",
                json={"message": "hi", "session_id": "sess-xyz"},
            )
        assert r.status_code == 200
