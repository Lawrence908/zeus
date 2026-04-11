# Zeus — Personal AI Assistant System

Zeus is a self-hosted, voice-first, privacy-preserving AI assistant built from proven open-source components. It runs on a Proxmox homelab: production on an RTX 3080 server (Olympus), dev/test on an RTX 5080 tower.

**This file (`CLAUDE.md` at repo root)** is the primary project brief for humans and for AI assistants (Claude Code, Cursor, etc.): stack, naming, layout, and conventions. Prefer updating it when assumptions change rather than scattering one-off context in chats.

## Stack

| Layer | Component | Notes |
|---|---|---|
| Orchestration | Ruflo v3.5 | Claude Code native, swarm agents |
| Safety | NemoClaw + OpenShell | Policy guardrails under Ruflo |
| STT | WhisperLiveKit | SimulStreaming, real-time |
| TTS | Voicebox REST API → LuxTTS | Voice cloning, 150x RT |
| Wake word | openWakeWord | CPU, passive trigger |
| Memory | mem0 | Self-hosted, hybrid vector+graph+KV |
| Sessions | Zeus session layer | Multi-turn chat/voice continuity + rolling summaries |
| Vector DB | Qdrant | Docker, self-hosted, port 6333 |
| API bus | FastAPI | Routes all services |
| Chat UI | FastAPI static/chat routes | Local text interface for dev + fallback use |
| MCP | Zeus MCP server | Exposes context/profile/memory tools to MCP clients |
| Observability | Zeus admin/metrics | Query and ingest metrics + operational status |
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
- **kairos** — background agent daemon (observe–decide–act cycles, generalised autonomy loop)

## Repo Structure

Repository root (this folder is the git checkout; `CLAUDE.md` lives here):

```
docs/             # Repo-level docs: Linear plan, phase/cursor prompts, ops runbooks (e.g. NemoClaw on hosts)
compose.yaml      # Docker Compose for core services
zeus/             # Python application package
  core/           # FastAPI bus, main router, health checks
  orchestration/  # Ruflo config, agent definitions (see orchestration/CLAUDE.md if present)
  memory/         # mem0 setup, Qdrant config, embed utils
  ingest/         # Iris data ingestion pipeline
  ingest/sources/ # Source-specific parsers (chatgpt.py, markdown.py, etc.)
  voice/          # Orpheus: STT (WhisperLiveKit), TTS (Voicebox), VAD
  safety/         # Aegis: NemoClaw/OpenShell config and policies
  api/            # Oracle: Zeus Context API
  mcp/            # Zeus MCP server and tool definitions
  core/static/    # Chat/admin UI assets
  core/chat.py    # Text chat routes
  core/sessions.py # Session lifecycle and continuity logic
  models/         # Ollama configs, prompt templates
  data/           # Raw exports (gitignored), processed chunks
  docs/           # Specs & architecture: MCP, Orpheus, ingest, deployment, sessions, roadmap
```

### Documentation layout (two `docs/` trees — do not conflate)

| Path | Use for |
|------|--------|
| **`docs/`** (repo root) | Planning and tracking (`ZEUS_LINEAR_TICKET_PLAN.md`), phase/cursor prompt artifacts, **host and ops runbooks** (e.g. `nemoclaw-ops.md`). Paths in prose are **`docs/<file>.md`** — not `zeus/docs/`. |
| **`zeus/docs/`** | **Product and subsystem design**: architecture, deployment, MCP/chat/orpheus/sessions specs, ingest guides, roadmap. Paths are **`zeus/docs/<file>.md`**. |

When adding a doc, pick the tree by audience: **ops / Linear / phases** → root `docs/`; **how Zeus is built and behaves** → `zeus/docs/`. When you link from either place, use the **path from repo root** so links stay unambiguous.

## Agent Orchestration Guidelines

Ruflo manages a swarm of task-specific agents (olympians). Each agent:

1. Has a single responsibility defined in `orchestration/agents/`
2. Communicates through the FastAPI bus (`core/`)
3. Can read from mnemosyne (memory) but writes go through iris (ingest)
4. Must respect aegis (safety) policies — no unfiltered LLM output reaches the user
5. Uses oracle (Context API) for structured personal context

### Orchestration principles

Zeus treats **orchestration** (task loops, tools, memory discipline, validation) as the main lever for capability — not incremental model changes alone.

- **Tool-first:** Agents call concrete tools (`olympian_file_read`, `olympian_search`, `olympian_memory_search`, `olympian_shell` [gated]) rather than reasoning in chat. Tool arguments are validated by the Aegis pre-hook (`zeus/safety/integration.py` `aegis_bus_pre_hook`) before the bus forwards any call. New tools go in `zeus/mcp/olympian_tools.py` and are registered in `zeus/mcp/server.py`.
- **Structured memory:** `QueryEngine` (`zeus/core/query.py`) fetches up to 5 relevant chunks via `search_memories()` and profile facts via `get_profile_facts()` before each LLM call. Session context comes from `SessionManager.get_context_window()` (`zeus/core/sessions.py`): a **single heuristic budget** `ZEUS_CONTEXT_MAX_TOKENS` (default 6144) splits **⅓** to retrieved memories and **⅔** to the session block (rolling summary plus recent turns). Recent turns are **packed newest-first** into that token budget (≈4 chars/token); only the newest `ZEUS_SESSION_PACK_MAX_TURNS` (default 150, `0` = unlimited) are candidates before packing. When stored turns reach `ZEUS_SESSION_SUMMARY_AT_TURNS` (default 200), older dialogue is merged into a rolling summary and only the last `ZEUS_SESSION_KEEP_RAW_TURNS` (default 150) stay as full turns. Durable long-term storage is mem0 + Qdrant; chat session state uses `InMemoryStorage` in `zeus/core/main.py` until a durable `SessionStorage` implementation is wired.
- **Plan, execute, reflect:** Multi-step tasks use `TaskRunner` (`zeus/orchestration/runtime.py`) which iterates `AgentStep` objects, collects `StepResult`, and supports `on_failure: retry`. `QueryEngine.query()` retries LLM calls up to 3 times with a refined prompt when `_is_empty_or_failed_reply()` returns True. The reflection loop is subject to Aegis on every attempt — no safety bypass for autonomy.

Roadmap detail for runtime/bus/hooks and related backlog items lives in **`docs/ZEUS_LINEAR_TICKET_PLAN.md`** (Projects 7 and 10).

### Agentic Safety Contract

Every autonomous code path (bus calls, KAIROS cycles, TaskRunner steps) must pass through Aegis:

1. **Pre-execution** — `aegis_bus_pre_hook` validates tool arguments before `bus_call()` forwards them. Prompt injection patterns are rejected at the bus layer (`zeus/safety/policies/standard.yaml`, rule `prompt_injection_attempt`).
2. **Post-execution** — `aegis_bus_post_hook` filters LLM output before it returns from `bus_call()`. For `QueryEngine` paths, `evaluate_text()` runs on the assembled reply.
3. **Tool gating** — `olympian_shell` requires `ZEUS_SHELL_ENABLED=1` and a non-empty `ZEUS_SHELL_ALLOWLIST`. KAIROS daemon defaults to read-only tools only (`ZEUS_KAIROS_TOOL_ALLOWLIST`). Never widen an allowlist in a PR without a safety review comment.
4. **No silent failures** — Aegis rejections raise, log at WARNING level, and return a structured error to the caller.

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
- Text chat is intentionally included as a first-class fallback to accelerate development and support non-voice interaction modes
- MCP exposure is a first-class integration boundary so Zeus memory/context can be reused by external assistant clients
- Session continuity is required for natural multi-turn interactions across both chat and voice paths
- Observability is mandatory once always-on deployment begins (query latency, ingest cadence, service health)

## Writing Style

- **No emdashes**: Never use emdashes (the long dash character) in generated text. Use commas, semicolons, colons, or restructure sentences instead.
