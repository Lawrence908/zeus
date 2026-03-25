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

import websockets


def wav_bytes_to_float32(wav_bytes: bytes) -> bytes:
    """
    Convert a WAV file (PCM int16, any sample rate) to raw float32 LE bytes
    in the range [-1, 1] that WhisperLive expects.

    Mono is assumed; stereo input is downmixed to mono by taking the left channel.
    """
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    n_samples = len(raw) // 2
    samples = struct.unpack_from(f"<{n_samples}h", raw)

    if n_channels == 2:
        samples = samples[::2]

    float32_bytes = struct.pack(f"<{len(samples)}f", *(s / 32768.0 for s in samples))
    return float32_bytes


class WhisperSTT:
    def __init__(self, url: str | None = None) -> None:
        self.url = (url or os.getenv("WHISPER_URL", "ws://localhost:9090")).rstrip("/")
        self.model = os.getenv("WHISPER_MODEL", "small")

    async def transcribe(
        self,
        *,
        audio_source: AsyncIterator[bytes],
        language: str = "en",
        use_vad: bool = True,
        is_wav: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Yield transcript events from WhisperLiveKit.

        Protocol:
          1. Send JSON config (with uid)
          2. Wait for SERVER_READY
          3. Stream float32 audio chunks
          4. Send END_OF_AUDIO string
          5. Yield segment dicts until DISCONNECT or is_final

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

        async with websockets.connect(self.url) as ws:
            await ws.send(json.dumps({
                "uid": uid,
                "language": language,
                "task": "transcribe",
                "model": self.model,
                "use_vad": use_vad,
            }))

            # Wait for server handshake
            deadline = asyncio.get_event_loop().time() + 30
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
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
            if is_wav:
                # Collect full WAV then convert once
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
                async for chunk in audio_source:
                    if chunk:
                        await ws.send(chunk)

            # Do NOT send "END_OF_AUDIO" — older WhisperLive builds pass all
            # messages to numpy before type-checking, crashing on a string.
            # Instead, collect results until the server closes the connection
            # or a per-recv timeout fires (server has received all audio and
            # will finalize when it runs out of new frames).
            last_text = ""
            recv_timeout = 15.0
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
                if not segments:
                    continue

                text = " ".join(s.get("text", "").strip() for s in segments if s.get("text"))
                if not text:
                    continue

                is_final = all(s.get("completed", False) for s in segments)
                last_text = text
                yield {"text": text, "is_final": is_final, "raw": data}

                if is_final:
                    break

            # If the loop exited on timeout/close with accumulated text but no
            # final segment, emit one last event so the caller always gets output.
            if last_text:
                yield {"text": last_text, "is_final": True, "raw": {}}
