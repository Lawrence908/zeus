# CLAUDE.md — Zeus Project Entry Point

> This file is the Ruflo entry point. It tells AI agents what Zeus is, how it's built, and how to work within it.

## Project Overview

Zeus is a self-hosted personal AI assistant system. It connects fragmented personal data stores (ChatGPT history, markdown files, context packs), runs local models for privacy, and provides a voice-first interface. Built on proven open-source repos, composed into a unified stack.

**Owner:** Chris — CS degree, experienced with AI tooling, self-hosts on Proxmox/Docker, runs RTX 3080 server (production) and RTX 5080 tower (dev/test).

---

## Stack

| Layer | Component | Notes |
|-------|-----------|-------|
| **Orchestration** | Ruflo v3.5 | Claude Code native, swarm agents, 60+ specialized agents |
| **Safety** | NemoClaw + OpenShell | Policy guardrails, sandboxed execution, privacy router |
| **STT** | WhisperLiveKit | SimulStreaming, real-time, GPU-accelerated |
| **TTS** | Voicebox + LuxTTS | Voice cloning, 150x realtime, REST API |
| **Wake Word** | openWakeWord | CPU-only, passive trigger |
| **Memory** | mem0 | Hybrid vector + graph + KV storage |
| **Vector DB** | Qdrant | Docker, self-hosted |
| **API Bus** | FastAPI | Routes all services |
| **Embedding** | nomic-embed-text | Via Ollama |
| **Dev Model** | Claude API (Sonnet 4.6) | Used during development |
| **Prod Model** | Qwen2.5-7B-Instruct Q4_K_M | Ollama on 3080 (10GB VRAM) |

---

## Greek Naming Convention

All Zeus components follow a Greek mythology theme:

| Name | Component |
|------|-----------|
| **zeus** | Main system / core orchestrator |
| **mnemosyne** | Memory layer (mem0 + Qdrant) |
| **hermes** | Ingest pipeline (data import) |
| **apollo** | Voice interface (STT/TTS) |
| **aegis** | Safety layer (NemoClaw/OpenShell) |
| **olympians** | Agent swarm (Ruflo agents) |
| **olympus** | Production server (3080) |
| **oracle** | Zeus Context API |

Use these names in code, configs, logs, and documentation.

---

## Repository Structure

```
zeus/
  core/           # FastAPI bus, main router, health endpoints
  orchestration/  # Ruflo config, CLAUDE.md, agent definitions
  memory/         # mem0 setup, Qdrant config, embedding utilities
  ingest/         # Data ingestion pipeline
    sources/      # chatgpt.py, markdown.py, context_pack.py
  voice/          # STT (WhisperLiveKit), TTS (Voicebox), VAD
  safety/         # NemoClaw/OpenShell config and policies
  api/            # Zeus Context API (oracle)
  models/         # Ollama configs, prompt templates
  data/           # Raw exports (gitignored), processed chunks
docs/             # Architecture docs, decision logs
tests/            # Test suites per component
```

---

## Agent Orchestration Guidelines

### Ruflo Integration

Zeus uses Ruflo v3.5 for task orchestration. Key concepts:

1. **Swarm Memory**: SQLite-backed at `.swarm/memory.db` — agents share context
2. **Hooks System**: Auto-routes tasks to specialized agents in background
3. **Lazy Loading**: 215 MCP tools available, loaded on-demand
4. **Dual Mode**: Primary Claude Code workers, fallback to OpenAI Codex

### Agent Responsibilities

When working in this repo, agents should:

- **Respect component boundaries**: Each subdirectory is a distinct service
- **Use FastAPI patterns**: All HTTP interfaces use FastAPI
- **Type everything**: Python 3.11+ with full type hints
- **Async where it matters**: Voice pipeline, API endpoints, I/O-bound operations
- **Keep services independently startable**: Each component should run standalone for testing

### Memory Operations

The memory layer (mnemosyne) uses mem0 with environment-based backend switching:

- **Development (`ZEUS_ENV=dev`)**: Claude API as extraction LLM
- **Production (`ZEUS_ENV=prod`)**: Ollama with local models

Never hardcode model endpoints — always read from environment.

---

## Code Standards

```python
# Python 3.11+, always typed
async def process_chunk(text: str, metadata: dict[str, Any]) -> ChunkResult:
    ...
```

- **FastAPI** for all HTTP interfaces
- **Docker Compose** for all service definitions
- **Type hints** always — no `Any` unless unavoidable
- **Async** for voice pipeline, API endpoints, I/O operations
- **Comments** only for non-obvious decisions
- **Composition over inheritance**
- **Each service independently startable**

---

## Development Workflow

1. **Dev & test** on 5080 tower (16GB VRAM, 14B models comfortable)
2. **Deploy** working versions to 3080 server (10GB VRAM, 7B models Q4/Q5)
3. **Branches** per tool/experiment, merge when working
4. **Test locally** before committing — each service should be runnable standalone

---

## Environment Variables

Required env vars (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `ZEUS_ENV` | `dev` or `prod` — controls model backend |
| `ANTHROPIC_API_KEY` | Claude API key (dev mode) |
| `QDRANT_HOST` | Qdrant server host |
| `QDRANT_PORT` | Qdrant server port (default: 6333) |
| `OLLAMA_HOST` | Ollama server URL (prod mode) |

---

## Quick Commands

```bash
# Start all services
docker compose up -d

# Run Zeus Core API
uvicorn zeus.core.main:app --reload --port 8000

# Check service status
curl http://localhost:8000/status

# Run tests
pytest tests/ -v

# Start Qdrant standalone
docker run -p 6333:6333 qdrant/qdrant
```

---

## Current Sprint: Sprint 0 — Foundation

**Goal**: Initialize repo, basic service scaffolding, Qdrant running.

**Deliverables**:
- [x] CLAUDE.md (this file)
- [ ] Directory structure
- [ ] docker-compose.yml
- [ ] Zeus Core /status endpoint
- [ ] mem0 config with env-based switching
- [ ] .env.example

---

## What Agents Help With

1. Writing and structuring code for any Zeus component
2. Debugging integration issues between services
3. Suggesting architecture improvements as system evolves
4. Writing Docker Compose configs, Dockerfiles, env files
5. Writing Ruflo agent definitions
6. Designing ingest pipelines for new data sources
7. Setting up and testing components before wiring together

---

## Response Style for Agents

- Be direct and specific — Chris knows what he's doing
- Show full file contents when writing new files, not snippets
- Add file path as comment at top of new files
- Flag architectural decisions that will be hard to change
- Mention known gotchas upfront
- Don't explain obvious imports
- Prefer working code over explanation
