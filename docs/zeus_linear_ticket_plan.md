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

**Status (28 Mar 2026):** Ruflo config and agent YAMLs exist (`zeus/orchestration/ruflo.yaml`, `zeus/orchestration/agents/*.yaml`). **`zeus/safety/policies/`** is populated and wired: per-agent `safety.policy` values (`standard`, `ingest`, `voice`, `memory`, etc.) map to YAML files; `/orchestration/call` runs an Aegis post-hook when `ZEUS_AEGIS_ENABLED=1`. **LAB-119** is **partially done** in-repo (policy engine + integration); **host install** of NVIDIA NemoClaw + OpenShell (OpenClaw sandboxes) remains a separate step—documented in `compose.yaml` and `.env.example`, not as a Zeus compose service. Full Ruflo spike validation (LAB-121) is still broader than policy files alone.

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

**Still out of repo / manual:** NVIDIA NemoClaw installer, OpenShell on host, OpenClaw inside sandboxes per [NemoClaw quickstart](https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html). Optional future: `NEMOCLAW_RUNTIME_URL` if a stable HTTP sidecar appears.


## Project 6 — Deploy to Olympus

**Compose / network (dev tower):** `compose.yaml` declares `homelab-web` as an **external** Docker network so Zeus can sit alongside other homelab stacks. On a fresh machine that network must exist (`docker network create homelab-web`) or you need a compose override that replaces it with an internal network for isolated local testing. Tracked in Backlog as **Compose dev ergonomics**.

**Aegis / NemoClaw:** Compose file includes a comment block clarifying that the full NemoClaw + OpenShell stack is **not** a Zeus service image—host or separate homelab stack—while Zeus applies in-process policies when enabled.


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


## Backlog


| Title                                        | Labels             |
| -------------------------------------------- | ------------------ |
| Orpheus voice LLM env parity (Claude vs Ollama) | Feature, orpheus |
| Compose dev ergonomics: `homelab-web` vs internal network | Feature, oracle |
| VR Prototype — Zeus voice + avatar in Oculus | Feature, orpheus   |
| Meta AR Glasses Integration                  | Feature, orpheus   |
| Watch Vitals Integration                     | Feature, iris      |
| Web Dashboard                                | Feature, oracle    |
| Business Productization                      | Feature            |
| Model Fine-Tuning                            | Feature, mnemosyne |
| Graph Memory (mem0g)                         | Feature, mnemosyne |
| Memory Decay Policy                          | Feature, mnemosyne |


**Note:** Some Project 7/8 sub-issues and all Backlog items hit the Linear workspace issue limit. These need to be created after upgrading or archiving old issues.

---

## Key Dependencies

- **LAB-48 (Context API)** blocks Projects 3, 4, 5, 6, 7, 8
- **LAB-184 (Session Layer)** blocks chat interface + voice pipeline
- **LAB-49 (Query Engine)** blocks voice pipeline + agents
- **LAB-121 (Ruflo Spike)** blocks Project 5 architecture

