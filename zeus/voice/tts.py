"""zeus/voice/tts.py — Orpheus TTS client.

Speaks an OpenAI-compatible /v1/audio/speech API (Kokoro-FastAPI by default).
The class keeps the historical ``VoiceboxTTS`` name so existing imports in
``voice_ws.py``, ``chat.py`` and ``pipeline.py`` are unchanged.

Config (env):
  ZEUS_TTS_URL     base URL (default http://tts:8880; falls back to VOICEBOX_URL
                   for older deployments)
  ZEUS_TTS_VOICE   voice id (default af_heart; ORPHEUS_VOICE_ID still honored)
  ZEUS_TTS_MODEL   model name (default kokoro)
  ZEUS_TTS_FORMAT  response_format (default wav — the pipeline/orb both expect WAV)
  ZEUS_TTS_SPEED   playback speed multiplier (default 1.0)
"""

from __future__ import annotations

import logging
import os
import re
from collections.abc import AsyncIterator

import httpx

logger = logging.getLogger("orpheus.tts")

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _default_base_url() -> str:
    # ZEUS_TTS_URL is the current knob; VOICEBOX_URL is honored for backward
    # compatibility with pre-Kokoro deployments.
    return (
        os.getenv("ZEUS_TTS_URL")
        or os.getenv("VOICEBOX_URL")
        or "http://tts:8880"
    ).rstrip("/")


class VoiceboxTTS:
    def __init__(self, *, url: str | None = None, voice_id: str | None = None) -> None:
        self.url = (url or _default_base_url()).rstrip("/")
        # ORPHEUS_VOICE_ID historically held a Voicebox handle; ignore obviously
        # non-Kokoro placeholders (e.g. "12345") and fall through to the default.
        raw_voice = (
            voice_id
            if voice_id is not None
            else os.getenv("ZEUS_TTS_VOICE") or os.getenv("ORPHEUS_VOICE_ID", "")
        ).strip()
        self.voice_id = raw_voice if _looks_like_voice(raw_voice) else "af_heart"
        self.model = os.getenv("ZEUS_TTS_MODEL", "kokoro").strip() or "kokoro"
        self.response_format = os.getenv("ZEUS_TTS_FORMAT", "wav").strip() or "wav"
        try:
            self.speed = float(os.getenv("ZEUS_TTS_SPEED", "1.0"))
        except ValueError:
            self.speed = 1.0
        # Fail fast: on a contended host a slow synth should surface quickly so
        # the browser can fall back to Web Speech instead of sitting silent.
        try:
            self.timeout = float(os.getenv("ZEUS_TTS_TIMEOUT_SEC", "20"))
        except ValueError:
            self.timeout = 20.0

    def _split_sentences(self, text: str) -> list[str]:
        return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]

    async def synthesize(self, text: str) -> bytes:
        payload = {
            "model": self.model,
            "input": text,
            "voice": self.voice_id,
            "response_format": self.response_format,
            "speed": self.speed,
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.url}/v1/audio/speech", json=payload, timeout=self.timeout)
            r.raise_for_status()
            return r.content

    async def speak_streaming(self, token_stream: AsyncIterator[str]) -> AsyncIterator[bytes]:
        """Buffer tokens into sentences and synthesize each as it completes.

        A failure on one sentence is logged and skipped rather than aborting the
        whole reply, so a transient TTS hiccup drops at most a clause instead of
        killing the turn.
        """
        buffer = ""
        async for token in token_stream:
            buffer += token
            sentences = self._split_sentences(buffer)
            if len(sentences) > 1:
                for sentence in sentences[:-1]:
                    audio = await self._synthesize_safe(sentence)
                    if audio:
                        yield audio
                buffer = sentences[-1]

        if buffer.strip():
            audio = await self._synthesize_safe(buffer.strip())
            if audio:
                yield audio

    async def _synthesize_safe(self, text: str) -> bytes | None:
        try:
            return await self.synthesize(text)
        except (httpx.HTTPError, OSError) as exc:
            logger.warning("tts: synth failed for %r — %s", text[:60], exc)
            return None


def _looks_like_voice(value: str) -> bool:
    # Kokoro voice ids look like "af_heart", "am_adam", "bf_emma" — a lang/gender
    # prefix, underscore, name. Reject bare numbers and empty strings.
    return bool(re.match(r"^[a-z]{2}_[a-z]+$", value))
