# zeus/core/sessions.py — Multi-turn session storage and rolling summaries
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


def topic_from_first_message(message: str, max_len: int = 56) -> str:
    """Short single-line label for session lists (first user message)."""
    t = " ".join((message or "").split())
    if not t:
        return "New chat"
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def effective_session_topic(session: Session) -> str | None:
    """Stored topic, or a label derived from the first user turn (legacy sessions)."""
    if session.topic and session.topic.strip():
        return session.topic.strip()
    if session.turns:
        return topic_from_first_message(session.turns[0].user)
    return None


class Turn(BaseModel):
    user: str
    assistant: str
    timestamp: float
    context_sources: list[str] = Field(default_factory=list)
    latency_ms: int = 0


class Session(BaseModel):
    id: str
    created_at: float
    updated_at: float
    turns: list[Turn] = Field(default_factory=list)
    summary: str | None = None
    topic: str | None = Field(
        default=None,
        description="Short label from the first user message for UI lists.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


TURN_SUMMARY_THRESHOLD = 20
KEEP_RECENT_TURNS = 10

LlmFn = Callable[..., Awaitable[str]]


def _truncate_to_token_budget(text: str, max_tokens: int) -> str:
    if max_tokens <= 0 or not text:
        return ""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[truncated]"


@runtime_checkable
class SessionStorage(Protocol):
    async def save(self, session: Session) -> None: ...

    async def load(self, session_id: str) -> Session | None: ...

    async def list_recent(self, limit: int) -> list[Session]: ...

    async def delete(self, session_id: str) -> bool: ...


class InMemoryStorage:
    def __init__(self) -> None:
        self._by_id: dict[str, Session] = {}

    async def save(self, session: Session) -> None:
        self._by_id[session.id] = session.model_copy(deep=True)

    async def load(self, session_id: str) -> Session | None:
        s = self._by_id.get(session_id)
        return s.model_copy(deep=True) if s else None

    async def list_recent(self, limit: int) -> list[Session]:
        items = sorted(self._by_id.values(), key=lambda s: s.updated_at, reverse=True)
        return [s.model_copy(deep=True) for s in items[:limit]]

    async def delete(self, session_id: str) -> bool:
        return self._by_id.pop(session_id, None) is not None


class SessionManager:
    def __init__(
        self,
        storage: SessionStorage,
        *,
        llm_fn: LlmFn | None = None,
    ) -> None:
        self._storage = storage
        self._llm_fn = llm_fn

    async def create(self, metadata: dict[str, Any] | None = None) -> Session:
        now = time.time()
        sid = str(uuid.uuid4())
        session = Session(
            id=sid,
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )
        await self._storage.save(session)
        return session

    async def get_or_create(
        self,
        session_id: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> Session:
        if session_id is None:
            return await self.create(metadata)
        existing = await self.get(session_id)
        if existing is not None:
            return existing
        now = time.time()
        session = Session(
            id=session_id,
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )
        await self._storage.save(session)
        return session

    async def get(self, session_id: str) -> Session | None:
        return await self._storage.load(session_id)

    async def append_turn(self, session_id: str, turn: Turn) -> Session:
        session = await self._storage.load(session_id)
        if session is None:
            raise KeyError(f"Unknown session: {session_id}")
        session.turns.append(turn)
        if not (session.topic and session.topic.strip()):
            first_user = session.turns[0].user if session.turns else ""
            session.topic = topic_from_first_message(first_user)
        session.updated_at = time.time()
        await self._storage.save(session)
        if len(session.turns) > TURN_SUMMARY_THRESHOLD:
            await self.generate_summary(session_id)
            session = await self._storage.load(session_id)
            if session is None:
                raise KeyError(f"Unknown session after summary: {session_id}")
        return session

    async def get_context_window(
        self,
        session_id: str,
        *,
        max_turns: int = 10,
        max_tokens: int = 4096,
    ) -> str:
        session = await self._storage.load(session_id)
        if session is None:
            return ""

        summary_token_budget = max_tokens // 3
        turns_token_budget = max_tokens - summary_token_budget

        parts: list[str] = []
        if session.summary:
            summary_block = _truncate_to_token_budget(session.summary, summary_token_budget)
            if summary_block.strip():
                parts.append(f"## Earlier conversation (summary)\n{summary_block.strip()}")

        recent = session.turns[-max_turns:]
        turn_blocks = [f"User: {t.user}\nAssistant: {t.assistant}" for t in recent]
        recent_block = "\n\n".join(turn_blocks)
        recent_block = _truncate_to_token_budget(recent_block, turns_token_budget)
        if recent_block.strip():
            parts.append("## Recent turns\n" + recent_block.strip())

        return "\n\n".join(parts).strip()

    async def generate_summary(self, session_id: str) -> str:
        session = await self._storage.load(session_id)
        if session is None:
            return ""
        if len(session.turns) <= TURN_SUMMARY_THRESHOLD:
            return session.summary or ""

        to_summarize = session.turns[:-KEEP_RECENT_TURNS]
        if not to_summarize:
            return session.summary or ""

        transcript_lines: list[str] = []
        for t in to_summarize:
            transcript_lines.append(f"User: {t.user}")
            transcript_lines.append(f"Assistant: {t.assistant}")
        transcript = "\n".join(transcript_lines)

        system = (
            "You compress older chat turns into a short rolling summary for an assistant's context. "
            "Preserve facts, decisions, and open threads. Be concise; bullet points ok."
        )
        prior = (session.summary or "").strip()
        user_prompt = (
            (f"Previous summary:\n{prior}\n\n" if prior else "")
            + "Summarize the following older turns into one coherent summary "
            "(merge with the previous summary if present):\n\n"
            f"{transcript}"
        )

        new_summary: str
        if self._llm_fn is not None:
            try:
                new_summary = await self._llm_fn(
                    system=system,
                    user_prompt=user_prompt,
                    max_tokens=512,
                )
            except Exception:
                new_summary = (session.summary or "") + "\n\n" + transcript[:2000]
        else:
            new_summary = (session.summary or "") + "\n\n" + transcript[:2000]

        session.summary = (new_summary or "").strip() or session.summary
        session.turns = session.turns[-KEEP_RECENT_TURNS:]
        session.updated_at = time.time()
        await self._storage.save(session)
        return session.summary or ""

    async def list_recent(self, limit: int = 10) -> list[Session]:
        return await self._storage.list_recent(limit)

    async def delete(self, session_id: str) -> bool:
        return await self._storage.delete(session_id)
