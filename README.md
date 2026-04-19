# Zeus: Personal AI Assistant System

A self-hosted, voice-first, privacy-preserving AI assistant built from proven open-source components. Runs on consumer GPUs (RTX 3080 production, RTX 5080 dev) and keeps all data and computation on your own hardware.

**Status (2026-04-18):** Foundation, memory + knowledge + reference retrieval, text chat, Telegram bot, MCP server, benchmarks, and Aegis safety layer are live. Voice pipeline is scaffolded; Kairos background daemon is opt-in. Olympus production deploy pending.

> Docs map: [`docs/INDEX.md`](docs/INDEX.md). Project brief: [`CLAUDE.md`](CLAUDE.md). Ticket plan: [`docs/ZEUS_LINEAR_TICKET_PLAN.md`](docs/ZEUS_LINEAR_TICKET_PLAN.md).

---

## Vision

Zeus is a personal knowledge engine that knows you. It ingests your data (markdown notes, Obsidian vault, ChatGPT exports, newsletters, bookmarks), remembers context across sessions, and answers questions over a three-layer retrieval architecture. Unlike cloud assistants, everything stays on your hardware.

Principles:

- **Privacy-first.** All data stays local. PII-bearing LLM calls are gated to providers with strict retention guarantees; free tiers that train on input are excluded.
- **Voice-native.** Wake word to STT to LLM to TTS runs as a streaming host-native pipeline. Text and Telegram are first-class fallbacks.
- **Modular.** Swap a component (chat LLM, embedder, reranker, storage backend) without rewriting orchestration.
- **Tool-first.** Agents call concrete tools (MCP) with Aegis validation on every call.

---

## Architecture

```text
              ┌─────────────────────────────────────────────┐
              │           Zeus Core (FastAPI, 8203)         │
              │  chat · oracle · admin · orchestration ·    │
              │  voice-state · newsletter · benchmarks      │
              └─────────────────────────────────────────────┘
                 │              │                │         │
          ┌──────┴──────┐  ┌────┴─────┐   ┌──────┴──────┐ ┌┴────────┐
          │ QueryEngine │  │  Iris    │   │  Kairos     │ │ MCP     │
          │ retrieval + │  │  ingest  │   │  daemon     │ │ server  │
          │ reflection  │  │ pipeline │   │ (optional)  │ │ FastMCP │
          └──────┬──────┘  └────┬─────┘   └──────┬──────┘ └─────────┘
                 │              │                │
     ┌───────────┼──────────────┼────────────────┘
     │           │              │
┌────┴────┐ ┌────┴──────┐ ┌────┴──────┐ ┌──────────────┐
│ Profile │ │ Memories  │ │ Knowledge │ │ Reference    │
│ facts   │ │ (curated) │ │ (bulk)    │ │ (live proxy) │
└────┬────┘ └────┬──────┘ └────┬──────┘ └──────┬───────┘
     │          │              │               │
     └────┬─────┘              │          kiwix / NOMAD
          ▼                    ▼
    Qdrant `zeus_memories`    Qdrant `zeus_knowledge`
    (MemoryStore,             (KnowledgeStore, dense +
     bi-temporal, LLM-         BM25 RRF hybrid, optional
     extracted facts)          BGE-reranker-v2-m3)
          │                    │
          └──────┬─────────────┘
                 ▼
          Ollama (nomic-embed-text 768d + chat model)
```

Voice: openWakeWord → WhisperLiveKit STT → QueryEngine → Voicebox + LuxTTS. Phaos publishes voice-state to a React orb via WebSocket.

Full subsystem map: [`zeus/docs/architecture.md`](zeus/docs/architecture.md).

### Subsystems (Greek naming)

| Name | Role | State |
|------|------|-------|
| **zeus** | Main orchestration, FastAPI bus | Live |
| **mnemosyne** | Memory layer (`MemoryStore`, `zeus_memories`) | Live |
| **library / knowledge** | Bulk RAG (`KnowledgeStore`, `zeus_knowledge`) | Live |
| **reference** | Live proxy for kiwix and NOMAD | Live |
| **iris** | Ingest pipeline, per-source routing | Live |
| **oracle** | Context API (`/context/query`, `/context/profile`, `/memory/*`) | Live |
| **orpheus** | Voice interface (wake, STT, TTS) | Scaffolded; needs end-to-end validation |
| **phaos** | Voice-state visualization (WebSocket + Three.js orb in React) | Live |
| **aegis** | Safety layer (YAML policies + bus pre/post hooks) | Live |
| **olympians** | Ruflo agent swarm | YAML manifests + runtime wired |
| **kairos** | Background observe-decide-act daemon | Shipped, off by default |
| **olympus** | Production server (RTX 3080) | Deploy pending; daedalus hosts today |

### Tech stack

| Layer | Component | Why |
|-------|-----------|-----|
| Orchestration | Ruflo v3.5 manifests + Zeus `AgentRuntime` | Claude Code native, no framework lock-in |
| Vector DB | Qdrant 1.15+ | Self-hosted, native BM25 sparse vectors, RRF fusion |
| Memory | `zeus/memory/store.py` (`MemoryStore`) | Hand-rolled; replaced mem0 in April 2026 |
| Knowledge | `zeus/memory/library.py` (`KnowledgeStore`) | Dense + BM25 hybrid, optional BGE-reranker |
| Small-task LLM | `zeus/core/small_llm.py` | Provider router with privacy-tier gate and daily USD cap |
| Chat LLM (dev) | Claude Sonnet 4.6 via Anthropic API | Best quality during iteration |
| Chat LLM (prod) | Ollama `qwen2.5:7b-instruct` Q4_K_M | Fits 10 GB VRAM on the 3080 |
| Embeddings | `nomic-embed-text:v1.5` via Ollama | 768-dim cosine, fast, self-hosted |
| HTTP API | FastAPI on port 8203 | Async-first, validated schemas |
| MCP | `zeus/mcp/server.py` (FastMCP) | Zeus memory exposed to Cursor / Claude Desktop |
| STT | WhisperLiveKit | Real-time, streaming, SimulStreaming |
| TTS | Voicebox REST + LuxTTS | 150x realtime, voice cloning |
| Wake word | openWakeWord | CPU, always-on |
| Frontend | Vite + React + `@react-three/fiber` | SPA chat + settings + Phaos orb |
| Container | Docker Compose | Qdrant + Ollama + Whisper + Zeus Core |

---

## Current status

**Live:**

- Foundation, compose stack, `compose.override.yaml` dev bind-mount pattern
- Memory layer (`MemoryStore`) with bi-temporal payloads and LLM fact extraction via `small_llm_call`
- Knowledge layer (`KnowledgeStore`) with hybrid dense + BM25 RRF retrieval and optional BGE-reranker
- Reference layer (kiwix + NOMAD HTTP proxies)
- QueryEngine retrieval fan-out with sub-budgeted context blocks
- Small-LLM router (Gemini paid, Groq, OpenRouter, Anthropic Haiku, Ollama) with daily USD cap
- Text chat + SSE streaming + sessions (in-memory or SQLite)
- Telegram bot with allow-list, Aegis filter, plain-text replies, runtime hot-restart
- MCP server: `zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_memory_search`, `zeus_ingest_trigger`
- Aegis policy engine with pre + post bus hooks
- Agent runtime, bus, hooks, `TaskRunner`, correlation IDs
- Kairos daemon (off by default, read-only tool allowlist)
- Ingest sources: context_pack, markdown, obsidian, chatgpt, email, newsletter, bookmarks, git, gcal
- Benchmarks module with per-host JSON persistence and UI surface
- React SPA for chat, settings, agents, orb

**Near-term:**

- Olympus deploy (daedalus is the current always-on host)
- Retrieval eval extension with labelled Profile vs Knowledge ground truth
- End-to-end voice latency validation on the 3080
- Kairos observability surfaces

Full ticket-level roadmap: [`docs/ZEUS_LINEAR_TICKET_PLAN.md`](docs/ZEUS_LINEAR_TICKET_PLAN.md).

---

## Repository layout

```text
docs/             # Ops runbooks, Linear plan, memory-architecture plan, INDEX.md
compose.yaml
compose.override.yaml   # Dev bind-mount of ./zeus into zeus-core
zeus/
  core/           # FastAPI main, chat, admin, query, sessions, voice_ws, small_llm, runtime_settings, newsletter, bench-API
  core/prompts/   # chat_system.md, memory_extract.md (ZEUS_PROMPT_RELOAD=1 for hot reload)
  core/static/    # admin.html, chat.html, viz/, newsletters.html, app/ (built React SPA)
  orchestration/  # runtime.py, bus.py, hooks.py, daemon.py, ruflo.yaml, agents/*.yaml
  memory/         # store.py, library.py, reference.py, reranker.py, search.py, eval.py, _embed.py, config.py
  ingest/         # pipeline.py, run.py, config.py, config.yaml, sources/*, scheduler.py
  voice/          # state.py, stt.py, tts.py, wake.py, pipeline.py
  safety/         # policy_engine.py, integration.py, policies/*.yaml
  api/            # Oracle: context + profile + memory search
  mcp/            # server.py, tools.py
  bench/          # runner.py, __main__.py
  integrations/telegram/   # bot.py
  frontend/       # Vite + React + TypeScript SPA
  docs/           # Subsystem and product specs (see docs/INDEX.md)
  data/           # Raw exports, processed chunks, SQLite DBs (all gitignored)
tests/            # retrieval_eval.py + baselines
```

---

## Getting started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- NVIDIA Container Toolkit (for GPU-backed Ollama and Whisper)
- `.env` populated from [`.env.example`](.env.example). At minimum: `ANTHROPIC_API_KEY` for dev, or none for all-local Ollama.

### Start services

```bash
docker compose up -d
docker compose ps
curl http://localhost:8203/status | jq
```

Brings up Qdrant (6333), Ollama (11435), WhisperLiveKit (9090), and Zeus Core (8203).

### First ingest

```bash
# Curated profile sources (memory layer, LLM fact extraction)
docker exec zeus-core python -m zeus.ingest.run --target memory

# Bulk sources (knowledge layer, raw embed)
docker exec zeus-core python -m zeus.ingest.run --target knowledge
```

Per-source routing lives in [`zeus/ingest/config.yaml`](zeus/ingest/config.yaml). See [`zeus/docs/ingest-guide.md`](zeus/docs/ingest-guide.md) for priority order and [`zeus/docs/ingest-paths.md`](zeus/docs/ingest-paths.md) for raw-data layout.

### Chat

- Web: open `http://localhost:8203/` (React SPA).
- Telegram: set `TELEGRAM_ENABLED=1` plus token and allow-list; bot starts in the FastAPI lifespan.
- MCP: point Cursor or Claude Desktop at `python -m zeus.mcp.server`. See [`zeus/docs/mcp-server-spec.md`](zeus/docs/mcp-server-spec.md).

### Run the benchmark suite

```bash
docker exec zeus-core python -m zeus.bench
```

Writes per-model tok/s + TTFT + prompt-eval to `zeus/data/benchmarks.json`; results show up in the Settings UI. Measured on the 3080: `qwen2.5:7b-instruct` 119 tok/s, `llama3.1:8b-instruct` 113 tok/s, `qwen3:8b` 100 tok/s. Full context in [`zeus/docs/model-comparison.md`](zeus/docs/model-comparison.md).

---

## Key concepts

**Three-layer retrieval.** `QueryEngine._collect_retrieval_context()` runs profile, memory, knowledge, and reference lookups in parallel and renders them as labelled blocks in the system prompt. Sub-budgets: profile 20%, memory 25%, knowledge 45%, reference 10%, all under `ZEUS_CONTEXT_MAX_TOKENS` (default 6144). The other 2/3 of the context budget is the session block.

**Two LLM layers.** `_run_llm()` is the chat path (Claude in dev, Ollama in prod, 3-attempt reflection). `small_llm_call()` is the batch / structured-output path (fact extraction, titles, classifiers) with a privacy-tier gate and a daily USD cap. LiteLLM is forbidden (March 2026 supply-chain attack).

**Environment modes.**

| Mode | Chat LLM | Hardware | Use case |
|------|----------|----------|----------|
| `dev` | Claude Sonnet 4.6 | RTX 5080 tower or daedalus | Rapid iteration |
| `prod` | Ollama `qwen2.5:7b-instruct` | RTX 3080 (Olympus) | Always-on |

Switch via `ZEUS_ENV` and optionally `ZEUS_LLM`. See [`zeus/docs/deployment.md`](zeus/docs/deployment.md).

**Session continuity.** `SessionManager` in `zeus/core/sessions.py`. In-memory by default; set `ZEUS_SESSION_BACKEND=sqlite` to persist to `zeus/data/sessions.db`. Rolling summary fires at `ZEUS_SESSION_SUMMARY_AT_TURNS` (default 200), keeping the last `ZEUS_SESSION_KEEP_RAW_TURNS` (default 150) as raw turns. See [`zeus/docs/sessions-spec.md`](zeus/docs/sessions-spec.md).

**Aegis safety.** Every autonomous code path passes through the policy engine. `aegis_bus_pre_hook` validates tool arguments; `aegis_bus_post_hook` filters LLM output. Policies live in `zeus/safety/policies/`. Optional NemoClaw + OpenShell host sandbox for OS-level isolation: [`docs/nemoclaw-ops.md`](docs/nemoclaw-ops.md).

---

## Development workflow

Dev on the 5080 tower or daedalus; `compose.override.yaml` bind-mounts `./zeus` read-only into `zeus-core` so pure-Python edits take effect with a container restart. Production hosts do not apply the override; they run a baked image.

1. Create a feature branch: `git checkout -b chrislawrencedev/LAB-XXX-description`
2. Iterate locally with `docker compose up -d`
3. Run tests: `pytest` + `python -m zeus.memory.eval` for retrieval
4. Run `python -m zeus.bench` if you touched model config
5. Open a PR linked to the Linear ticket
6. Merge to `main` (always deployable)

Docs freshness is enforced by a git pre-commit hook:

```bash
ln -sf ../../scripts/check-docs.sh .git/hooks/pre-commit
```

It fails the commit on forbidden package tokens (`mem0ai`, `litellm`) outside historical framing and on any `.md` file under `docs/` or `zeus/docs/` that isn't listed in `docs/INDEX.md`. Emdashes in prose are reported as warnings.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`docs/INDEX.md`](docs/INDEX.md) | Map of every doc with audience tags |
| [`CLAUDE.md`](CLAUDE.md) | Primary project brief for humans and AI collaborators |
| [`docs/ZEUS_LINEAR_TICKET_PLAN.md`](docs/ZEUS_LINEAR_TICKET_PLAN.md) | Ticket-level roadmap |
| [`docs/SYSTEM_PROMPT.md`](docs/SYSTEM_PROMPT.md) | AI-collaborator bootstrap prompt |
| [`docs/memory-architecture-plan.md`](docs/memory-architecture-plan.md) | Three-layer memory plan + migration runbook |
| [`docs/nemoclaw-ops.md`](docs/nemoclaw-ops.md) | NemoClaw + OpenShell operational runbook |
| [`zeus/docs/architecture.md`](zeus/docs/architecture.md) | Subsystem map |
| [`zeus/docs/deployment.md`](zeus/docs/deployment.md) | Deployment runbook |
| [`zeus/docs/model-comparison.md`](zeus/docs/model-comparison.md) | Measured tok/s and VRAM fit per model |

---

## License

Personal project. No license specified. If released publicly, likely MIT or similar permissive.

---

*Last updated: 2026-04-18.*
