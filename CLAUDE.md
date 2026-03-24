# Zeus — Personal AI Assistant System

Zeus is a self-hosted, voice-first, privacy-preserving AI assistant built from proven open-source components. It runs on a Proxmox homelab: production on an RTX 3080 server (Olympus), dev/test on an RTX 5080 tower.

## Stack

| Layer | Component | Notes |
|---|---|---|
| Orchestration | Ruflo v3.5 | Claude Code native, swarm agents |
| Safety | NemoClaw + OpenShell | Policy guardrails under Ruflo |
| STT | WhisperLiveKit | SimulStreaming, real-time |
| TTS | Voicebox REST API → LuxTTS | Voice cloning, 150x RT |
| Wake word | openWakeWord | CPU, passive trigger |
| Memory | mem0 | Self-hosted, hybrid vector+graph+KV |
| Vector DB | Qdrant | Docker, self-hosted, port 6333 |
| API bus | FastAPI | Routes all services |
| Embeddings | nomic-embed-text via Ollama | |
| Dev LLM | Claude API (Sonnet 4.6) | Used during development |
| Prod LLM | Qwen2.5-7B-Instruct Q4_K_M | Ollama on 3080 (10GB VRAM) |

## Greek Naming Convention

All subsystems use Greek mythology names. Agents and humans working in this repo must use these names consistently in code, configs, logs, and docs.

- **zeus** — main system, orchestration entry point
- **mnemosyne** — memory layer (mem0 + Qdrant)
- **iris** — ingest pipeline (data sources → processed chunks)
- **orpheus** — voice interface (STT + TTS + wake word)
- **aegis** — safety layer (NemoClaw + OpenShell policies)
- **olympians** — agent swarm (Ruflo-managed task agents)
- **olympus** — production server (RTX 3080)
- **oracle** — Zeus Context API (serves structured context to agents)

## Repo Structure

```
zeus/
  core/           # FastAPI bus, main router, health checks
  orchestration/  # Ruflo config, CLAUDE.md, agent definitions
  memory/         # mem0 setup, Qdrant config, embed utils
  ingest/         # Iris data ingestion pipeline
  ingest/sources/ # Source-specific parsers (chatgpt.py, markdown.py, etc.)
  voice/          # Orpheus: STT (WhisperLiveKit), TTS (Voicebox), VAD
  safety/         # Aegis: NemoClaw/OpenShell config and policies
  api/            # Oracle: Zeus Context API
  models/         # Ollama configs, prompt templates
  data/           # Raw exports (gitignored), processed chunks
  docs/           # Architecture docs
```

## Agent Orchestration Guidelines

Ruflo manages a swarm of task-specific agents (olympians). Each agent:

1. Has a single responsibility defined in `orchestration/agents/`
2. Communicates through the FastAPI bus (`core/`)
3. Can read from mnemosyne (memory) but writes go through iris (ingest)
4. Must respect aegis (safety) policies — no unfiltered LLM output reaches the user
5. Uses oracle (Context API) for structured personal context

### Agent Definition Format

Agent definitions live in `orchestration/agents/<name>.yaml` and follow this structure:

```yaml
name: <agent_name>
description: <what this agent does>
model: <claude-sonnet-4-6 | qwen2.5-7b-instruct>
tools:
  - <tool_name>
context:
  - <oracle endpoint or memory namespace>
safety:
  policy: <aegis policy name>
```

### Environment Switching

The system supports two environments controlled by `ZEUS_ENV`:

- `dev` — Uses Claude API for LLM calls, runs on 5080 tower, verbose logging
- `prod` — Uses Ollama (Qwen2.5-7B) for LLM calls, runs on 3080 server, structured logging

All services must check `ZEUS_ENV` and configure themselves accordingly. Never hardcode model names or API endpoints.

## Code Standards

- Python 3.11+ for all services
- FastAPI for all HTTP interfaces
- Docker Compose for all service definitions
- Type hints always
- Async where it matters (voice pipeline, API endpoints)
- Comments only for non-obvious decisions
- Prefer composition over inheritance
- Each service must be independently startable for testing
- File paths as comments at the top of each file

## Development Workflow

- Dev & test on 5080 tower (16GB VRAM, 14B models comfortable)
- Deploy working versions to 3080 server (10GB VRAM, 7B models Q4/Q5)
- Branches per tool/experiment, merge when working
- `main` branch is always deployable to Olympus

## Key Decisions

- mem0 was chosen over raw Qdrant because it handles hybrid storage (vector + graph + KV) with a single API, reducing integration surface
- Ruflo v3.5 over LangGraph/CrewAI because it's Claude Code native and supports swarm patterns without framework lock-in
- Voicebox + LuxTTS over Coqui/Bark because 150x realtime speed makes conversational latency viable on consumer GPUs
- Qwen2.5-7B Q4_K_M fits in 10GB VRAM on the 3080 while maintaining instruction-following quality adequate for structured agent tasks
