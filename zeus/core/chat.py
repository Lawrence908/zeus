# zeus/core/chat.py — Text chat UI routes (Sprint 7) + Phaos integration surface
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from zeus.core.query import QueryEngine, _active_model_name
from zeus.core.sessions import Session, SessionManager
from zeus.voice.stt import WhisperSTT

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


class ChatSessionSummary(BaseModel):
    id: str
    created_at: float
    updated_at: float
    turn_count: int
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatSessionsListResponse(BaseModel):
    sessions: list[ChatSessionSummary]


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


@router.get("/chat")
async def chat_page() -> FileResponse:
    path = _STATIC / "chat.html"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="chat.html not found")
    return FileResponse(path, media_type="text/html")


@router.get("/viz")
async def viz_page() -> FileResponse:
    path = _STATIC / "viz" / "viz.html"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="viz.html not found")
    return FileResponse(path, media_type="text/html")


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
    stt = WhisperSTT()

    wav_bytes = await audio.read()
    if not wav_bytes:
        raise HTTPException(status_code=400, detail="empty audio upload")

    async def _one_chunk() -> AsyncIterator[bytes]:
        yield wav_bytes

    transcript = ""
    try:
        async for evt in stt.transcribe(audio_source=_one_chunk()):
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
        raise HTTPException(status_code=422, detail="no transcript produced — audio may be silent or too short")

    result = await engine.query(
        transcript,
        session_id=session_id,
        use_context=use_context,
        max_tokens=max_tokens,
        source="voice_interact",
    )

    return {
        "transcript": transcript,
        "session_id": result.session_id,
        "assistant_message": result.assistant_message,
        "model_used": result.model_used,
        "latency_ms": result.latency_ms,
        "context_sources": result.context_sources,
    }


def _sse_token_event(content: str) -> str:
    return f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"


def _sse_done_event(*, session_id: str, latency_ms: int, model_used: str) -> str:
    payload = {"type": "done", "session_id": session_id, "latency_ms": latency_ms, "model_used": model_used}
    return f"data: {json.dumps(payload)}\n\n"


def _sse_error_event(detail: str) -> str:
    return f"data: {json.dumps({'type': 'error', 'detail': detail})}\n\n"


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
            async for chunk in engine.query_stream(
                body.message,
                session_id_out,
                use_context=body.use_context,
                max_tokens=max_out,
                source="chat",
            ):
                yield _sse_token_event(chunk).encode("utf-8")
            latency_ms = int((time.monotonic() - t0) * 1000)
            yield _sse_done_event(
                session_id=session_id_out,
                latency_ms=latency_ms,
                model_used=_active_model_name(),
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
            metadata=s.metadata,
        )
        for s in recent
    ]
    return ChatSessionsListResponse(sessions=summaries)


@router.get("/chat/sessions/{session_id}", response_model=Session)
async def get_chat_session(session_id: str, request: Request) -> Session:
    sm = _session_manager(request)
    session = await sm.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, request: Request) -> dict[str, bool]:
    sm = _session_manager(request)
    ok = await sm.delete(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}
