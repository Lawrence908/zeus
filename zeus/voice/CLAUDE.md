# zeus/voice/ — Orpheus

Host-native voice pipeline: wake word to STT to chat LLM to TTS to speaker. Root brief: [`../../CLAUDE.md`](../../CLAUDE.md). Full spec: [`../docs/orpheus-spec.md`](../docs/orpheus-spec.md). Phaos protocol: [`../docs/phaos-voice-state-protocol.md`](../docs/phaos-voice-state-protocol.md).

## Layout

| File | Role |
|------|------|
| `wake.py` | `WakeWordDetector` using openWakeWord; blocking `listen()` until threshold crossed |
| `stt.py` | `WhisperSTT` WebSocket client; `transcribe_wav_rest()` for WAV-upload mode |
| `tts.py` | `VoiceboxTTS` REST client; `speak_streaming()` buffers tokens into sentences |
| `state.py` | `VoiceStateHub`, `VoiceStateEmitter`, protocol types |
| `pipeline.py` | `OrpheusPipeline.run_forever()` orchestrator; wake to STT to QueryEngine to TTS |

## Invariants

- **Runs on the host, not in Docker.** Needs direct access to audio devices (PyAudio 16 kHz int16 mono for wake and STT).
- **Streams at every stage.** First TTS sentence plays before the LLM is done generating. Don't buffer the entire reply.
- **Phaos state emission at every boundary.** `idle` to `wake_detected` to `listening` to `processing` to `speaking` to `idle`. Use `VoiceStateEmitter` from `state.py`; when Core is in Docker and Orpheus is host-native, set `ZEUS_VOICE_STATE_PUBLISH_URL` so the emitter POSTs to `/voice-state/publish`.
- **`audio_level` is `[0.0, 1.0]`.** Apply a log curve before sending so the orb reads perceptually. Send `0.0` when unmeasured; never None.
- **Sentence boundary for TTS** is `[.!?]` plus whitespace. Keep the tail buffer for the incomplete sentence.
- **WhisperLiveKit sends `isFinal: false` partials and one `isFinal: true`.** Only the final transcript goes to `QueryEngine`; partials are for Phaos subtitles if wanted.

## Env flags

| Env | Default | Purpose |
|-----|---------|---------|
| `WHISPER_URL` | `ws://localhost:9090` | WhisperLiveKit WebSocket |
| `WHISPER_MODEL` | `small` | large-v3 in prod; `medium` if tight on VRAM |
| `WHISPER_USE_VAD` | `true` | Silero VAD for end-of-utterance |
| `WHISPER_RECV_TIMEOUT_SEC` | `90` | Receive timeout |
| `WHISPER_LANGUAGE` | `en` | Lock to skip auto-detect overhead |
| `VOICEBOX_URL` | `http://localhost:5050` | Voicebox REST |
| `ORPHEUS_VOICE_ID` | (unset) | Cloned voice handle |
| `WAKE_WORD_MODEL` | `hey_jarvis` | Use `hey_jarvis` until a custom `hey_zeus` is trained |
| `WAKE_WORD_THRESHOLD` | `0.5` | Raise to `0.7` if false positives in background noise |
| `WAKE_WORD_INFERENCE_FRAMEWORK` | `onnx` | `onnx` or `tflite` |
| `WAKE_WORD_INPUT_DEVICE_INDEX` | (unset) | Force PyAudio device |
| `ZEUS_CORE_URL` | `http://127.0.0.1:8203` | Where to fetch context and chat tokens |
| `ZEUS_VOICE_STATE_PUBLISH_URL` | (unset) | HTTP endpoint for Phaos state events |
| `ZEUS_VOICE_STATE_SECRET` | (unset) | Optional header for publish auth |

## Running

```bash
# Host-native, outside Docker
cd /path/to/zeus
source .venv-orpheus/bin/activate   # or appropriate venv
python -m zeus.voice.pipeline
```

The WebSocket orb at `/viz` (or the React app's `/viz` route) picks up state events via `WS /ws/voice-state`. A WAV smoke test without wake hardware:

```bash
curl -F audio=@sample.wav http://localhost:8203/voice/interact
```

## VRAM budget on the 3080

| Component | VRAM |
|-----------|------|
| WhisperLiveKit `large-v3` | ~3.0 GB |
| `nomic-embed-text:v1.5` | ~0.3 GB |
| `qwen2.5:7b-instruct` Q4_K_M | ~5.5 GB |
| Activations / KV scratch | ~0.3 GB |
| **Total** | **~9.1 GB** |

Margin ~0.9 GB. If you want `medium` Whisper to free ~1.5 GB, fine; latency impact is minor.

## What not to do

- Don't containerize Orpheus without host PulseAudio / ALSA passthrough. It does not end well.
- Don't synth a full reply before playing audio. First-sentence latency is the whole point.
- Don't run two Ollamas on the 3080. OOM and churn.
- Don't widen wake-word sensitivity below `0.5` in production; background noise will false-positive.
- Don't publish voice-state events without `ZEUS_VOICE_STATE_SECRET` when Core is reachable outside localhost.
