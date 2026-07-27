"""zeus/voice/pipeline.py — Orpheus voice loop (wake → STT → query → TTS → play)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import wave
from collections.abc import AsyncIterator
from io import BytesIO

import httpx
import pyaudio

from zeus.voice.state import VoiceStateEmitter
from zeus.voice.stt import WhisperSTT
from zeus.voice.tts import VoiceboxTTS
from zeus.voice.wake import WakeWordDetector

logger = logging.getLogger("orpheus")


class OrpheusPipeline:
    def __init__(self) -> None:
        self.core_url = os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")
        self.emitter = VoiceStateEmitter(
            publish_url=os.getenv("ZEUS_VOICE_STATE_PUBLISH_URL", f"{self.core_url}/voice-state/publish"),
            secret=os.getenv("ZEUS_VOICE_STATE_SECRET", ""),
            source="orpheus",
        )
        self.wake = WakeWordDetector()
        self.stt = WhisperSTT()
        self.tts = VoiceboxTTS()
        # Persisted across turns so spoken conversation shares one session with
        # text chat (updated from each /chat/stream `done` event).
        self.session_id: str | None = None

    async def llm_stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream a spoken reply from Core's /chat/stream.

        Routing through Core (rather than calling Ollama directly) gives the
        voice path the full tool loop, Aegis output filtering, retrieval, and
        session continuity. ``voice=True`` makes Core render the terse
        voice_system prompt, and runtime model switches flow through for free.
        """
        payload = {
            "message": prompt,
            "session_id": self.session_id,
            "voice": True,
            "max_tokens": 512,
        }
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"{self.core_url}/chat/stream", json=payload, timeout=180.0
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[len("data:"):].strip()
                    if not raw:
                        continue
                    try:
                        evt = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    etype = evt.get("type")
                    if etype == "token":
                        piece = evt.get("content")
                        if piece:
                            yield str(piece)
                    elif etype == "done":
                        sid = evt.get("session_id")
                        if sid:
                            self.session_id = str(sid)
                    elif etype == "error":
                        logger.warning("orpheus: chat/stream error — %s", evt.get("detail"))

    def play_audio_wav(self, audio_bytes: bytes) -> None:
        wf = wave.open(BytesIO(audio_bytes), "rb")
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                format=pa.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )
            try:
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
            finally:
                stream.stop_stream()
                stream.close()
        finally:
            pa.terminate()

    def mic_stream(self, *, max_seconds: float = 30.0) -> AsyncIterator[bytes]:
        CHUNK = 1280
        RATE = 16000
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        async def _gen() -> AsyncIterator[bytes]:
            try:
                chunks = int(max_seconds / (CHUNK / RATE))
                for _ in range(max(chunks, 1)):
                    yield stream.read(CHUNK, exception_on_overflow=False)
                    await asyncio.sleep(0)
            finally:
                stream.stop_stream()
                stream.close()
                pa.terminate()

        return _gen()

    async def run_forever(self) -> None:
        logger.info("orpheus: listening for wake word…")
        while True:
            self.wake.listen()
            await self.emitter.emit("wake_detected")

            await self.emitter.emit("listening", audio_level=0.0)
            transcript = ""
            async for evt in self.stt.transcribe(audio_source=self.mic_stream()):
                transcript = str(evt.get("text") or "").strip()
                if transcript:
                    await self.emitter.emit("listening", metadata={"partial_transcript": transcript})
                if evt.get("is_final"):
                    break

            transcript = transcript.strip()
            if not transcript:
                await self.emitter.emit("idle")
                continue

            await self.emitter.emit("processing", metadata={"final_transcript": transcript})
            token_stream = self.llm_stream(transcript)

            await self.emitter.emit("speaking")
            async for wav_bytes in self.tts.speak_streaming(token_stream):
                self.play_audio_wav(wav_bytes)

            await self.emitter.emit("idle")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    pipe = OrpheusPipeline()
    await pipe.run_forever()


if __name__ == "__main__":
    asyncio.run(main())

