# Zeus — Linear Ticket Plan (Revised)

Full ticket structure for the Zeus project. Incorporates feedback on sprint ordering, Phaos subsystem, retrieval eval, collection versioning, and dependency awareness.

**Team:** Chris Lawrence Homelab
**Linear Projects:** Zeus 0–8 + Backlog

## Labels


| Label     | Color   | Subsystem                                              |
| --------- | ------- | ------------------------------------------------------ |
| mnemosyne | #7C3AED | Memory layer — mem0 + Qdrant                           |
| iris      | #10B981 | Ingest pipeline — data sources → chunks                |
| orpheus   | #F59E0B | Voice interface — STT, TTS, wake word                  |
| aegis     | #EF4444 | Safety layer — NemoClaw + OpenShell                    |
| oracle    | #3B82F6 | Zeus Context API — structured context                  |
| olympians | #EC4899 | Agent swarm — Ruflo-managed agents                     |
| phaos     | #06B6D4 | Voice-state visualization — Three.js, WebSocket, WebXR |


---

## Revised Sprint Ordering

Key changes from v1:

1. **Sessions & Chat moved to Project 1** — dev acceleration, text interface before voice
2. **Query Engine moved to Project 2** — it's the brain, not voice-specific
3. **MCP Server moved to Project 4** — use during agent development
4. **Phaos added as subsystem** — existing code tracked, future work planned
5. **Retrieval eval suite added** — ground-truth queries for tuning
6. **Collection versioning added** — Qdrant migration strategy
7. **Email ingest moved to Project 2** — it's a data source, not a deploy concern
8. **Ruflo validation spike added** — verify before betting architecture on it

---

## Project 0 — Foundation (Mostly Complete)

**Status (28 Mar 2026):** Core service skeleton is in place (FastAPI bus, env wiring, Qdrant/Ollama health check). Ruflo config + agent YAMLs exist; **Aegis policy files** now live under `zeus/safety/policies/` (see Project 5 / LAB-119). The **Ruflo validation spike (LAB-121)** remains **partially unverified** relative to full swarm behavior—bus + `AgentRuntime` are wired, but deep Ruflo-native validation is still open.


| Parent  | Title                              | Labels             | Subs |
| ------- | ---------------------------------- | ------------------ | ---- |
| LAB-43  | Repository & Dev Environment Setup | Feature, oracle    | 4    |
| LAB-130 | Qdrant & Ollama Infrastructure     | Feature, mnemosyne | 3    |
| LAB-134 | mem0 Initial Setup                 | Feature, mnemosyne | 3    |
| LAB-117 | Voice Tooling Validation           | Feature, orpheus   | 3    |
| LAB-135 | ChatGPT Data Export                | Feature, iris      | 2    |
| LAB-121 | Validate Ruflo v3.5 (spike)        | Feature, olympians | 0    |


## Project 1 — Text Chat + Sessions

**Status (25 Mar 2026):** Phase 1 shipped — session layer + text chat UI are implemented (`zeus/core/sessions.py`, `zeus/core/chat.py`, `zeus/core/static/chat.html`) and wired into the Core app (`zeus/core/main.py`). Mark **LAB-184** and **LAB-187** done in Linear after smoke tests.

| Parent  | Title               | Labels          | Subs |
| ------- | ------------------- | --------------- | ---- |
| LAB-184 | Session Layer       | Feature, oracle | 5    |
| LAB-187 | Text Chat Interface | Feature, oracle | 5    |


## Project 2 — Data Brain

**Status (28 Mar 2026):**

- **Implemented**:
  - **LAB-45 (ChatGPT Export Parser)**: `zeus/ingest/sources/chatgpt.py`
  - **LAB-46 (Markdown File Walker)**: `zeus/ingest/sources/markdown.py`
  - **LAB-47 (Context-Pack Migration)**: `zeus/ingest/sources/context_pack.py`
  - **Ingest runner/CLI plumbing** (supports the above): `zeus/ingest/run.py`, `zeus/ingest/pipeline.py`
  - **LAB-48 (Zeus Context API v1 / Oracle)**: `zeus/api/main.py` (mounted by `zeus/core/main.py`)
  - **LAB-49 (Zeus Query Engine)**: `zeus/core/query.py` (used by chat routes)
- **Partially implemented / needs validation**:
  - **LAB-61 (mem0 Integration & Retrieval Quality)**: mem0 client + retrieval helpers exist (`zeus/memory/config.py`, `zeus/memory/search.py`), but quality eval harness / tuning loop isn’t represented as a dedicated suite yet.
  - **LAB-56 (Privacy & Data Governance / Aegis)**: **in-process Aegis** is present (`zeus/safety/policy_engine.py`, YAML under `zeus/safety/policies/`, optional `ZEUS_AEGIS_ENABLED` / `ZEUS_AEGIS_POLICY` / `NEMOCLAW_POLICY` per `.env.example`). Chat, streaming chat, voice text responses, and `/orchestration/call` outputs can be filtered by policy. **Still open** on this ticket: privacy level tagging, PII scanning across ingest, deduplication strategy, collection versioning—see ticket scope.
- **Not started (no code present yet)**:
  - **LAB-64 (Email Ingest)**: no email source/parser found under `zeus/ingest/sources/`.

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

### LAB-152 — Obsidian frontmatter full YAML support
**File:** `zeus/ingest/sources/obsidian.py`, `_parse_frontmatter()` · **Priority:** Low · **Status:** Deferred

Current parser is a hand-rolled `key: value` line splitter — won't handle lists, quoted strings with colons, multiline values, or nested objects. The misleading "YAML" comment has been fixed to say "simple key:value frontmatter". Only matters if the vault uses complex frontmatter.

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

### LAB-153 — IngestPipeline memory client injection
**File:** `zeus/ingest/pipeline.py`, `run_ingest()` · **Priority:** Medium · **Status:** Deferred (pre-Olympus always-on)

`run_ingest()` calls `get_memory_client()` internally on every scheduled run, creating a fresh mem0/Qdrant client each time instead of reusing `app.state.memory`. Adds connection overhead and complicates clean shutdown.

**Fix:** Add optional `memory` param to `IngestPipeline.__init__` and thread it through to `run_ingest`. In `main.py` lifespan, pass `memory=app.state.memory` when constructing the pipeline. Gate on **Project 6**.


## Project 3 — Voice Loop

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


## Project 4 — MCP Server

**Status (25 Mar 2026):** MCP server implementation is now checked in under `zeus/mcp/` using the MCP Python SDK `FastMCP`. Tool calls proxy to Zeus Core HTTP endpoints. Automated integration tests are not present yet; smoke testing is supported via running the server and calling tools from an MCP client.

| Parent  | Title                   | Labels          | Subs |
| ------- | ----------------------- | --------------- | ---- |
| LAB-104 | MCP Server Core         | Feature, oracle | 4    |
| LAB-107 | MCP Tool Definitions    | Feature, oracle | 5    |
| LAB-108 | MCP Integration Testing | Feature, oracle | 4    |


## Project 5 — Ruflo Agents

**Status (28 Mar 2026):** Ruflo config and agent YAMLs exist (`zeus/orchestration/ruflo.yaml`, `zeus/orchestration/agents/*.yaml`). **`zeus/safety/policies/`** is populated and wired: per-agent `safety.policy` values (`standard`, `ingest`, `voice`, `memory`, etc.) map to YAML files; `/orchestration/call` runs an Aegis post-hook when `ZEUS_AEGIS_ENABLED=1`. **NemoClaw + OpenShell** are **operational on daedalus**: sandbox running, Control UI via SSH tunnel, inference routed OpenShell gateway → **zeus-ollama** (`11435`) → `qwen2.5:7b-instruct`; **`openclaw.json`** `models.providers.inference.api` set to **`openai-completions`** for Ollama (not `openai-responses`). Operational runbook: **`docs/nemoclaw-ops.md`**. **Still open:** custom network policies (Phase 5 YAML) not fully validated end-to-end, context-budget / workspace trimming for 7B, Ruflo spike (**LAB-121**) broader than NemoClaw wiring alone.

| Parent  | Title                          | Labels             | Subs |
| ------- | ------------------------------ | ------------------ | ---- |
| LAB-112 | Ruflo Initialization           | Feature, olympians | 3    |
| LAB-113 | Zeus Personal Agent            | Feature, olympians | 4    |
| LAB-114 | Zeus Dev Agent                 | Feature, olympians | 4    |
| LAB-116 | Zeus Research Agent            | Feature, olympians | 4    |
| LAB-119 | NemoClaw Safety Layer (Aegis)  | Feature, aegis     | 5    |
| LAB-120 | Multi-Agent Orchestration Test | Feature, olympians | 4    |

### LAB-119 — NemoClaw Safety Layer (Aegis)
**Files:** `zeus/safety/policy_engine.py`, `zeus/safety/integration.py`, `zeus/safety/policies/*.yaml` · **`compose.yaml`** (Aegis comment block) · **`.env.example`** (Aegis env vars) · **`zeus/core/query.py`** (chat + stream) · **`zeus/orchestration/bus.py`** (bus post-hook) · **`zeus/core/main.py`** (`orchestration_hooks`)

**Done in repo (Mar 2026):** YAML rule packs; `AegisPolicyEngine`; optional enforcement on Core query paths and orchestration bus responses; policy names aligned with agent YAML + Phase 5e examples (`personal`, `code_execution`, `citation_required`, etc.).

**Done on daedalus (Mar 2026):** NemoClaw + OpenShell installed per [NemoClaw quickstart](https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html); OpenClaw sandbox + Control UI; inference to **zeus-ollama** on host port **11435** with **`openai-completions`** API mode in `openclaw.json`. Commands and troubleshooting: **`docs/nemoclaw-ops.md`**.

**Closed (Mar 2026):** `trustedProxies` / `allowedOrigins` verified; Phase 5 `policy-zeus.yaml` applied and confirmed no 403s to zeus-ollama:11435 or zeus-core:8203 (fill in after daedalus validation); first `nemo-backup` completed (see Phase 6 notes in `nemoclaw-ops.md`); slim workspace templates (`SOUL.md`, `IDENTITY.md`, `AGENTS.md`) added to `zeus/safety/workspace-templates/` — context budget reduced from ~16K to ~350 tokens; agent quality pass completed.

**Still open (optional):** Rename OpenShell provider `ollama-local` → `zeus-ollama` (cosmetic, low priority). `NEMOCLAW_RUNTIME_URL` sidecar integration deferred until NemoClaw ships a stable HTTP API.


## Project 6 — Deploy to Olympus

**Compose / network (dev tower):** `compose.yaml` declares `homelab-web` as an **external** Docker network so Zeus can sit alongside other homelab stacks. On a fresh machine that network must exist (`docker network create homelab-web`) or you need a compose override that replaces it with an internal network for isolated local testing. Tracked in Backlog as **Compose dev ergonomics**.

**Aegis / NemoClaw:** Compose file includes a comment block clarifying that the full NemoClaw + OpenShell stack is **not** a Zeus compose service image; it runs on the host (daedalus). Zeus still applies in-process Aegis when enabled. See **`docs/nemoclaw-ops.md`** for the live install.


| Parent  | Title                           | Labels           | Subs |
| ------- | ------------------------------- | ---------------- | ---- |
| LAB-124 | Docker Compose Production Stack | Feature, oracle  | 4    |
| LAB-128 | Server Deployment               | Feature, oracle  | 4    |
| LAB-140 | Always-On Service Mode          | Feature, oracle  | 4    |
| LAB-141 | Server Voice Pipeline           | Feature, orpheus | 4    |


## Project 7 — Orchestration Runtime


| Parent  | Title                   | Labels             | Subs |
| ------- | ----------------------- | ------------------ | ---- |
| LAB-144 | Agent Runtime Engine    | Feature, olympians | 4    |
| LAB-145 | Agent Communication Bus | Feature, olympians | 4    |
| LAB-146 | Orchestration Hooks     | Feature, olympians | 4    |


## Project 8 — Observability + Admin

**Status (27 Mar 2026):** Sprint 9/10 PR merged. Middleware ring-buffer wiring, consolidate empty-payload guard, and pipeline incremental no-op log are fixed. Two security hardening tickets (LAB-150, LAB-151) deferred until Olympus deployment — VPN boundary covers them during dev.

| Parent  | Title                          | Labels                | Subs |
| ------- | ------------------------------ | --------------------- | ---- |
| LAB-147 | Metrics Collection             | Feature, oracle       | 4    |
| LAB-148 | Admin API Routes               | Feature, oracle       | 4    |
| LAB-149 | Admin Dashboard                | Feature, oracle       | 4    |
| LAB-150 | Admin endpoint auth hardening  | Feature, aegis        | 3    |
| LAB-151 | Admin dashboard XSS hardening  | Feature, aegis        | 2    |

### LAB-150 — Admin endpoint auth hardening
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

### LAB-151 — Admin dashboard XSS hardening
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
Do alongside LAB-150 — both are the same admin surface hardening pass.


## Project 9 — React Frontend + Integrations

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

### LAB-286 — React App Scaffold
**Files:** `zeus/frontend/` (new) · **Priority:** High · **Blocks:** LAB-287, LAB-288, LAB-290, LAB-293

Vite 5 + React 19 + TypeScript project with React Router v6 routes (`/`, `/agents`, `/settings`, `/viz`), Tailwind CSS v3 theme tokens mirroring existing Zeus CSS vars, Zustand stores (`chatStore`, `voiceStore`, `settingsStore`), Vite dev proxy to FastAPI :8000, and `App.tsx` shell with header nav + theme toggle.

**Sub-issues:** LAB-294 (project init), LAB-295 (router + stubs), LAB-296 (Tailwind theme), LAB-297 (Zustand stores), LAB-298 (App shell + proxy)

### LAB-287 — React Chat + Sessions View
**Files:** `zeus/frontend/src/pages/ChatPage.tsx`, `src/components/chat/` · **Priority:** High · **Blocks:** LAB-290

Port `chat.html` to React components: `SessionsSidebar` (GET /chat/sessions), `MessageList` + `ChatBubble`, `MarkdownMessage` (port `chat-markdown.js` via react-markdown), `ChatInput` (Enter/Shift+Enter), `useStreamingChat` SSE hook (POST /chat/stream).

**Sub-issues:** LAB-299 (SessionsSidebar), LAB-300 (MessageList + ChatBubble), LAB-301 (MarkdownMessage), LAB-302 (ChatInput), LAB-303 (StreamingChat SSE hook)

### LAB-288 — Phaos Orb React Component
**Files:** `zeus/frontend/src/components/orb/PhaosOrb.tsx`, `src/hooks/useVoiceState.ts` · **Priority:** High

Port `orb.js` Three.js orb to `@react-three/fiber` `<Canvas>` preserving GLSL shaders verbatim. `useVoiceState` hook subscribes to `WS /ws/voice-state` → Zustand `voiceStore`. Compact sidebar panel mode on `/` + fullscreen `/viz` route (replaces `viz/viz.html`).

**Sub-issues:** LAB-304 (R3F Canvas + GLSL), LAB-305 (useVoiceState hook), LAB-306 (uniforms + state machine), LAB-307 (responsive + /viz route)

### LAB-289 — Agent Orchestration Panel
**Files:** `zeus/frontend/src/pages/AgentsPage.tsx`, `src/components/agents/` · **Priority:** Normal · **Blocks:** LAB-290 (FastAPI SPA)

`/agents` page: `AgentCard` (name, model, aegis policy badge, status) from `GET /admin/agents`; `AgentInvokePanel` (task input → `POST /orchestration/call`, SSE stream); `ToolCallFeed` (collapsible per-tool log); `AegisPolicyBadge` colour-coded per policy.

**Sub-issues:** LAB-308 (AgentCard + list), LAB-309 (AgentInvokePanel), LAB-310 (ToolCallFeed + AegisPolicyBadge)

### LAB-290 — FastAPI SPA Serve
**Files:** `zeus/core/main.py`, `zeus/core/chat.py`, `vite.config.ts`, `zeus/docs/deployment.md` · **Priority:** High · **Blocks:** LAB-289

Vite `outDir → zeus/core/static/app/`. `main.py`: mount `/assets`, add SPA catch-all `GET /{path:path}` returning `index.html` (registered last). `chat.py`: remove `GET /chat` HTML route, keep all API routes, add redirects for `/chat` → `/` and `/viz` → `/#/viz`.

**Sub-issues:** LAB-311 (Vite outDir + asset mount), LAB-312 (SPA catch-all), LAB-313 (API preservation + redirects), LAB-314 (deployment docs)

### LAB-291 — Telegram Bot Backend
**Files:** `zeus/integrations/telegram/` (new), `zeus/core/main.py` (lifespan), `.env.example` · **Priority:** Normal · **Blocks:** LAB-292

`python-telegram-bot` async bot in `zeus/integrations/telegram/bot.py`. Each Telegram `chat_id` → persistent Zeus session keyed `telegram:{chat_id}` with `metadata.source = "telegram"`. Allowed-list guard (`TELEGRAM_ALLOWED_CHAT_IDS`). All outgoing responses pass through `AegisPolicyEngine`. Bot starts/stops in FastAPI lifespan. New endpoint: `GET /integrations/telegram/status`.

**Env vars:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS`, `TELEGRAM_ENABLED`

**Sub-issues:** LAB-315 (module scaffold), LAB-316 (bot.py + allowed-list), LAB-317 (session mapping), LAB-318 (lifespan + env vars), LAB-319 (Aegis safety hook)

### LAB-292 — Telegram Frontend Integration
**Files:** `zeus/frontend/src/components/SourceBadge.tsx`, `src/components/TelegramStatus.tsx` · **Priority:** Normal

`SourceBadge` on messages + session entries (telegram/web/voice icons). `TelegramStatus` dot in App header (polls `/integrations/telegram/status` every 30s). Settings page Telegram section (token, chat IDs, enable toggle, test button).

**Sub-issues:** LAB-320 (SourceBadge), LAB-321 (TelegramStatus + endpoint), LAB-322 (Settings Telegram section)

### LAB-293 — React Settings Page
**Files:** `zeus/frontend/src/pages/SettingsPage.tsx` · **Priority:** Normal

`/settings` two-column layout (nav sidebar + content pane). Sections: Model (dev/prod toggle), Aegis (policy selector from `GET /safety/policies`), Telegram (see LAB-292), Sessions (auto-summarize, window size), Appearance (theme, orb size). New `PATCH /settings` FastAPI endpoint for runtime state overrides; UI prefs to `localStorage`.

**Sub-issues:** LAB-323 (layout + scaffold), LAB-324 (Model + Aegis sections), LAB-325 (Sessions prefs + PATCH /settings)

---

## Backlog


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


**Note:** Some Project 7/8 sub-issues and all Backlog items may hit the Linear workspace issue limit. Archive completed issues before creating new ones.

---

## Key Dependencies

- **LAB-48 (Context API)** blocks Projects 3, 4, 5, 6, 7, 8
- **LAB-184 (Session Layer)** blocks chat interface + voice pipeline
- **LAB-49 (Query Engine)** blocks voice pipeline + agents
- **LAB-121 (Ruflo Spike)** blocks Project 5 architecture
- **LAB-286 (React Scaffold)** blocks LAB-287, LAB-288, LAB-290, LAB-293
- **LAB-290 (FastAPI SPA Serve)** blocks LAB-289 (Agent Panel)
- **LAB-291 (Telegram Backend)** blocks LAB-292 (Telegram Frontend)

