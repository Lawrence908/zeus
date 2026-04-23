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

from zeus.core.prompts import render as render_prompt
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

    async def get_context(self, query: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{self.core_url}/context/query",
                    json={"query": query, "top_k": 5, "max_tokens": 1024},
                    timeout=10,
                )
                r.raise_for_status()
                return str((r.json() or {}).get("context") or "")
        except Exception as e:
            logger.warning(f"orpheus: context fetch failed — {e}")
            return ""

    async def llm_stream(self, prompt: str, context: str) -> AsyncIterator[str]:
        # Resolve the currently-active model/provider at call time so runtime
        # model switches (POST /models/active) flow through the voice path too.
        from zeus.core.query import _active_model_name, _chat_use_claude
        model = _active_model_name()
        provider = "Anthropic Claude" if _chat_use_claude() else "Ollama (local)"

        system = render_prompt(
            "voice_system",
            context=context.strip() or "(No retrieved context for this query.)",
            model_name=model,
            provider=provider,
        )

        base = os.getenv("OLLAMA_URL", "http://localhost:11435").rstrip("/")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "options": {"num_predict": 512},
        }
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", f"{base}/api/chat", json=payload, timeout=120.0) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = data.get("message") or {}
                    piece = msg.get("content")
                    if piece:
                        yield str(piece)
                    if data.get("done"):
                        break

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
            context = await self.get_context(transcript)

            token_stream = self.llm_stream(transcript, context)

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

