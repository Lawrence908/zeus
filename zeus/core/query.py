# zeus/core/query.py — Central query pipeline (memories + session + LLM)
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger("zeus.query")

MAX_REFLECT = 3
_REFLECT_BACKOFF = [0.5, 1.0]  # seconds after attempt 1, 2

_FAILED_REPLY_RE = re.compile(
    r"^(sorry|i (can't|cannot)|i don't know|i'm unable)", re.IGNORECASE
)

from zeus.core.prompts import render as render_prompt
from zeus.core.sessions import SessionManager, Turn
from zeus.core.tools.adapters import (
    parse_anthropic_message,
    parse_ollama_message,
    tools_to_anthropic,
    tools_to_ollama,
)
from zeus.core.tools.base import ToolCall, ToolSpec
from zeus.memory.search import (
    KNOWLEDGE_SEARCH_TOP_K,
    MEMORY_SEARCH_TOP_K,
    REFERENCE_SEARCH_TOP_K,
    format_context_block,
    get_profile_facts,
    search_knowledge,
    search_memories,
    search_reference,
)
from zeus.safety.policy_engine import aegis_enabled, evaluate_text

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")
ZEUS_LLM = os.getenv("ZEUS_LLM", "").strip().lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZEUS_DEV_MODEL = os.getenv("ZEUS_DEV_MODEL") or os.getenv(
    "ZEUS_CLAUDE_MODEL", "claude-sonnet-4-6"
)

ZEUS_USER_ID = os.getenv("ZEUS_USER_ID", "user")

_TIMING_LOG_THRESHOLD_MS = int(os.getenv("ZEUS_TIMING_LOG_THRESHOLD_MS", "250"))


def _llm_context_budget_tokens() -> int:
    """
    Single heuristic token budget for memory retrieval + session conversation blocks.
    Split ⅓ memories, ⅔ conversation (then summary vs recent turns inside the session).
    Default 6144 ≈ prior 2048 + 4096. Tune with hardware / model context.
    """
    raw = os.getenv("ZEUS_CONTEXT_MAX_TOKENS", "6144").strip()
    return max(1536, int(raw))


def _log_timing(step: str, elapsed_ms: float) -> None:
    if elapsed_ms < _TIMING_LOG_THRESHOLD_MS:
        return
    import logging

    logging.getLogger("zeus.timing").warning(f"{step} took {elapsed_ms:.0f}ms")


def _ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://localhost:11435").rstrip("/")


# Mutable at runtime via POST /models/active — defaults from env vars.
_active_ollama_model: str | None = None


def _ollama_model() -> str:
    if _active_ollama_model:
        return _active_ollama_model
    return os.getenv("ZEUS_OLLAMA_MODEL") or os.getenv(
        "ZEUS_PROD_MODEL", "qwen2.5:7b-instruct"
    )


def set_ollama_model(model: str) -> None:
    """Switch the active Ollama model at runtime (no restart needed)."""
    global _active_ollama_model
    _active_ollama_model = model.strip() if model.strip() else None


def _ollama_http_timeout() -> httpx.Timeout:
    """httpx timeout for Ollama /api/chat. Default 30m for long summarization jobs."""
    raw = os.getenv("ZEUS_OLLAMA_HTTP_TIMEOUT_SEC", "1800").strip()
    if raw.lower() in ("0", "none", "unlimited"):
        return httpx.Timeout(connect=60.0, read=None, write=120.0, pool=60.0)
    try:
        sec = max(120.0, float(raw))
    except (TypeError, ValueError):
        sec = 900.0
    return httpx.Timeout(
        connect=min(60.0, sec),
        read=sec,
        write=min(120.0, sec),
        pool=60.0,
    )


def _ollama_num_ctx() -> int | None:
    """Per-request `options.num_ctx` for the chat path.

    Ollama's default ctx is 4096 — too tight when ZEUS_TOOLS_ENABLED=1 stuffs
    10+ tool schemas into the system prompt (typical: 6k-7k tokens). 8192 fits
    comfortably and is well within Qwen2.5-7B's native 32k. Set to 0 / empty
    to fall back to the model's default.
    """
    raw = os.getenv("ZEUS_OLLAMA_NUM_CTX", "8192").strip()
    if not raw or raw == "0":
        return None
    try:
        return max(2048, int(raw))
    except (TypeError, ValueError):
        return 8192


def _ollama_options(*, max_tokens: int, **extra: Any) -> dict[str, Any]:
    """Build the Ollama `options` block. Caller adds anything model-specific."""
    opts: dict[str, Any] = {"num_predict": max_tokens}
    nc = _ollama_num_ctx()
    if nc is not None:
        opts["num_ctx"] = nc
    opts.update(extra)
    return opts


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
    reflection_attempts: int = 0
    aegis_flags: list[str] = Field(default_factory=list)
    tool_calls: list[dict] = Field(default_factory=list)


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
        "options": _ollama_options(max_tokens=max_tokens),
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


async def _run_llm_with_tools(
    *,
    system: str,
    messages: list[dict],
    tools: list[ToolSpec],
    max_tokens: int,
    turn_idx: int,
) -> tuple[str, list[ToolCall], str]:
    """Single tool-aware round-trip. Sibling to _run_llm; caller drives the loop.

    Returns (text, tool_calls, stop_reason). `messages` is the full conversation
    so far (user turn, any prior assistant turns with tool_use, and tool_result
    follow-ups). `turn_idx` is the loop iteration — used only to synthesise
    unique call_ids on the Ollama path (Ollama has no native tool_use_id).
    """
    if _chat_use_claude():
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model=ZEUS_DEV_MODEL,
            max_tokens=max_tokens,
            system=system,
            tools=tools_to_anthropic(tools),
            messages=messages,
        )
        return parse_anthropic_message(msg)

    base = _ollama_url()
    model = _ollama_model()
    # Ollama wants the system prompt inside the messages array.
    ollama_messages: list[dict] = [{"role": "system", "content": system}, *messages]
    payload = {
        "model": model,
        "messages": ollama_messages,
        "tools": tools_to_ollama(tools),
        "stream": False,
        # Qwen2.5-7B Q4_K_M is unreliable above ~0.3 on tool routing (schema
        # drift, argument fabrication). See zeus/docs/tool-use-spec.md.
        "options": _ollama_options(max_tokens=max_tokens, temperature=0.2),
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/api/chat", json=payload, timeout=_ollama_http_timeout()
        )
        if r.status_code == 404:
            body = (r.text or "")[:300]
            raise RuntimeError(_ollama_model_missing_message(detail=body))
        r.raise_for_status()
        return parse_ollama_message(r.json(), turn_idx=turn_idx)


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
        "options": _ollama_options(max_tokens=max_tokens),
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


# Sub-budget split within the retrieval third of the context window.
# Phase 2 (LAB-NEW-C): reference layer is live; 10% of retrieval budget is
# carved out of knowledge for kiwix + NOMAD snippets.
_RETRIEVAL_SPLIT = {
    "profile": 0.20,
    "memory": 0.25,
    "knowledge": 0.45,
    "reference": 0.10,
}


async def _collect_retrieval_context(
    *,
    message: str,
    retrieval_budget: int,
    use_context: bool,
) -> tuple[str, str, str, str, list[str]]:
    """Fetch profile + memory + knowledge in parallel; format each as a labelled block.

    Returns (profile_section, memory_section, knowledge_section, reference_section, sources).
    Reference is a Phase 2 placeholder and always empty here.
    """
    prof_budget = max(128, int(retrieval_budget * _RETRIEVAL_SPLIT["profile"]))
    mem_budget = max(128, int(retrieval_budget * _RETRIEVAL_SPLIT["memory"]))
    know_budget = max(256, int(retrieval_budget * _RETRIEVAL_SPLIT["knowledge"]))
    ref_budget = max(128, int(retrieval_budget * _RETRIEVAL_SPLIT["reference"]))

    async def _mem_task() -> list[dict]:
        if not use_context:
            return []
        return await asyncio.to_thread(
            search_memories,
            query=message,
            user_id=ZEUS_USER_ID,
            top_k=MEMORY_SEARCH_TOP_K,
            namespaces=[],
        )

    async def _know_task() -> list[dict]:
        if not use_context:
            return []
        return await asyncio.to_thread(
            search_knowledge,
            query=message,
            user_id=ZEUS_USER_ID,
            top_k=KNOWLEDGE_SEARCH_TOP_K,
        )

    async def _prof_task() -> list[str]:
        if not use_context:
            return []
        return await asyncio.to_thread(
            get_profile_facts, user_id=ZEUS_USER_ID, top_k=8
        )

    async def _ref_task() -> list[dict]:
        if not use_context:
            return []
        try:
            return await search_reference(message, top_k=REFERENCE_SEARCH_TOP_K)
        except Exception as exc:
            logger.warning("reference search failed: %s", exc)
            return []

    t_retrieve = time.monotonic()
    facts, mem_results, know_results, ref_results = await asyncio.gather(
        _prof_task(), _mem_task(), _know_task(), _ref_task()
    )
    _log_timing("retrieval.parallel", (time.monotonic() - t_retrieve) * 1000)

    if facts:
        profile_section = "\n".join(f"- {f}" for f in facts[:5])
    else:
        profile_section = "No profile facts loaded yet. Run iris ingest if needed."
    # Crude profile char cap to stay under sub-budget (~4 chars/token).
    prof_char_cap = prof_budget * 4
    if len(profile_section) > prof_char_cap:
        profile_section = profile_section[:prof_char_cap].rstrip() + "\n…"

    memory_section = ""
    sources: list[str] = []
    if mem_results:
        memory_section, _ = format_context_block(mem_results, max_tokens=mem_budget)
        for mem in mem_results:
            md = mem.get("metadata", {}) or {}
            label = md.get("source_id") or md.get("source") or "unknown"
            sources.append(f"memory:{label}")

    knowledge_section = ""
    if know_results:
        knowledge_section, _ = format_context_block(
            know_results, max_tokens=know_budget
        )
        for hit in know_results:
            md = hit.get("metadata", {}) or {}
            label = md.get("file") or md.get("source") or "knowledge"
            sources.append(f"knowledge:{label}")

    reference_section = ""
    if ref_results:
        reference_section, _ = format_context_block(
            ref_results, max_tokens=ref_budget
        )
        for hit in ref_results:
            md = hit.get("metadata", {}) or {}
            label = md.get("title") or md.get("source") or "reference"
            sources.append(f"reference:{md.get('source', 'unknown')}:{label}")

    return profile_section, memory_section, knowledge_section, reference_section, sources


def _build_system_prompt(
    *,
    profile_section: str,
    memory_section: str,
    conversation_section: str,
    knowledge_section: str = "",
    reference_section: str = "",
    tools_section: str = "",
) -> str:
    """Render zeus/core/prompts/chat_system.md with the current runtime context.

    Template lives in a .md file so it can be edited without touching Python.
    Set ZEUS_PROMPT_RELOAD=1 to re-read on every call during iteration.
    """
    return render_prompt(
        "chat_system",
        model_name=_active_model_name(),
        provider="Anthropic Claude" if _chat_use_claude() else "Ollama (local)",
        profile_section=profile_section.strip() or "(No profile facts loaded yet.)",
        memory_section=memory_section.strip() or "(No retrieved memories for this query.)",
        knowledge_section=knowledge_section.strip() or "(No knowledge hits for this query.)",
        reference_section=reference_section.strip() or "(No reference hits — kiwix/NOMAD returned nothing or are unreachable.)",
        conversation_section=conversation_section.strip() or "(No prior turns in this session.)",
        tools_section=tools_section.strip() or "(No tools available for this turn.)",
    )


def _build_tools_section() -> str:
    """Format the registered-tools list for the system prompt when tools are enabled.

    Returns an empty string when tools are disabled or no tools are registered
    so the chat_system.md template falls back to "(No tools available for this turn.)".
    """
    from zeus.core.tools import registry as tool_registry
    from zeus.core.tools import tools_enabled

    if not (tools_enabled() and tool_registry.available()):
        return ""
    lines: list[str] = []
    for spec in tool_registry.list_specs():
        # First sentence of the description is usually the most load-bearing —
        # keep the whole thing for Qwen since it needs the forceful "you must
        # call this" language that lives in the full description.
        lines.append(f"- `{spec.name}` — {spec.description}")
    return "\n".join(lines)


def _is_empty_or_failed_reply(reply: str) -> bool:
    """True if the reply is empty, too short, or a known refusal pattern."""
    stripped = reply.strip()
    if not stripped or len(stripped) < 10:
        return True
    return bool(_FAILED_REPLY_RE.match(stripped))


def _build_reflection_prompt(original: str, failed_reply: str, attempt: int) -> str:
    """Prepend a reflection instruction to the original query for retry."""
    truncated = failed_reply[:100]
    return (
        f"[Attempt {attempt}] Your previous response was insufficient: "
        f"'{truncated}'. Rephrase and try again.\n\n{original}"
    )


class QueryEngine:
    def __init__(self, session_manager: SessionManager, memory: object | None = None) -> None:
        # `memory` is accepted for backwards compatibility with callers still
        # passing the old mem0 client; it's unused — MemoryStore is a singleton
        # accessed via get_memory_store() inside the retrieval helpers.
        self.sessions = session_manager
        self.memory = memory

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

        budget = _llm_context_budget_tokens()
        memory_token_budget = budget // 3
        conversation_token_budget = budget - memory_token_budget

        (
            profile_section,
            memory_section,
            knowledge_section,
            reference_section,
            sources,
        ) = await _collect_retrieval_context(
            message=message,
            retrieval_budget=memory_token_budget,
            use_context=use_context,
        )

        t_conv = time.monotonic()
        conversation_section = await self.sessions.get_context_window(
            sid,
            max_tokens=conversation_token_budget,
        )
        _log_timing("sessions.get_context_window", (time.monotonic() - t_conv) * 1000)
        system = _build_system_prompt(
            profile_section=profile_section,
            memory_section=memory_section,
            conversation_section=conversation_section,
            knowledge_section=knowledge_section,
            reference_section=reference_section,
            tools_section=_build_tools_section(),
        )
        user_prompt = f"User: {message}\nAssistant:"
        t_llm = time.monotonic()
        reflection_attempts = 0
        current_prompt = user_prompt

        # Tool-use path (ZEUS_TOOLS_ENABLED=1). Skips the reflection loop when
        # any tool fired -- a tool-informed reply is treated as authoritative.
        from zeus.core.tools import registry as tool_registry
        from zeus.core.tools import tools_enabled, tools_max_calls

        tool_calls_out: list[dict] = []
        skip_reflection = False
        if tools_enabled() and tool_registry.available():
            from zeus.core.tools.loop import run_tool_loop

            loop_result = await run_tool_loop(
                system=system,
                user_prompt=current_prompt,
                tools=tool_registry.list_specs(),
                max_tokens=max_tokens,
                max_calls=tools_max_calls(),
                use_claude=_chat_use_claude(),
            )
            reply = loop_result.reply
            if loop_result.tool_calls:
                skip_reflection = True
                sources.extend(f"tool:{c.name}" for c in loop_result.tool_calls)
                tool_calls_out = [
                    {"name": c.name, "arguments": c.arguments}
                    for c in loop_result.tool_calls
                ]
        else:
            reply = await _run_llm(system=system, user_prompt=current_prompt, max_tokens=max_tokens)

        if not skip_reflection:
            for attempt in range(2, MAX_REFLECT + 1):
                if not _is_empty_or_failed_reply(reply):
                    break
                reflection_attempts += 1
                backoff = _REFLECT_BACKOFF[attempt - 2] if attempt - 2 < len(_REFLECT_BACKOFF) else _REFLECT_BACKOFF[-1]
                logger.info(
                    "Reflection attempt %d/%d (backoff %.1fs) — reply was: %r",
                    attempt, MAX_REFLECT, backoff, reply[:100],
                )
                await asyncio.sleep(backoff)
                current_prompt = _build_reflection_prompt(user_prompt, reply, attempt)
                reply = await _run_llm(system=system, user_prompt=current_prompt, max_tokens=max_tokens)
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
            reflection_attempts=reflection_attempts,
            aegis_flags=aegis_flags,
            tool_calls=tool_calls_out,
        )

    async def query_stream(
        self,
        message: str,
        session_id: str,
        *,
        use_context: bool = True,
        max_tokens: int = 512,
        source: str = "chat",
        tool_calls_out: list[dict] | None = None,
    ) -> AsyncIterator[str]:
        """Stream a reply chunk-by-chunk.

        When ZEUS_TOOLS_ENABLED is on and any tool is registered, the tool loop
        runs end-to-end before any text is yielded (the loop is inherently
        multi-round). The final assistant reply is then emitted as a single
        chunk. Tool-call descriptions are appended to ``tool_calls_out`` so
        the caller can surface them on the done SSE event.
        """
        _ = source
        t0 = time.monotonic()
        t = t0
        session = await self.sessions.get(session_id)
        if session is None:
            raise KeyError(f"Unknown session: {session_id}")
        _log_timing("sessions.get", (time.monotonic() - t) * 1000)
        sid = session.id

        budget = _llm_context_budget_tokens()
        memory_token_budget = budget // 3
        conversation_token_budget = budget - memory_token_budget

        (
            profile_section,
            memory_section,
            knowledge_section,
            reference_section,
            sources,
        ) = await _collect_retrieval_context(
            message=message,
            retrieval_budget=memory_token_budget,
            use_context=use_context,
        )

        t_conv = time.monotonic()
        conversation_section = await self.sessions.get_context_window(
            sid,
            max_tokens=conversation_token_budget,
        )
        _log_timing("sessions.get_context_window", (time.monotonic() - t_conv) * 1000)
        system = _build_system_prompt(
            profile_section=profile_section,
            memory_section=memory_section,
            conversation_section=conversation_section,
            knowledge_section=knowledge_section,
            reference_section=reference_section,
            tools_section=_build_tools_section(),
        )
        user_prompt = f"User: {message}\nAssistant:"

        t_llm = time.monotonic()
        current_prompt = user_prompt
        aegis_on = aegis_enabled()

        # Tool-aware path: if tools are enabled and any are registered, run the
        # tool loop to completion (it requires multiple round trips that can't
        # be naturally streamed) and yield the assembled reply as one chunk.
        # The model's final turn is what the user sees; tool calls flow back
        # to the caller through tool_calls_out so the SSE done event can carry
        # them and the Chat UI can render the collapsible tool-call card.
        from zeus.core.tools import registry as tool_registry
        from zeus.core.tools import tools_enabled, tools_max_calls

        if tools_enabled() and tool_registry.available():
            from zeus.core.tools.loop import run_tool_loop

            loop_result = await run_tool_loop(
                system=system,
                user_prompt=current_prompt,
                tools=tool_registry.list_specs(),
                max_tokens=max_tokens,
                max_calls=tools_max_calls(),
                use_claude=_chat_use_claude(),
            )
            reply = loop_result.reply
            if loop_result.tool_calls and tool_calls_out is not None:
                tool_calls_out.extend(
                    {"name": c.name, "arguments": c.arguments}
                    for c in loop_result.tool_calls
                )
                sources.extend(f"tool:{c.name}" for c in loop_result.tool_calls)
            if aegis_on:
                outcome = evaluate_text(reply, policy_name=None)
                if outcome.status == "rejected":
                    reply = outcome.message or "This response was blocked by safety policy."
                else:
                    reply = outcome.text
            yield reply
            _log_timing("llm.stream_total", (time.monotonic() - t_llm) * 1000)
            latency_ms = int((time.monotonic() - t0) * 1000)
            turn = Turn(
                user=message,
                assistant=reply,
                timestamp=time.time(),
                context_sources=sources,
                latency_ms=latency_ms,
            )
            await self.sessions.append_turn(sid, turn)
            return

        # Stream incrementally when Aegis is disabled; buffer when enabled so
        # we can evaluate the full reply before emitting.
        parts: list[str] = []
        async for chunk in _run_llm_stream(
            system=system,
            user_prompt=current_prompt,
            max_tokens=max_tokens,
        ):
            parts.append(chunk)
            if not aegis_on:
                yield chunk
        reply = "".join(parts)
        streamed_live = not aegis_on

        # Reflection loop for streaming
        for attempt in range(2, MAX_REFLECT + 1):
            if not _is_empty_or_failed_reply(reply):
                break
            backoff = _REFLECT_BACKOFF[attempt - 2] if attempt - 2 < len(_REFLECT_BACKOFF) else _REFLECT_BACKOFF[-1]
            logger.info(
                "Stream reflection attempt %d/%d (backoff %.1fs) — reply was: %r",
                attempt, MAX_REFLECT, backoff, reply[:100],
            )
            yield "[Retry]"
            await asyncio.sleep(backoff)
            current_prompt = _build_reflection_prompt(user_prompt, reply, attempt)
            parts = []
            # Retry streams are buffered: we need the full text to re-check
            # _is_empty_or_failed_reply, and the reply is emitted once below.
            async for chunk in _run_llm_stream(
                system=system,
                user_prompt=current_prompt,
                max_tokens=max_tokens,
            ):
                parts.append(chunk)
            reply = "".join(parts)
            streamed_live = False

        _log_timing("llm.stream_total", (time.monotonic() - t_llm) * 1000)
        # Aegis on final reply only
        if aegis_on:
            outcome = evaluate_text(reply, policy_name=None)
            if outcome.status == "rejected":
                reply = outcome.message or "This response was blocked by safety policy."
            else:
                reply = outcome.text
            yield reply
        elif not streamed_live:
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
