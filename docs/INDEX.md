# Zeus Doc Index

Single map of every doc in the repo. Two trees, different audiences:

- **`docs/`** (this directory): ops, Linear tracking, host runbooks, bootstrap prompts, master plans.
- **`zeus/docs/`**: product and subsystem design for how Zeus is built and behaves.

Audience tag legend: **ops** (operational runbook), **product** (subsystem design), **ticket** (plan / tracking), **bootstrap** (AI-collaborator prompt), **legacy** (superseded, preserved for decision history).

## Root entry points

| Doc | Audience | One-liner |
|-----|----------|-----------|
| [`../CLAUDE.md`](../CLAUDE.md) | product | Primary project brief: stack, naming, layout, conventions, key decisions. |
| [`../README.md`](../README.md) | ops | Repo-level getting-started. |

## Subsystem CLAUDE.md files (auto-loaded by Claude Code when editing that tree)

| Doc | Audience | One-liner |
|-----|----------|-----------|
| [`../zeus/memory/CLAUDE.md`](../zeus/memory/CLAUDE.md) | product | MemoryStore, KnowledgeStore, Reference: invariants, flags, what not to do. |
| [`../zeus/ingest/CLAUDE.md`](../zeus/ingest/CLAUDE.md) | product | Iris pipeline: source/target routing, config.yaml, how to add a source. |
| [`../zeus/voice/CLAUDE.md`](../zeus/voice/CLAUDE.md) | product | Orpheus host-native loop: wake, STT, TTS, Phaos emitter, VRAM budget. |
| [`../zeus/orchestration/CLAUDE.md`](../zeus/orchestration/CLAUDE.md) | product | AgentRuntime, bus, hooks, Kairos: FastAPI surface, invariants, allowlists. |
| [`../zeus/kronos/CLAUDE.md`](../zeus/kronos/CLAUDE.md) | product | Kronos scheduler: job registry, asyncio loop, built-in/agent dispatch, Aegis-gated execution. |

## docs/ (repo root)

| Doc | Audience | One-liner |
|-----|----------|-----------|
| [INDEX.md](INDEX.md) | product | This file. |
| [ZEUS_LINEAR_TICKET_PLAN.md](ZEUS_LINEAR_TICKET_PLAN.md) | ticket | Authoritative Linear ticket + project plan. Do not regenerate. |
| [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) | bootstrap | Prompt for AI collaborators (Cursor, Claude Code) working on the Zeus codebase. |
| [memory-architecture-plan.md](memory-architecture-plan.md) | product | Three-layer memory plan (Mnemosyne / Library / Reference), migration runbook. Phase 1 shipped. |
| [kronos-backend-plan.md](kronos-backend-plan.md) | product | Kronos scheduler subsystem plan: job registry, asyncio loop, three dispatch modes, REST + MCP, Aegis-gated execution. |
| [kronos-frontend-plan.md](kronos-frontend-plan.md) | product | `/jobs` dashboard plan for the React SPA: jobs table, detail drawer, cron builder, live execution feed. |
| [kronos-job-catalog.md](kronos-job-catalog.md) | ticket | Brainstorm of useful scheduled jobs grouped by domain, with tools each needs (existing vs to-build) and a recommended build order. Use as the planning surface when picking the next Kronos work item. |
| [nemoclaw-ops.md](nemoclaw-ops.md) | ops | NemoClaw + OpenShell templated runbook: SSH tunnels, inference routing, policies, backups. Fill in your own host names and paths. |
| [claude-code-architecture-notes.md](claude-code-architecture-notes.md) | product | External analysis of Claude Code architecture patterns that informed Zeus's design. |
| [zeus-mcp-tool-expansion-prompt.md](zeus-mcp-tool-expansion-prompt.md) | bootstrap | Triage prompt for a Claude Code session to review candidate MCP tools, flag safety/deps, and pick which ones become Linear tickets. |

## zeus/docs/ (product and subsystem design)

| Doc | Audience | One-liner |
|-----|----------|-----------|
| [architecture.md](../zeus/docs/architecture.md) | product | Subsystem map: retrieval fan-out, writes, two LLM layers, safety, topology. Start here. |
| [agent-runtime-spec.md](../zeus/docs/agent-runtime-spec.md) | product | AgentRuntime, bus, hooks, TaskRunner, Kairos: module map + FastAPI surface. |
| [chat-interface-spec.md](../zeus/docs/chat-interface-spec.md) | product | HTTP surface for text chat, SSE streaming, sessions; shared by React SPA and Telegram. |
| [chat-ui-improvements.md](../zeus/docs/chat-ui-improvements.md) | product | Living checklist for the legacy static `chat.html` fallback (React SPA is primary). |
| [comparison.md](../zeus/docs/comparison.md) | product | What Zeus borrowed from Ruflo, Squad, Claude Code, and what it keeps unique. |
| [deployment.md](../zeus/docs/deployment.md) | ops | Deployment runbook (daedalus today, Olympus target): compose, first ingest, monitoring. |
| [ingest-guide.md](../zeus/docs/ingest-guide.md) | product | Priority order for feeding Iris; memory vs knowledge routing; retrieval eval. |
| [kronos-job-guide.md](../zeus/docs/kronos-job-guide.md) | product | How to create a Kronos job: every field explained, three creation surfaces, recipes, troubleshooting. Use this as agent context when authoring jobs. |
| [congressional-scrutiny-job.md](../zeus/docs/congressional-scrutiny-job.md) | product | Weekly CapitolScope congressional-trading brief job: context-pack synthesis + news digest on local Ollama, inbox + knowledge writeback. |
| [scrutiny-watch-job.md](../zeus/docs/scrutiny-watch-job.md) | product | Daily CapitolScope scrutiny-watch job: catch/dedup/triage signals, threshold-gated auto-escalation into deep_research, durable-path deploy notes. |
| [ingest-paths.md](../zeus/docs/ingest-paths.md) | ops | `zeus/data/raw/` layout, symlink table, cron patterns. |
| [mcp-server-spec.md](../zeus/docs/mcp-server-spec.md) | product | MCP tool catalog (`zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_memory_search`, `zeus_ingest_trigger`). |
| [meshtastic-bridge.md](../zeus/docs/meshtastic-bridge.md) | product | LoRa mesh into `/chat/message` via MQTT uplink + Node-RED + TCP sender sidecar. Topics, session id, allowlist, Aegis wiring. |
| [mesh-outbound-spec.md](../zeus/docs/mesh-outbound-spec.md) | product | Outbound direction: `/mesh/notify` choke point, Kairos proactive push, read-only break-glass `!commands`. Gates, quiet hours, dedupe, mesh Aegis policy, audit. |
| [model-comparison.md](../zeus/docs/model-comparison.md) | product | Measured tok/s, TTFT, VRAM fit per Ollama model on the 3080. |
| [pheme.md](../zeus/docs/pheme.md) | product | Pheme news subsystem: `zeus_news` store, Canary + CapitolScope ingest, staged local pipeline, Kronos daily digest, breaking observer, Telegram push, gated Twitter. |
| [pheme-twitter-setup.md](../zeus/docs/pheme-twitter-setup.md) | ops | One-time X/Twitter OAuth2 setup for Pheme: developer-app values, `.env` keys, `scripts/twitter_oauth_setup.py` token bootstrap, verification, troubleshooting. |
| [zeus-os.md](../zeus/docs/zeus-os.md) | product | Tiling-WM web shell: SvelteKit frontend at `zeus-os/`, FastAPI bridge at `zeus/core/zeus_os/`, served at `/os/`. Keymap, env vars, phase plan. |
| [obsidian-livesync-ingest.md](../zeus/docs/obsidian-livesync-ingest.md) | ops | CouchDB to local vault to ingest: LiveSync CLI setup, headless troubleshooting. |
| [orpheus-spec.md](../zeus/docs/orpheus-spec.md) | product | Voice pipeline: wake, STT, TTS, streaming LLM, Phaos emitter. |
| [phaos-voice-state-protocol.md](../zeus/docs/phaos-voice-state-protocol.md) | product | WebSocket + HTTP publish protocol for voice-state events. |
| [project-nomad-integration.md](../zeus/docs/project-nomad-integration.md) | product | N.O.M.A.D. reference-layer integration plan (live proxy, optional metadata ingest). |
| [roadmap.md](../zeus/docs/roadmap.md) | ticket | Current-state snapshot + near-term pointers to the ticket plan. |
| [sessions-spec.md](../zeus/docs/sessions-spec.md) | product | Session model, packing, rolling summary, storage backends. |
| [token-usage.md](../zeus/docs/token-usage.md) | ops | Token-usage ledger: `small_llm_usage.db` schema, writers (`small_llm.py`, `query.py`), `GET /admin/llm_usage` reader, historical CSV import. |
| [tool-use-spec.md](../zeus/docs/tool-use-spec.md) | product | Chat-path tool-call loop: registry, per-provider adapters, Aegis policy, feature flags. |

## zeus/docs/legacy/

| Doc | Audience | One-liner |
|-----|----------|-----------|
| [architecture_legacy.md](../zeus/docs/legacy/architecture_legacy.md) | legacy | Original (March 2026) architecture brief. Superseded by `zeus/docs/architecture.md`. |
| [memory_ingest_legacy.md](../zeus/docs/legacy/memory_ingest_legacy.md) | legacy | Original mem0-era ingest + memory playbook. Superseded by `docs/memory-architecture-plan.md` and `zeus/docs/ingest-guide.md`. |
| [roadmap_legacy.md](../zeus/docs/legacy/roadmap_legacy.md) | legacy | Original Sprint 0–4 roadmap with "hermes/apollo" naming. Superseded by the Linear ticket plan. |

## Open TODOs and known contradictions

- **TODO: resolve.** CLAUDE.md previously named `olympian_file_read`, `olympian_search`, `olympian_memory_search`, `olympian_shell` as first-class tools. The shipped MCP tools are `zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_memory_search`, `zeus_ingest_trigger`; `zeus/mcp/olympian_tools.py` does not exist. The current CLAUDE.md text has been updated to match shipped state; Linear ticket LAB-328 tracks the olympian tool pack if it is ever built.
- **TODO: resolve.** `zeus/core/static/chat.html` + `zeus/core/static/admin.html` + `viz/` are still served alongside the React SPA in `zeus/core/static/app/`. The spec docs call the React SPA primary; no ticket yet for removing the static pages.
- **TODO: resolve.** "Olympus" is referenced as the production target throughout the docs; in practice the always-on host is whichever box the deployer currently runs (the example deployment uses a workstation host called "daedalus"). The deployment runbook covers either topology — pick a host-name convention once a permanent production box is in place.
- **TODO: resolve.** `zeus/docs/model-comparison.md:94` retains one historical `mem0` reference (explaining a past Telegram retrieval bug). Kept intentionally; flag if the narrative becomes confusing to new readers.
