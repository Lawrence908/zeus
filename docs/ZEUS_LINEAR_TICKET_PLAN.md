# Zeus: Linear Ticket Plan (Revised)

Full ticket structure for the Zeus project. Incorporates feedback on sprint ordering, Phaos subsystem, retrieval eval, collection versioning, and dependency awareness.

**Team:** `<YOUR_LINEAR_TEAM>`
**Linear Projects:** Zeus 0–8 + Backlog

## Labels


| Label     | Color   | Subsystem                                              |
| --------- | ------- | ------------------------------------------------------ |
| mnemosyne | #7C3AED | Memory layer, mem0 + Qdrant                           |
| iris      | #10B981 | Ingest pipeline, data sources → chunks                |
| orpheus   | #F59E0B | Voice interface, STT, TTS, wake word                  |
| aegis     | #EF4444 | Safety layer, NemoClaw + OpenShell                    |
| oracle    | #3B82F6 | Zeus Context API, structured context                  |
| olympians | #EC4899 | Agent swarm, Ruflo-managed agents                     |
| phaos     | #06B6D4 | Voice-state visualization, Three.js, WebSocket, WebXR |


---

## Revised Sprint Ordering

Key changes from v1:

1. **Sessions & Chat moved to Project 1**: dev acceleration, text interface before voice
2. **Query Engine moved to Project 2**: it's the brain, not voice-specific
3. **MCP Server moved to Project 4**: use during agent development
4. **Phaos added as subsystem**: existing code tracked, future work planned
5. **Retrieval eval suite added**: ground-truth queries for tuning
6. **Collection versioning added**: Qdrant migration strategy
7. **Email ingest moved to Project 2**: it's a data source, not a deploy concern
8. **Ruflo validation spike added**: verify before betting architecture on it

---

## Project 0: Foundation (Mostly Complete)

**Status (28 Mar 2026):** Core service skeleton is in place (FastAPI bus, env wiring, Qdrant/Ollama health check). Ruflo config + agent YAMLs exist; **Aegis policy files** now live under `zeus/safety/policies/` (see Project 5 / LAB-119). The **Ruflo validation spike (LAB-121)** remains **partially unverified** relative to full swarm behavior; bus + `AgentRuntime` are wired, but deep Ruflo-native validation is still open.


| Parent  | Title                              | Labels             | Subs |
| ------- | ---------------------------------- | ------------------ | ---- |
| LAB-43  | Repository & Dev Environment Setup | Feature, oracle    | 4    |
| LAB-130 | Qdrant & Ollama Infrastructure     | Feature, mnemosyne | 3    |
| LAB-134 | mem0 Initial Setup                 | Feature, mnemosyne | 3    |
| LAB-117 | Voice Tooling Validation           | Feature, orpheus   | 3    |
| LAB-135 | ChatGPT Data Export                | Feature, iris      | 2    |
| LAB-121 | Validate Ruflo v3.5 (spike)        | Feature, olympians | 0    |

### LAB-121: Validate Ruflo v3.5 (spike)
**Files:** `zeus/orchestration/ruflo.yaml`, `zeus/orchestration/agents/*.yaml`, `zeus/orchestration/bus.py`, `zeus/orchestration/runtime.py`

Closing this spike should establish whether **Ruflo owns** multi-step swarm semantics end-to-end. If yes, Zeus Core (**Project 7**, LAB-144–146) stays focused on routing, validation, and hooks. If not, Core must host explicit **plan → execute → reflect** patterns behind `/orchestration/call` without needlessly duplicating Ruflo. Cross-link: **Backlog** items *Olympians: planner–executor–reflector pipeline* and *tool/LLM retry + validation policy*; **LAB-144** for task runtime.


## Project 1: Text Chat + Sessions

**Status (25 Mar 2026):** Phase 1 shipped, session layer + text chat UI are implemented (`zeus/core/sessions.py`, `zeus/core/chat.py`, `zeus/core/static/chat.html`) and wired into the Core app (`zeus/core/main.py`). Mark **LAB-184** and **LAB-187** done in Linear after smoke tests.

| Parent  | Title               | Labels          | Subs |
| ------- | ------------------- | --------------- | ---- |
| LAB-184 | Session Layer       | Feature, oracle | 5    |
| LAB-187 | Text Chat Interface | Feature, oracle | 5    |


## Project 2: Data Brain

**Status (28 Mar 2026):**

- **Implemented**:
  - **LAB-45 (ChatGPT Export Parser)**: `zeus/ingest/sources/chatgpt.py`
  - **LAB-46 (Markdown File Walker)**: `zeus/ingest/sources/markdown.py`
  - **LAB-47 (Context-Pack Migration)**: `zeus/ingest/sources/context_pack.py`
  - **Ingest runner/CLI plumbing** (supports the above): `zeus/ingest/run.py`, `zeus/ingest/pipeline.py`
  - **LAB-48 (Zeus Context API v1 / Oracle)**: `zeus/api/main.py` (mounted by `zeus/core/main.py`)
  - **LAB-49 (Zeus Query Engine)**: `zeus/core/query.py` (used by chat routes)
- **Partially implemented / needs validation**:
  - **LAB-61 (mem0 Integration & Retrieval Quality)**: mem0 client + retrieval helpers exist (`zeus/memory/config.py`, `zeus/memory/search.py`), but quality eval harness / tuning loop isn’t represented as a dedicated suite yet. **Orchestration alignment:** add sub-scope or child work for **retrieval after summarization** and **execution-log / task summaries** in memory (short-term session vs long-term vector vs structured execution trail). Cross-link: **Backlog** *Mnemosyne: task execution log + rolling summaries*; **Project 7** LAB-144.
  - **LAB-56 (Privacy & Data Governance / Aegis)**: **in-process Aegis** is present (`zeus/safety/policy_engine.py`, YAML under `zeus/safety/policies/`, optional `ZEUS_AEGIS_ENABLED` / `ZEUS_AEGIS_POLICY` / `NEMOCLAW_POLICY` per `.env.example`). Chat, streaming chat, voice text responses, and `/orchestration/call` outputs can be filtered by policy. **Still open** on this ticket: privacy level tagging, PII scanning across ingest, deduplication strategy, collection versioning; see ticket scope. **Orchestration alignment:** **input validation**, **tool argument checks**, and **defensive execution** (no blind tool runs). Cross-link: **Backlog** *Aegis: tool argument verification + execution guardrails*; **Project 7** LAB-145–146; **Project 10** LAB-326 (bus pre-hook + `evaluate_payload`).
- **Not started (no code present yet)**:
  - **LAB-64 (Email Ingest)**: General email ingest (starred/sent) not started. Newsletter-specific email ingest shipped via LAB-336.

| Parent | Title                                | Labels             | Subs |
| ------ | ------------------------------------ | ------------------ | ---- |
| LAB-45 | ChatGPT Export Parser                | Feature, iris      | 5    |
| LAB-46 | Markdown File Walker                 | Feature, iris      | 5    |
| LAB-47 | Context-Pack Migration               | Feature, iris      | 4    |
| LAB-48 | Zeus Context API v1 (Oracle)         | Feature, oracle    | 6    |
| LAB-49 | Zeus Query Engine                    | Feature, oracle    | 4    |
| LAB-61 | mem0 Integration & Retrieval Quality | Feature, mnemosyne | 6    |
| LAB-56 | Privacy & Data Governance            | Feature, aegis     | 5    |
| LAB-64 | Phase 2 Data Sources — Email Ingest  | Feature, iris      | 4    |
| LAB-152 | Obsidian frontmatter full YAML support | Feature, iris    | 2    |
| LAB-153 | IngestPipeline memory client injection | Feature, iris    | 3    |

### LAB-152: Obsidian frontmatter full YAML support
**File:** `zeus/ingest/sources/obsidian.py`, `_parse_frontmatter()` · **Priority:** Low · **Status:** Deferred

Current parser is a hand-rolled `key: value` line splitter, won't handle lists, quoted strings with colons, multiline values, or nested objects. The misleading "YAML" comment has been fixed to say "simple key:value frontmatter". Only matters if the vault uses complex frontmatter.

**Fix:** Replace with PyYAML:
```python
import yaml
def _parse_frontmatter(text: str) -> tuple[dict, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, text[match.end():].strip()
```
Add `pyyaml` to `requirements.txt`. Trigger: ingestion failing on real vault frontmatter.

### LAB-153: IngestPipeline memory client injection
**File:** `zeus/ingest/pipeline.py`, `run_ingest()` · **Priority:** Medium · **Status:** Deferred (pre-Olympus always-on)

`run_ingest()` calls `get_memory_client()` internally on every scheduled run, creating a fresh mem0/Qdrant client each time instead of reusing `app.state.memory`. Adds connection overhead and complicates clean shutdown.

**Fix:** Add optional `memory` param to `IngestPipeline.__init__` and thread it through to `run_ingest`. In `main.py` lifespan, pass `memory=app.state.memory` when constructing the pipeline. Gate on **Project 6**.

### LAB-336: Newsletter Digest System ✅
**Status (9 Apr 2026): Shipped**: merged via PR #22.
**Files:** `zeus/ingest/sources/newsletter.py`, `zeus/core/newsletter.py`, `zeus/core/static/newsletters.html`, `tests/test_newsletter.py` (44 tests)

IMAP fetch → LLM summarization → optional TTS audio → web UI. Uses `IngestSource` protocol, `_run_llm()` for env-aware Claude/Ollama, `VoiceboxTTS.synthesize()`, `asyncio.to_thread()` for blocking IMAP.

| Sub | Title | Status | Notes |
|-----|-------|--------|-------|
| LAB-337 | Newsletter IMAP Fetch + Parse | ✅ Done | `zeus/ingest/sources/newsletter.py` |
| LAB-338 | Newsletter Summarization Endpoint | ✅ Done | `POST /api/newsletter/digest` |
| LAB-339 | Newsletter TTS Audio Generation | ✅ Done | Voicebox WAV, `/api/newsletter/audio/` |
| LAB-340 | Newsletter Web UI Page | ✅ Done | `/newsletters` route, dark/light theme |
| LAB-341 | Newsletter Schedule Skeleton + Manifest | ✅ Done | JSON manifest at `zeus/data/newsletters/` |

**Extension tickets (deferred):**

| Sub | Title | Priority | Notes |
|-----|-------|----------|-------|
| LAB-342 | Newsletter Qdrant Ingest — Wire chunks() into Mnemosyne | Medium | Store summaries + raw content in Qdrant for retrieval; cross-link LAB-61 |
| LAB-343 | Newsletter Scheduled Digests via KAIROS | Low | `NewsletterObservationSource` for KAIROS daemon; depends on LAB-330 |
| LAB-344 | Newsletter Multi-Source Aggregated Digest | Low | Theme-grouped bullets, source attribution, dedup overlapping stories |

**Dependencies:** LAB-342 is self-contained. LAB-343 requires LAB-330 (KAIROS). LAB-344 is self-contained (prompt + model + UI changes only).


## Project 3: Voice Loop

**Status (25 Mar 2026):** Phaos “voice-state” plumbing + visualization assets exist, and the Orpheus voice loop now has initial code checked in (STT client, wake word detector, TTS client, and an end-to-end host-native pipeline). WhisperLiveKit is added as a Docker service in `compose.yaml`; Voicebox remains host-managed (no compose image yet).

- **Implemented (Phaos surface area)**:
  - Voice-state protocol + hub/emitter: `zeus/voice/state.py`
  - WebSocket + publish endpoint: `zeus/core/voice_ws.py`
  - Viz UI assets: `zeus/core/static/viz/` (served via `/viz` in `zeus/core/chat.py`)
- **Implemented (Orpheus initial loop)**:
  - WhisperLiveKit STT client (WebSocket): `zeus/voice/stt.py`
  - openWakeWord detector (PyAudio 16kHz): `zeus/voice/wake.py`
  - Voicebox REST TTS client (streaming sentences): `zeus/voice/tts.py`
  - Orpheus orchestrator loop + Phaos emitter: `zeus/voice/pipeline.py`
  - Non-wake-word test endpoint (WAV upload): `zeus/core/chat.py` (`POST /voice/interact`)
- **Gap (future):** `llm_stream()` in `zeus/voice/pipeline.py` always streams from Ollama, while text chat can use Claude in dev via `zeus/core/query.py` (`_chat_use_claude()`). Closing the gap means Anthropic streaming + the same env switches (`ZEUS_ENV`, `ZEUS_LLM`, `ANTHROPIC_API_KEY`). Tracked in Backlog as **Orpheus voice LLM env parity**.

| Parent | Title                           | Labels           | Subs |
| ------ | ------------------------------- | ---------------- | ---- |
| LAB-51 | WhisperLiveKit STT Setup        | Feature, orpheus | 4    |
| LAB-52 | openWakeWord Integration        | Feature, orpheus | 4    |
| LAB-53 | Voicebox TTS Client             | Feature, orpheus | 4    |
| LAB-54 | Phaos Voice-State Visualization | Feature, phaos   | 5    |
| LAB-55 | Voice Pipeline End-to-End       | Feature, orpheus | 5    |


## Project 4: MCP Server

**Status (25 Mar 2026):** MCP server implementation is now checked in under `zeus/mcp/` using the MCP Python SDK `FastMCP`. Tool calls proxy to Zeus Core HTTP endpoints. Automated integration tests are not present yet; smoke testing is supported via running the server and calling tools from an MCP client.

| Parent  | Title                   | Labels          | Subs |
| ------- | ----------------------- | --------------- | ---- |
| LAB-104 | MCP Server Core         | Feature, oracle | 4    |
| LAB-107 | MCP Tool Definitions    | Feature, oracle | 5    |
| LAB-108 | MCP Integration Testing | Feature, oracle | 4    |


## Project 5: Ruflo Agents

**Status (28 Mar 2026):** Ruflo config and agent YAMLs exist (`zeus/orchestration/ruflo.yaml`, `zeus/orchestration/agents/*.yaml`). **`zeus/safety/policies/`** is populated and wired: per-agent `safety.policy` values (`standard`, `ingest`, `voice`, `memory`, etc.) map to YAML files; `/orchestration/call` runs an Aegis post-hook when `ZEUS_AEGIS_ENABLED=1`. **NemoClaw + OpenShell** are **operational on daedalus**: sandbox running, Control UI via SSH tunnel, inference routed OpenShell gateway → **zeus-ollama** (`11435`) → `qwen2.5:7b-instruct`; **`openclaw.json`** `models.providers.inference.api` set to **`openai-completions`** for Ollama (not `openai-responses`). Operational runbook: **`docs/nemoclaw-ops.md`**. **Still open:** custom network policies (Phase 5 YAML) not fully validated end-to-end, context-budget / workspace trimming for 7B, Ruflo spike (**LAB-121**) broader than NemoClaw wiring alone.

| Parent  | Title                          | Labels             | Subs |
| ------- | ------------------------------ | ------------------ | ---- |
| LAB-112 | Ruflo Initialization           | Feature, olympians | 3    |
| LAB-113 | Zeus Personal Agent            | Feature, olympians | 4    |
| LAB-114 | Zeus Dev Agent                 | Feature, olympians | 4    |
| LAB-116 | Zeus Research Agent            | Feature, olympians | 4    |
| LAB-119 | NemoClaw Safety Layer (Aegis)  | Feature, aegis     | 5    |
| LAB-120 | Multi-Agent Orchestration Test | Feature, olympians | 4    |

### LAB-119: NemoClaw Safety Layer (Aegis)
**Files:** `zeus/safety/policy_engine.py`, `zeus/safety/integration.py`, `zeus/safety/policies/*.yaml` · **`compose.yaml`** (Aegis comment block) · **`.env.example`** (Aegis env vars) · **`zeus/core/query.py`** (chat + stream) · **`zeus/orchestration/bus.py`** (bus post-hook) · **`zeus/core/main.py`** (`orchestration_hooks`)

**Done in repo (Mar 2026):** YAML rule packs; `AegisPolicyEngine`; optional enforcement on Core query paths and orchestration bus responses; policy names aligned with agent YAML + Phase 5e examples (`personal`, `code_execution`, `citation_required`, etc.).

**Done on daedalus (Mar 2026):** NemoClaw + OpenShell installed per [NemoClaw quickstart](https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html); OpenClaw sandbox + Control UI; inference to **zeus-ollama** on host port **11435** with **`openai-completions`** API mode in `openclaw.json`. Commands and troubleshooting: **`docs/nemoclaw-ops.md`**.

**Closed (Mar 2026):** `trustedProxies` / `allowedOrigins` verified; Phase 5 `policy-zeus.yaml` applied and confirmed no 403s to zeus-ollama:11435 or zeus-core:8203 (fill in after daedalus validation); first `nemo-backup` completed (see Phase 6 notes in `nemoclaw-ops.md`); slim workspace templates (`SOUL.md`, `IDENTITY.md`, `AGENTS.md`) added to `zeus/safety/workspace-templates/`, context budget reduced from ~16K to ~350 tokens; agent quality pass completed.

**Still open (optional):** Rename OpenShell provider `ollama-local` → `zeus-ollama` (cosmetic, low priority). `NEMOCLAW_RUNTIME_URL` sidecar integration deferred until NemoClaw ships a stable HTTP API.


## Project 6: Deploy to Olympus

**Compose / network (dev tower):** `compose.yaml` declares `homelab-web` as an **external** Docker network so Zeus can sit alongside other homelab stacks. On a fresh machine that network must exist (`docker network create homelab-web`) or you need a compose override that replaces it with an internal network for isolated local testing. Tracked in Backlog as **Compose dev ergonomics**.

**Aegis / NemoClaw:** Compose file includes a comment block clarifying that the full NemoClaw + OpenShell stack is **not** a Zeus compose service image; it runs on the host (daedalus). Zeus still applies in-process Aegis when enabled. See **`docs/nemoclaw-ops.md`** for the live install.


| Parent  | Title                           | Labels           | Subs |
| ------- | ------------------------------- | ---------------- | ---- |
| LAB-124 | Docker Compose Production Stack | Feature, oracle  | 4    |
| LAB-128 | Server Deployment               | Feature, oracle  | 4    |
| LAB-140 | Always-On Service Mode          | Feature, oracle  | 4    |
| LAB-141 | Server Voice Pipeline           | Feature, orpheus | 4    |


## Project 7: Orchestration Runtime

**Status (2 Apr 2026):** Runtime skeleton is in place: `zeus/orchestration/runtime.py` (YAML load, agent lifecycle), `zeus/orchestration/bus.py` (`/orchestration/call`, status, agent actions), `zeus/orchestration/hooks.py`. Aegis can post-filter orchestration responses. **LAB-144–146** below spell out **task-oriented** behavior (plan → act → reflect), bus hardening, and hook-based retries, patterns that improve reliability more than raw model swaps alone.

**Cross-links:** **LAB-121** (whether Ruflo owns multi-step semantics vs Core); **LAB-61** (execution summaries + retrieval); **LAB-56** (tool validation / defensive execution). **Backlog** rows under *Orchestration patterns (agent systems roadmap)* implement the same themes as dedicated Linear issues when the workspace limit allows.

| Parent  | Title                   | Labels             | Subs |
| ------- | ----------------------- | ------------------ | ---- |
| LAB-144 | Agent Runtime Engine    | Feature, olympians | 4    |
| LAB-145 | Agent Communication Bus | Feature, olympians | 4    |
| LAB-146 | Orchestration Hooks     | Feature, olympians | 4    |

### LAB-144: Agent Runtime Engine
**Files:** `zeus/orchestration/runtime.py`, `zeus/orchestration/bus.py`, `zeus/core/main.py`

`start_agent()` in `runtime.py` is currently a status-flag flip only (no task runner, no step executor). Task-based invocation requires three concrete additions:

1. **`AgentStep` + `TaskRecord` models**: `AgentDefinition` gains optional `steps: list[AgentStep]` parsed from YAML. `TaskRecord` (id, steps, status, elapsed_ms) goes into a ring buffer on `app.state.task_records` so the agent panel (LAB-289) can read them without a database.
2. **`TaskRunner` inner class** in `runtime.py`, iterates `AgentStep` objects, collects `StepResult`, surfaces `TaskRecord`. Step `on_failure` can be `skip | retry | abort`.
3. **`POST /orchestration/tasks`** in `bus.py`, accepts `{agent, task_description, steps: list | None}`, dispatches to `TaskRunner`, returns `{task_id, status}` immediately; poll via `/orchestration/tasks/{task_id}`.

**LAB-121** decides whether Ruflo calls this route or Zeus Core does, avoid duplicating the controller.

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-331 | AgentStep + TaskRecord models | Add to `runtime.py`; parse `steps:` block from agent YAML |
| LAB-332 | TaskRunner inner class | Iterates steps, collects StepResult, ring buffer |
| LAB-333 | `POST /orchestration/tasks` route | `bus.py`; returns task_id, poll endpoint |
| LAB-334 | TaskRunner integration tests | Smoke test with oracle agent's `/context/query` step |

### LAB-145: Agent Communication Bus
**Files:** `zeus/orchestration/bus.py`

Current `bus_call()` route has no correlation ID, hardcoded 30s timeout, and `payload: dict[str, Any]` (unvalidated). Concrete additions:

1. **Correlation IDs**: `BusCallRequest` gets `correlation_id: str | None = None`; generate `uuid4()` if absent; echo in `BusCallResponse`; log `[bus:call correlation_id=...]` in pre-hook.
2. **Per-agent timeouts**: read `config.timeout_seconds` from `AgentDefinition.config` (freeform dict already parsed from YAML); pass to `client.post(..., timeout=timeout)`.
3. **Idempotency flag**: `idempotent: bool = False` on `BusCallRequest`; if `True` and status is non-500 error, log warning instead of raising. Document retry contract in docstring.

Validated tool outputs feed the next hop and **LAB-146** (retry/refine). Aligns with **LAB-56** defensive execution.

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-335 | Correlation IDs on BusCallRequest/Response | Generate uuid4 if absent; echo in response |
| LAB-336 | Per-agent timeout from config YAML | Read `config.timeout_seconds`; pass to httpx |
| LAB-337 | Idempotency flag + retry contract docs | `BusCallRequest.idempotent`; docstring update |

### LAB-146: Orchestration Hooks
**Files:** `zeus/orchestration/hooks.py`, `zeus/orchestration/bus.py`, `zeus/safety/integration.py`

The pre-hook slot in `HookRegistry.run_pre()` is called by `bus_call()` but **no pre-hook is registered**: only the Aegis post-hook exists. The pre-hook slot is structurally ready (confirmed in `main.py` lifespan). Concrete additions:

1. **Retry-with-backoff post-hook**: `retry_on_error_post_hook` in `hooks.py`; mirrors the `_is_transient_ingest_error` / exponential backoff pattern from `ingest/pipeline.py`; sets `context["should_retry"] = True`; `bus_call()` checks after `run_post()` and loops up to `MAX_RETRIES = 3` (0.5s / 1s backoff).
2. **Bus metrics post-hook**: increments `app.state.bus_metrics[agent][calls/errors/latency_total_ms]`; surfaces to `/admin` (LAB-148).
3. **Pre-hook context contract**: document mandatory keys (`source`, `target`, `endpoint`, `payload`, `safety_policy`, `correlation_id`); add `validate_context_keys()` helper enforced in `ZEUS_ENV=dev`.

Hooks do not replace Aegis policy, they add orchestration-level validate → retry → refine on top.

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-338 | Retry-with-backoff post-hook | Max 3 attempts, exponential backoff, `should_retry` flag |
| LAB-339 | Bus metrics post-hook | `app.state.bus_metrics`; surfaces to `/admin` |
| LAB-340 | Pre-hook context contract + validator | `validate_context_keys()`; enforced in `ZEUS_ENV=dev` |


## Project 8: Observability + Admin

**Status (27 Mar 2026):** Sprint 9/10 PR merged. Middleware ring-buffer wiring, consolidate empty-payload guard, and pipeline incremental no-op log are fixed. Two security hardening tickets (LAB-150, LAB-151) deferred until Olympus deployment, VPN boundary covers them during dev.

| Parent  | Title                          | Labels                | Subs |
| ------- | ------------------------------ | --------------------- | ---- |
| LAB-147 | Metrics Collection             | Feature, oracle       | 4    |
| LAB-148 | Admin API Routes               | Feature, oracle       | 4    |
| LAB-149 | Admin Dashboard                | Feature, oracle       | 4    |
| LAB-150 | Admin endpoint auth hardening  | Feature, aegis        | 3    |
| LAB-151 | Admin dashboard XSS hardening  | Feature, aegis        | 2    |

### LAB-150: Admin endpoint auth hardening
**File:** `zeus/core/admin.py` · **Priority:** Medium · **Status:** Deferred (pre-Olympus)

`/admin/*` exposes agent status, Qdrant counts, and recent query metadata with no access control. Fine while bound to localhost/VPN; must be gated before any external exposure.

**Fix:** Add a `Depends` bearer token check on the `APIRouter`:
```python
import os
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()

def require_admin(credentials: HTTPAuthorizationCredentials = Security(_bearer)):
    token = os.getenv("ZEUS_ADMIN_TOKEN", "")
    if not token or credentials.credentials != token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
```
Wire `ZEUS_ADMIN_TOKEN` into `.env` and `compose.yaml`. Gate on **Project 6 (Deploy to Olympus)**.

### LAB-151: Admin dashboard XSS hardening
**File:** `zeus/core/static/admin.html` · **Priority:** Low · **Status:** Deferred (internal tool, same boundary as LAB-150)

`renderAgents()` and related render functions use `innerHTML` template literals with API-provided values (agent description, path, request ID). Any field containing `<`/`>` creates an XSS vector.

**Fix:** Add an escape helper and use it for all interpolated values:
```js
function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str ?? '';
  return d.innerHTML;
}
```
Do alongside LAB-150, both are the same admin surface hardening pass.


## Project 9: React Frontend + Integrations

**Status (31 Mar 2026):** Planned. Replaces the monolithic `chat.html` + `viz/viz.html` with a Vite + React + TypeScript SPA at `zeus/frontend/`. Multi-page routing, Phaos orb ported to `@react-three/fiber`, Telegram bot integration, OpenClaw agent orchestration panel.

**Tech:** Vite 5, React 19, TypeScript strict, React Router v6, Tailwind CSS v3, Zustand, `@react-three/fiber`, `python-telegram-bot`

**Repo layout (new):**
```
zeus/
  frontend/           # Vite + React app (build → zeus/core/static/app/)
    src/
      components/     # PhaosOrb, MessageList, SessionsSidebar, AgentCard, SourceBadge, …
      pages/          # ChatPage, AgentsPage, SettingsPage, VizPage
      hooks/          # useStreamingChat, useVoiceState
      store/          # chatStore, voiceStore, settingsStore (Zustand)
  integrations/
    telegram/         # bot.py — python-telegram-bot async bot
```

**Routes:** `/` (Chat + Orb), `/agents` (OpenClaw panel), `/settings` (Telegram, model, policy), `/viz` (Phaos orb fullscreen)

| Parent  | Title                            | Labels             | Subs |
| ------- | -------------------------------- | ------------------ | ---- |
| LAB-286 | React App Scaffold               | Feature, oracle    | 5    |
| LAB-287 | React Chat + Sessions View       | Feature, oracle    | 5    |
| LAB-288 | Phaos Orb React Component        | Feature, phaos     | 4    |
| LAB-289 | Agent Orchestration Panel        | Feature, olympians | 3    |
| LAB-290 | FastAPI SPA Serve                | Feature, oracle    | 4    |
| LAB-291 | Telegram Bot Backend             | Feature, iris      | 5    |
| LAB-292 | Telegram Frontend Integration    | Feature, oracle    | 3    |
| LAB-293 | React Settings Page              | Feature, oracle    | 3    |

### LAB-286: React App Scaffold
**Files:** `zeus/frontend/` (new) · **Priority:** High · **Blocks:** LAB-287, LAB-288, LAB-290, LAB-293

Vite 5 + React 19 + TypeScript project with React Router v6 routes (`/`, `/agents`, `/settings`, `/viz`), Tailwind CSS v3 theme tokens mirroring existing Zeus CSS vars, Zustand stores (`chatStore`, `voiceStore`, `settingsStore`), Vite dev proxy to FastAPI :8000, and `App.tsx` shell with header nav + theme toggle.

**Sub-issues:** LAB-294 (project init), LAB-295 (router + stubs), LAB-296 (Tailwind theme), LAB-297 (Zustand stores), LAB-298 (App shell + proxy)

### LAB-287: React Chat + Sessions View
**Files:** `zeus/frontend/src/pages/ChatPage.tsx`, `src/components/chat/` · **Priority:** High · **Blocks:** LAB-290

Port `chat.html` to React components: `SessionsSidebar` (GET /chat/sessions), `MessageList` + `ChatBubble`, `MarkdownMessage` (port `chat-markdown.js` via react-markdown), `ChatInput` (Enter/Shift+Enter), `useStreamingChat` SSE hook (POST /chat/stream).

**Sub-issues:** LAB-299 (SessionsSidebar), LAB-300 (MessageList + ChatBubble), LAB-301 (MarkdownMessage), LAB-302 (ChatInput), LAB-303 (StreamingChat SSE hook)

### LAB-288: Phaos Orb React Component
**Files:** `zeus/frontend/src/components/orb/PhaosOrb.tsx`, `src/hooks/useVoiceState.ts` · **Priority:** High

Port `orb.js` Three.js orb to `@react-three/fiber` `<Canvas>` preserving GLSL shaders verbatim. `useVoiceState` hook subscribes to `WS /ws/voice-state` → Zustand `voiceStore`. Compact sidebar panel mode on `/` + fullscreen `/viz` route (replaces `viz/viz.html`).

**Sub-issues:** LAB-304 (R3F Canvas + GLSL), LAB-305 (useVoiceState hook), LAB-306 (uniforms + state machine), LAB-307 (responsive + /viz route)

### LAB-289: Agent Orchestration Panel
**Files:** `zeus/frontend/src/pages/AgentsPage.tsx`, `src/components/agents/` · **Priority:** Normal · **Blocks:** LAB-290 (FastAPI SPA)

`/agents` page: `AgentCard` (name, model, aegis policy badge, status) from `GET /admin/agents`; `AgentInvokePanel` (task input → `POST /orchestration/call`, SSE stream); `ToolCallFeed` (collapsible per-tool log); `AegisPolicyBadge` colour-coded per policy.

**Sub-issues:** LAB-308 (AgentCard + list), LAB-309 (AgentInvokePanel), LAB-310 (ToolCallFeed + AegisPolicyBadge)

### LAB-290: FastAPI SPA Serve
**Files:** `zeus/core/main.py`, `zeus/core/chat.py`, `vite.config.ts`, `zeus/docs/deployment.md` · **Priority:** High · **Blocks:** LAB-289

Vite `outDir → zeus/core/static/app/`. `main.py`: mount `/assets`, add SPA catch-all `GET /{path:path}` returning `index.html` (registered last). `chat.py`: remove `GET /chat` HTML route, keep all API routes, add redirects for `/chat` → `/` and `/viz` → `/#/viz`.

**Sub-issues:** LAB-311 (Vite outDir + asset mount), LAB-312 (SPA catch-all), LAB-313 (API preservation + redirects), LAB-314 (deployment docs)

### LAB-291: Telegram Bot Backend
**Status (14 Apr 2026):** **Shipped** on `frontend-improvements`. End-to-end working in prod: the user messages the bot, QueryEngine runs, grounded reply comes back in plain text. Files: `zeus/integrations/telegram/{__init__,bot}.py` (new), `zeus/core/main.py` (lifespan + `/integrations/telegram/status`), `.env.example`, `requirements.txt`.

Delivered beyond the original scope:
- `markdown_to_plaintext()` stripper in `bot.py`, Telegram replies go out as clean plain text (code fences unwrapped, bold/italic removed, links rewritten as `text (url)`, list markers to `•`). Avoids MarkdownV2 parse failures from LLM output.
- Diagnostic logging: every incoming update is logged at INFO with `chat_id`/`user`/`text`, disallowed chats log at WARNING so drops are visible in docker logs.
- Runtime hot-restart: the bot can be rebuilt in-place from `PATCH /admin/settings` without a zeus-core restart.

**Sub-issues (all Done):** LAB-315 (module scaffold), LAB-316 (bot.py + allowed-list), LAB-317 (session mapping), LAB-318 (lifespan + env vars), LAB-319 (Aegis safety hook)

### LAB-292: Telegram Frontend Integration
**Files:** `zeus/frontend/src/components/SourceBadge.tsx`, `src/components/TelegramStatus.tsx` · **Priority:** Normal

`SourceBadge` on messages + session entries (telegram/web/voice icons). `TelegramStatus` dot in App header (polls `/integrations/telegram/status` every 30s). Settings page Telegram section (token, chat IDs, enable toggle, test button).

**Sub-issues:** LAB-320 (SourceBadge), LAB-321 (TelegramStatus + endpoint), LAB-322 (Settings Telegram section)

### LAB-293: React Settings Page
**Status (14 Apr 2026):** Partially shipped. Settings page layout and sections (Model, Aegis, Telegram, Sessions, Voice, Appearance) exist on `frontend-improvements`. Runtime settings now persist server-side:

- `zeus/core/runtime_settings.py`, JSON-backed `RuntimeSettings` store at `zeus/data/runtime_settings.json` (under `ZEUS_RUNTIME_SETTINGS_PATH`), thread-safe, section-scoped, survives rebuilds via the `zeus_data` volume.
- `GET /admin/settings` returns runtime settings with `bot_token` replaced by `bot_token_masked`.
- `PATCH /admin/settings` merges a `{telegram: {...}}` section, persists, and calls `_restart_telegram_bot(app)` so changes take effect in-place.
- Settings page hydrates from `GET /admin/settings` on mount and writes back on the Telegram section's **Save & Restart Bot** button. Token never leaves the server, UI shows a masked placeholder like `Saved: abcd…wxyz, leave blank to keep`.
- Model section shows live **benchmarks** (see LAB-363 below): tok/s next to each model, `Run Benchmarks` button, polling while a run is in progress.

Files: `zeus/core/main.py`, `zeus/core/runtime_settings.py`, `zeus/frontend/src/pages/SettingsPage.tsx`.

**Sub-issues:** LAB-323 (layout + scaffold), LAB-324 (Model + Aegis sections), LAB-325 (Sessions prefs + PATCH /settings).

**Still open:** wiring the Aegis policy dropdown to a `PATCH /admin/settings {aegis: {...}}` section, and moving the Sessions prefs off localStorage onto the runtime store.

---

## Project 10: Agentic Resilience

**Status (2 Apr 2026):** Planned. Fills five concrete gaps identified from Claude Code leak takeaways: Aegis pre-execution validation, QueryEngine reflection loop, expanded olympian tool pack, session persistence, and the KAIROS background agent daemon.

| Parent | Title | Labels | Subs |
|--------|-------|--------|------|
| LAB-326 | Aegis Pre-Hook (tool argument validation) | Feature, aegis, olympians | 3 |
| LAB-327 | QueryEngine Reflection Loop | Feature, oracle | 3 |
| LAB-328 | Olympian Tool Pack Expansion | Feature, olympians, aegis | 4 |
| LAB-329 | Session Persistence Backend | Feature, oracle, mnemosyne | 3 |
| LAB-330 | KAIROS Background Agent Daemon | Feature, olympians | 4 |

### LAB-326: Aegis Pre-Hook (Tool Argument Validation)
**Files:** `zeus/orchestration/hooks.py`, `zeus/safety/integration.py`, `zeus/safety/policy_engine.py` · **Priority:** High · **Blocks:** LAB-330 (KAIROS safety gates)

`aegis_bus_post_hook` in `integration.py` filters output. The `HookRegistry.register_pre()` slot in `main.py` is **empty**: only `register_aegis_bus_post_hook` is called in the lifespan. This ticket closes that gap.

1. **`aegis_bus_pre_hook(context)`** in `integration.py`, serialise `context["payload"]` field-by-field and run `evaluate_text(text, policy_name=context.get("safety_policy"))`; raise `HTTPException(400, detail=outcome.message)` on rejection. Aborts `bus_call()` before the httpx forward.
2. **`register_aegis_bus_pre_hook(registry)`** in `integration.py`, mirror of existing `register_aegis_bus_post_hook`; called from `main.py` lifespan alongside post-hook.
3. **`AegisPolicyEngine.evaluate_payload(payload: dict)`**: new method; flattens dict values to strings, runs each through the rule set, returns first rejection or aggregate `SafetyOutcome`. Used by pre-hook instead of serialising the whole payload to JSON (avoids false positives on structured data).

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-341 | `aegis_bus_pre_hook` + register function | `integration.py`; raises 400 on rejection; wired in `main.py` |
| LAB-342 | Prompt injection YAML rule | `policies/standard.yaml`; pattern `(?i)(ignore previous instructions\|disregard your system prompt\|act as .{0,40} without restrictions)`; action `reject` |
| LAB-343 | `AegisPolicyEngine.evaluate_payload()` | Field-by-field dict evaluation; used by pre-hook and KAIROS |

**Cross-links:** LAB-146 (hook context contract, LAB-340), LAB-56 (defensive execution)

### LAB-327: QueryEngine Reflection Loop
**Files:** `zeus/core/query.py` · **Priority:** High

`QueryEngine.query()` calls `_run_llm()` exactly once; any failure or empty reply propagates immediately. The ingest pipeline (`ingest/pipeline.py`) already demonstrates the canonical Zeus retry pattern (attempt counter, exponential backoff, `_is_transient_error()` classifier), replicate it here.

1. **`_is_empty_or_failed_reply(reply: str) -> bool`**: returns `True` if reply is empty, `< 10 chars`, or matches `^(sorry|I (can't|cannot)|I don't know)`. Testable pure function.
2. **`_build_reflection_prompt(original, failed_reply, attempt)`**: prepends `"[Attempt {attempt}] Your previous response was insufficient: '{failed_reply[:100]}'. Rephrase and try again.\n\n"` before the original query.
3. **Retry loop in `QueryEngine.query()`**: replace single `_run_llm()` call with loop up to `MAX_REFLECT = 3`; 0.5s / 1s backoff; add `reflection_attempts: int` to `QueryResult`.
4. **Same for `query_stream()`**: collect first stream fully, classify; if failed emit `[Retry]` sentinel token then stream refined attempt (React frontend can show "retrying…" state).

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-344 | `_is_empty_or_failed_reply` + reflection prompt builder | `query.py`; pure functions, unit-testable |
| LAB-345 | Reflection loop in `query()` | Replace single `_run_llm` call; add `reflection_attempts` to `QueryResult` |
| LAB-346 | Streaming reflection + `[Retry]` sentinel | `query_stream()` path; frontend can show retry state |

**Cross-links:** LAB-144 (TaskRunner uses same pattern), LAB-61 (retrieval alignment after reflection)

### LAB-328: Olympian Tool Pack Expansion
**Files:** new `zeus/mcp/olympian_tools.py`, `zeus/mcp/server.py` · **Priority:** Medium · **Blocks:** LAB-330 (KAIROS)

Current MCP tools (`zeus_query`, `zeus_profile`, `zeus_remember`) are memory read/write only. Agent YAMLs list `file_read`, `bus_call`, none exist as callable tools. All new tools follow the `olympian_` prefix and the existing `zeus_` pattern (httpx call to `_core_url()`).

1. **`olympian_file_read(path, max_lines=200)`**: validate `path` against `ZEUS_FILE_READ_ROOTS` allowlist (env var, default `./,/tmp/zeus-sandbox`); return `{content, lines, path, truncated}`.
2. **`olympian_search(query, path, glob, max_results=20)`**: async `rg --json` subprocess; Python `re.findall` fallback; same path allowlist; return `{matches: [{file, line, text}], total}`.
3. **`olympian_shell(command, timeout=30)`**: gated by `ZEUS_SHELL_ENABLED=1`; command must match `ZEUS_SHELL_ALLOWLIST` (newline-separated regexes); Aegis post-filters stdout; hard kill after timeout; **never** in KAIROS default allowlist.
4. **`olympian_memory_search(query, namespace, top_k=5)`**: extends `zeus_query` with explicit namespace filtering; proxies to `/context/query` with `namespaces=[namespace]`.

All four tools registered in `server.py` via `@mcp.tool()`. Shell tool env-gated at registration time.

**Agent YAML update:** rename `file_read` → `olympian_file_read` in `iris.yaml`; `mem0_search` → `olympian_memory_search` in `mnemosyne.yaml`.

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-347 | `olympian_file_read` + path allowlist | `olympian_tools.py`; `ZEUS_FILE_READ_ROOTS` env var |
| LAB-348 | `olympian_search` (ripgrep + Python fallback) | Async subprocess; same sandbox |
| LAB-349 | `olympian_shell` + allowlist guard | Gated by `ZEUS_SHELL_ENABLED`; Aegis post-filter |
| LAB-350 | `olympian_memory_search` + server registration | Namespace-aware; register all 4 tools in `server.py` |

**Cross-links:** LAB-326 (pre-hook validates tool args before shell runs), LAB-56

### LAB-329: Session Persistence Backend
**Files:** new `zeus/core/session_storage.py`, `zeus/core/main.py` · **Priority:** Medium · **Blocks:** LAB-291 (Telegram sessions), LAB-330 (KAIROS memory continuity)

`SessionManager` accepts any `SessionStorage` Protocol (`sessions.py` lines 67-75), `InMemoryStorage` is the only implementation. Sessions are **lost on every server restart**. The Protocol is the seam: no changes needed to `SessionManager` or `QueryEngine`.

1. **`SQLiteSessionStorage`** in `zeus/core/session_storage.py`, implements `SessionStorage` Protocol; `asyncio.to_thread` + stdlib `sqlite3` (no new deps); table `sessions(id TEXT PK, data TEXT, updated_at REAL)`; serialises via `Session.model_dump_json()` / `model_validate_json()`.
2. **`ZEUS_SESSION_BACKEND`** env var in `main.py` lifespan, `"memory"` (default, backward-compatible) or `"sqlite"`; `ZEUS_SESSION_DB_PATH` defaults to `zeus/data/sessions.db`.
3. **`.env.example` + `compose.yaml`** update, document both vars; add `zeus/data/` volume mount so SQLite persists across container restarts.

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-351 | `SQLiteSessionStorage` class | `session_storage.py`; no new deps |
| LAB-352 | `ZEUS_SESSION_BACKEND` env var + lifespan wiring | `main.py`; backward-compatible default |
| LAB-353 | `.env.example` + `compose.yaml` update | Document vars; mount `zeus/data/` volume |

**Cross-links:** LAB-153 (IngestPipeline memory client injection, same swap pattern), LAB-291

### LAB-330: KAIROS Background Agent Daemon
**Files:** new `zeus/orchestration/daemon.py`, `zeus/core/main.py` · **Priority:** Low · **Requires:** LAB-332 (TaskRunner), LAB-328 (tool pack), LAB-329 (session persistence)

**Naming:** `kairos`, Greek personification of the opportune moment. Generalises `OrpheusPipeline.run_forever()` (observe→decide→act loop) without audio hardware dependency. Reuses `TaskRunner` (LAB-332) for step execution.

1. **`ObservationSource` Protocol + `MemoryDriftObserver`**: `async def observe() -> Observation | None`; `MemoryDriftObserver` calls `search_memories("what changed recently", limit=1)` and compares timestamps with last-cycle watermark; returns `None` on idle cycle.
2. **`KairosAgent` class**: `observe() / decide(obs) / act(plan) / update_memory(result)`; `decide()` is an LLM call returning `CognitivePlan(steps: list[ToolCall])`; `act()` iterates steps via `olympian_*` tools using `TaskRunner`; `update_memory()` calls `zeus_remember(text=summary, namespace="execution_log")`.
3. **`KairosDaemon` wrapper + lifespan**: `asyncio.Event` stop; gated by `ZEUS_KAIROS_ENABLED=1`; `KAIROS_INTERVAL_MINUTES` (default 60); `KAIROS_MAX_ACTIONS_PER_CYCLE` (default 5); registered as `asyncio.create_task` in FastAPI lifespan; shutdown sets stop event.
4. **Safety gates + status endpoint**: `evaluate_payload()` (LAB-343) on every `ToolCall.args` before execution; default `ZEUS_KAIROS_TOOL_ALLOWLIST = olympian_file_read,olympian_memory_search` (no shell, no write); `GET /orchestration/kairos/status` returns `{enabled, last_cycle_at, last_action_summary, cycle_count, errors}`.

| Sub | Title | Notes |
|-----|-------|-------|
| LAB-354 | `ObservationSource` Protocol + `MemoryDriftObserver` | `daemon.py`; checks mem0 for new additions |
| LAB-355 | `KairosAgent` observe/decide/act/update loop | LLM-driven decision; reuses TaskRunner |
| LAB-356 | `KairosDaemon` wrapper + lifespan wiring | `asyncio.Event` stop; `ZEUS_KAIROS_ENABLED` gate |
| LAB-357 | KAIROS safety gates + `/orchestration/kairos/status` | Tool allowlist; status endpoint |

**Cross-links:** LAB-327 (reflection loop for KAIROS decide step), LAB-144 (TaskRunner reuse)


---

## Backlog

Themes below that mirror **task loops, tool-first design, structured memory, and defensive execution** are tracked under **Project 7 (LAB-144–146)** and **Project 10 (LAB-326–357)**. **Linear (Apr 2026):** Project 10 **parents** are filed as **LAB-326–330**; Project 7 **subs** LAB-331–340 are doc IDs only until you create child issues under LAB-144–146. Subs under LAB-326–330 (LAB-341+) remain to be filed when the workspace limit allows.

| Title                                        | Labels             |
| -------------------------------------------- | ------------------ |
| Orpheus voice LLM env parity (Claude vs Ollama) | Feature, orpheus |
| Compose dev ergonomics: `homelab-web` vs internal network | Feature, oracle |
| VR Prototype — Zeus voice + avatar in Oculus | Feature, orpheus   |
| Meta AR Glasses Integration                  | Feature, orpheus   |
| Watch Vitals Integration                     | Feature, iris      |
| Business Productization                      | Feature            |
| Model Fine-Tuning                            | Feature, mnemosyne |
| Graph Memory (mem0g)                         | Feature, mnemosyne |
| Memory Decay Policy                          | Feature, mnemosyne |
| Mnemosyne: task execution log + rolling summaries (index / pointer pattern) | Feature, mnemosyne, oracle |
| Olympians: planner–executor–reflector pipeline (structured steps) | Feature, olympians |
| Olympians: tool/LLM retry + validation policy | Feature, olympians, aegis |
| Olympians: core tool pack (read / search / run) + sandbox contract | Feature, olympians, aegis |
| Aegis: tool argument verification + execution guardrails | Feature, aegis, olympians |
| Background agent loop (observe–decide–act) — design + safety + resource gates | Feature, olympians, aegis |

### Backlog Implementation Notes

**Mnemosyne: task execution log + rolling summaries**
How: append `StepResult` objects to `Session.metadata["execution_log"]` (`metadata` is a freeform dict already present in `sessions.py`); KAIROS `update_memory()` (LAB-355) writes a summarised task record via `zeus_remember(namespace="execution_log")` so it survives session expiry. No schema migration needed.

**Olympians: planner–executor–reflector pipeline**
How: planner = LLM call in `POST /orchestration/tasks` (LAB-333) converting `task_description: str` into an ordered `list[AgentStep]` (Pydantic-validated); executor = `TaskRunner` (LAB-332); reflector = `_is_empty_or_failed_reply` (LAB-344) applied to each step's output before proceeding to the next step.

**Olympians: tool/LLM retry + validation policy**
How: bus-level retries via `retry_on_error_post_hook` (LAB-338); LLM-level via reflection loop (LAB-345). Extract `_is_transient_ingest_error` from `zeus/ingest/pipeline.py` into `zeus/core/retry.py` and import it from both retry sites. `MAX_RETRIES` configurable via `ZEUS_MAX_RETRIES` env var (default 3).

**Olympians: core tool pack + sandbox contract**
How: LAB-328 is the full implementation. Sandbox contract: all path-accepting tools validate against `ZEUS_FILE_READ_ROOTS`; shell gated by `ZEUS_SHELL_ENABLED`; contract documented in `zeus/mcp/olympian_tools.py` module docstring and `CLAUDE.md` Agentic Safety Contract section.

**Aegis: tool argument verification + execution guardrails**
How: LAB-326 (pre-hook + `evaluate_payload()`). For direct tool calls that bypass the bus (KAIROS, TaskRunner), each tool function also validates path allowlist internally, defence in depth. Pre-hook fires first; tool-level check is the backstop.

**Background agent loop (observe–decide–act), design + safety + resource gates**
How: LAB-330 KAIROS is the implementation. Resource gates: `KAIROS_MAX_ACTIONS_PER_CYCLE` (default 5) limits tool calls per cycle; `KAIROS_INTERVAL_MINUTES` (default 60) prevents runaway loops; CPU/memory bounded by existing Docker resource limits in `compose.yaml` (KAIROS runs in-process with Core).

**Note:** Some Project 7/8 sub-issues and all Backlog items may hit the Linear workspace issue limit. Archive completed issues before creating new ones.

---

## Recent deliveries on `frontend-improvements` (April 2026)

Tickets shipped in this branch that are not yet reflected in their original project summaries:

### LAB-361: Mnemosyne retrieval bug (URGENT, Done)
**Files:** `zeus/memory/search.py` · **Priority:** Urgent · **Parent:** LAB-61

mem0 ≥ 0.1.x changed `Memory.search()` to return `{"results": [...]}` instead of a bare list. `search_memories()` had `if not isinstance(results, list): return []`, so every retrieval silently dropped to empty, Telegram and chat both replied "I don't have that in memory" even though Qdrant had 396 points keyed by the configured `user_id`. Same bug in `get_profile_facts()`. Fix: `_unwrap_mem0_results()` handles both shapes. Verified end-to-end: `POST /memory/search "will allow OpenSSH in ufw"` → score 0.9654, `GET /context/profile` → 8 facts.

No data was lost; the Qdrant volume was intact throughout.

### LAB-363: `zeus.bench` local model benchmarking (In Progress, mostly shipped)
**Files:** `zeus/bench/{__init__,runner,__main__}.py` (new), `zeus/core/main.py`, `zeus/frontend/src/pages/SettingsPage.tsx` · **Priority:** Medium · **Linked:** `zeus/docs/model-comparison.md`

New `zeus/bench/` module that measures real tok/s, TTFT, and prompt-eval rate for every Ollama chat model on the current host using native `/api/generate` streaming response fields (`eval_count` / `eval_duration`). Suite: short / medium / long prompts at 16 / 200 / 600 max tokens, warm-up pass, `keep_alive=10m` to prevent cold-reload TTFT spikes. Persists to `zeus/data/benchmarks.json` (in the `zeus_data` volume).

Backend: `GET /models/benchmarks` (results + run status), `POST /models/benchmarks/run` (background asyncio task, 409 if already running, persists each result as it finishes).

Frontend: **Run Benchmarks** button in Settings → Model, tok/s shown inline next to each model in cyan with TTFT / prompt-eval tok/s in the tooltip, 2s polling while a run is in progress, `benchmarking…` badge on the current model.

CLI: `docker exec zeus-core python -m zeus.bench [models...] -v`.

**Measured on olympus (RTX 3080 10 GB + 112 GB host RAM, ~90–100 GB to the zeus VM):**

| Model | Gen tok/s | TTFT | Fits VRAM? |
|---|---:|---:|---|
| `qwen2.5:7b-instruct` | **119.4** | 304 ms | ✅ |
| `llama3.1:8b-instruct-q4_K_M` | 112.7 | 351 ms | ✅ |
| `qwen3:8b` | 100.3 | 274 ms | ✅ (thinking mode = longer replies) |
| `gpt-oss:20b` | 0.8 | 6.6 s | ❌ CPU offload |
| `qwen2.5:32b` | 0.1 | 15.8 s | ❌ heavy CPU offload |

Confirmed: **112 GB host RAM does not rescue models that exceed VRAM.** The 32B run sat at 0.1 tok/s and took 13 min for the long prompt. Only interactive-usable models on the 3080 are the 7–8B class. Active model set to `qwen2.5:7b-instruct` via `POST /models/active`.

**Follow-ups:** per-host comparison view (3080 vs future 5080 tower), grounded-answer quality eval tied to `tests/retrieval_eval.py`, benchmark history (currently only the latest run per model is stored).

### Dev ergonomics: `compose.override.yaml`
**Files:** `compose.override.yaml` (new) · Not ticketed

Auto-loaded docker-compose overlay that bind-mounts `./zeus:/app/zeus:ro` into `zeus-core` and sets `PYTHONDONTWRITEBYTECODE=1`. Lets pure-Python edits (server modules and one-shot CLI scripts like `zeus.bench`) take effect with a container restart (or no restart at all for `docker exec` scripts) instead of requiring a full ~6-minute image rebuild. Should be renamed or excluded from the prod deploy path on olympus, where the baked image is the source of truth.

### Collateral: Telegram plain-text formatter
See LAB-291 notes above. Not a new ticket.

### LAB-NEW-A: Memory / Knowledge layer split (Phase 1 parent, Code complete)
**Files:** `zeus/memory/library.py` (new), `zeus/memory/search.py`, `zeus/ingest/pipeline.py`, `zeus/ingest/sources/*.py`, `zeus/core/query.py`, `zeus/core/prompts/chat_system.md` · **Priority:** High · **Parent:** LAB-61 · **Doc:** `docs/memory-architecture-plan.md`

Splits the single `zeus_memories` Qdrant collection into a three-layer retrieval architecture so bulk RAG stops polluting the profile layer:

- **Mnemosyne / Memory** (`zeus_memories`, rebuilt), mem0 with LLM fact extraction; curated profile sources only (`context_pack`, `gcal`). Target size: 100–500 items.
- **Library / Knowledge** (`zeus_knowledge`, new), `KnowledgeStore` raw embed + Qdrant upsert, **no LLM** on the write path. Every bulk source (`markdown`, `obsidian`, `chatgpt`, `email`, `newsletter`, `bookmarks`, `git`). Target size: 10k–1M chunks.
- **Reference / Live** (Phase 2), kiwix Wikipedia + Project NOMAD via live HTTP proxy, schema-accepted but pipeline-rejected until then.

**What landed in Phase 1 code (prior to migration run):**

- `KnowledgeStore` class with batched Ollama embedding, Qdrant upsert, filtered search (user_id + sources), and `delete_by_source` for idempotent re-ingest. Singleton via `get_knowledge_store()`.
- Class-level `target: str` attribute on every `IngestSource` subclass.
- `run_ingest()` lazy-resolves mem0 client and/or `KnowledgeStore` based on which targets appear, dispatches per-chunk through `_store_chunk_memory` / `_store_chunk_knowledge`. Transient-retry loop, privacy classifier, progress bar, and error collection all wrap both paths identically. `IngestResult` gained `target` and `knowledge_ops` fields.
- `search_knowledge()` helper in `zeus/memory/search.py` returns mem0-shaped dicts so `format_context_block()` renders both layers through the same code path.
- `_collect_retrieval_context()` in `QueryEngine` runs profile + memory + knowledge fetches in parallel via `asyncio.gather`, applies sub-budgets (profile 20% / memory 25% / knowledge 55%; reference 10% rolled into knowledge until Phase 2). Used by both `query()` and `query_stream()`, eliminating the duplicated retrieval block.
- `zeus/core/prompts/chat_system.md` rewritten with four labelled blocks (`Profile`, `Memories`, `Knowledge`, `Reference`) plus reader guidance telling the model what each block represents.

**CJK hallucination bug (task J):** Root-caused, not an ingest parser bug. `rg` over the whole raw tree found zero CJK codepoints in any source file. The Chinese characters in `zeus_memories` came from **Qwen2.5-7B hallucinating CJK tokens during mem0 fact extraction** on short/garbled chunks under `ZEUS_LLM=ollama`. Fix is structural: routing bulk sources to Knowledge (no LLM extraction) eliminates it for every non-curated source. For the remaining memory-layer sources (`context_pack`, `gcal`), the mitigation is running ingest with `ZEUS_LLM=claude`. No source-parser change or file exclusion needed.

**Remaining, task K (migration):** Qdrant backup → drop `zeus_memories` → restart `zeus-core` → re-run ingest via `--target memory` (ZEUS_LLM=claude) and `--target knowledge` → spot-check via Telegram. Runbook in `docs/memory-architecture-plan.md`.

### LAB-NEW-B: Declarative ingest config (`ingest/config.yaml`)
**Files:** `zeus/ingest/config.py` (new), `zeus/ingest/config.yaml` (new), `zeus/ingest/run.py` · **Priority:** Medium · **Parent:** LAB-NEW-A

Pydantic-backed ingest config that declares per-source target (memory / knowledge / reference) and per-folder exclude rules. `zeus/ingest/run.py` loads it on every invocation, applies per-source target overrides onto built sources, and supports `--config`, `--no-config`, and `--target {memory,knowledge,both}` CLI flags. Env-var interpolation via `${VAR}` so `OBSIDIAN_VAULT_PATH` etc. stay out of the file. `reject_if_phase2_only()` hook makes the pipeline refuse `target: reference` until Phase 2 lands.

### LAB-NEW-C: Reference layer (Phase 2, not started)
**Files:** TBD, likely `zeus/memory/reference.py`, new `zeus_cache_reference` Qdrant collection · **Priority:** Low · **Blocked by:** Phase 1 migration (LAB-NEW-A task K) + quality eval (LAB-NEW-D)

Live HTTP proxy to kiwix-serve for Wikipedia ZIM and to Project NOMAD's Qdrant RAG (see `zeus/docs/project-nomad-integration.md`). No ingest, query at retrieval time. Optional `zeus_cache_reference` collection for frequently-hit snippets. `QueryEngine` adds the `Reference` block with its reserved 10% sub-budget once wired.

### LAB-NEW-D: Retrieval eval extension (Phase 3)
**Files:** `tests/retrieval_eval.py` · **Priority:** Medium · **Parent:** LAB-61

Extend the existing retrieval eval with labelled ground-truth queries (`profile_questions.yaml`, `knowledge_questions.yaml`) and measure recall@5 per layer. Use results to retune the retrieval sub-budget percentages, which are currently starting guesses (profile 20% / memory 25% / knowledge 55%).

---

## Retrieval + Fact-Extraction Spikes (April 2026) — results + tabled follow-ups

Four pre-implementation spikes from the hand-rolled memory / small-LLM / hybrid-retrieval plan (`/home/chris/.claude/plans/ok-i-tried-another-serene-lagoon.md`) ran against the live corpus (10,580 → 275k knowledge chunks across chatgpt, obsidian, markdown, newsletter, git). Summaries below; results JSONs under `tests/`.

### Spike 1: 30-query retrieval baseline ✅ Done
**Files:** `tests/retrieval_eval.py`, `tests/retrieval_eval_baseline.json`, `tests/retrieval_eval_dense_only.json`

Dense-only baseline on the existing `KnowledgeStore`: hit@1 = 0.60, hit@5 = 0.867, hit@10 = 0.933, MRR@10 = 0.71 over 30 hand-written queries covering Zeus system docs, astronomy coursework, homelab, chatgpt conversations, TLDR newsletter, git. Eval writes per-query report + aggregate JSON; optional `ZEUS_RETRIEVAL_MIN_HIT5` gate for CI.

### Spike 2: Hybrid (dense + BM25 RRF) vs dense-only ✅ Done
**Files:** `tests/retrieval_eval_baseline.json` (hybrid run)

No measurable lift at top-10 on this query set (keyword criterion already saturated at 86.7% headroom). Hybrid is kept on by default (`ZEUS_KNOWLEDGE_HYBRID=1`) because it's free, pairs well with rerank, and the eval's keyword-match criterion is a blunt instrument — a ground-truth extension (LAB-NEW-D) should give hybrid a fairer comparison.

### Spike 3: BGE-reranker-v2-m3 on CPU ✅ Done (rerank tabled for prod)
**Files:** `zeus/memory/reranker.py`, `tests/retrieval_eval_hybrid_rerank.json`

Real lift: hit@1 0.60 → **0.867**, MRR@10 0.71 → **0.875**. But CPU latency was 59 min for 30 queries × 40 candidates — ~2 min/query, unusable in a live chat path. Also uncovered one regression (Amazon Leo antenna query lost its top-10 hit to reranker score noise).

Action: `ZEUS_KNOWLEDGE_RERANK` stays `0` in prod. See LAB-NEW-F below for the GPU path that makes this viable.

### Spike 4: Fact-extraction provider shootout ✅ Done (2 router fixes tabled)
**Files:** `tests/fact_extract_spike.py`, `tests/fact_extract_spike_results.json`

20 representative messages × {gemini_paid, anthropic_haiku, ollama} with `response_format=FactExtraction, min_privacy_tier=1`:

| Provider | Schema OK | p50 / p95 | Cost (20 calls) | Failure mode |
|---|---|---|---|---|
| gemini_paid (2.5-flash-lite) | 12/20 | 1.6s / 2.8s | $0.0038 | HTTP 429 after ~12 rapid calls |
| anthropic_haiku (4.5) | **20/20** | 2.2s / 7.0s | $0.0653 | none |
| ollama (qwen2.5:7b) | 0/20 | — | $0 | ReadTimeout on every call |

Chain order `gemini_paid → anthropic_haiku → ollama` is confirmed as the right default for tier-1 fact extraction; two router fixes are needed before the chain is trustworthy in prod (LAB-NEW-E).

<<<<<<< Updated upstream
### LAB-NEW-E: `small_llm_call` router hardening (tabled)
**Files:** `zeus/core/small_llm.py` · **Priority:** Medium · **Parent:** LAB-NEW-A

Two targeted fixes before Spike 4 numbers can be trusted in prod:

1. **Gemini 429 backoff + jitter.** On HTTP 429 from `gemini_paid`, retry with exponential backoff (2s, 5s, 15s + jitter) up to 3 attempts before falling through to the next provider. Current behaviour is fail-fast, which burned $0.06 on the shootout because Haiku absorbed every Gemini rate-limit.
2. **Ollama structured-output timeout.** Raise `_call_ollama` read timeout from the default 120s to 300s (or stream + assemble) — qwen2.5:7b with a full extraction prompt + JSON schema exceeds 120s cold. After this, re-run Spike 4; if qwen still fails schema, ollama is empty-only fallback until we move to qwen2.5:14b on a larger GPU.

Verify: re-run `tests/fact_extract_spike.py` after each fix lands; Gemini row should be 20/20; ollama row should be schema_ok > 0.

### LAB-NEW-F: Reranker GPU sidecar (tabled)
=======
### LAB-NEW-E: `small_llm_call` router hardening ✅ Done (April 2026)

**Files:** `zeus/core/small_llm.py`, `.env.example`, `tests/fact_extract_spike_results_v2.json`, `tests/fact_extract_spike_ollama_only.json` · **Priority:** Medium · **Parent:** LAB-NEW-A

Two fixes landed:

1. **Gemini 429 backoff + jitter** — new `ZEUS_SMALL_LLM_RETRY_DELAYS_MS` (default `2000,5000,15000`, ±20% jitter) retries 429s inside `_call_openai_compat` before falling through to the next provider. Applies to all OpenAI-compat providers (gemini_paid, groq, openrouter).
2. **Ollama structured-output timeout** — `ZEUS_OLLAMA_SMALL_READ_TIMEOUT_SEC` (default `300`) replaces the hard-coded 120s read timeout in `_call_ollama`. Cold qwen2.5:7b loads that evict behind embeddings/reranker now have headroom.

Verification (v2 re-run + isolated ollama run):

| Provider        | v1               | v2 (router fixes, combined)          | v2-isolated (ollama)                                |
| --------------- | ---------------- | ------------------------------------ | --------------------------------------------------- |
| gemini_paid     | 12/20 (429s)     | 11/20 (persistent quota, 429/503)    | —                                                   |
| anthropic_haiku | 20/20            | 20/20 (p50 2.2s, p95 7.0s)           | —                                                   |
| ollama          | 0/20 (timeout)   | 0/20 (cold-reload after 15 min idle) | **20/20** (p50 2.8s, p95 5.1s, avg_conf 0.957)      |

Conclusion: chain `gemini_paid → anthropic_haiku → ollama` works in prod as long as qwen stays warm. Remaining Gemini failures are upstream quota (Google API key tier), not retryable in-process; per-minute quota tuning is out of scope for this ticket.

**Follow-up LAB-NEW-G**: VRAM contention between chat model (qwen2.5:7b), embedder (nomic-embed-text:v1.5), and reranker when it's enabled. On the 3080's 10 GB, `OLLAMA_MAX_LOADED_MODELS=2` means one of the three gets evicted under load and subsequent cold-reloads blow through 300s. Prod options: pin qwen + nomic with ollama preload; move reranker to a sidecar (LAB-NEW-F covers this for the 5080 path).

### LAB-NEW-F: Reranker GPU sidecar (tabled)

**Files:** TBD — likely a small FastAPI service on the 5080 (WSL) or a separate box · **Priority:** Low · **Parent:** LAB-NEW-A

Spike 3 showed +26.7 pp hit@1 and +0.165 MRR when reranker is on — the quality is there. CPU latency isn't. Prod path: run `BAAI/bge-reranker-v2-m3` on a GPU that isn't the 3080 (olympus keeps 10 GB dedicated to qwen2.5:7b). Two options, listed by effort:

- **Option A** (small): Tailscale the dev 5080 tower, expose a tiny `/rerank` endpoint, swap `zeus/memory/reranker.py` to HTTP-call mode. Works until the 5080 box is off.
- **Option B** (proper): A dedicated reranker service in `compose.yaml` on a host with spare VRAM (Jetson, second 3080, cloud GPU).

Re-enable `ZEUS_KNOWLEDGE_RERANK=1` in prod only when median rerank latency on a 20-candidate pass stays under 500 ms.

---

## Key Dependencies

- **LAB-48 (Context API)** blocks Projects 3, 4, 5, 6, 7, 8
- **LAB-184 (Session Layer)** blocks chat interface + voice pipeline
- **LAB-49 (Query Engine)** blocks voice pipeline + agents
- **LAB-121 (Ruflo Spike)** blocks Project 5 architecture; **informs Project 7 (LAB-144–146)**: Ruflo vs Core ownership of multi-step agent loops
- **LAB-144–146 (Orchestration Runtime)** depend on **LAB-48** and stable bus/runtime wiring; **LAB-145–146** align with **LAB-56** (defensive execution) and **LAB-61** (retrieval + summaries)
- **LAB-286 (React Scaffold)** blocks LAB-287, LAB-288, LAB-290, LAB-293
- **LAB-290 (FastAPI SPA Serve)** blocks LAB-289 (Agent Panel)
- **LAB-291 (Telegram Backend)** blocks LAB-292 (Telegram Frontend)
- **LAB-335–337 (Bus hardening)** are prerequisites for **LAB-338–340 (hook policies)** and **LAB-330 (KAIROS reliable cycles)**
- **LAB-326 (Aegis Pre-Hook)**: self-contained; plugs into existing `HookRegistry.register_pre()` slot in `main.py`; no other new LABs required first
- **LAB-327 (Reflection Loop)**: self-contained in `query.py`; benefits from LAB-340 (pre-hook context contract) being done first
- **LAB-328 (Tool Pack)** blocks LAB-330 (KAIROS needs tools to act with)
- **LAB-329 (Session Persistence)** blocks LAB-291 (Telegram sessions need persistence) and LAB-330 (KAIROS memory continuity across restarts)
- **LAB-330 (KAIROS)** depends on LAB-332 (TaskRunner), LAB-328 (tool pack), LAB-329 (session persistence)
- **LAB-342 (Newsletter Qdrant Ingest)**: self-contained; wires existing `chunks()` into digest flow
- **LAB-343 (Newsletter Scheduled Digests)** depends on LAB-330 (KAIROS daemon)
- **LAB-344 (Newsletter Multi-Source Aggregation)**: self-contained; prompt + model + UI only

