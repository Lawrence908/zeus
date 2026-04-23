# zeus/core/chat.py — Text chat UI routes (Sprint 7) + Phaos integration surface
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Any, AsyncIterator, Literal

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("zeus.chat")

# Maximum number of async chat jobs to keep in memory. Oldest are evicted first
# so callers always have recent ones accessible via GET /chat/async/{id}.
_CHAT_JOB_MAX = 100

from zeus.core.query import QueryEngine, _active_model_name
from zeus.core.sessions import Session, SessionManager, effective_session_topic
import httpx

from zeus.voice.stt import WhisperSTT, transcribe_wav_rest

router = APIRouter(tags=["chat"])

_STATIC = Path(__file__).resolve().parent / "static"


class ChatMessageRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=32000)
    max_tokens: int | None = Field(None, ge=64, le=4096)
    use_context: bool = True


class ChatMessageResponse(BaseModel):
    session_id: str
    assistant_message: str
    context_sources: list[str]
    latency_ms: int
    model_used: str
    token_estimate: int
    topic: str | None = None
    aegis_flags: list[str] = Field(default_factory=list)
    tool_calls: list[dict] = Field(default_factory=list)


class ChatAsyncRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=32000)
    max_tokens: int | None = Field(None, ge=64, le=4096)
    use_context: bool = True
    # If set, the final ChatMessageResponse is POSTed to this URL once the
    # background query finishes. Meshtastic bridge uses this so Node-RED never
    # holds an HTTP connection open for long tool-using queries.
    callback_url: str | None = Field(None, max_length=2048)


class ChatAsyncCreatedResponse(BaseModel):
    job_id: str
    status: Literal["queued"]
    session_id: str
    created_at: float


class ChatJob(BaseModel):
    job_id: str
    session_id: str
    status: Literal["queued", "running", "done", "error"]
    created_at: float
    updated_at: float
    callback_url: str | None = None
    callback_status: Literal["pending", "ok", "failed", "skipped"] = "skipped"
    result: ChatMessageResponse | None = None
    error: str | None = None


class ChatSessionSummary(BaseModel):
    id: str
    created_at: float
    updated_at: float
    turn_count: int
    summary: str | None = None
    topic: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatSessionsListResponse(BaseModel):
    sessions: list[ChatSessionSummary]


class ChatMessagesResponse(BaseModel):
    messages: list[dict[str, Any]]


def _session_manager(request: Request) -> SessionManager:
    sm = getattr(request.app.state, "session_manager", None)
    if sm is None:
        raise HTTPException(status_code=503, detail="Session manager not initialized")
    return sm


def _query_engine(request: Request) -> QueryEngine:
    qe = getattr(request.app.state, "query_engine", None)
    if qe is None:
        raise HTTPException(status_code=503, detail="Query engine not initialized")
    return qe


@router.get("/chat", include_in_schema=False)
async def chat_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=301)



@router.post("/chat/message", response_model=ChatMessageResponse)
async def chat_message(body: ChatMessageRequest, request: Request) -> ChatMessageResponse:
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    engine = _query_engine(request)
    max_out = body.max_tokens or 512
    try:
        result = await engine.query(
            body.message,
            body.session_id,
            use_context=body.use_context,
            max_tokens=max_out,
            source="chat",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Query failed: {e}") from e

    return ChatMessageResponse(
        session_id=result.session_id,
        assistant_message=result.assistant_message,
        context_sources=result.context_sources,
        latency_ms=result.latency_ms,
        model_used=result.model_used,
        token_estimate=result.token_estimate,
        topic=result.topic,
        aegis_flags=result.aegis_flags,
        tool_calls=result.tool_calls,
    )

def _chat_jobs(request: Request) -> OrderedDict[str, ChatJob]:
    jobs = getattr(request.app.state, "chat_jobs", None)
    if jobs is None:
        jobs = OrderedDict()
        request.app.state.chat_jobs = jobs
    return jobs


def _record_job(jobs: OrderedDict[str, ChatJob], job: ChatJob) -> None:
    jobs[job.job_id] = job
    jobs.move_to_end(job.job_id)
    while len(jobs) > _CHAT_JOB_MAX:
        jobs.popitem(last=False)


async def _run_chat_job_background(
    *,
    jobs: OrderedDict[str, ChatJob],
    job_id: str,
    engine: QueryEngine,
    message: str,
    session_id: str,
    max_tokens: int,
    use_context: bool,
    callback_url: str | None,
    http_client: Any,
) -> None:
    """Run engine.query() and record the outcome; fire the optional callback."""
    job = jobs.get(job_id)
    if job is None:
        logger.warning("chat_async job %s vanished before run", job_id)
        return
    job.status = "running"
    job.updated_at = time.time()
    try:
        result = await engine.query(
            message,
            session_id=session_id,
            use_context=use_context,
            max_tokens=max_tokens,
            source="chat_async",
        )
    except Exception as exc:
        logger.exception("chat_async job %s failed", job_id)
        job.status = "error"
        job.error = str(exc)
        job.updated_at = time.time()
        # Callback still fires on error so the caller isn't left hanging.
    else:
        job.status = "done"
        job.result = ChatMessageResponse(
            session_id=result.session_id,
            assistant_message=result.assistant_message,
            context_sources=result.context_sources,
            latency_ms=result.latency_ms,
            model_used=result.model_used,
            token_estimate=result.token_estimate,
            topic=result.topic,
            aegis_flags=result.aegis_flags,
            tool_calls=result.tool_calls,
        )
        job.updated_at = time.time()

    if not callback_url:
        return

    # Best-effort callback — one attempt, log the outcome, do not let a bad
    # callback URL wedge the job record.
    import httpx

    payload: dict[str, Any] = {
        "job_id": job_id,
        "status": job.status,
        "session_id": session_id,
    }
    if job.result is not None:
        payload["result"] = job.result.model_dump()
    if job.error is not None:
        payload["error"] = job.error

    try:
        client = http_client if http_client is not None else httpx.AsyncClient()
        r = await client.post(callback_url, json=payload, timeout=10.0)
        r.raise_for_status()
        job.callback_status = "ok"
    except Exception as exc:
        logger.warning("chat_async callback to %s failed: %s", callback_url, exc)
        job.callback_status = "failed"
    finally:
        job.updated_at = time.time()


@router.post("/chat/async", response_model=ChatAsyncCreatedResponse, status_code=202)
async def chat_async(body: ChatAsyncRequest, request: Request) -> ChatAsyncCreatedResponse:
    """Fire-and-forget chat.

    Returns job_id immediately; the model call runs in a background task.
    Clients either poll GET /chat/async/{job_id} or pass a callback_url and
    wait for a POST from Zeus when the job completes. Built for long
    tool-using queries (web_search, etc.) where holding the HTTP connection
    for 30+ seconds is impractical (notably the Meshtastic LoRa bridge).
    """
    engine = _query_engine(request)

    # Create (or reuse) a session so we can return a session_id immediately.
    session = await engine.sessions.get_or_create(
        body.session_id,
        metadata={"source": "chat_async"},
    )
    session_id_out = session.id
    max_out = body.max_tokens or 512
    now = time.time()
    job_id = uuid.uuid4().hex[:12]

    job = ChatJob(
        job_id=job_id,
        session_id=session_id_out,
        status="queued",
        created_at=now,
        updated_at=now,
        callback_url=body.callback_url,
        callback_status="pending" if body.callback_url else "skipped",
    )
    jobs = _chat_jobs(request)
    _record_job(jobs, job)

    http_client = getattr(request.app.state, "http_client", None)
    asyncio.create_task(
        _run_chat_job_background(
            jobs=jobs,
            job_id=job_id,
            engine=engine,
            message=body.message,
            session_id=session_id_out,
            max_tokens=max_out,
            use_context=body.use_context,
            callback_url=body.callback_url,
            http_client=http_client,
        )
    )

    return ChatAsyncCreatedResponse(
        job_id=job_id,
        status="queued",
        session_id=session_id_out,
        created_at=now,
    )


@router.get("/chat/async/{job_id}", response_model=ChatJob)
async def chat_async_status(job_id: str, request: Request) -> ChatJob:
    jobs = _chat_jobs(request)
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Unknown chat job {job_id!r}")
    # Touch LRU order so a recently polled job isn't evicted under load.
    jobs.move_to_end(job_id)
    return job


# ---------------------------------------------------------------------------
# /classify — pre-classify an incoming message so a bridge (Meshtastic, etc.)
# can pick a specific ack ("🔍 searching..." vs "💭 thinking...") and route
# latency-sensitive work appropriately. Uses small_llm_call at tier 1 so PII
# in the user's message never leaves privacy-tier-safe providers.
# ---------------------------------------------------------------------------


class ClassifyRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None  # accepted but not used today; kept for forward-compat


class ChatClassification(BaseModel):
    """Structured output schema; also used as the HTTP response body."""

    intent: Literal["chat", "search", "recall", "write", "compute"]
    estimated_ms: int = Field(..., ge=100, le=300_000)
    tool_hint: str | None = None
    reasoning: str | None = None


_CLASSIFY_SYSTEM = (
    "You classify a single user message for an AI assistant router. "
    "Return JSON only. Intents:\n"
    "- chat: small talk, simple Q&A, or anything you can answer without tools or retrieval (≈2-5s).\n"
    "- search: needs up-to-date web info; the web_search tool will fire (≈10-30s).\n"
    "- recall: asks about the user's own notes, memories, or past conversations (≈3-8s).\n"
    "- write: draft / summarize / rewrite longer content (≈8-20s).\n"
    "- compute: math, conversions, code execution, or clock time (≈1-3s).\n"
    "tool_hint: suggested tool name if obvious (e.g. 'web_search', 'current_time'), "
    "else null. reasoning: one short sentence, no commentary. "
    "Be decisive; do not include fields outside the schema."
)


@router.post("/classify", response_model=ChatClassification)
async def classify_message(body: ClassifyRequest) -> ChatClassification:
    """Lightweight intent / latency classifier.

    Fires one small-LLM call via the tier-1 provider chain. Falls back to a
    safe 'chat' classification on any failure so callers can always proceed.
    """
    from zeus.core.small_llm import small_llm_call

    try:
        result = await small_llm_call(
            system=_CLASSIFY_SYSTEM,
            user=f"Message: {body.message!r}",
            max_tokens=200,
            response_format=ChatClassification,
            min_privacy_tier=1,
            caller="chat.classify",
        )
    except Exception as exc:
        logger.warning("classify failed (will return fallback): %s", exc)
        return ChatClassification(
            intent="chat",
            estimated_ms=3000,
            tool_hint=None,
            reasoning=f"classifier unavailable: {exc!s}",
        )

    parsed = result.parsed
    if isinstance(parsed, ChatClassification):
        return parsed
    # Validation failed across all providers. Return fallback.
    logger.warning(
        "classify returned no parsed result after %d attempts; errors=%s",
        result.attempts,
        result.errors,
    )
    return ChatClassification(
        intent="chat",
        estimated_ms=3000,
        tool_hint=None,
        reasoning="classifier returned unparseable output",
    )


@router.post("/voice/interact")
async def voice_interact(
    request: Request,
    audio: UploadFile = File(...),
    session_id: str | None = Form(default=None),
    use_context: bool = Form(default=True),
    max_tokens: int = Form(default=256),
) -> dict[str, Any]:
    """
    Non-wake-word voice interaction endpoint.

    Accepts a WAV upload + optional session_id, runs STT -> QueryEngine ->
    returns transcript + text response. session_id is threaded through so
    voice turns share history with the text chat session.
    TTS/audio return is intentionally deferred until Voicebox is standardized.
    """
    engine = _query_engine(request)

    wav_bytes = await audio.read()
    if not wav_bytes:
        raise HTTPException(status_code=400, detail="empty audio upload")

    rest_url = os.getenv("WHISPER_REST_URL", "").strip()
    transcript = ""
    rest_err: str | None = None
    try:
        if rest_url:
            try:
                transcript = await transcribe_wav_rest(wav_bytes, base_url=rest_url)
            except (httpx.HTTPError, RuntimeError) as exc:
                rest_err = str(exc)

        if not transcript:
            stt = WhisperSTT()

            async def _one_chunk() -> AsyncIterator[bytes]:
                yield wav_bytes

            async for evt in stt.transcribe(audio_source=_one_chunk(), is_wav=True):
                transcript = str(evt.get("text") or "").strip()
                if evt.get("is_final"):
                    break
    except ConnectionRefusedError:
        raise HTTPException(
            status_code=503,
            detail="WhisperLive STT service is not reachable. Start it with: docker compose up whisper -d",
        )
    except OSError as exc:
        raise HTTPException(status_code=503, detail=f"STT connection failed: {exc}") from exc

    if not transcript:
        hint = (
            "no transcript produced — audio may be silent, VAD-stripped, or STT unreachable. "
            "Ensure whisper runs with --enable_rest and zeus-core has WHISPER_REST_URL; "
            "or speak closer to the mic."
        )
        if rest_err:
            hint = f"{hint} (REST error: {rest_err})"
        raise HTTPException(status_code=422, detail=hint)

    result = await engine.query(
        transcript,
        session_id=session_id,
        use_context=use_context,
        max_tokens=max_tokens,
        source="voice_interact",
    )

    sess = await engine.sessions.get(result.session_id)
    topic = effective_session_topic(sess) if sess else result.topic

    return {
        "transcript": transcript,
        "session_id": result.session_id,
        "assistant_message": result.assistant_message,
        "model_used": result.model_used,
        "latency_ms": result.latency_ms,
        "context_sources": result.context_sources,
        "topic": topic,
        "aegis_flags": result.aegis_flags,
    }


def _sse_token_event(content: str) -> str:
    return f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"


def _sse_done_event(
    *,
    session_id: str,
    latency_ms: int,
    model_used: str,
    topic: str | None = None,
    token_estimate: int | None = None,
) -> str:
    payload: dict[str, Any] = {
        "type": "done",
        "session_id": session_id,
        "latency_ms": latency_ms,
        "model_used": model_used,
    }
    if topic is not None:
        payload["topic"] = topic
    if token_estimate is not None:
        payload["token_estimate"] = token_estimate
    return f"data: {json.dumps(payload)}\n\n"


def _sse_error_event(detail: str) -> str:
    return f"data: {json.dumps({'type': 'error', 'detail': detail})}\n\n"


def _sse_phase_event(detail: str) -> str:
    return f"data: {json.dumps({'type': 'phase', 'detail': detail})}\n\n"


@router.post("/chat/stream")
async def chat_stream(body: ChatMessageRequest, request: Request) -> StreamingResponse:
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    engine = _query_engine(request)
    max_out = body.max_tokens or 512
    session = await engine.sessions.get_or_create(
        body.session_id,
        metadata={"source": "chat"},
    )
    session_id_out = session.id

    async def event_iter() -> AsyncIterator[bytes]:
        t0 = time.monotonic()
        try:
            # Immediate bytes keep reverse proxies (e.g. Cloudflare) from closing idle streams
            # while mem0 / profile work runs before the first model token.
            yield b": stream-open\n\n"
            yield _sse_phase_event("context").encode("utf-8")
            accumulated: list[str] = []
            async for chunk in engine.query_stream(
                body.message,
                session_id_out,
                use_context=body.use_context,
                max_tokens=max_out,
                source="chat",
            ):
                accumulated.append(chunk)
                yield _sse_token_event(chunk).encode("utf-8")
            reply = "".join(accumulated)
            token_estimate = max(len(reply) // 4, 0)
            latency_ms = int((time.monotonic() - t0) * 1000)
            sess = await engine.sessions.get(session_id_out)
            topic = effective_session_topic(sess) if sess else None
            yield _sse_done_event(
                session_id=session_id_out,
                latency_ms=latency_ms,
                model_used=_active_model_name(),
                topic=topic,
                token_estimate=token_estimate,
            ).encode("utf-8")
        except Exception as e:
            yield _sse_error_event(str(e)).encode("utf-8")

    return StreamingResponse(
        event_iter(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/sessions", response_model=ChatSessionsListResponse)
async def list_chat_sessions(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
) -> ChatSessionsListResponse:
    sm = _session_manager(request)
    recent = await sm.list_recent(limit=limit)
    summaries = [
        ChatSessionSummary(
            id=s.id,
            created_at=s.created_at,
            updated_at=s.updated_at,
            turn_count=len(s.turns),
            summary=s.summary,
            topic=effective_session_topic(s),
            metadata=s.metadata,
        )
        for s in recent
    ]
    return ChatSessionsListResponse(sessions=summaries)


@router.post("/chat/sessions", response_model=ChatSessionSummary)
async def create_chat_session(request: Request) -> ChatSessionSummary:
    """Create an empty session (React SPA \"+ New Session\" uses POST here)."""
    sm = _session_manager(request)
    session = await sm.create(metadata={"source": "chat"})
    return ChatSessionSummary(
        id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        turn_count=0,
        summary=None,
        topic="New chat",
        metadata=session.metadata,
    )


@router.get("/chat/sessions/{session_id}/messages", response_model=ChatMessagesResponse)
async def get_chat_session_messages(session_id: str, request: Request) -> ChatMessagesResponse:
    """Return turns as UI messages for session restore."""
    sm = _session_manager(request)
    session = await sm.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    out: list[dict[str, Any]] = []
    for i, turn in enumerate(session.turns):
        ts_ms = int(turn.timestamp * 1000)
        out.append(
            {
                "id": f"{session_id}-u-{i}",
                "role": "user",
                "content": turn.user,
                "timestamp": ts_ms,
                "source": getattr(turn, "source", None) or session.metadata.get("source", "web"),
            }
        )
        out.append(
            {
                "id": f"{session_id}-a-{i}",
                "role": "assistant",
                "content": turn.assistant,
                "timestamp": ts_ms,
                "source": getattr(turn, "source", None) or session.metadata.get("source", "web"),
                "context_sources": turn.context_sources,
            }
        )
    return ChatMessagesResponse(messages=out)


@router.get("/chat/sessions/{session_id}", response_model=Session)
async def get_chat_session(session_id: str, request: Request) -> Session:
    sm = _session_manager(request)
    session = await sm.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    eff = effective_session_topic(session)
    if eff is not None:
        session = session.model_copy(update={"topic": eff})
    return session


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, request: Request) -> dict[str, bool]:
    sm = _session_manager(request)
    ok = await sm.delete(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}
