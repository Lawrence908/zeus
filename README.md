# Zeus: Personal AI Assistant System

A self-hosted, voice-first, privacy-preserving AI assistant built from proven open-source components. Runs on consumer GPUs (example: RTX 3080 for production, RTX 5080 for dev; substitute your own) and keeps your data and computation on your own hardware.

**Status (2026-10-19):** Running always-on on the daedalus host. Three-layer retrieval, text chat with tool use, Telegram, MCP, the Kronos scheduler, Pheme news digests (with a spoken morning briefing), Pygmalion image generation, the Kokoro voice loop, and the Zeus OS browser desktop are all live. The Argo coding swarm is merged but dark, and the Meshtastic bridge is built and waiting on a radio.

> Docs map: [`docs/INDEX.md`](docs/INDEX.md). Project brief: [`CLAUDE.md`](CLAUDE.md). Ticket plan: [`docs/ZEUS_LINEAR_TICKET_PLAN.md`](docs/ZEUS_LINEAR_TICKET_PLAN.md).

---

## Vision

Zeus is a personal knowledge engine that knows you. It ingests your data (markdown notes, Obsidian vault, ChatGPT exports, newsletters, bookmarks, calendar, news feeds), remembers context across sessions, answers questions over a three-layer retrieval architecture, and acts through a set of audited tools. Unlike cloud assistants, everything stays on your hardware unless you opt a specific step out.

Principles:

- **Privacy-first.** Data stays local. PII-bearing LLM calls are gated to providers with strict retention guarantees; free tiers that train on input are excluded.
- **Voice-native.** Wake word to STT to LLM to TTS runs as a streaming pipeline. Text, Telegram, and MCP are first-class fallbacks that share the same sessions, tools, and safety stack.
- **Modular.** Swap a component (chat LLM, embedder, reranker, storage backend, GPU) without rewriting orchestration.
- **Tool-first.** The model calls concrete tools, and every argument and result passes Aegis.

---

## Architecture

```text
 Browser (React SPA, Zeus OS) · Telegram · MCP clients · Voice orb · Meshtastic
                                    │
              ┌─────────────────────┴───────────────────────┐
              │      Zeus Core (FastAPI, ZEUS_CORE_PORT)    │
              │  chat · oracle · admin · tools · kronos ·   │
              │  zeus-os bridge · voice · newsletter · swarm│
              └─────────────────────────────────────────────┘
          │              │              │             │            │
   ┌──────┴──────┐ ┌─────┴────┐  ┌──────┴─────┐ ┌─────┴─────┐ ┌────┴─────┐
   │ QueryEngine │ │  Iris    │  │  Kronos    │ │  Kairos   │ │  Pheme   │
   │ retrieval + │ │  ingest  │  │  cron      │ │  observe/ │ │  news    │
   │ tool loop   │ │ pipeline │  │  scheduler │ │  act loop │ │ pipeline │
   └──────┬──────┘ └────┬─────┘  └────────────┘ └───────────┘ └────┬─────┘
          │             │                                          │
  ┌───────┼─────────────┼──────────────┬──────────────┐            │
┌─┴───────┴┐ ┌──────────┴┐ ┌───────────┴┐ ┌───────────┴──┐ ┌───────┴──────┐
│ Profile  │ │ Memories  │ │ Knowledge  │ │ Reference    │ │ News         │
│ facts    │ │ (curated) │ │ (bulk)     │ │ (live proxy) │ │ (Canary,     │
└────┬─────┘ └────┬──────┘ └─────┬──────┘ └──────┬───────┘ │ CapitolScope)│
     └─────┬──────┘              │          kiwix / NOMAD  └──────┬───────┘
           ▼                     ▼                                ▼
   Qdrant `zeus_memories`  Qdrant `zeus_knowledge`         Qdrant `zeus_news`
   (bi-temporal facts)     (dense + BM25 RRF, rerank)      (45-day retention)
           │                     │                                │
           └──────────┬──────────┴────────────────────────────────┘
                      ▼
   ollama-gateway (Apollo 5080 primary, daedalus 3080 fallback)
   rerank-gateway (TEI, 5080 first, CPU fallback)
```

Voice: openWakeWord, WhisperLiveKit STT, the shared QueryEngine path (`voice=True`), Kokoro-FastAPI TTS on CPU. Phaos publishes voice state to a Three.js orb over WebSocket.

Full subsystem map: [`zeus/docs/architecture.md`](zeus/docs/architecture.md).

### Subsystems (Greek naming)

| Name | Role | State |
|------|------|-------|
| **zeus** | Main orchestration, FastAPI bus | Live |
| **mnemosyne** | Memory layer (`MemoryStore`, `zeus_memories`) | Live |
| **library / knowledge** | Bulk RAG (`KnowledgeStore`, `zeus_knowledge`) | Live, rerank on |
| **reference** | Live proxy for kiwix and NOMAD | Live |
| **iris** | Ingest pipeline, per-source routing | Live |
| **oracle** | Context API (`/context/query`, `/context/profile`, `/memory/*`) | Live |
| **pheme** | News consolidation, daily digest, breaking alerts, MP3 briefing | Live, ~07:10 weekdays / ~09:00 weekends |
| **kronos** | Cron scheduler and job executor | Live |
| **kairos** | Background observe-decide-act daemon | Shipped, read-only allowlist |
| **pygmalion** | Image generation via ComfyUI (FLUX on 5080, SDXL fallback on 3080) | Live |
| **orpheus** | Voice interface (wake, STT, Kokoro TTS) | Live in the browser orb |
| **phaos** | Voice-state visualization (WebSocket + Three.js orb) | Live |
| **zeus-os** | Tiling-WM browser desktop (SvelteKit) | Live at `/os/` |
| **aegis** | Safety layer (YAML policies + bus pre/post hooks) | Live |
| **olympians / argo** | Agent swarm: DAG-planned headless Claude Code workers in git worktrees | Merged, dark |
| **themis** | Per-layer retrieval eval + acceptance gate | Built; nightly Kronos job off until a baseline is promoted |
| **olympus** | Production server (always-on host; typical: RTX 3080-class) | daedalus fills this role |

### Tech stack

| Layer | Component | Why |
|-------|-----------|-----|
| Orchestration | Ruflo v3.5 manifests + Zeus `AgentRuntime` | Claude Code native, no framework lock-in |
| Vector DB | Qdrant 1.15+ | Self-hosted, native BM25 sparse vectors, RRF fusion |
| Memory | `zeus/memory/store.py` (`MemoryStore`) | Hand-rolled; replaced mem0 in April 2026 |
| Knowledge | `zeus/memory/library.py` (`KnowledgeStore`) | Dense + BM25 hybrid, BGE-reranker-v2-m3 via rerank-gateway |
| News | `zeus/memory/news.py` (`NewsStore`) + `zeus/pheme/` | Deterministic ids, idempotent re-ingest, retention sweep |
| Small-task LLM | `zeus/core/small_llm.py` | Provider router with privacy-tier gate and daily USD cap |
| Chat LLM (dev) | Claude Sonnet via Anthropic API | Best quality during iteration |
| Chat LLM (prod) | Ollama `qwen2.5:7b-instruct` Q4_K_M via ollama-gateway | Fits 10 GB VRAM; fails over between GPUs |
| Embeddings | `nomic-embed-text:v1.5` via Ollama | 768-dim cosine, model-aware query/document prefixes |
| HTTP API | FastAPI (container 8000, host `ZEUS_CORE_PORT`, default 8203) | Async-first, validated schemas |
| MCP | `zeus/mcp/server.py` (FastMCP) | Zeus memory and tools for Claude Code, Cursor, Claude Desktop |
| STT | WhisperLiveKit | Real-time, streaming, SimulStreaming |
| TTS | Kokoro-FastAPI (`zeus-tts`) | OpenAI-style `/v1/audio/speech`, CPU, no VRAM |
| Wake word | openWakeWord | CPU, always-on |
| Image gen | ComfyUI | Python-built graphs, in-process failover |
| Frontends | Vite + React (dashboard), SvelteKit + Tailwind (Zeus OS) | Data-dense dashboard plus a keyboard-driven desktop |
| Container | Docker Compose | Qdrant + Ollama + Whisper + TTS + Zeus Core |

---

## Highlights

### Zeus OS

A Hyprland-style tiling window manager that runs in the browser, served from `/os/` on the same port as the React dashboard. Binary-space-partition tiling, ten workspaces, floating windows, vim-style focus and move keys, a launcher, a cheatsheet, three themes (Catppuccin Mocha, Tokyo Night, Gruvbox Dark), session restore on reload, and a touch-friendly mobile shell.

Apps: Chat, Voice Orb (push-to-talk with handoff to Chat), Terminal (real host shell over a restricted SSH key, multi-tab), System Monitor (CPU, memory, GPU via `nvidia-smi`), File Manager, Monaco Editor with a file tree, Obsidian vault viewer, Notepad, Memories (quick-add, multi-select), Knowledge, Ingest, Jobs (Kronos), Agents, Swarm (runs grouped by what they need from a human), Tools (with a "try it" invoke form), Token Usage, Images, Calendar, Home Assistant, Linear, Processes, Network, and Settings.

The backend is a FastAPI bridge under `/zeus-os/*` (PTY WebSocket, 1 Hz system stream, allowlisted file I/O with gated writes, config, launcher registry). The file roots the desktop can see are deliberately separate from the roots the LLM's `file_read` tool can see, so widening one never widens the other. See [`zeus/docs/zeus-os.md`](zeus/docs/zeus-os.md).

### Pheme: news that reads like an editor wrote it

Canary (OSINT feeds and GDELT) and CapitolScope (congressional trading signals) ingest into `zeus_news`. A staged pipeline then runs on local Ollama: extract entities and claims, cluster same-story articles (entity overlap plus an embedding bridge), match clusters to persistent story threads so ongoing stories read as "day N" with a what-changed note, correlate congressional trades against news that shares an entity, and rank by heuristics blended with profile relevance and decayed 👍/👎 feedback.

The final editor stage runs on Claude through the owner's Claude Code subscription (`PHEME_EDITOR=claude`), headless with no tools, an empty sandbox, and schema-validated output. It cites candidates by number and links are attached from cluster data, so it cannot invent a URL. Any failure falls back to the local path, and the digest records which path served.

Delivery around 07:10 on weekdays and 09:00 on weekends: a Telegram HTML digest with sections, insights, and congressional connections, a spoken 450 to 750 word briefing rendered by Kokoro into an MP3 for the morning listen, a newsletter-page mirror, and an approval-first Twitter thread (**Tweet it / Skip** buttons in Telegram; built, currently gated off). Breaking alerts fire from a Kairos observer on entity bursts, capped at three per day. See [`zeus/docs/pheme.md`](zeus/docs/pheme.md).

### Tools the model actually uses

With `ZEUS_TOOLS_ENABLED=1` the chat model runs a provider-agnostic tool loop (Anthropic and Ollama wire adapters) over 15+ tools: `current_time` (location-aware), `web_search`, `deep_research`, `image_generate`, `zeus_news_search`, `zeus_calendar_today`, `zeus_newsletter_latest`, file read and search, status and server health, inbox append, the action runner, and swarm propose/approve/answer.

- **Same tools everywhere.** Each tool is a chat-path `ToolSpec` and an MCP tool wrapping the same Core endpoint, so chat, voice, Telegram, Kairos, and external MCP clients behave identically.
- **Per-env allowlist.** `ZEUS_TOOLS_ALLOWLIST` decides what the model is even told about; write tools stay double-gated (`ZEUS_MCP_ALLOW_WRITE`, `ZEUS_ACTIONS_ENABLED`).
- **Aegis on both sides.** Every argument dict and every result text is evaluated under the `tool_arguments` policy.
- **Observable.** Invocations roll up into `/admin/metrics` (error rate, cache-hit rate, Aegis rejects, p50/p95 latency per tool), and the Zeus OS Tools app lets you invoke any tool by hand.
- **Measured.** `tests/tool_use_eval.py` scores tool selection and false positives. The `qwen2.5:7b` baseline: selection 11/11, false positives 0/6.
- **Cached where safe.** A TTL+LRU cache for read tools whose data changes on the order of minutes; errors and side-effecting tools are never cached.

See [`zeus/docs/tool-use-spec.md`](zeus/docs/tool-use-spec.md).

### Retrieval you can trust the numbers on

Reranking runs out of process through a rerank-gateway (Apollo 5080 first, CPU fallback), and Themis now records whether the reranker was actually applied, not just whether the flag was set. The original 30-query suite saturated at hit@1 1.0 because each query contained its own answer, so a harder suite was written under two rules: no query may contain its expected keywords, and each targets a crowded document family. That suite sits at hit@1 0.56 on 32 queries, which leaves real room to improve. A baseline is proposed, not promoted; promotion is a separate human commit, because the process producing a number must not write the number it is compared against.

---

## Repository layout

```text
docs/             # Ops runbooks, Linear plan, swarm + themis + kronos plans, INDEX.md
compose.yaml
compose.override.yaml   # Dev bind-mount of ./zeus into zeus-core
zeus-os/          # SvelteKit tiling-WM frontend; builds into zeus/core/static/zeus-os/
zeus/
  core/           # FastAPI main, chat, admin, query, sessions, voice_ws, small_llm, comfyui, newsletter
  core/tools/     # Chat-path tool registry, loop, adapters, cache, recorder, one module per tool
  core/zeus_os/   # /zeus-os/* bridge (pty, sys, fs, config, apps)
  prompts/        # templates/ (chat_system.md, voice_system.md, memory_extract.md) + overrides/
  orchestration/  # runtime.py, bus.py, hooks.py, daemon.py (Kairos), swarm/ (Argo), agents/*.yaml
  memory/         # store.py, library.py, news.py, reference.py, reranker.py, search.py, eval.py
  ingest/         # pipeline.py, run.py, config.yaml, sources/* (incl. canary, capitolscope, gcal)
  pheme/          # pipeline, threads, editor (Claude), audio (Kokoro MP3), delivery, feedback, observer
  kronos/         # scheduler, executor, registry, storage, api, jobs/
  voice/          # state.py, stt.py, tts.py, wake.py, pipeline.py
  safety/         # policy_engine.py, integration.py, policies/*.yaml
  api/            # Oracle: context + profile + memory search
  mcp/            # server.py, tools.py
  bench/          # runner.py, __main__.py
  integrations/   # telegram/, twitter/
  frontend/       # Vite + React + TypeScript dashboard
  docs/           # Subsystem and product specs (see docs/INDEX.md)
  data/           # Raw exports, processed chunks, SQLite DBs (all gitignored)
scripts/          # check-docs, acceptance, reembed, zeus-mcp.sh, zeus-usage.sh
tests/            # Mock-based unit suite, retrieval + tool-use evals and baselines
```

---

## Getting started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- NVIDIA Container Toolkit (for GPU-backed Ollama and Whisper)
- Node 20+ if you want to rebuild the frontends
- `.env` populated from [`.env.example`](.env.example). At minimum: `ANTHROPIC_API_KEY` for dev, or none for all-local Ollama.

### Start services

```bash
docker compose up -d
docker compose ps
curl http://localhost:${ZEUS_CORE_PORT:-8203}/status | jq
```

Brings up Qdrant (6333), Ollama, WhisperLiveKit (9090), Kokoro TTS, and Zeus Core. Zeus Core listens on 8000 inside the container and is published on `ZEUS_CORE_PORT` (default 8203; the reference daedalus deployment uses 8102). Code that needs the bus address should call `core_base_url()` in [`zeus/core/config.py`](zeus/core/config.py).

### First ingest

```bash
# Curated profile sources (memory layer, LLM fact extraction)
docker exec zeus-core python -m zeus.ingest.run --target memory

# Bulk sources (knowledge layer, raw embed)
docker exec zeus-core python -m zeus.ingest.run --target knowledge

# News (Pheme)
docker exec zeus-core python -m zeus.ingest.run --source canary --target news --news-days-back 3
```

Per-source routing lives in [`zeus/ingest/config.yaml`](zeus/ingest/config.yaml). See [`zeus/docs/ingest-guide.md`](zeus/docs/ingest-guide.md) for priority order and [`zeus/docs/ingest-paths.md`](zeus/docs/ingest-paths.md) for raw-data layout.

### Use it

- Dashboard: `http://localhost:8203/` (React SPA).
- Zeus OS: `http://localhost:8203/os/`. Rebuild with `cd zeus-os && npm install && npm run build`.
- Telegram: set `TELEGRAM_ENABLED=1` plus token and allow-list; the bot starts in the FastAPI lifespan.
- MCP: `scripts/zeus-mcp.sh` launches the stdio server for Claude Code, Cursor, or Claude Desktop. See [`zeus/docs/mcp-server-spec.md`](zeus/docs/mcp-server-spec.md).
- Scheduled jobs: manage live Kronos jobs from the Jobs app or `/kronos/*`; the seed is [`zeus/data/kronos.yaml`](zeus/data/kronos.yaml) on first boot.

### Run the benchmark suite

```bash
docker exec zeus-core python -m zeus.bench
```

Writes per-model tok/s + TTFT + prompt-eval to `zeus/data/benchmarks.json`; results show up in the Settings UI. Reference numbers from the example RTX 3080 deployment: `qwen2.5:7b-instruct` 119 tok/s, `llama3.1:8b-instruct` 113 tok/s, `qwen3:8b` 100 tok/s. Full context in [`zeus/docs/model-comparison.md`](zeus/docs/model-comparison.md).

---

## Key concepts

**Three-layer retrieval.** `QueryEngine._collect_retrieval_context()` runs profile, memory, knowledge, and reference lookups in parallel and renders them as labelled blocks in the system prompt. Sub-budgets: profile 20%, memory 25%, knowledge 45%, reference 10%, all inside 1/3 of `ZEUS_CONTEXT_MAX_TOKENS` (default 6144). The other 2/3 is the session block. News is reached through the `zeus_news_search` tool by default.

**Two LLM layers.** `_run_llm()` is the chat path (Claude in dev, Ollama in prod, 3-attempt reflection when no tool fired). `small_llm_call()` is the batch / structured-output path (fact extraction, titles, classifiers) with a privacy-tier gate and a daily USD cap. LiteLLM is forbidden (March 2026 supply-chain attack).

**Environment modes.**

| Mode | Chat LLM | Hardware | Use case |
|------|----------|----------|----------|
| `dev` | Claude Sonnet | Dev workstation (typical: RTX 5080-class, 16 GB VRAM) | Rapid iteration |
| `prod` | Ollama `qwen2.5:7b-instruct` | Always-on production host (typical: RTX 3080-class, 10 GB VRAM) | Always-on |

Switch via `ZEUS_ENV` and optionally `ZEUS_LLM`. See [`zeus/docs/deployment.md`](zeus/docs/deployment.md).

**Session continuity.** `SessionManager` in `zeus/core/sessions.py`. In-memory by default; set `ZEUS_SESSION_BACKEND=sqlite` to persist to `zeus/data/sessions.db`. Rolling summary fires at `ZEUS_SESSION_SUMMARY_AT_TURNS` (default 200), keeping the last `ZEUS_SESSION_KEEP_RAW_TURNS` (default 150) as raw turns. Voice turns share history with text chat. See [`zeus/docs/sessions-spec.md`](zeus/docs/sessions-spec.md).

**Aegis safety.** Every autonomous code path passes through the policy engine: bus calls, tool arguments and results, Kronos jobs, Kairos cycles, outbound Telegram and Twitter. Policies live in `zeus/safety/policies/`. Optional NemoClaw + OpenShell host sandbox for OS-level isolation: [`docs/nemoclaw-ops.md`](docs/nemoclaw-ops.md).

---

## Development workflow

Dev on the workstation host or the always-on host itself; start from `compose.override.example.yaml` (copy to `compose.override.yaml` and fill in host-side bind-mount paths; the real override is gitignored). It bind-mounts `./zeus` into `zeus-core` so pure-Python edits take effect with a container restart. Production hosts run a baked image.

1. Create a feature branch: `git checkout -b <github-user>/LAB-XXX-description`
2. Iterate locally with `docker compose up -d`
3. Run tests: `pytest` (mock-based, no live services) and `python -m zeus.memory.eval` for retrieval
4. Run `python -m zeus.bench` if you touched model config
5. Open a PR linked to the Linear ticket; CI must be green
6. Merge to `main` (always deployable)

CI ([`docs/ci.md`](docs/ci.md)) runs on every push and PR: `ruff` + `pytest` with coverage, builds and type-checks both frontends, and builds the runtime Docker image.

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
| [`docs/swarm-system.md`](docs/swarm-system.md) | Argo swarm system brief |
| [`docs/themis-spec.md`](docs/themis-spec.md) | Retrieval eval and acceptance gate |
| [`docs/ci.md`](docs/ci.md) | CI pipeline |
| [`zeus/docs/architecture.md`](zeus/docs/architecture.md) | Subsystem map |
| [`zeus/docs/zeus-os.md`](zeus/docs/zeus-os.md) | Zeus OS desktop and bridge |
| [`zeus/docs/pheme.md`](zeus/docs/pheme.md) | News pipeline, editor, delivery |
| [`zeus/docs/tool-use-spec.md`](zeus/docs/tool-use-spec.md) | Chat-path tool loop |
| [`zeus/docs/kronos-job-guide.md`](zeus/docs/kronos-job-guide.md) | Writing scheduled jobs |
| [`zeus/docs/deployment.md`](zeus/docs/deployment.md) | Deployment runbook |
| [`zeus/docs/model-comparison.md`](zeus/docs/model-comparison.md) | Measured tok/s and VRAM fit per model |

---

## License

Personal project. No license specified. If released publicly, likely MIT or similar permissive.

---

*Last updated: 2026-10-19.*
