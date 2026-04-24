# Zeus: Personal AI Assistant System

Zeus is a self-hosted, voice-first, privacy-preserving AI assistant built from proven open-source components. It runs on a Proxmox homelab with consumer GPUs: a smaller always-on production GPU (e.g. 10 GB VRAM for a 7B Q4/Q5 chat model) and a larger dev GPU for iteration. The example deployment targets RTX 3080 (prod, "olympus") and RTX 5080 (dev) — substitute your own hardware.

**This file (`CLAUDE.md` at repo root)** is the primary project brief for humans and for AI assistants (Claude Code, Cursor). Stack, naming, layout, and conventions live here. Prefer updating it when assumptions change rather than scattering one-off context in chats. Companion doc index: [docs/INDEX.md](docs/INDEX.md).

## Stack

| Layer | Component | Notes |
|---|---|---|
| Memory (Mnemosyne) | `zeus/memory/store.py` (`MemoryStore`) | Qdrant + Ollama embed. LLM fact extraction via `small_llm_call`. Replaced mem0 in April 2026 after the v2.0.0 rewrite and repeated breaking changes. Bi-temporal payload with `valid_from` / `valid_until` ISO-8601 strings, `category`, `contains_pii`, `confidence`. |
| Knowledge (Library) | `zeus/memory/library.py` (`KnowledgeStore`) | Qdrant collection `zeus_knowledge`, dense + BM25 hybrid fusion (RRF) with optional BGE-reranker-v2-m3. Feature flags: `ZEUS_KNOWLEDGE_HYBRID` (default 1), `ZEUS_KNOWLEDGE_RERANK` (default 0). No LLM on the write path. |
| Reference | `zeus/memory/reference.py` | Live HTTP proxy: kiwix-serve for Wikipedia ZIM, optional NOMAD Qdrant RAG. Query-time only, nothing ingested. `ZEUS_KIWIX_ENABLED`, `ZEUS_NOMAD_ENABLED`. |
| Small-task LLMs | `zeus/core/small_llm.py` | Provider router for batch / structured-output tasks (fact extraction, titles, classifiers). Default chain: `gemini_paid,groq,openrouter,anthropic_haiku,ollama`. Every call declares `min_privacy_tier` (1 or 2). Gemini free tier trains on input and is not in the chain. LiteLLM is explicitly forbidden (March 2026 supply-chain attack). Daily USD cap `ZEUS_SMALL_LLM_DAILY_USD_CAP` (default `2.00`); usage ledger in `zeus/data/small_llm_usage.db`. |
| Chat LLM | `zeus/core/query.py` (`_run_llm`) | Claude Sonnet in dev, Ollama in prod. Env-gated via `ZEUS_ENV` and `ZEUS_LLM`. Reflection loop (up to 3 retries) on empty or failed replies. |
| Orchestration | Ruflo v3.5 config + Zeus `AgentRuntime` | YAML agent manifests in `zeus/orchestration/agents/`. `AgentRuntime` (`zeus/orchestration/runtime.py`) owns lifecycle. Bus in `zeus/orchestration/bus.py` with Aegis pre/post hooks. |
| Safety (Aegis) | `zeus/safety/policy_engine.py` + YAML policies | In-process regex/keyword rules on LLM output and tool payloads. Policies under `zeus/safety/policies/`: `standard`, `personal`, `voice`, `ingest`, `memory`, `code_execution`, `citation_required`, `default`. Optional NemoClaw + OpenShell OS sandbox runs on the host (see `docs/nemoclaw-ops.md`). |
| Background agent | `zeus/orchestration/daemon.py` (Kairos) | Observe / decide / act / update loop. Gated by `ZEUS_KAIROS_ENABLED`. Default tool allowlist is read-only (`ZEUS_KAIROS_TOOL_ALLOWLIST`, currently `zeus_memory_search`). Every tool call passes `aegis_bus_pre_hook` before dispatch. |
| STT | WhisperLiveKit (Docker, port 9090) | SimulStreaming, real-time. |
| TTS | Voicebox REST API with LuxTTS engine | Voice cloning, 150x realtime. Host-managed. |
| Wake word | openWakeWord | CPU, passive trigger. |
| Sessions | `zeus/core/sessions.py` | In-memory by default; `ZEUS_SESSION_BACKEND=sqlite` switches to `SQLiteSessionStorage` at `zeus/data/sessions.db`. Rolling summary at `ZEUS_SESSION_SUMMARY_AT_TURNS` (200), keep-raw at `ZEUS_SESSION_KEEP_RAW_TURNS` (150). |
| Vector DB | Qdrant 1.15+ (Docker, port 6333) | Two collections: `zeus_memories` (bi-temporal facts) and `zeus_knowledge` (dense + optional sparse BM25 vectors). |
| Embeddings | `nomic-embed-text:v1.5` via Ollama | 768-dim cosine. |
| API bus | FastAPI on port 8203 | All HTTP surfaces mount here: chat, oracle, admin, orchestration, voice, newsletter. |
| Chat UI | React SPA in `zeus/frontend/`, served from `zeus/core/static/app/` | Legacy static `chat.html` / `admin.html` / `viz/` still present for fallback. |
| MCP | `zeus/mcp/server.py` (FastMCP) | Memory tools: `zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_ingest_trigger`, `zeus_memory_search`. Olympian read tools: `olympian_status_read`, `olympian_server_health`, `olympian_file_read`, `olympian_file_search`, `olympian_action_list`, `zeus_calendar_today`, `zeus_newsletter_latest`. Olympian write tools (gated by `ZEUS_MCP_ALLOW_WRITE`): `olympian_inbox_append`, `olympian_action_run`. The action runner additionally requires `ZEUS_ACTIONS_ENABLED=1`. Each tool is mirrored as a chat-path `ToolSpec` in `zeus/core/tools/` and exposed through both surfaces. |
| Telegram | `zeus/integrations/telegram/bot.py` | python-telegram-bot, Aegis-filtered plain-text replies, chat-id allowlist. Runtime-restartable via `PATCH /admin/settings`. |
| Observability | `zeus/core/admin.py` + React Settings page | `/admin/metrics`, `/admin/ingest/stats`, runtime model switcher, benchmarks. In-process query-log ring buffer. |
| Benchmarks | `zeus/bench/` | Per-model tok/s, TTFT, prompt-eval rate. `GET /models/benchmarks`, `POST /models/benchmarks/run`, CLI `python -m zeus.bench`. Results in `zeus/data/benchmarks.json`. |

## Greek Naming Convention

All subsystems use Greek mythology names. Agents and humans working in this repo must use these names consistently in code, configs, logs, and docs.

- **zeus** main system, orchestration entry point
- **mnemosyne** memory layer (MemoryStore + Qdrant, LLM fact extraction via `small_llm_call`)
- **athena / library** bulk RAG knowledge layer (`KnowledgeStore` over `zeus_knowledge`)
- **reference** live external-source proxy (kiwix, NOMAD)
- **iris** ingest pipeline (data sources to processed chunks)
- **orpheus** voice interface (STT + TTS + wake word)
- **phaos** voice-state visualization (WebSocket + Three.js orb)
- **aegis** safety layer (YAML policies; optional NemoClaw + OpenShell on host)
- **olympians** agent swarm (Ruflo-managed task agents)
- **olympus** production server (the always-on host, typical: RTX 3080-class)
- **oracle** Zeus Context API (serves structured context to agents)
- **kairos** background agent daemon (observe, decide, act, update cycles)

## Repo Structure

```text
docs/             # Repo-level: Linear plan, ops runbooks, doc index (see docs/INDEX.md)
compose.yaml      # Docker Compose for core services (qdrant, ollama, whisper, zeus-core)
compose.override.yaml  # Dev-only bind mount of ./zeus into zeus-core for hot edits
zeus/             # Python application package
  core/           # FastAPI main, chat, admin, query, sessions, voice_ws, small_llm, runtime_settings, bench-API, newsletter
  core/prompts/   # chat_system.md, memory_extract.md (editable with ZEUS_PROMPT_RELOAD)
  core/static/    # admin.html, chat.html, viz/, newsletters.html, app/ (built React SPA)
  orchestration/  # CLAUDE.md + runtime.py, bus.py, hooks.py, daemon.py (Kairos), ruflo.yaml, agents/*.yaml
  memory/         # CLAUDE.md + store.py (MemoryStore), library.py (KnowledgeStore), reference.py, reranker.py, search.py, eval.py, _embed.py, config.py
  ingest/         # CLAUDE.md + pipeline.py, run.py, config.py, config.yaml, sources/*, scheduler.py
  voice/          # CLAUDE.md + state.py, stt.py, tts.py, wake.py, pipeline.py
  safety/         # policy_engine.py, integration.py, policies/*.yaml, workspace-templates/
  api/            # Oracle: context + profile + memory search
  mcp/            # server.py (FastMCP), tools.py
  bench/          # runner.py, __main__.py (CLI)
  integrations/
    telegram/     # bot.py
  frontend/       # Vite + React SPA source (builds into core/static/app/)
  docs/           # Product and subsystem design (see docs/INDEX.md for full map)
  data/           # Raw exports, processed chunks, SQLite DBs (all gitignored)
tests/            # retrieval_eval.py + baselines
```

**Subsystem `CLAUDE.md` files** add scoped context when you are editing a specific tree (`memory/`, `ingest/`, `voice/`, `orchestration/`). Claude Code auto-loads the nearest one; it layers on top of this root brief rather than replacing it. Keep invariants and "what not to do" items at the subsystem level so root stays readable.

### Documentation layout (two `docs/` trees, do not conflate)

| Path | Use for |
|------|--------|
| **`docs/`** (repo root) | Planning and tracking (`ZEUS_LINEAR_TICKET_PLAN.md`), host and ops runbooks (`nemoclaw-ops.md`), memory-architecture plan, `SYSTEM_PROMPT.md` bootstrap prompt, and the canonical doc map `docs/INDEX.md`. Paths in prose are `docs/<file>.md`. |
| **`zeus/docs/`** | Product and subsystem design: architecture, deployment, MCP / chat / orpheus / sessions specs, ingest guides, roadmap, model-comparison. Paths are `zeus/docs/<file>.md`. |

When adding a doc, pick the tree by audience: ops, Linear, or phases go to root `docs/`; how Zeus is built and behaves goes to `zeus/docs/`. Link with repo-root-relative paths so references stay unambiguous.

## Agent Orchestration Guidelines

Ruflo manages a swarm of task-specific agents (olympians). Each agent:

1. Has a single responsibility defined in `zeus/orchestration/agents/<name>.yaml`
2. Communicates through the FastAPI bus (`zeus/orchestration/bus.py`)
3. Can read from mnemosyne (MemoryStore) but writes go through iris (ingest pipeline) or the `/memory/add` endpoint
4. Must respect aegis (safety) policies; no unfiltered LLM output reaches the user
5. Uses oracle (Context API) for structured personal context

### Orchestration principles

Zeus treats **orchestration** (task loops, tools, memory discipline, validation) as the main lever for capability, not incremental model changes alone.

- **Tool-first.** Agents call concrete tools rather than reasoning in chat. MCP tool implementations live in `zeus/mcp/tools.py` and split into two bands: memory (`zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_ingest_trigger`, `zeus_memory_search`) and Olympian (`olympian_status_read`, `olympian_server_health`, `olympian_file_read`, `olympian_file_search`, `olympian_inbox_append`, `olympian_action_list`, `olympian_action_run`, `zeus_calendar_today`, `zeus_newsletter_latest`). Each Olympian tool wraps a Core HTTP endpoint in `zeus/core/{vault,inbox,actions,calendar}.py` (or extends `zeus/core/admin.py` for `/admin/status_file` and `/admin/system`) and is mirrored as a chat-path `ToolSpec` in `zeus/core/tools/` so the same tool fires from MCP clients (Cursor, Claude Desktop), the chat path (`QueryEngine.query()` when `ZEUS_TOOLS_ENABLED=1`), and Kairos. Write tools are gated by `ZEUS_MCP_ALLOW_WRITE`; the action runner additionally requires `ZEUS_ACTIONS_ENABLED=1`. Kairos draws from a separate allowlist (`ZEUS_KAIROS_TOOL_ALLOWLIST`, default read-only).
- **Structured memory, three layers.** `QueryEngine` (`zeus/core/query.py`) fans out via `_collect_retrieval_context()` into four labelled context blocks: **Profile** (from `get_profile_facts()`), **Memories** (from `search_memories()` on `MemoryStore`), **Knowledge** (from `search_knowledge()` on `KnowledgeStore`, hybrid+optional-rerank), and **Reference** (from kiwix / NOMAD proxies in `zeus/memory/reference.py`). Retrieval sub-budgets: profile 20%, memory 25%, knowledge 45%, reference 10%.
- **Bi-temporal memory payloads.** `MemoryStore` points carry `valid_from` / `valid_until` as ISO-8601 strings, plus `category`, `contains_pii`, `confidence`, `source`, `source_id`. Gives KG-style filtered queries without a graph DB.
- **Session window.** `SessionManager.get_context_window()` (`zeus/core/sessions.py`) uses one heuristic token budget, `ZEUS_CONTEXT_MAX_TOKENS` (default 6144), split **1/3** to retrieved context and **2/3** to the session block (rolling summary plus recent turns). Recent turns are packed newest-first (≈4 chars per token); only the newest `ZEUS_SESSION_PACK_MAX_TURNS` (default 150, `0` = unlimited) are candidates. When stored turns reach `ZEUS_SESSION_SUMMARY_AT_TURNS` (default 200), older dialogue is merged into a rolling summary and only the last `ZEUS_SESSION_KEEP_RAW_TURNS` (default 150) remain as full turns. In-memory `InMemoryStorage` is default; `ZEUS_SESSION_BACKEND=sqlite` persists to `zeus/data/sessions.db` via `SQLiteSessionStorage`.
- **Two LLM layers.** `_run_llm()` in `zeus/core/query.py` is the **chat** path (Claude in dev, Ollama in prod, reflection retries up to 3). `small_llm_call()` in `zeus/core/small_llm.py` is the **batch / structured-output** path (fact extraction, titles, classifiers). Every `small_llm_call` declares `min_privacy_tier` (1 or 2); tier-2 providers (OpenRouter default, etc.) are filtered out when a caller passes `min_privacy_tier=1`. Gemini free tier is not in the default chain because it trains on input. The daily USD cap prevents runaway spend.
- **Editable prompts.** The chat system prompt is [`zeus/core/prompts/chat_system.md`](zeus/core/prompts/chat_system.md); the fact-extraction prompt is [`zeus/core/prompts/memory_extract.md`](zeus/core/prompts/memory_extract.md). Both are rendered by `zeus/core/prompts/__init__.py` with `{{PLACEHOLDER}}` markers. Set `ZEUS_PROMPT_RELOAD=1` against a running `zeus-core` to re-read templates on every call during iteration; defaults to process-cached in production.
- **Plan, execute, reflect.** Multi-step tasks use `TaskRunner` in `zeus/orchestration/runtime.py` over `AgentStep` objects, collecting `StepResult` and supporting `on_failure: skip|retry|abort`. `QueryEngine.query()` retries up to 3 times with a refined prompt when `_is_empty_or_failed_reply()` returns True. The reflection loop passes Aegis on every attempt; no safety bypass for autonomy.
- **Chat-path tool-use (opt-in).** Behind `ZEUS_TOOLS_ENABLED=0` (default off), `QueryEngine.query()` routes through `run_tool_loop()` in `zeus/core/tools/loop.py`: the chat LLM can emit tool calls, results are fed back, loop continues until it stops calling tools or hits `ZEUS_TOOLS_MAX_CALLS_PER_QUERY` (default 5). Tools live in a process-local registry (`zeus/core/tools/registry.py`); reference tool is `web_search` (Brave). Per-provider wire-format adapters for Anthropic and Ollama are in `zeus/core/tools/adapters.py`. Every tool argument dict and every tool result text passes through Aegis under the `tool_arguments` policy. Reflection is skipped for tool-informed replies. See [`zeus/docs/tool-use-spec.md`](zeus/docs/tool-use-spec.md).

Roadmap detail for runtime, bus, hooks, and related backlog items lives in [`docs/ZEUS_LINEAR_TICKET_PLAN.md`](docs/ZEUS_LINEAR_TICKET_PLAN.md) (Projects 7 and 10).

### Agentic Safety Contract

Every autonomous code path (bus calls, Kairos cycles, TaskRunner steps) must pass through Aegis:

1. **Pre-execution.** `aegis_bus_pre_hook` in `zeus/safety/integration.py` runs `AegisPolicyEngine.evaluate_payload()` on tool arguments before the bus forwards any call. Prompt-injection patterns are rejected at the bus layer (see `zeus/safety/policies/standard.yaml`).
2. **Post-execution.** `aegis_bus_post_hook` filters LLM output before it returns from `bus_call()`. For `QueryEngine` paths, `evaluate_text()` runs on the assembled reply (chat, streaming chat, voice text, Telegram).
3. **Tool gating.** MCP write tools are gated by `ZEUS_MCP_ALLOW_WRITE`. Kairos defaults to read-only tools via `ZEUS_KAIROS_TOOL_ALLOWLIST`. Any shell-style tool must be gated by a dedicated env flag and a regex allowlist; do not widen an allowlist in a PR without a safety review note.
4. **No silent failures.** Aegis rejections raise, log at WARNING, and return a structured error to the caller.
5. **Privacy tier.** PII-bearing small-LLM calls must pass `min_privacy_tier=1`. The router statically removes tier-2 providers from the chain for such calls.

### Agent Definition Format

Agent definitions live in `zeus/orchestration/agents/<name>.yaml` and follow this shape:

```yaml
name: <agent_name>
description: <what this agent does>
model: <claude-sonnet-4-6 | qwen2.5:7b-instruct | ...>
tools:
  - <tool_name>
context:
  - <oracle endpoint or memory namespace>
safety:
  policy: <aegis policy name, matches zeus/safety/policies/<name>.yaml>
```

### Environment Switching

The system supports two environments controlled by `ZEUS_ENV`:

- `dev` uses Claude API for LLM calls, runs on the dev workstation (typical: RTX 5080-class, 16 GB VRAM), verbose logging.
- `prod` uses Ollama (Qwen2.5-7B) for LLM calls, runs on the always-on production host (typical: RTX 3080-class, 10 GB VRAM), structured logging.

`ZEUS_LLM` overrides per process (`claude` | `ollama` | unset). All services must check `ZEUS_ENV` / `ZEUS_LLM` and configure themselves accordingly. Never hardcode model names or API endpoints.

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

- Dev on the workstation host (16 GB VRAM class leaves headroom for 14B models), or on the production host itself with `compose.override.yaml` bind-mounting `./zeus` into `zeus-core` for hot-reload of pure-Python edits. See `compose.override.example.yaml` for a templated starting point.
- Prod deploys target the always-on "olympus" host (10 GB VRAM class, 7B Q4/Q5 models). The example deployment currently runs on a "daedalus" host; any always-on Linux+NVIDIA host works.
- Branches per tool or experiment; merge when working. `main` is always deployable to prod.
- Use `zeus.bench` (`python -m zeus.bench` or `POST /models/benchmarks/run`) after any model change to confirm per-model tok/s and prompt-eval on the host; results feed the Settings UI.

## Key Decisions

- **MemoryStore replaced mem0 (April 2026).** mem0 v2.0.0 deleted `mem0g`, shipped several breaking schema changes in 24 hours, and couldn't guarantee Qdrant payload stability. Zeus now owns the write path: ~200 LOC `MemoryStore` with LLM fact extraction via `small_llm_call`, bi-temporal payloads, ISO-8601 timestamps.
- **Memory + Knowledge + Reference split.** The single `zeus_memories` collection polluted profile retrieval with bulk doc chunks. Writes now fan out by source: curated profile sources (`context_pack`, `gcal`) go through fact extraction into `zeus_memories`; bulk sources (Obsidian, chatgpt, markdown, email, newsletter, bookmarks, git) go into `zeus_knowledge` raw (no LLM); Wikipedia / NOMAD are live-proxied (no ingest).
- **Hybrid retrieval with optional reranker.** `KnowledgeStore` uses Qdrant-native BM25 sparse vectors fused with dense via RRF (`ZEUS_KNOWLEDGE_HYBRID=1`). Optional BGE-reranker-v2-m3 on CPU or a dev GPU (`ZEUS_KNOWLEDGE_RERANK=1`) — do not load it onto the VRAM-constrained production chat GPU. Baseline on 30 hand-written queries: hit@1=0.60, hit@5=0.867, hit@10=0.933, MRR@10=0.71 (see `tests/retrieval_eval_baseline.json`).
- **Two LLM layers with privacy-tier gating.** `small_llm_call` routes structured-output / batch work across `gemini_paid`, `groq`, `openrouter`, `anthropic_haiku`, `ollama` with a daily USD cap and an allowed-models gate. Gemini free tier is not in the chain (trains on input). LiteLLM is forbidden (March 2026 supply-chain attack on versions 1.82.7/1.82.8).
- **Ruflo v3.5 over LangGraph / CrewAI** because it is Claude Code native and supports swarm patterns without framework lock-in.
- **Voicebox + LuxTTS over Coqui / Bark** because 150x realtime speed makes conversational latency viable on consumer GPUs.
- **Qwen2.5-7B-Instruct Q4_K_M in prod** fits in 10 GB VRAM (RTX 3080-class) while maintaining instruction-following quality. See `zeus/docs/model-comparison.md` for measured tok/s across candidate models.
- **Text chat is a first-class fallback** so dev and non-voice modes work without the full audio pipeline.
- **MCP is a first-class integration boundary** so Zeus memory and context can be reused by external assistant clients.
- **Session continuity** is required for natural multi-turn interactions across chat, voice, and Telegram.
- **Observability** is mandatory once always-on deployment begins: query latency, ingest cadence, service health, small-LLM usage ledger, and per-model benchmarks are all surfaced through `/admin`.

## Writing Style

No emdashes in generated text or in docs; runtime chat rules live in `zeus/core/prompts/chat_system.md`.
