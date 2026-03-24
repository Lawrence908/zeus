# Orpheus — Voice Pipeline Implementation Spec

Orpheus handles the full voice interaction loop: wake word detection → real-time STT → context retrieval → LLM → TTS → audio output. It runs as a host-native process (not containerised) because it needs direct access to audio devices.

---

## Architecture

```
Microphone
    │
    ▼
openWakeWord (CPU, always-on)
    │  "hey zeus" detected
    ▼
WhisperLiveKit (GPU, SimulStreaming)
    │  transcript (streaming)
    ▼
Silence / VAD end-of-utterance
    │  final transcript
    ▼
Oracle /context/query (FastAPI → mnemosyne)
    │  context block (≤ 2048 tokens)
    ▼
LLM (Claude API in dev / Qwen2.5-7B in prod)
    │  response tokens (streaming)
    ▼
Aegis filter
    │  filtered response
    ▼
Voicebox REST → LuxTTS (GPU)
    │  audio stream
    ▼
Speaker output
```

The pipeline is designed around **streaming at every stage** — TTS begins as soon as the first sentence is complete, not waiting for the full LLM response. This is what makes sub-2-second latency achievable.

---

## Components

### openWakeWord

**Role:** Passive, always-on CPU listener. Triggers the rest of the pipeline.

**Install:**
```bash
pip install openwakeword
# Download a prebuilt model
python -c "from openwakeword.model import Model; Model(wakeword_models=['hey_jarvis'])"
```

**Initial approach:** Use `hey_jarvis` as a placeholder during development. Record a custom `hey_zeus` model after the core pipeline works — the custom model is more reliable but not needed to start.

**Config in `orpheus.yaml`:**
```yaml
wake_word:
  model: hey_jarvis      # swap to hey_zeus once trained
  threshold: 0.5         # lower = more sensitive, more false positives
  device: cpu
```

**Implementation (`zeus/voice/wake.py`):**
```python
import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np

class WakeWordDetector:
    def __init__(self, model_name: str = "hey_jarvis", threshold: float = 0.5):
        self.model = Model(wakeword_models=[model_name])
        self.threshold = threshold
        self.chunk_size = 1280  # 80ms at 16kHz

    def listen(self) -> None:
        """Block until wake word detected, then return."""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        try:
            while True:
                chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_np = np.frombuffer(chunk, dtype=np.int16)
                prediction = self.model.predict(audio_np)
                score = max(prediction.values())
                if score >= self.threshold:
                    return   # wake word confirmed
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
```

**Gotcha:** openWakeWord expects 16kHz mono int16 audio. Make sure your input device matches or resample before passing chunks in.

---

### WhisperLiveKit — STT

**Role:** Real-time transcription of the user's utterance after wake word.

**Mode:** SimulStreaming — partial transcripts arrive before the user stops speaking, so the LLM call can start earlier.

**Install:**
```bash
pip install whisperlivekit
# Or run via Docker (no audio device needed for server)
docker run -p 9090:9090 collabora/whisperlive:latest
```

**Key settings:**
- Model: `large-v3` (best accuracy, ~3GB VRAM on 3080)
- Language: `en` (lock it — auto-detection adds ~100ms)
- VAD: built-in Silero VAD for end-of-utterance detection

**Implementation (`zeus/voice/stt.py`):**
```python
import asyncio
import websockets
import json
from typing import AsyncIterator

class WhisperSTT:
    def __init__(self, url: str = "ws://localhost:9090"):
        self.url = url

    async def transcribe(self, audio_source) -> AsyncIterator[str]:
        """
        Yield partial transcripts as they arrive.
        Final transcript is the last yielded value.
        audio_source: async generator yielding raw PCM chunks
        """
        async with websockets.connect(self.url) as ws:
            # Send config
            await ws.send(json.dumps({
                "language": "en",
                "task": "transcribe",
                "use_vad": True,
            }))

            # Stream audio while receiving transcripts concurrently
            async def send_audio():
                async for chunk in audio_source:
                    await ws.send(chunk)

            async def recv_transcripts():
                async for message in ws:
                    data = json.loads(message)
                    if text := data.get("text"):
                        yield text.strip()

            send_task = asyncio.create_task(send_audio())
            async for transcript in recv_transcripts():
                yield transcript

            await send_task
```

**Gotcha:** WhisperLiveKit's WebSocket protocol sends partial results with `"isFinal": false` and a final result with `"isFinal": true`. Parse accordingly — only pass the final transcript to the LLM.

---

### Voicebox / LuxTTS — TTS

**Role:** Convert LLM text response to natural speech audio using Chris's cloned voice.

**Voice cloning setup:**
1. Record 30–60 seconds of clean speech (quiet room, no background noise, varied sentences)
2. Save as `zeus/data/voice_sample.wav` (gitignored)
3. POST to Voicebox to register the voice: `POST /voice/clone` with the WAV file
4. Save the returned `voice_id` as `ORPHEUS_VOICE_ID` in `.env`

**Streaming approach:** Request audio in chunks as LLM tokens arrive. Don't wait for the full response — split on sentence boundaries (`.`, `!`, `?`) and synthesize each sentence independently. This gets first audio playing ~200ms after first LLM sentence is complete.

**Implementation (`zeus/voice/tts.py`):**
```python
import asyncio
import httpx
import re
from typing import AsyncIterator

SENTENCE_END = re.compile(r'(?<=[.!?])\s+')

class VoiceboxTTS:
    def __init__(self, url: str, voice_id: str):
        self.url = url
        self.voice_id = voice_id

    def _split_sentences(self, text: str) -> list[str]:
        return [s.strip() for s in SENTENCE_END.split(text) if s.strip()]

    async def synthesize(self, text: str) -> bytes:
        """Synthesize a single text chunk, return raw audio bytes."""
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.url}/synthesize",
                json={"text": text, "voice_id": self.voice_id, "speed": 1.0},
                timeout=10,
            )
            r.raise_for_status()
            return r.content

    async def speak_streaming(self, token_stream: AsyncIterator[str]) -> AsyncIterator[bytes]:
        """
        Buffer LLM tokens into sentences, synthesize each sentence as it completes.
        Yields audio bytes as soon as each sentence is ready.
        """
        buffer = ""
        async for token in token_stream:
            buffer += token
            sentences = self._split_sentences(buffer)
            if len(sentences) > 1:
                # All but the last fragment are complete sentences
                for sentence in sentences[:-1]:
                    audio = await self.synthesize(sentence)
                    yield audio
                buffer = sentences[-1]  # keep the incomplete tail

        # Flush remaining buffer
        if buffer.strip():
            audio = await self.synthesize(buffer.strip())
            yield audio
```

**Gotcha:** LuxTTS at 150x realtime means a 10-second audio clip generates in ~67ms. The bottleneck is network round-trip to the REST endpoint, not synthesis. Run Voicebox on the same machine as Orpheus to eliminate this.

---

### Voice Pipeline Orchestrator

**Implementation (`zeus/voice/pipeline.py`):**
```python
# zeus/voice/pipeline.py — Orpheus full voice loop
import asyncio
import logging
import os

import httpx

from zeus.voice.wake import WakeWordDetector
from zeus.voice.stt import WhisperSTT
from zeus.voice.tts import VoiceboxTTS

logger = logging.getLogger("orpheus")

ORACLE_URL = os.getenv("ZEUS_CORE_URL", "http://localhost:8000")
VOICEBOX_URL = os.getenv("VOICEBOX_URL", "http://localhost:5050")
ORPHEUS_VOICE_ID = os.getenv("ORPHEUS_VOICE_ID", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")
MAX_RESPONSE_TOKENS = 512

SYSTEM_PROMPT_TEMPLATE = """You are Zeus, a personal AI assistant. You are talking to Chris.
Answer concisely — you are speaking aloud, so avoid lists, markdown, and long explanations.
Keep responses under 3 sentences unless the question genuinely requires more.

## Personal Context
{context}
"""


async def get_context(query: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{ORACLE_URL}/context/query",
                json={"query": query, "top_k": 5, "max_tokens": 1024},
                timeout=5,
            )
            return r.json().get("context", "")
    except Exception as e:
        logger.warning(f"orpheus: context fetch failed — {e}")
        return ""


async def call_llm_streaming(prompt: str, context: str):
    """Yield response tokens from LLM (Claude in dev, Ollama in prod)."""
    system = SYSTEM_PROMPT_TEMPLATE.format(context=context)

    if ZEUS_ENV == "dev":
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        async with client.messages.stream(
            model=os.getenv("ZEUS_DEV_MODEL", "claude-sonnet-4-6-20250514"),
            max_tokens=MAX_RESPONSE_TOKENS,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
    else:
        # Prod: Ollama streaming
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": os.getenv("ZEUS_PROD_MODEL", "qwen2.5:7b-instruct-q4_K_M"),
                    "prompt": f"{system}\n\nUser: {prompt}\nAssistant:",
                    "stream": True,
                    "options": {"num_predict": MAX_RESPONSE_TOKENS},
                },
                timeout=30,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if token := data.get("response"):
                            yield token
                        if data.get("done"):
                            break


def play_audio(audio_bytes: bytes) -> None:
    """Play raw audio bytes through the default output device."""
    import pyaudio
    import wave
    import io
    wf = wave.open(io.BytesIO(audio_bytes))
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
    )
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    pa.terminate()


async def run_voice_loop():
    wake = WakeWordDetector()
    stt = WhisperSTT()
    tts = VoiceboxTTS(url=VOICEBOX_URL, voice_id=ORPHEUS_VOICE_ID)

    logger.info("orpheus: listening for wake word...")
    while True:
        # Block until wake word
        wake.listen()
        logger.info("orpheus: wake word detected")

        # TODO: play a short audio cue to indicate zeus is listening

        # Capture utterance via STT
        # (audio_source needs to be wired to microphone stream)
        transcript = ""
        async for partial in stt.transcribe(audio_source=mic_stream()):
            transcript = partial   # keep updating until final
            logger.debug(f"orpheus: partial transcript: {partial!r}")

        if not transcript:
            logger.warning("orpheus: empty transcript, ignoring")
            continue

        logger.info(f"orpheus: final transcript: {transcript!r}")

        # Get context and stream LLM response into TTS
        context = await get_context(transcript)
        token_gen = call_llm_streaming(transcript, context)

        async for audio_chunk in tts.speak_streaming(token_gen):
            play_audio(audio_chunk)

        logger.info("orpheus: response complete, listening again...")


def mic_stream():
    """Async generator yielding raw PCM chunks from microphone."""
    import pyaudio
    import asyncio

    CHUNK = 1280
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=CHUNK,
    )

    async def _gen():
        # Stream until silence (VAD handled by WhisperLiveKit)
        for _ in range(300):  # ~30 seconds max utterance
            yield stream.read(CHUNK, exception_on_overflow=False)
            await asyncio.sleep(0)
        stream.stop_stream()
        stream.close()
        pa.terminate()

    return _gen()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(run_voice_loop())
```

---

## Dependencies

Add to `requirements.txt` for Sprint 2:
```
openwakeword>=0.6.0
whisperlivekit>=0.1.0
pyaudio>=0.2.14
websockets>=12.0
anthropic>=0.30.0    # for dev env streaming
```

**System deps (Ubuntu/Debian):**
```bash
sudo apt install portaudio19-dev ffmpeg
```

---

## Latency Tuning Notes

- **Wake word false positives:** raise `threshold` from 0.5 → 0.7 if triggers happen in background noise
- **STT lag:** if first-word latency is > 500ms, switch Whisper to `medium` model (trades accuracy for speed)
- **LLM slow on 3080:** if Qwen inference > 800ms/token, try `qwen2.5:3b-instruct-q4_K_M` — smaller but faster
- **TTS lag:** ensure Voicebox is on the same host; network latency kills the 150x realtime advantage
- **Audio glitches:** increase PyAudio `frames_per_buffer` if you hear crackling; decrease if latency is high

---

## Testing Voice Components Independently

```bash
# Test wake word only
python -c "from zeus.voice.wake import WakeWordDetector; WakeWordDetector().listen(); print('Wake word detected')"

# Test TTS only
python -c "
import asyncio
from zeus.voice.tts import VoiceboxTTS
import os
tts = VoiceboxTTS(os.getenv('VOICEBOX_URL'), os.getenv('ORPHEUS_VOICE_ID'))
audio = asyncio.run(tts.synthesize('Zeus voice test. Hello Chris.'))
open('/tmp/test.wav', 'wb').write(audio)
print('Saved to /tmp/test.wav')
"

# Test STT only (with a recorded WAV file)
python -c "
import asyncio
from zeus.voice.stt import WhisperSTT
# TODO: adapt to feed a file instead of mic
"
```
