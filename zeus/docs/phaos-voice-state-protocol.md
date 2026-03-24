# Phaos — Voice State WebSocket Protocol

Real-time events from Orpheus (voice pipeline) to browser / WebXR clients for the **Phaos** visualization layer.

## Transport

- **WebSocket** URL: `ws://<host>:<port>/ws/voice-state` (or `wss:` when TLS terminates in front of Core).
- **Encoding:** UTF-8 text frames, each frame is one JSON object (no newline-delimited batching).
- **Direction:** Server → client for state events. Clients may send optional JSON pings; servers ignore unknown fields.

## Message envelope

Every server message is a JSON object with:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | Always `"voice_state"` for visualization events. |
| `state` | string | yes | One of the states below. |
| `audio_level` | number | yes | Normalized RMS-like level in `[0.0, 1.0]`. Use `0.0` when not applicable. |
| `timestamp_ms` | integer | yes | Unix epoch milliseconds (UTC). |
| `metadata` | object | no | Optional bag; common keys listed below. |

### Example

```json
{
  "type": "voice_state",
  "state": "listening",
  "audio_level": 0.73,
  "timestamp_ms": 1711300000000,
  "metadata": {
    "partial_transcript": "what are my current projects"
  }
}
```

## States

| State | Meaning |
|-------|---------|
| `idle` | No active voice turn; visualization rests. |
| `wake_detected` | Wake word fired; pipeline is arming. |
| `listening` | Capturing user speech (STT active). `audio_level` SHOULD reflect microphone energy when known. |
| `processing` | STT finalized; Oracle + LLM (and safety) running. |
| `speaking` | TTS / playback active. `audio_level` SHOULD reflect output audio envelope when known. |

Clients MUST accept unknown future state strings and treat them as `idle`-adjacent (subtle motion only).

## `audio_level` semantics

- Range: **closed interval `[0.0, 1.0]`**.
- Producers SHOULD apply a gentle log or power curve before sending so whisper-to-loud maps perceptually (e.g. `min(1.0, rms * k)` with tuned `k`).
- When the producer cannot measure level (e.g. remote TTS without analysis), send **`0.0`** and let the client fall back to state-based animation only.
- Clients MAY combine `audio_level` with **local** Web Audio microphone analysis during `listening` for lower-latency reactivity.

## `metadata` (optional)

| Key | Type | When |
|-----|------|------|
| `partial_transcript` | string | During `listening`, partial STT text (may be truncated). |
| `final_transcript` | string | After STT final (optional). |
| `request_id` | string | Correlation id for logs / debugging. |
| `source` | string | Producer hint, e.g. `"orpheus"` or `"debug_ui"`. |

Unknown keys MUST be ignored by clients.

## HTTP publish (Orpheus → Core)

When Orpheus runs **host-native** and Zeus Core runs in another process, publish the same payload via HTTP:

- **Method / path:** `POST /voice-state/publish`
- **Body:** JSON object with at least `state` and optionally `audio_level`, `metadata`.
- Server fills `type`, and `timestamp_ms` if omitted.
- **Auth (optional):** If `ZEUS_VOICE_STATE_SECRET` is set in Core’s environment, clients MUST send header `X-Zeus-Voice-State-Secret: <secret>`. If the env var is unset, the endpoint is open (dev-only).

## Versioning

- Protocol version **1** is defined by this document.
- Future breaking changes SHOULD use a top-level `protocol` integer or new `type` values.

## Related code

- Hub + validation: [`zeus/voice/state.py`](../voice/state.py)
- WebSocket + HTTP publish: [`zeus/core/voice_ws.py`](../core/voice_ws.py)

## Future protocol and client work

Tracked in the roadmap **Future / backlog** section:

- **Richer `speaking` levels:** Orpheus may send per-frame or chunked `audio_level` derived from TTS PCM so the orb matches output loudness (today clients can blend server level with local mic during `listening` only).
- **Optional `type` values:** e.g. `voice_partial_transcript` for subtitle-style UI without overloading `metadata` (would bump protocol version or add `protocol: 2`).
- **WebXR AR:** Same JSON contract; client adds `ARButton` / `immersive-ar` (see [`zeus/core/static/viz/xr.js`](../core/static/viz/xr.js) comments).
