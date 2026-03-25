# zeus/core/chat.py — Text chat UI routes (Sprint 7) + Phaos integration surface
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from zeus.memory.search import format_context_block, search_memories

router = APIRouter(tags=["chat"])

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")
ZEUS_LLM = os.getenv("ZEUS_LLM", "").strip().lower()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11435")
OLLAMA_MODEL = os.getenv("ZEUS_OLLAMA_MODEL") or os.getenv(
    "ZEUS_PROD_MODEL", "qwen2.5:7b-instruct-q4_K_M"
)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZEUS_DEV_MODEL = os.getenv("ZEUS_DEV_MODEL") or os.getenv(
    "ZEUS_CLAUDE_MODEL", "claude-sonnet-4-6-20250514"
)
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


def _sessions(request: Request) -> dict[str, list[dict[str, str]]]:
    if not hasattr(request.app.state, "chat_sessions"):
        request.app.state.chat_sessions = {}
    return request.app.state.chat_sessions  # type: ignore[assignment]


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
    t0 = time.monotonic()
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    sessions = _sessions(request)
    sid = body.session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = []

    context = ""
    sources: list[str] = []
    if body.use_context:
        try:
            results = search_memories(
                memory=memory,
                query=body.message,
                user_id="chris",
                top_k=5,
                namespaces=[],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Memory search failed: {e}") from e
        if results:
            context, _ = format_context_block(results, max_tokens=2048)
            for mem in results:
                sources.append(mem.get("metadata", {}).get("source", "unknown"))

    history = sessions[sid][-10:]
    transcript_lines: list[str] = []
    for turn in history:
        transcript_lines.append(f"User: {turn['user']}")
        transcript_lines.append(f"Assistant: {turn['assistant']}")
    transcript_block = "\n".join(transcript_lines)
    system = (
        "You are Zeus, a personal AI assistant for Chris. Be concise and helpful.\n"
        "You are in a text chat — markdown is ok but keep answers readable.\n"
    )
    if context:
        system += f"\n## Personal Context\n{context}\n"

    user_block = transcript_block + ("\n" if transcript_block else "") + f"User: {body.message}\nAssistant:"

    max_out = body.max_tokens or 512
    try:
        reply = await _run_llm(system=system, user_prompt=user_block, max_tokens=max_out)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}") from e

    sessions[sid].append({"user": body.message, "assistant": reply})
    latency_ms = int((time.monotonic() - t0) * 1000)
    return ChatMessageResponse(
        session_id=sid,
        assistant_message=reply,
        context_sources=sources,
        latency_ms=latency_ms,
    )


def _chat_use_claude() -> bool:
    """Honor ZEUS_LLM override, then fall back to dev + API key."""
    if ZEUS_LLM == "ollama":
        return False
    if ZEUS_LLM == "claude":
        return bool(ANTHROPIC_API_KEY)
    return ZEUS_ENV == "dev" and bool(ANTHROPIC_API_KEY)


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

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system}\n\n{user_prompt}",
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120.0)
        r.raise_for_status()
        data = r.json()
        return (data.get("response") or "").strip()
