"""zeus/voice/tts.py — Orpheus TTS client (Voicebox REST → LuxTTS)."""

from __future__ import annotations

import os
import re
from collections.abc import AsyncIterator

import httpx

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


class VoiceboxTTS:
    def __init__(self, *, url: str | None = None, voice_id: str | None = None) -> None:
        self.url = (url or os.getenv("VOICEBOX_URL", "http://localhost:5050")).rstrip("/")
        self.voice_id = (voice_id if voice_id is not None else os.getenv("ORPHEUS_VOICE_ID", "")).strip()

    def _split_sentences(self, text: str) -> list[str]:
        return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]

    async def synthesize(self, text: str) -> bytes:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.url}/synthesize",
                json={"text": text, "voice_id": self.voice_id, "speed": 1.0},
                timeout=30,
            )
            r.raise_for_status()
            return r.content

    async def speak_streaming(self, token_stream: AsyncIterator[str]) -> AsyncIterator[bytes]:
        buffer = ""
        async for token in token_stream:
            buffer += token
            sentences = self._split_sentences(buffer)
            if len(sentences) > 1:
                for sentence in sentences[:-1]:
                    audio = await self.synthesize(sentence)
                    yield audio
                buffer = sentences[-1]

        if buffer.strip():
            audio = await self.synthesize(buffer.strip())
            yield audio

