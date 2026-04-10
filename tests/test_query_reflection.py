# tests/test_query_reflection.py — Unit tests for QueryEngine reflection loop (LAB-327)
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zeus.core.query import (
    MAX_REFLECT,
    QueryEngine,
    _build_reflection_prompt,
    _is_empty_or_failed_reply,
)


# ---------------------------------------------------------------------------
# _is_empty_or_failed_reply
# ---------------------------------------------------------------------------

class TestIsEmptyOrFailedReply:
    def test_empty_string(self) -> None:
        assert _is_empty_or_failed_reply("") is True

    def test_whitespace_only(self) -> None:
        assert _is_empty_or_failed_reply("   \n\t  ") is True

    def test_too_short(self) -> None:
        assert _is_empty_or_failed_reply("Hi") is True
        assert _is_empty_or_failed_reply("123456789") is True  # 9 chars

    def test_exactly_ten_chars(self) -> None:
        assert _is_empty_or_failed_reply("1234567890") is False

    def test_sorry_prefix(self) -> None:
        assert _is_empty_or_failed_reply("Sorry, I can't help with that.") is True

    def test_i_cant(self) -> None:
        assert _is_empty_or_failed_reply("I can't answer that question.") is True

    def test_i_cannot(self) -> None:
        assert _is_empty_or_failed_reply("I cannot provide that information.") is True

    def test_i_dont_know(self) -> None:
        assert _is_empty_or_failed_reply("I don't know the answer to that.") is True

    def test_im_unable(self) -> None:
        assert _is_empty_or_failed_reply("I'm unable to do that right now.") is True

    def test_case_insensitive(self) -> None:
        assert _is_empty_or_failed_reply("SORRY, that is not possible.") is True
        assert _is_empty_or_failed_reply("i CAN'T do that.") is True

    def test_valid_reply(self) -> None:
        assert _is_empty_or_failed_reply("The answer to your question is 42.") is False

    def test_sorry_in_middle_is_ok(self) -> None:
        assert _is_empty_or_failed_reply("I am sorry but here is the answer: blah blah blah") is False

    def test_none_like_empty(self) -> None:
        # Callers pass str, but empty is the edge
        assert _is_empty_or_failed_reply("") is True


# ---------------------------------------------------------------------------
# _build_reflection_prompt
# ---------------------------------------------------------------------------

class TestBuildReflectionPrompt:
    def test_basic_format(self) -> None:
        result = _build_reflection_prompt("What is 2+2?", "Sorry", 2)
        assert result.startswith("[Attempt 2]")
        assert "Sorry" in result
        assert "What is 2+2?" in result

    def test_truncates_failed_reply(self) -> None:
        long_reply = "x" * 200
        result = _build_reflection_prompt("query", long_reply, 3)
        # Should only contain first 100 chars of failed reply
        assert "x" * 100 in result
        assert "x" * 101 not in result

    def test_original_preserved(self) -> None:
        original = "User: Tell me about Zeus\nAssistant:"
        result = _build_reflection_prompt(original, "idk", 2)
        assert result.endswith(original)

    def test_attempt_number_in_output(self) -> None:
        result = _build_reflection_prompt("q", "bad", 3)
        assert "[Attempt 3]" in result


# ---------------------------------------------------------------------------
# QueryEngine.query() reflection loop
# ---------------------------------------------------------------------------

def _make_engine() -> QueryEngine:
    """Create a QueryEngine with mocked memory and session dependencies."""
    memory = MagicMock()
    session_mgr = MagicMock(spec=["get_or_create", "get_context_window", "append_turn", "get"])

    fake_session = MagicMock()
    fake_session.id = "test-session-id"
    fake_session.topic = None

    session_mgr.get_or_create = AsyncMock(return_value=fake_session)
    session_mgr.get = AsyncMock(return_value=fake_session)
    session_mgr.get_context_window = AsyncMock(return_value="")

    session_after = MagicMock()
    session_after.topic = "test"
    session_mgr.append_turn = AsyncMock(return_value=session_after)

    engine = QueryEngine(memory=memory, session_manager=session_mgr)
    return engine


@pytest.fixture()
def _patch_externals():
    """Patch memory search, profile facts, and aegis so query() focuses on LLM loop."""
    with (
        patch("zeus.core.query.search_memories", return_value=[]),
        patch("zeus.core.query.get_profile_facts", return_value=[]),
        patch("zeus.core.query.aegis_enabled", return_value=False),
        patch("zeus.core.query.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        yield mock_sleep


class TestQueryReflectionLoop:
    def test_no_retry_on_good_reply(self, _patch_externals: AsyncMock) -> None:
        engine = _make_engine()
        call_count = 0

        async def fake_llm(*, system: str, user_prompt: str, max_tokens: int) -> str:
            nonlocal call_count
            call_count += 1
            return "Here is a perfectly good answer for you."

        with patch("zeus.core.query._run_llm", side_effect=fake_llm):
            result = asyncio.run(engine.query("test question", use_context=False))

        assert call_count == 1
        assert result.reflection_attempts == 0
        assert result.assistant_message == "Here is a perfectly good answer for you."

    def test_retries_on_empty_then_succeeds(self, _patch_externals: AsyncMock) -> None:
        engine = _make_engine()
        mock_sleep = _patch_externals
        responses = ["", "too short", "Here is the real answer to your question."]
        call_count = 0

        async def fake_llm(*, system: str, user_prompt: str, max_tokens: int) -> str:
            nonlocal call_count
            resp = responses[call_count]
            call_count += 1
            return resp

        with patch("zeus.core.query._run_llm", side_effect=fake_llm):
            result = asyncio.run(engine.query("test question", use_context=False))

        assert call_count == 3
        assert result.reflection_attempts == 2
        assert result.assistant_message == "Here is the real answer to your question."
        # Verify backoff sleeps happened
        assert mock_sleep.call_count == 2

    def test_max_retries_exhausted(self, _patch_externals: AsyncMock) -> None:
        engine = _make_engine()
        call_count = 0

        async def fake_llm(*, system: str, user_prompt: str, max_tokens: int) -> str:
            nonlocal call_count
            call_count += 1
            return "Sorry"

        with patch("zeus.core.query._run_llm", side_effect=fake_llm):
            result = asyncio.run(engine.query("test question", use_context=False))

        assert call_count == MAX_REFLECT
        assert result.reflection_attempts == MAX_REFLECT - 1
        # Last reply is returned even if still bad
        assert result.assistant_message == "Sorry"

    def test_reflection_prompt_passed_to_llm(self, _patch_externals: AsyncMock) -> None:
        engine = _make_engine()
        prompts_seen: list[str] = []

        async def fake_llm(*, system: str, user_prompt: str, max_tokens: int) -> str:
            prompts_seen.append(user_prompt)
            if len(prompts_seen) == 1:
                return ""
            return "A good answer with enough characters."

        with patch("zeus.core.query._run_llm", side_effect=fake_llm):
            asyncio.run(engine.query("test question", use_context=False))

        assert len(prompts_seen) == 2
        assert "[Attempt 2]" in prompts_seen[1]
        assert "insufficient" in prompts_seen[1]


# ---------------------------------------------------------------------------
# query_stream() reflection with [Retry] sentinel
# ---------------------------------------------------------------------------

class TestQueryStreamReflection:
    def test_stream_no_retry_on_good_reply(self, _patch_externals: AsyncMock) -> None:
        engine = _make_engine()

        async def fake_stream(*, system: str, user_prompt: str, max_tokens: int):
            for chunk in ["Hello ", "world!"]:
                yield chunk

        with patch("zeus.core.query._run_llm_stream", side_effect=fake_stream):
            async def collect() -> list[str]:
                parts = []
                async for chunk in engine.query_stream("hi", "test-session-id", use_context=False):
                    parts.append(chunk)
                return parts

            parts = asyncio.run(collect())

        assert "[Retry]" not in parts
        # Should yield the full reply
        assert "Hello world!" in "".join(parts)

    def test_stream_retry_yields_sentinel(self, _patch_externals: AsyncMock) -> None:
        engine = _make_engine()
        call_count = 0

        async def fake_stream(*, system: str, user_prompt: str, max_tokens: int):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                yield ""
            else:
                for chunk in ["Good ", "answer ", "here."]:
                    yield chunk

        with patch("zeus.core.query._run_llm_stream", side_effect=fake_stream):
            async def collect() -> list[str]:
                parts = []
                async for chunk in engine.query_stream("hi", "test-session-id", use_context=False):
                    parts.append(chunk)
                return parts

            parts = asyncio.run(collect())

        assert "[Retry]" in parts
        combined = "".join(p for p in parts if p != "[Retry]")
        assert "Good answer here." in combined
