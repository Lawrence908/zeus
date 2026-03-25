"""zeus/voice/stt.py — Orpheus STT client (WhisperLiveKit over WebSocket)."""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from typing import Any

import websockets


class WhisperSTT:
    def __init__(self, url: str | None = None) -> None:
        self.url = (url or os.getenv("WHISPER_URL", "ws://localhost:9090")).rstrip("/")

    async def transcribe(
        self,
        *,
        audio_source: AsyncIterator[bytes],
        language: str = "en",
        use_vad: bool = True,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Yield transcript events from WhisperLiveKit.

        Yields dicts like:
          {"text": "...", "is_final": bool, "raw": {...}}
        """
        async with websockets.connect(self.url) as ws:
            await ws.send(
                json.dumps(
                    {
                        "language": language,
                        "task": "transcribe",
                        "use_vad": use_vad,
                    }
                )
            )

            async def _send_audio() -> None:
                async for chunk in audio_source:
                    if chunk:
                        await ws.send(chunk)

            send_task = None
            try:
                import asyncio

                send_task = asyncio.create_task(_send_audio())
                async for message in ws:
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        continue

                    text = str(data.get("text") or "").strip()
                    if not text:
                        continue

                    is_final = bool(data.get("isFinal") or data.get("is_final") or data.get("final"))
                    yield {"text": text, "is_final": is_final, "raw": data}

                    if is_final:
                        break
            finally:
                if send_task is not None:
                    send_task.cancel()
