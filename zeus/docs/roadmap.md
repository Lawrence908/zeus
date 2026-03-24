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

6. **Add Orpheus to `compose.yaml`** (optional — voice pipeline may stay host-native for audio device access)

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

## Post-Sprint 4 — Future Work

These are tracked but not yet scoped into sprints. Pick up after Olympus is stable.

**Continuous ingest** — Iris runs on a schedule (cron or Ruflo timer) to pick up new notes/exports automatically.

**Memory consolidation** — mem0 deduplication pass: merge overlapping memories, promote frequently-accessed ones.

**Additional ingest sources:**
- Obsidian vault sync
- Browser history (selective)
- Calendar/task data (Google Calendar, Todoist)
- Git commit messages from active projects

**Multi-agent tasks** — use Ruflo's swarm mode to dispatch parallel olympians for research, summarisation, code review.

**Web UI** — minimal local dashboard (Next.js or plain HTML) showing memory stats, recent queries, ingest history.

**Telephony** — route voice to a SIP endpoint so Zeus can answer calls via a physical handset or phone number.
