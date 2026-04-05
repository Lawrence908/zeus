# Zeus — Personal AI Assistant System

A self-hosted, voice-first, privacy-preserving AI assistant built from proven open-source components. Runs on consumer GPUs (RTX 3080 production, RTX 5080 dev/test).

**Status:** Foundation complete (2026-03-25). Text chat and session continuity shipped. Data ingestion pipeline in progress. [View development plan](docs/zeus_linear_ticket_plan.md).

---

## Vision

Zeus is a personal knowledge engine that knows you. It ingests your data (ChatGPT conversations, markdown files, emails), remembers context across sessions, and answers questions about your own information with voice and text interfaces. Unlike cloud assistants, everything stays on your hardware.

**Key principles:**
- Privacy-first: All data and computation remain on your server
- Voice-native: Conversational interaction is primary, text is fallback
- Modular: Swap components without rewriting the orchestration
- Extensible: Add new data sources and agents via structured interfaces

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Zeus Core (FastAPI)                  │
│          HTTP router + session management               │
└─────────────────────────────────────────────────────────┘
        ↓              ↓              ↓
    ┌───────┐     ┌────────┐    ┌──────────┐
    │ Iris  │     │ Oracle │    │ Orpheus  │
    │(Ingest)    │(Context)    │(Voice)   │
    └───────┘     └────────┘    └──────────┘
        ↓              ↓              ↓
    ┌───────────────────────────────────────┐
    │        Mnemosyne (Memory Layer)       │
    │  mem0 + Qdrant vector DB + KV store   │
    └───────────────────────────────────────┘
        ↓              ↓
    ┌──────────┐  ┌──────────┐
    │ Qdrant   │  │ Ollama   │
    │(Vector)  │  │(LLM)     │
    └──────────┘  └──────────┘
```

### Subsystems (Greek naming convention)

| Subsystem | Role | Status |
|-----------|------|--------|
| **zeus** | Main orchestration entry point | ✓ Core wired |
| **mnemosyne** | Memory layer (search, storage, retrieval) | ▶ Implementing retrieval quality |
| **iris** | Data ingest pipeline (sources → chunks → embed → store) | ▶ ChatGPT, Markdown done; Email next |
| **orpheus** | Voice interface (STT, TTS, wake word) | ⧬ Architecture defined, not yet coded |
| **aegis** | Safety layer (policy enforcement, privacy filtering) | ⧬ Config templates exist |
| **olympians** | Agent swarm (Ruflo v3.5 orchestration) | ⧬ Config exists, spike pending |
| **oracle** | Context API (structured context serving) | ✓ Full REST API implemented |
| **olympus** | Production server (RTX 3080) | ⧬ Deployment pipeline TBD |

### Tech Stack

| Layer | Component | Why |
|-------|-----------|-----|
| Orchestration | Ruflo v3.5 | Claude Code native, no framework lock-in |
| Vector DB | Qdrant | Self-hosted, scalable, namespace-aware |
| Memory | mem0 | Unified API for hybrid storage (vector + graph + KV) |
| HTTP API | FastAPI | Async-first, validated schemas, auto-docs |
| Embeddings | nomic-embed-text (Ollama) | Fast, good quality, self-hosted |
| Dev LLM | Claude API (Sonnet 4.6) | Rapid iteration during development |
| Prod LLM | Qwen2.5-7B-Instruct Q4_K_M | Fits 10GB VRAM, solid instruction-following |
| STT | WhisperLiveKit | Real-time, streaming-capable |
| TTS | Voicebox → LuxTTS | 150x realtime speed, voice cloning |
| Wake Word | openWakeWord | CPU-efficient, always-on detection |
| Container | Docker Compose | Reproducible multi-service setup |

---

## Current Status

### ✓ Complete
- **Project 0 (Foundation):** Repo structure, core FastAPI bus, Qdrant+Ollama health checks, service wiring
- **Project 1 (Text Chat + Sessions):** Session layer (`core/sessions.py`), text chat UI (`core/chat.py`), WebSocket plumbing
- **Ingest Sources:** ChatGPT export parser, Markdown file walker, context-pack migration
- **Context API:** Full REST interface (`/context/query`, `/memory/search`, `/ingest/trigger`, `/status`)
- **Query Engine:** Text-in → semantic search → LLM → response pipeline

### ▶ In Progress
- **Retrieval Quality:** mem0 integration complete, eval harness and tuning pending
- **Ruflo Spike:** Validating Ruflo v3.5 before committing Project 5 architecture
- **Email Ingest:** IMAP parser not yet implemented

### ⧬ Not Started
- **Privacy/Governance (Aegis):** Policy templates exist, enforcement layer not wired
- **Voice Pipeline (Orpheus):** STT, TTS, wake word components not integrated
- **Agent Swarm (Olympians):** Ruflo config exists pending spike validation
- **Production Deployment:** Docker stack for always-on service mode
- **Observability:** Metrics collection and admin dashboard

[Full roadmap with 90 tickets across 8 projects](docs/zeus_linear_ticket_plan.md).

---

## Project Structure

```
zeus/
├── core/                    # FastAPI entry point, router, session layer
│   ├── main.py             # App initialization, route setup
│   ├── sessions.py         # Multi-turn session continuity
│   ├── chat.py             # Text chat routes + static UI
│   ├── query.py            # Query handler (text → search → LLM → response)
│   └── voice_ws.py         # WebSocket for voice state streaming
├── api/                     # Oracle: Context API (semantic search)
│   └── main.py             # REST endpoints for context retrieval
├── memory/                  # Mnemosyne: mem0 + Qdrant integration
│   ├── config.py           # mem0 client setup
│   └── search.py           # Token-budgeted retrieval helpers
├── ingest/                  # Iris: Data ingestion pipeline
│   ├── pipeline.py         # Chunk → embed → store orchestration
│   ├── run.py              # CLI for triggering ingest
│   └── sources/            # Source-specific parsers
│       ├── chatgpt.py      # ChatGPT conversations.json parser
│       ├── markdown.py     # .md file walker with heading-aware chunking
│       └── context_pack.py # Legacy context-pack migration
├── voice/                   # Orpheus: STT, TTS, wake word (not yet coded)
│   └── state.py            # Voice-state protocol + WebSocket publisher
├── safety/                  # Aegis: Policy enforcement (templates only)
│   └── __init__.py
├── orchestration/           # Ruflo config + agent definitions
│   ├── ruflo.yaml          # Swarm orchestration config
│   └── agents/             # YAML definitions for task agents
├── models/                  # Ollama configs, prompt templates
├── docs/                    # Architecture docs, guides
└── docker-compose.yaml     # Multi-service stack (Qdrant + Ollama + Zeus)
```

---

## Getting Started

### Explore the Codebase

Start with the **architecture overview**:
- [`CLAUDE.md`](CLAUDE.md) — Full system design, naming convention, dev workflow
- [`docs/zeus_linear_ticket_plan.md`](docs/zeus_linear_ticket_plan.md) — Feature roadmap and status by project

Quick orientation by subsystem:
- **Session continuity:** `zeus/core/sessions.py` (multi-turn state; tune with `ZEUS_CONTEXT_MAX_TOKENS` / `ZEUS_SESSION_*` — see `CLAUDE.md`)
- **Query engine:** `zeus/core/query.py` (search + LLM orchestration)
- **Data ingestion:** `zeus/ingest/sources/` (source adapters)
- **Memory layer:** `zeus/memory/config.py` and `memory/search.py`
- **REST API:** `zeus/api/main.py` (semantic search endpoints)

### Run Locally

**Prerequisites:**
- Docker & Docker Compose
- Python 3.11+
- `.env` file (see `.env.example` if present)

**Start services:**
```bash
docker compose up -d
```

This brings up:
- **Qdrant** (vector DB) on port 6333
- **Ollama** (local LLM) on port 11434
- **Zeus Core** (API bus) on port 8203

**Test health:**
```bash
curl http://localhost:8203/status
```

**Access text chat:**
Open `http://localhost:8203/` in your browser.

**Ingest data:**
```bash
# Prepare ChatGPT export at ./data/raw/chatgpt/conversations.json
python -m zeus.ingest.run --source chatgpt
```

---

## Key Concepts

### Greek Naming Convention

All subsystems use Greek mythology names. This is **intentional and required** for consistency across docs, code, configs, and PRs. See `CLAUDE.md` for the full glossary and rationale.

### Environment Modes

Zeus supports two modes controlled by `ZEUS_ENV`:

| Mode | LLM | Hardware | Use Case |
|------|-----|----------|----------|
| `dev` | Claude API (Sonnet 4.6) | RTX 5080 tower | Rapid iteration, debugging |
| `prod` | Ollama (Qwen2.5-7B Q4_K_M) | RTX 3080 server | Always-on deployment |

Switch via `.env` file. All services detect and configure themselves.

### Session Continuity

Sessions persist multi-turn state with rolling summaries. Each message is append-only. By default the process uses in-memory session storage (sessions are lost on restart); swap in a durable `SessionStorage` when ready. Context size is tuned with `ZEUS_CONTEXT_MAX_TOKENS` and related `ZEUS_SESSION_*` variables (see `.env.example`). See `zeus/core/sessions.py` and `CLAUDE.md`.

### Data Ingestion Flow

```
Source (ChatGPT JSON, .md files, etc.)
  ↓ [Parser]
Chunks (headings, context windows)
  ↓ [Embedding]
Vectors (nomic-embed-text via Ollama)
  ↓ [mem0 Integration]
Qdrant namespaces (one per source type)
```

---

## Development Workflow

**Active development on RTX 5080 tower** (16GB VRAM, fast iteration).
**Production deployment to RTX 3080 server** (10GB VRAM, stable, always-on).

1. Create feature branch: `git checkout -b chrislawrencedev/LAB-XXX-description`
2. Iterate locally with `docker compose up` (uses Claude API in dev mode)
3. Write and run tests
4. Submit PR with link to Linear ticket
5. Merge to `main` (always deployable to production)

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Complete system design, code standards, orchestration guidelines |
| [`docs/zeus_linear_ticket_plan.md`](docs/zeus_linear_ticket_plan.md) | Feature roadmap, current status, dependencies |
| [`docs/SYSTEM_PROMPT.md`](docs/SYSTEM_PROMPT.md) | Ruflo agent system prompt template |

---

## Future: Open Source Roadmap

Zeus is currently a personal project. If it becomes public or open-source, this README will expand with:

- **Installation Guide:** Detailed setup for different hardware (consumer GPUs, servers, clouds)
- **Configuration Guide:** Tuning memory size, retrieval quality, LLM parameters
- **Data Import Guide:** Standard format for contributing new data sources
- **Contribution Guide:** How to add agents, safety policies, or subsystems
- **Troubleshooting:** Common issues and solutions
- **Performance Tuning:** Optimization for different hardware targets

For now, the focus is shipping core functionality and validating the architecture on real personal data.

---

## License

Personal project. No license specified yet. If released publicly, will likely use MIT or similar permissive open-source license.

---

## Questions?

- **Architecture decisions?** See `CLAUDE.md` → "Key Decisions" section
- **Feature status?** See `docs/zeus_linear_ticket_plan.md` for roadmap
- **Code style?** See `CLAUDE.md` → "Code Standards"
- **How to contribute?** Create a branch and link to a Linear ticket (if you have access)

---

*Last updated: 2026-03-25 | Zeus on GitHub: (TBD)*