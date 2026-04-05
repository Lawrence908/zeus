# zeus/core/query.py — Central query pipeline (memories + session + LLM)
from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator

import httpx
from pydantic import BaseModel, Field

from zeus.core.sessions import SessionManager, Turn
from zeus.memory.search import (
    MEMORY_SEARCH_TOP_K,
    format_context_block,
    get_profile_facts,
    search_memories,
)
from zeus.safety.policy_engine import aegis_enabled, evaluate_text

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")
ZEUS_LLM = os.getenv("ZEUS_LLM", "").strip().lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZEUS_DEV_MODEL = os.getenv("ZEUS_DEV_MODEL") or os.getenv(
    "ZEUS_CLAUDE_MODEL", "claude-sonnet-4-6"
)

ZEUS_USER_ID = os.getenv("ZEUS_USER_ID", "chris")

_TIMING_LOG_THRESHOLD_MS = int(os.getenv("ZEUS_TIMING_LOG_THRESHOLD_MS", "250"))


def _log_timing(step: str, elapsed_ms: float) -> None:
    if elapsed_ms < _TIMING_LOG_THRESHOLD_MS:
        return
    import logging

    logging.getLogger("zeus.timing").warning(f"{step} took {elapsed_ms:.0f}ms")


def _ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://localhost:11435").rstrip("/")


def _ollama_model() -> str:
    return os.getenv("ZEUS_OLLAMA_MODEL") or os.getenv(
        "ZEUS_PROD_MODEL", "qwen2.5:7b-instruct"
    )


def _ollama_http_timeout() -> httpx.Timeout:
    """httpx timeout for Ollama /api/chat. Default 15m — GPU queues + embed contention often exceed 120s."""
    raw = os.getenv("ZEUS_OLLAMA_HTTP_TIMEOUT_SEC", "900").strip()
    if raw.lower() in ("0", "none", "unlimited"):
        return httpx.Timeout(connect=60.0, read=None, write=120.0, pool=60.0)
    sec = max(120.0, float(raw))
    return httpx.Timeout(
        connect=min(60.0, sec),
        read=sec,
        write=min(120.0, sec),
        pool=60.0,
    )


def _ollama_model_missing_message(*, detail: str = "") -> str:
    base = (
        f"Ollama 404 for model {_ollama_model()!r} at {_ollama_url()}/api/chat — "
        "ZEUS_OLLAMA_MODEL must match a name from "
        "`docker compose exec ollama ollama list` (Zeus uses the container, not host `ollama list`). "
        "Pull with `docker compose exec ollama ollama pull <name>`."
    )
    return f"{base} {detail}".strip() if detail else base


class QueryResult(BaseModel):
    session_id: str
    assistant_message: str
    context_sources: list[str]
    latency_ms: int
    model_used: str
    token_estimate: int
    topic: str | None = None
    aegis_flags: list[str] = Field(default_factory=list)


def _chat_use_claude() -> bool:
    if ZEUS_LLM == "ollama":
        return False
    if ZEUS_LLM == "claude":
        return bool(ANTHROPIC_API_KEY)
    return ZEUS_ENV == "dev" and bool(ANTHROPIC_API_KEY)


def _active_model_name() -> str:
    return ZEUS_DEV_MODEL if _chat_use_claude() else _ollama_model()


async def _run_llm(*, system: str, user_prompt: str, max_tokens: int) -> str:
    if _chat_use_claude():
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model=ZEUS_DEV_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        block = msg.content[0]
        if block.type != "text":
            return ""
        return block.text

    base = _ollama_url()
    model = _ollama_model()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{base}/api/chat", json=payload, timeout=_ollama_http_timeout())
        if r.status_code == 404:
            body = (r.text or "")[:300]
            raise RuntimeError(_ollama_model_missing_message(detail=body))
        r.raise_for_status()
        data = r.json()
        msg = data.get("message") or {}
        return str(msg.get("content") or "").strip()


async def _run_llm_stream(
    *,
    system: str,
    user_prompt: str,
    max_tokens: int,
) -> AsyncIterator[str]:
    if _chat_use_claude():
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        stream = await client.messages.create(
            model=ZEUS_DEV_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            stream=True,
        )
        async for event in stream:
            et = getattr(event, "type", None)
            et_str = et.value if hasattr(et, "value") else et
            if et_str != "content_block_delta":
                continue
            delta = event.delta
            dt = getattr(delta, "type", None)
            dt_str = dt.value if hasattr(dt, "value") else dt
            if dt_str != "text_delta":
                continue
            text = getattr(delta, "text", None) or ""
            if text:
                yield text
        return

    base = _ollama_url()
    model = _ollama_model()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        "stream": True,
        "options": {"num_predict": max_tokens},
    }
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{base}/api/chat",
            json=payload,
            timeout=_ollama_http_timeout(),
        ) as r:
            if r.status_code == 404:
                body = (await r.aread()).decode("utf-8", errors="replace")[:300]
                raise RuntimeError(_ollama_model_missing_message(detail=body))
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = data.get("message") or {}
                piece = msg.get("content")
                if piece:
                    yield str(piece)
                if data.get("done"):
                    break


def _build_system_prompt(
    *,
    profile_section: str,
    memory_section: str,
    conversation_section: str,
) -> str:
    conv = conversation_section.strip() if conversation_section.strip() else "(No prior turns in this session.)"
    mem = memory_section.strip() if memory_section.strip() else "(No retrieved memories for this query.)"
    return (
        "You are Zeus, a personal AI assistant for Chris. You have access to Chris's "
        "personal knowledge base and conversation history.\n\n"
        f"## Profile\n{profile_section}\n\n"
        f"## Relevant Context\n{mem}\n\n"
        f"## Conversation\n{conv}\n\n"
        "Be concise, direct, and helpful. Use markdown when it aids clarity.\n"
        "If you don't know something, say so — don't fabricate."
    )


class QueryEngine:
    def __init__(self, memory: object, session_manager: SessionManager) -> None:
        self.memory = memory
        self.sessions = session_manager

    async def query(
        self,
        message: str,
        session_id: str | None = None,
        *,
        use_context: bool = True,
        max_tokens: int = 512,
        stream: bool = False,
        source: str = "chat",
    ) -> QueryResult:
        _ = stream
        t0 = time.monotonic()
        t = t0
        session = await self.sessions.get_or_create(
            session_id,
            metadata={"source": source},
        )
        _log_timing("sessions.get_or_create", (time.monotonic() - t) * 1000)
        t = time.monotonic()
        sid = session.id

        memory_section = ""
        sources: list[str] = []
        if use_context:
            t_search = time.monotonic()
            results = await asyncio.to_thread(
                search_memories,
                memory=self.memory,
                query=message,
                user_id=ZEUS_USER_ID,
                top_k=MEMORY_SEARCH_TOP_K,
                namespaces=[],
            )
            _log_timing("mem0.search_memories", (time.monotonic() - t_search) * 1000)
            if results:
                t_fmt = time.monotonic()
                memory_section, _ = format_context_block(results, max_tokens=2048)
                _log_timing("format_context_block", (time.monotonic() - t_fmt) * 1000)
                for mem in results:
                    sources.append(mem.get("metadata", {}).get("source", "unknown"))

        t_prof = time.monotonic()
        facts = await asyncio.to_thread(
            get_profile_facts, memory=self.memory, user_id=ZEUS_USER_ID, top_k=8
        )
        _log_timing("get_profile_facts", (time.monotonic() - t_prof) * 1000)
        if facts:
            profile_section = "\n".join(f"- {f}" for f in facts[:5])
        else:
            profile_section = "No profile facts loaded yet. Run iris ingest if needed."

        t_conv = time.monotonic()
        conversation_section = await self.sessions.get_context_window(
            sid,
            max_turns=10,
            max_tokens=4096,
        )
        _log_timing("sessions.get_context_window", (time.monotonic() - t_conv) * 1000)
        system = _build_system_prompt(
            profile_section=profile_section,
            memory_section=memory_section,
            conversation_section=conversation_section,
        )
        user_prompt = f"User: {message}\nAssistant:"
        t_llm = time.monotonic()
        reply = await _run_llm(system=system, user_prompt=user_prompt, max_tokens=max_tokens)
        _log_timing("llm.call", (time.monotonic() - t_llm) * 1000)
        aegis_flags: list[str] = []
        if aegis_enabled():
            outcome = evaluate_text(reply, policy_name=None)
            aegis_flags = list(outcome.flags)
            if outcome.status == "rejected":
                reply = outcome.message or "This response was blocked by safety policy."
            else:
                reply = outcome.text
        latency_ms = int((time.monotonic() - t0) * 1000)
        model_used = _active_model_name()
        token_estimate = max(len(reply) // 4, 0)

        t_store = time.monotonic()
        turn = Turn(
            user=message,
            assistant=reply,
            timestamp=time.time(),
            context_sources=sources,
            latency_ms=latency_ms,
        )
        session_after = await self.sessions.append_turn(sid, turn)
        _log_timing("sessions.append_turn", (time.monotonic() - t_store) * 1000)

        return QueryResult(
            session_id=sid,
            assistant_message=reply,
            context_sources=sources,
            latency_ms=latency_ms,
            model_used=model_used,
            token_estimate=token_estimate,
            topic=session_after.topic,
            aegis_flags=aegis_flags,
        )

    async def query_stream(
        self,
        message: str,
        session_id: str,
        *,
        use_context: bool = True,
        max_tokens: int = 512,
        source: str = "chat",
    ) -> AsyncIterator[str]:
        _ = source
        t0 = time.monotonic()
        t = t0
        session = await self.sessions.get(session_id)
        if session is None:
            raise KeyError(f"Unknown session: {session_id}")
        _log_timing("sessions.get", (time.monotonic() - t) * 1000)
        sid = session.id

        memory_section = ""
        sources: list[str] = []
        if use_context:
            t_search = time.monotonic()
            results = await asyncio.to_thread(
                search_memories,
                memory=self.memory,
                query=message,
                user_id=ZEUS_USER_ID,
                top_k=MEMORY_SEARCH_TOP_K,
                namespaces=[],
            )
            _log_timing("mem0.search_memories", (time.monotonic() - t_search) * 1000)
            if results:
                t_fmt = time.monotonic()
                memory_section, _ = format_context_block(results, max_tokens=2048)
                _log_timing("format_context_block", (time.monotonic() - t_fmt) * 1000)
                for mem in results:
                    sources.append(mem.get("metadata", {}).get("source", "unknown"))

        t_prof = time.monotonic()
        facts = await asyncio.to_thread(
            get_profile_facts, memory=self.memory, user_id=ZEUS_USER_ID, top_k=8
        )
        _log_timing("get_profile_facts", (time.monotonic() - t_prof) * 1000)
        if facts:
            profile_section = "\n".join(f"- {f}" for f in facts[:5])
        else:
            profile_section = "No profile facts loaded yet. Run iris ingest if needed."

        t_conv = time.monotonic()
        conversation_section = await self.sessions.get_context_window(
            sid,
            max_turns=10,
            max_tokens=4096,
        )
        _log_timing("sessions.get_context_window", (time.monotonic() - t_conv) * 1000)
        system = _build_system_prompt(
            profile_section=profile_section,
            memory_section=memory_section,
            conversation_section=conversation_section,
        )
        user_prompt = f"User: {message}\nAssistant:"

        t_llm = time.monotonic()
        parts: list[str] = []
        async for chunk in _run_llm_stream(
            system=system,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
        ):
            parts.append(chunk)
            if not aegis_enabled():
                yield chunk

        _log_timing("llm.stream_total", (time.monotonic() - t_llm) * 1000)
        reply = "".join(parts)
        if aegis_enabled():
            outcome = evaluate_text(reply, policy_name=None)
            if outcome.status == "rejected":
                reply = outcome.message or "This response was blocked by safety policy."
            else:
                reply = outcome.text
            yield reply
        latency_ms = int((time.monotonic() - t0) * 1000)
        turn = Turn(
            user=message,
            assistant=reply,
            timestamp=time.time(),
            context_sources=sources,
            latency_ms=latency_ms,
        )
        await self.sessions.append_turn(sid, turn)
