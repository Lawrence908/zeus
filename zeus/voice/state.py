# zeus/voice/state.py — Phaos voice-state hub and emitter for Orpheus ↔ Core ↔ UI
from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, field_validator

VoiceStateLiteral = Literal[
    "idle",
    "wake_detected",
    "listening",
    "processing",
    "speaking",
]

VALID_STATES: frozenset[str] = frozenset(
    ("idle", "wake_detected", "listening", "processing", "speaking")
)


def voice_state_message(
    state: str,
    *,
    audio_level: float = 0.0,
    metadata: dict[str, Any] | None = None,
    timestamp_ms: int | None = None,
) -> dict[str, Any]:
    """Build a protocol v1 voice_state JSON object."""
    if state not in VALID_STATES:
        raise ValueError(f"invalid voice state: {state!r}")
    level = max(0.0, min(1.0, float(audio_level)))
    ts = int(timestamp_ms if timestamp_ms is not None else time.time() * 1000)
    msg: dict[str, Any] = {
        "type": "voice_state",
        "state": state,
        "audio_level": level,
        "timestamp_ms": ts,
    }
    if metadata:
        msg["metadata"] = metadata
    return msg


class VoiceStatePublishBody(BaseModel):
    """HTTP POST body for /voice-state/publish (partial — server may fill type/timestamp)."""

    state: str
    audio_level: float = Field(0.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp_ms: int | None = None

    @field_validator("state")
    @classmethod
    def _valid_state(cls, v: str) -> str:
        if v not in VALID_STATES:
            raise ValueError(f"state must be one of {sorted(VALID_STATES)}")
        return v


class VoiceStateHub:
    """
    In-process pub/sub for voice visualization.

    Zeus Core holds one hub on app.state; WebSocket handlers subscribe to queues
    and receive broadcast copies of each message.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._queues: list[asyncio.Queue[dict[str, Any]]] = []
        self._last: dict[str, Any] = voice_state_message("idle")

    @property
    def last_message(self) -> dict[str, Any]:
        return self._last.copy()

    async def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
        async with self._lock:
            self._queues.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue[dict[str, Any]]) -> None:
        async with self._lock:
            if q in self._queues:
                self._queues.remove(q)

    async def publish(self, message: dict[str, Any]) -> None:
        """Broadcast a full voice_state dict to all subscribers."""
        async with self._lock:
            self._last = message.copy()
            for q in self._queues:
                try:
                    q.put_nowait(message.copy())
                except asyncio.QueueFull:
                    try:
                        _ = q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    try:
                        q.put_nowait(message.copy())
                    except asyncio.QueueFull:
                        pass


class VoiceStateEmitter:
    """
    Emit voice state into a local hub and/or remote Core via HTTP.

    Orpheus in-process: pass ``hub=app.state.voice_hub``.
    Orpheus host-native: set ``publish_url`` to ``http://<core>/voice-state/publish``.
    """

    def __init__(
        self,
        *,
        hub: VoiceStateHub | None = None,
        publish_url: str | None = None,
        secret: str | None = None,
        source: str = "orpheus",
    ) -> None:
        self._hub = hub
        self._publish_url = publish_url or os.getenv("ZEUS_VOICE_STATE_PUBLISH_URL")
        self._secret = secret if secret is not None else os.getenv("ZEUS_VOICE_STATE_SECRET", "")
        self._source = source

    async def emit(
        self,
        state: str,
        *,
        audio_level: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        meta: dict[str, Any] = {"source": self._source}
        if metadata:
            meta.update(metadata)
        msg = voice_state_message(state, audio_level=audio_level, metadata=meta)
        if self._hub is not None:
            await self._hub.publish(msg)
        if self._publish_url:
            await self._emit_http(msg)

    async def _emit_http(self, msg: dict[str, Any]) -> None:
        headers: dict[str, str] = {}
        if self._secret:
            headers["X-Zeus-Voice-State-Secret"] = self._secret
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(self._publish_url, json=msg, headers=headers, timeout=3.0)
                r.raise_for_status()
        except Exception:
            # Orpheus must not crash on viz plumbing failures
            pass
