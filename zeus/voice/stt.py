"""zeus/voice/stt.py — Orpheus STT client (WhisperLiveKit over WebSocket)."""

from __future__ import annotations

import asyncio
import io
import json
import os
import struct
import uuid
import wave
from collections.abc import AsyncIterator
from typing import Any

import httpx
import websockets


def wav_bytes_to_float32(wav_bytes: bytes) -> bytes:
    """
    Convert a WAV file (16-bit PCM, 16 kHz mono) to raw float32 LE bytes
    in the range [-1, 1] that WhisperLive expects.

    Raises ValueError if the WAV is not 16-bit PCM (WhisperLive requires it).
    Stereo input is downmixed to mono by taking the left channel.
    Sample rate is not resampled — caller must ensure 16 kHz input.
    """
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sampwidth != 2:
        raise ValueError(
            f"wav_bytes_to_float32 requires 16-bit PCM WAV (got {sampwidth * 8}-bit); "
            "re-encode or resample before passing to WhisperLive."
        )

    n_samples = len(raw) // 2
    samples = struct.unpack_from(f"<{n_samples}h", raw)

    if n_channels == 2:
        samples = samples[::2]

    float32_bytes = struct.pack(f"<{len(samples)}f", *(s / 32768.0 for s in samples))
    return float32_bytes


async def _stream_audio_chunks(ws: Any, source: AsyncIterator[bytes]) -> None:
    """Send raw audio chunks over an open WebSocket. Used as a background task."""
    async for chunk in source:
        if chunk:
            await ws.send(chunk)


async def transcribe_wav_rest(
    wav_bytes: bytes,
    *,
    base_url: str,
    language: str | None = None,
    timeout: float = 120.0,
) -> str:
    """
    OpenAI-compatible POST /v1/audio/transcriptions (WhisperLive with --enable_rest).

    Uses vad_filter=False on the server, avoiding Silero stripping whole browser clips.
    """
    url = f"{base_url.rstrip('/')}/v1/audio/transcriptions"
    lang = language if language is not None else os.getenv("WHISPER_LANGUAGE", "en") or None
    data: dict[str, str] = {"model": "whisper-1", "response_format": "json"}
    if lang:
        data["language"] = lang
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(
            url,
            files={"file": ("voice.wav", wav_bytes, "audio/wav")},
            data=data,
        )
    if r.status_code >= 400:
        detail = (r.text or "")[:500]
        raise RuntimeError(f"Whisper REST HTTP {r.status_code}: {detail}")
    body = r.json()
    return str(body.get("text") or "").strip()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


class WhisperSTT:
    def __init__(self, url: str | None = None) -> None:
        self.url = (url or os.getenv("WHISPER_URL", "ws://localhost:9090")).rstrip("/")
        self.model = os.getenv("WHISPER_MODEL", "small")
        self.use_vad = _env_bool("WHISPER_USE_VAD", True)
        self.recv_timeout = float(os.getenv("WHISPER_RECV_TIMEOUT_SEC", "90"))

    async def transcribe(
        self,
        *,
        audio_source: AsyncIterator[bytes],
        language: str = "en",
        use_vad: bool | None = None,
        is_wav: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Yield transcript events from WhisperLiveKit.

        Protocol:
          1. Send JSON config (with uid)
          2. Wait for SERVER_READY
          3. Stream float32 PCM chunks (16 kHz mono; see WhisperLive docs)
          4. Yield segment dicts until DISCONNECT, is_final, timeout, or close

        Yields dicts like:
          {"text": "...", "is_final": bool, "raw": {...}}

        Args:
            audio_source: async iterator of bytes chunks.
            language: BCP-47 language code.
            use_vad: enable server-side VAD.
            is_wav: if True, audio_source yields a full WAV file that will be
                    converted to float32 before sending.
        """
        uid = uuid.uuid4().hex[:12]
        # Full-file WAV uploads (e.g. chat hold-to-talk): server VAD often strips the
        # entire clip as "non-speech" on short/noisy browser captures — disable by default.
        if use_vad is not None:
            vad = use_vad
        elif is_wav:
            vad = False
        else:
            vad = self.use_vad

        async with websockets.connect(self.url) as ws:
            await ws.send(json.dumps({
                "uid": uid,
                "language": language,
                "task": "transcribe",
                "model": self.model,
                "use_vad": vad,
            }))

            # Wait for server handshake
            loop = asyncio.get_running_loop()
            deadline = loop.time() + 30
            while True:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    raise TimeoutError("WhisperLive: timed out waiting for SERVER_READY")
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=remaining)
                except asyncio.TimeoutError:
                    raise TimeoutError("WhisperLive: timed out waiting for SERVER_READY")
                try:
                    data = json.loads(msg)
                except json.JSONDecodeError:
                    continue
                status = data.get("message", "")
                if status == "SERVER_READY":
                    break
                if status == "WAIT":
                    await asyncio.sleep(0.5)
                    continue
                if status == "DISCONNECT":
                    raise RuntimeError("WhisperLive: server disconnected during handshake")

            # Stream audio
            send_task: asyncio.Task[None] | None = None
            if is_wav:
                # Collect full WAV then convert once; sequential send is fine for finite files.
                wav_chunks: list[bytes] = []
                async for chunk in audio_source:
                    if chunk:
                        wav_chunks.append(chunk)
                if wav_chunks:
                    float32_bytes = wav_bytes_to_float32(b"".join(wav_chunks))
                    # Send in ~80ms chunks (4096 float32 samples = 16384 bytes at 16kHz)
                    chunk_bytes = 4096 * 4
                    for i in range(0, len(float32_bytes), chunk_bytes):
                        await ws.send(float32_bytes[i : i + chunk_bytes])
                        await asyncio.sleep(0)
            else:
                # Live mic stream: send concurrently with recv so partial transcripts
                # can flow back while audio is still being captured.
                send_task = asyncio.create_task(_stream_audio_chunks(ws, audio_source))

            # Do NOT send "END_OF_AUDIO" — older WhisperLive builds pass all
            # messages to numpy before type-checking, crashing on a string.
            # Instead, collect results until the server closes the connection
            # or a per-recv timeout fires (server has received all audio and
            # will finalize when it runs out of new frames).
            last_text = ""
            final_emitted = False
            recv_timeout = max(5.0, self.recv_timeout)
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=recv_timeout)
                except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                    break
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue

                if data.get("message") == "DISCONNECT":
                    break

                segments = data.get("segments") or []
                text = ""
                if segments:
                    text = " ".join(s.get("text", "").strip() for s in segments if s.get("text"))
                elif isinstance(data.get("text"), str) and data["text"].strip():
                    text = data["text"].strip()

                if not text:
                    continue

                is_final = True
                if segments:
                    is_final = all(s.get("completed", False) for s in segments)
                elif str(data.get("status", "")).upper() == "FINAL":
                    is_final = True
                else:
                    is_final = False

                last_text = text
                yield {"text": text, "is_final": is_final, "raw": data}

                if is_final:
                    final_emitted = True
                    break

            # Clean up background sender if it's still running (e.g. recv loop
            # exited early on timeout/close before the audio source was exhausted).
            if send_task is not None and not send_task.done():
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass

            # If the loop exited on timeout/close with accumulated text but no
            # final segment, emit one last event so the caller always gets output.
            if last_text and not final_emitted:
                yield {"text": last_text, "is_final": True, "raw": {}}
