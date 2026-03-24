# Zeus — Build Roadmap

This document is the authoritative sprint plan. Each sprint has a concrete exit criterion — if you can't run the validation commands at the bottom of the sprint, it's not done.

School finishes in ~5 weeks. The target is: memory working end-to-end by week 2, voice working locally by week 4, deployed to Olympus by week 5.

---

## Sprint 0 — Scaffold ✅ DONE

**Goal:** Repo structure, configs, and service definitions exist and are ready to run.

**Deliverables:**
- `compose.yaml` with Qdrant, Ollama, Zeus Core
- `zeus/core/main.py` — FastAPI with `/status`
- `zeus/memory/config.py` — mem0 config with env switching
- `zeus/ingest/` — Iris pipeline, markdown + ChatGPT sources
- `zeus/api/main.py` — Oracle context API skeleton
- `zeus/orchestration/` — Ruflo config + all agent YAMLs
- `scripts/smoke_test.py` — stack smoke test

**Exit criterion:**
```bash
python scripts/smoke_test.py --skip-core  # Qdrant + Ollama + embed model pass
```

---

## Sprint 1 — Memory Loop (Mnemosyne end-to-end)

**Goal:** Personal data flows from files into Qdrant, and can be queried back out through Oracle. This is the foundation everything else depends on.

**Tasks:**

1. **Prepare ingest data** — see `docs/ingest-guide.md` for what to collect and in what order
2. **Run first ingest** — dry-run first, then live
   ```bash
   python -m zeus.ingest.run --source markdown --glob "**/*.md" --base-dir zeus/data/raw --dry-run
   python -m zeus.ingest.run --source markdown --glob "**/*.md" --base-dir zeus/data/raw
   ```
3. **Verify Qdrant has data** — check collection via UI or API
   ```bash
   curl localhost:6333/collections/zeus_memories | python3 -m json.tool
   ```
4. **Wire Oracle into Core** — add `/context/query` route to zeus-core that proxies to Oracle
5. **Implement `/context/profile`** — query mnemosyne for stable facts, build a user profile summary
6. **ChatGPT export ingest** — export from ChatGPT, run `--source chatgpt`
7. **Add `context_pack` source** — write `zeus/ingest/sources/context_pack.py` for a hand-curated `context_pack.md` (see ingest guide)

**New files:**
- `zeus/ingest/sources/context_pack.py`
- `zeus/data/raw/context_pack.md` (hand-written, gitignored)
- `zeus/memory/search.py` — search utilities on top of mem0

**Exit criterion:**
```bash
# Start services
docker compose up qdrant ollama -d
uvicorn zeus.api.main:app --port 8001 --reload

# Query Oracle
curl -s -X POST localhost:8001/context/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what are my current projects", "top_k": 5}' | python3 -m json.tool

# Should return non-empty context with sources from your ingested data
```

---

## Sprint 2 — Orpheus Voice Pipeline

**Goal:** Wake word → STT → LLM → TTS loop works locally. Audio in, audio out, no text interface.

**Dependency:** Sprint 1 complete (Oracle must be serving context).

**Tasks:**

1. **WhisperLiveKit setup**
   - Docker service or local install
   - Verify SimulStreaming works with a test audio file
   - Target: < 300ms first-word latency on 5080

2. **openWakeWord setup**
   - Install on host CPU (not in Docker — needs audio device access)
   - Train or download `hey_zeus` model (or use `hey_jarvis` as placeholder)
   - Wire to trigger Orpheus pipeline

3. **Voicebox/LuxTTS setup**
   - Clone voice sample (record 30–60 seconds of yourself)
   - Test TTS REST endpoint: `POST /synthesize` → WAV/MP3 response
   - Target: < 200ms TTFB on 5080

4. **`zeus/voice/` implementation**
   - `zeus/voice/stt.py` — WhisperLiveKit WebSocket client
   - `zeus/voice/tts.py` — Voicebox REST client
   - `zeus/voice/wake.py` — openWakeWord listener loop
   - `zeus/voice/pipeline.py` — orchestrates the full loop

5. **LLM integration in voice loop**
   - On utterance: call Oracle for context → build prompt → call LLM → speak response
   - Keep response tokens ≤ 512 for latency
   - Stream TTS as tokens arrive (don't wait for full completion)

6. **Phaos state emission (voice UI)**
   - Wire `VoiceStateEmitter` from [`zeus/voice/state.py`](../voice/state.py) through the pipeline stages
   - When Core runs separately (Docker/systemd), set `ZEUS_VOICE_STATE_PUBLISH_URL` to `http://<host>:<port>/voice-state/publish` and optional `ZEUS_VOICE_STATE_SECRET`
   - Emit transitions: `idle` → `wake_detected` → `listening` (with mic `audio_level` when available) → `processing` → `speaking` (with TTS level when available) → `idle`
   - Protocol reference: [`docs/phaos-voice-state-protocol.md`](phaos-voice-state-protocol.md)

7. **Add Orpheus to `compose.yaml`** (optional — voice pipeline may stay host-native for audio device access)

**Latency budget (target on 5080):**
| Stage | Target |
|---|---|
| Wake word detect | < 50ms |
| STT (first word) | < 300ms |
| Oracle context fetch | < 100ms |
| LLM first token | < 500ms (Claude) / < 800ms (Qwen) |
| TTS first audio | < 200ms |
| **Total to first speech** | **< 1.5s** |

**New files:**
- `zeus/voice/stt.py`
- `zeus/voice/tts.py`
- `zeus/voice/wake.py`
- `zeus/voice/pipeline.py`
- `zeus/voice/state.py` (Phaos hub types + `VoiceStateEmitter` — **scaffold present**; finish wiring in pipeline)
- `zeus/voice/Dockerfile` (if containerising)

**Exit criterion:**
```bash
python zeus/voice/pipeline.py
# Say "hey zeus, what are my current projects"
# Should respond with audio within 2 seconds
```

---

## Sprint 3 — Aegis Safety Layer

**Goal:** No LLM output reaches the user (audio or text) without passing through Aegis. This is a prerequisite for deploying to prod.

**Dependency:** Sprint 2 complete (voice loop must exist to wire in).

**Tasks:**

1. **Define policy files** in `zeus/safety/policies/`
   - `standard.yaml` — default policy for Oracle/text responses
   - `voice.yaml` — stricter, no hedging language, no unsafe content
   - `ingest.yaml` — permissive, for trusted personal data
   - `memory.yaml` — blocks PII writes without consent flag

2. **NemoClaw integration**
   - Wire NemoClaw as a FastAPI middleware or post-processing step
   - Implement `AegisFilter` class: `filter(text, policy) -> (safe: bool, filtered_text: str)`

3. **OpenShell sandbox**
   - Wrap any tool-use calls (file reads, bus calls) in OpenShell policy checks
   - Prevent agent actions outside their declared tool list

4. **Wire into voice loop** — Orpheus pipes every LLM response through Aegis before TTS

5. **Wire into Oracle** — every `/context/query` response filtered before return

6. **Add `zeus/safety/aegis.py`** — unified filter interface

**New files:**
- `zeus/safety/aegis.py`
- `zeus/safety/policies/standard.yaml`
- `zeus/safety/policies/voice.yaml`
- `zeus/safety/policies/ingest.yaml`
- `zeus/safety/policies/memory.yaml`

**Exit criterion:**
```bash
# Inject a policy-violating string and confirm it's blocked
python -c "
from zeus.safety.aegis import AegisFilter
f = AegisFilter(policy='voice')
result = f.filter('Here is some clearly unsafe content...')
assert not result.safe
print('Aegis blocking correctly')
"
```

---

## Sprint 4 — Olympus Deployment

**Goal:** Zeus running 24/7 on the RTX 3080 server, switching to Qwen2.5-7B-Instruct for all LLM calls. Stable enough to use daily.

**Dependency:** Sprints 1–3 complete and validated on 5080 tower.

**Tasks:**

1. **Prepare Olympus environment**
   - Clone repo to Olympus
   - Copy `.env` with `ZEUS_ENV=prod`
   - Pull `qwen2.5:7b-instruct-q4_K_M` via Ollama
   - Pull `nomic-embed-text` via Ollama

2. **VRAM budget check** (10GB on 3080)
   | Model | VRAM |
   |---|---|
   | Qwen2.5-7B Q4_K_M | ~5.5GB |
   | nomic-embed-text | ~0.3GB |
   | WhisperLiveKit large-v3 | ~3.0GB |
   | **Total** | **~8.8GB** ← fits with margin |

3. **Prod smoke test**
   ```bash
   ZEUS_ENV=prod python scripts/smoke_test.py
   ```

4. **Systemd services** — make Qdrant, Ollama, Zeus Core, and Orpheus restart on boot
   - `zeus-qdrant.service` (or via Docker)
   - `zeus-ollama.service` (or via Docker)
   - `zeus-core.service`
   - `zeus-orpheus.service` (host-native, needs audio)

5. **Re-ingest on Olympus** — run full Iris ingest on prod (same data, prod models)

6. **Latency validation on 3080** — Qwen inference is slower than Claude, re-measure latency budget

**Exit criterion:**
```bash
# On Olympus, ZEUS_ENV=prod
python scripts/smoke_test.py
# All checks pass with prod models
# Voice loop works end-to-end with Qwen2.5-7B
```

---

## Sprint 5 — Agent Runtime Engine

**Goal:** Move from static YAML contracts to a running orchestration engine in Python.

**Tasks:**

1. Build `zeus/orchestration/runtime.py` to load `orchestration/agents/*.yaml`
2. Build `zeus/orchestration/bus.py` for inter-agent request routing over FastAPI
3. Build `zeus/orchestration/hooks.py` for before/after policy hooks
4. Add lifecycle control for olympians (start, stop, status)
5. Add a lightweight event bus for asynchronous agent notifications

**Exit criterion:**
```bash
# Start zeus-core
uvicorn zeus.core.main:app --reload

# Confirm runtime loaded and agents are visible
curl -s localhost:8000/orchestration/status | python3 -m json.tool
```

---

## Sprint 6 — Conversation Sessions

**Goal:** Add multi-turn continuity so Zeus is no longer stateless per request.

**Tasks:**

1. Add session model (`session_id`, turns, summary, metadata)
2. Store recent turns and rolling summaries
3. Make Oracle session-aware (`/context/query` can include `session_id`)
4. Add session resume and expiration behavior
5. Persist session artifacts in memory layer (or SQLite sidecar)

**Exit criterion:**
```bash
# Start zeus-core
uvicorn zeus.core.main:app --reload

# Run two turns in same session and verify contextual continuity
curl -s -X POST localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test-session-1","message":"I am working on Zeus sprint planning"}' | python3 -m json.tool

curl -s -X POST localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test-session-1","message":"what did I just say I was working on?"}' | python3 -m json.tool
```

---

## Sprint 7 — Text Chat Interface

**Goal:** Add a minimal local web chat UI for development, testing, and non-voice interaction.

**Tasks:**

1. Add `zeus/core/chat.py` routes (`/chat`, `/chat/message`, optional stream endpoint)
2. Add `zeus/core/static/chat.html` lightweight UI
3. Use same LLM + Oracle context path as Orpheus
4. Use session model from Sprint 6
5. Add basic request/latency logging for chat calls

**Land early (already in tree):**

- `GET /chat`, `GET /viz`, `POST /chat/message`, static mount `/static`, in-memory session continuity (until Sprint 6 SQLite)
- Phaos orb embedded in `chat.html` + standalone [`zeus/core/static/viz/viz.html`](../core/static/viz/viz.html) (Three.js + WebXR VR button)
- `ZEUS_LLM` respected for chat (`claude` | `ollama` | unset → dev+key uses Claude)

**Still open for Sprint 7 “done”:**

- `GET /chat/stream` (SSE) and `GET /chat/sessions/{session_id}` per [`chat-interface-spec.md`](chat-interface-spec.md)
- Structured logging fields (request_id, prompt_hash, …)
- Aegis on chat path once Sprint 3 lands

**Exit criterion:**
```bash
uvicorn zeus.core.main:app --reload
# Open http://localhost:8000/chat and send messages
# Context-assisted replies should render in the UI
```

---

## Sprint 8 — Zeus MCP Server

**Goal:** Make Zeus memory and profile functions callable from MCP clients.

**Tasks:**

1. Add `zeus/mcp/server.py` and `zeus/mcp/tools.py`
2. Implement tools:
   - `zeus_query` (context lookup)
   - `zeus_remember` (store memory)
   - `zeus_profile` (profile summary)
3. Wire MCP calls to Oracle and memory layer endpoints
4. Provide `mcp.json` example config for Cursor/Claude clients

**Exit criterion:**
```bash
# Run MCP server
python -m zeus.mcp.server

# From MCP client, call zeus_query with a natural language prompt
# Tool returns structured context and source references
```

---

## Sprint 9 — Observability + Continuous Ingest

**Goal:** Improve day-2 operations with metrics, logging, and automatic ingest.

**Tasks:**

1. Add query logging (query text hash, latency, source counts)
2. Add ingest stats endpoint (`/admin/ingest/stats`)
3. Add minimal admin dashboard (`/admin`)
4. Add scheduler for periodic Iris runs
5. Add memory consolidation job (dedup, merge overlap candidates)

**Exit criterion:**
```bash
uvicorn zeus.core.main:app --reload
curl -s localhost:8000/admin/ingest/stats | python3 -m json.tool
# Dashboard and stats should reflect recent query and ingest activity
```

---

## Sprint 10 — Additional Ingest Sources

**Goal:** Expand memory coverage with high-signal personal data sources.

**Tasks:**

1. Add Obsidian parser (`zeus/ingest/sources/obsidian.py`)
2. Add Git history parser (`zeus/ingest/sources/git.py`)
3. Add Google Calendar parser (`zeus/ingest/sources/gcal.py`)
4. Add bookmarks parser (`zeus/ingest/sources/bookmarks.py`)
5. Register each source in `zeus/ingest/run.py` and `orchestration/agents/iris.yaml`

**Exit criterion:**
```bash
python -m zeus.ingest.run --source all --dry-run
# Dry-run lists chunks from all registered sources without failures
```

---

## Future / backlog (post–Sprint 10)

Work that does not block the baseline sprints but extends Phaos, voice UX, and XR.

### Phaos and browser voice

- **TTS level sync:** Analyze PCM from Voicebox/LuxTTS (or speaker loopback) in Orpheus and send `audio_level` on `speaking` over `POST /voice-state/publish` so the orb matches the model’s voice without guessing from state alone.
- **Browser voice turn:** Push-to-talk or continuous capture → STT (WhisperLiveKit or Web Speech API prototype) → same Core/Oracle/LLM path → TTS playback, with Phaos driven by real pipeline state instead of debug buttons.
- **Visual polish:** Optional particle / arc layer on the orb; shader tuning for “lightning” motif; reduced motion / high-contrast accessibility toggle.

### WebXR and AR

- **Immersive AR:** Three.js `ARButton` + `immersive-ar` session (passthrough) using the same scene as VR; scale and anchor orb for comfortable viewing on Quest / Vision Pro browsers.
- **Session stability:** Test long-lived WebSocket + XR session handoff (tab background, headset sleep).

### Hardening

- Rate-limit or auth on `POST /voice-state/publish` when Core is exposed beyond localhost (secret is already supported).
- Integration tests: WebSocket receives published state; chat round-trip with mock LLM.
