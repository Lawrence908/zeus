# Zeus — Linear Ticket Plan

Full ticket structure for the Zeus project, organized into sprint-based Linear Projects with parent issues and sub-tasks per feature area.

**Team:** Chris Lawrence Homelab
**Project:** Zeus
**Labels:** mnemosyne, iris, orpheus, aegis, oracle, olympians (+ existing Feature/Bug/Improvement)

---

## Project 0 — Foundation

> Repo init, infrastructure services up, basic tooling verified.
> **Status:** Mostly complete — track for closure.

### ZEUS-F01: Repository & Dev Environment Setup [Feature] [oracle]
- ZEUS-F01a: Init zeus repo with CLAUDE.md, README, .gitignore, requirements.txt
- ZEUS-F01b: Create docker-compose scaffold (Qdrant, Ollama, Zeus Core)
- ZEUS-F01c: Set up FastAPI core bus with /status health check (core/main.py)
- ZEUS-F01d: Implement ZEUS_ENV environment switching (dev/prod)

### ZEUS-F02: Qdrant & Ollama Infrastructure [Feature] [mnemosyne]
- ZEUS-F02a: Deploy Qdrant via Docker, verify admin UI at localhost:6333
- ZEUS-F02b: Pull nomic-embed-text + qwen2.5:7b models via Ollama on tower
- ZEUS-F02c: Test basic embedding generation via Ollama API

### ZEUS-F03: mem0 Initial Setup [Feature] [mnemosyne]
- ZEUS-F03a: Install mem0ai, configure with Ollama backend (memory/config.py)
- ZEUS-F03b: Test basic add/search operations against local Qdrant
- ZEUS-F03c: Implement dev/prod config switching (Claude API vs Ollama)

### ZEUS-F04: Voice Tooling Validation [Feature] [orpheus]
- ZEUS-F04a: Install Voicebox on tower, select LuxTTS engine
- ZEUS-F04b: Record reference audio samples for Zeus voice
- ZEUS-F04c: Verify TTS output quality and latency

### ZEUS-F05: ChatGPT Data Export [Feature] [iris]
- ZEUS-F05a: Export ChatGPT data via Settings → Data Controls
- ZEUS-F05b: Validate conversations.json structure and size

---

## Project 1 — Data Brain (Iris + Mnemosyne)

> Build the ingest pipeline and knowledge base. Zeus can answer questions about your data.

### ZEUS-D01: ChatGPT Export Parser [Feature] [iris]
- ZEUS-D01a: Build conversations.json parser (ingest/sources/chatgpt.py)
- ZEUS-D01b: Implement user-message-only filtering with curated assistant inclusion
- ZEUS-D01c: Add date-based temporal tagging and topic auto-categorization
- ZEUS-D01d: Wire into ingest pipeline (chunk → embed → Qdrant)
- ZEUS-D01e: Test with real ChatGPT export, verify chunk quality

### ZEUS-D02: Markdown File Walker [Feature] [iris]
- ZEUS-D02a: Build recursive .md walker (ingest/sources/markdown.py)
- ZEUS-D02b: Implement YAML frontmatter extraction (title, tags, date)
- ZEUS-D02c: Add heading-aware chunking (split at heading boundaries)
- ZEUS-D02d: Respect .gitignore patterns for exclusion
- ZEUS-D02e: Test against server context directories

### ZEUS-D03: Context-Pack Migration [Feature] [iris]
- ZEUS-D03a: Build context_pack.py source parser (ingest/sources/context_pack.py)
- ZEUS-D03b: Pull all existing context-pack entries via API
- ZEUS-D03c: Re-chunk and re-embed with standardized Zeus chunking
- ZEUS-D03d: Verify backward-compatible query interface

### ZEUS-D04: Zeus Context API v1 (Oracle) [Feature] [oracle]
- ZEUS-D04a: Implement POST /context/query endpoint with semantic search
- ZEUS-D04b: Implement POST /memory/add and /memory/search endpoints
- ZEUS-D04c: Implement POST /ingest/trigger endpoint
- ZEUS-D04d: Implement GET /status with index stats
- ZEUS-D04e: Add /context-pack/query backward-compat endpoint
- ZEUS-D04f: Implement /context/profile endpoint for structured personal context

### ZEUS-D05: mem0 Integration & Retrieval Quality [Feature] [mnemosyne]
- ZEUS-D05a: Connect mem0 to Qdrant with namespace separation
- ZEUS-D05b: Implement memory search with token budgeting (memory/search.py)
- ZEUS-D05c: Build context block formatting for LLM consumption
- ZEUS-D05d: Test retrieval quality — run benchmark queries against personal data
- ZEUS-D05e: Tune chunk size / overlap / embedding params for relevance

### ZEUS-D06: Privacy & Data Governance [Feature] [aegis]
- ZEUS-D06a: Implement privacy level tagging (public/personal/sensitive/private)
- ZEUS-D06b: Build PII scanner for stripping secrets from .md files before ingest
- ZEUS-D06c: Add hash-based deduplication to ingest pipeline
- ZEUS-D06d: Test privacy filtering end-to-end

---

## Project 2 — Voice Loop (Orpheus)

> Wake word → STT → Zeus Core → TTS → speaker. Full voice conversation.

### ZEUS-V01: WhisperLiveKit STT Setup [Feature] [orpheus]
- ZEUS-V01a: Install WhisperLiveKit on tower, configure faster-whisper GPU backend
- ZEUS-V01b: Build STT WebSocket client (voice/stt.py)
- ZEUS-V01c: Test real-time transcription from microphone, measure latency
- ZEUS-V01d: Configure VAD thresholds for conversational use

### ZEUS-V02: openWakeWord Integration [Feature] [orpheus]
- ZEUS-V02a: Install openWakeWord, select/train wake word ("Hey Zeus")
- ZEUS-V02b: Build wake word listener loop (voice/wake.py)
- ZEUS-V02c: Wire wake word detection → WhisperLiveKit activation trigger
- ZEUS-V02d: Test false positive/negative rates in real environment

### ZEUS-V03: Voicebox TTS Client [Feature] [orpheus]
- ZEUS-V03a: Build Voicebox REST API client (voice/tts.py)
- ZEUS-V03b: Implement audio playback via sounddevice
- ZEUS-V03c: Configure LuxTTS voice cloning with reference audio
- ZEUS-V03d: Test TTS latency and audio quality at conversational speed

### ZEUS-V04: Zeus Core v1 — Query Engine [Feature] [oracle]
- ZEUS-V04a: Build main query handler: text in → mem0+Qdrant search → LLM → response
- ZEUS-V04b: Implement system prompt with personal context injection
- ZEUS-V04c: Add LLM provider switching (Claude API dev / Ollama prod)
- ZEUS-V04d: Test response quality with various query types

### ZEUS-V05: Voice Pipeline End-to-End [Feature] [orpheus]
- ZEUS-V05a: Build voice orchestration loop (voice/pipeline.py)
- ZEUS-V05b: Wire: wake word → STT → Zeus Core → TTS → speaker
- ZEUS-V05c: Add interrupt handling (stop TTS when user starts speaking)
- ZEUS-V05d: Full voice conversation test session — document pain points
- ZEUS-V05e: Measure end-to-end latency (wake → response audio starts)

---

## Project 3 — Ruflo Agents (Olympians)

> Multi-agent orchestration with safety guardrails.

### ZEUS-A01: Ruflo Initialization [Feature] [olympians]
- ZEUS-A01a: Run ruflo init in zeus repo, configure CLAUDE.md for Zeus agents
- ZEUS-A01b: Verify Ruflo v3.5 swarm memory (SQLite .swarm/memory.db)
- ZEUS-A01c: Test basic single-agent execution through Ruflo

### ZEUS-A02: Zeus Personal Agent [Feature] [olympians]
- ZEUS-A02a: Define agent YAML (orchestration/agents/personal.yaml)
- ZEUS-A02b: Build system prompt with personal context + RAG access
- ZEUS-A02c: Wire agent to Oracle context API for memory retrieval
- ZEUS-A02d: Test conversational personal assistant queries

### ZEUS-A03: Zeus Dev Agent [Feature] [olympians]
- ZEUS-A03a: Define agent YAML (orchestration/agents/dev.yaml)
- ZEUS-A03b: Build system prompt with project context from vector DB
- ZEUS-A03c: Configure code-aware tools and file access
- ZEUS-A03d: Test with real development assistance tasks

### ZEUS-A04: Zeus Research Agent [Feature] [olympians]
- ZEUS-A04a: Define agent YAML (orchestration/agents/research.yaml)
- ZEUS-A04b: Configure web search + summarization tools
- ZEUS-A04c: Implement memory write-back (research findings → mem0)
- ZEUS-A04d: Test research workflow with follow-up recall

### ZEUS-A05: NemoClaw Safety Layer (Aegis) [Feature] [aegis]
- ZEUS-A05a: Install NemoClaw + OpenShell runtime
- ZEUS-A05b: Define safety policies — what agents can/cannot do autonomously
- ZEUS-A05c: Configure privacy router for outbound data monitoring
- ZEUS-A05d: Wire Aegis policies into Ruflo agent definitions
- ZEUS-A05e: Test policy enforcement — verify blocked actions are caught

### ZEUS-A06: Multi-Agent Orchestration Test [Feature] [olympians]
- ZEUS-A06a: Design complex task requiring 2+ agents simultaneously
- ZEUS-A06b: Test parallel agent execution through Ruflo swarm
- ZEUS-A06c: Verify inter-agent communication via FastAPI bus
- ZEUS-A06d: Document agent coordination patterns and failure modes

---

## Project 4 — Deploy to Olympus

> Ship to the 3080 production server. Always-on Zeus.

### ZEUS-S01: Docker Compose Production Stack [Feature] [oracle]
- ZEUS-S01a: Finalize docker-compose.yml — Qdrant, mem0, Zeus Core, Voicebox, Ollama
- ZEUS-S01b: Add healthchecks, restart policies, resource limits for 10GB VRAM
- ZEUS-S01c: Create .env.prod with all production configuration
- ZEUS-S01d: Test full stack startup/shutdown on tower before server deploy

### ZEUS-S02: Server Deployment [Feature] [oracle]
- ZEUS-S02a: Deploy Zeus stack to 3080 server (Olympus)
- ZEUS-S02b: Pull Qwen2.5-7B Q4_K_M on server, benchmark latency vs tower
- ZEUS-S02c: Verify all services running stable under production load
- ZEUS-S02d: Test memory/ingest operations on server hardware

### ZEUS-S03: Always-On Service Mode [Feature] [oracle]
- ZEUS-S03a: Create systemd service for Zeus stack
- ZEUS-S03b: Configure wake-on-keyword + sleep-otherwise behavior
- ZEUS-S03c: Add auto-restart on crash with backoff
- ZEUS-S03d: Test 24h+ uptime stability

### ZEUS-S04: Server Voice Pipeline [Feature] [orpheus]
- ZEUS-S04a: Move WhisperLiveKit to server
- ZEUS-S04b: Test STT latency over LAN (mic on tower/laptop → server)
- ZEUS-S04c: Optimize audio streaming for network conditions
- ZEUS-S04d: Verify full voice loop works with server-side processing

### ZEUS-S05: Phase 2 Ingestion — Email [Feature] [iris]
- ZEUS-S05a: Build IMAP email parser (ingest/sources/email.py)
- ZEUS-S05b: Implement privacy-filtered ingestion (scope: starred/sent only vs all)
- ZEUS-S05c: Add email-specific metadata tagging (sender, subject, thread)
- ZEUS-S05d: Test ingestion and retrieval of email content

---

## Project 5 — Sessions & Chat

> Multi-turn continuity and text-based chat interface.

### ZEUS-C01: Session Layer [Feature] [oracle]
- ZEUS-C01a: Design session data model (session ID, turns, timestamps, summary)
- ZEUS-C01b: Implement core/sessions.py — session create, append, retrieve
- ZEUS-C01c: Add rolling summary generation (compress old turns)
- ZEUS-C01d: Wire sessions into Zeus Core query handler
- ZEUS-C01e: Test multi-turn continuity across chat and voice paths

### ZEUS-C02: Text Chat Interface [Feature] [oracle]
- ZEUS-C02a: Build core/chat.py — FastAPI routes for text chat
- ZEUS-C02b: Create minimal static chat UI (core/static/)
- ZEUS-C02c: Implement WebSocket for streaming responses
- ZEUS-C02d: Wire chat into session layer for multi-turn support
- ZEUS-C02e: Test as dev fallback when voice isn't available

---

## Project 6 — Orchestration Runtime

> Make agent YAMLs executable — the bridge between config and action.

### ZEUS-O01: Agent Runtime Engine [Feature] [olympians]
- ZEUS-O01a: Build orchestration/runtime.py — load and execute agent YAMLs
- ZEUS-O01b: Implement tool registration and dispatch
- ZEUS-O01c: Add agent lifecycle management (start, monitor, terminate)
- ZEUS-O01d: Test single-agent execution from YAML → completion

### ZEUS-O02: Agent Communication Bus [Feature] [olympians]
- ZEUS-O02a: Build orchestration/bus.py — inter-agent message passing via FastAPI
- ZEUS-O02b: Implement request/response and pub/sub patterns
- ZEUS-O02c: Add message logging and traceability
- ZEUS-O02d: Test multi-agent coordination through the bus

### ZEUS-O03: Orchestration Hooks [Feature] [olympians]
- ZEUS-O03a: Build orchestration/hooks.py — event-driven agent triggers
- ZEUS-O03b: Implement Ruflo hooks integration (auto-route tasks to agents)
- ZEUS-O03c: Add webhook support for external triggers
- ZEUS-O03d: Test event → agent activation flow

---

## Project 7 — MCP Server

> Expose Zeus tools via Model Context Protocol for external clients.

### ZEUS-M01: MCP Server Core [Feature] [oracle]
- ZEUS-M01a: Build mcp/server.py — MCP protocol implementation
- ZEUS-M01b: Define tool schemas for context query, memory search, profile lookup
- ZEUS-M01c: Register tools with MCP registry
- ZEUS-M01d: Test with Claude Desktop as MCP client

### ZEUS-M02: MCP Tool Definitions [Feature] [oracle]
- ZEUS-M02a: Implement zeus_context_query tool (semantic search)
- ZEUS-M02b: Implement zeus_memory_search tool (personal memories)
- ZEUS-M02c: Implement zeus_profile tool (structured personal context)
- ZEUS-M02d: Implement zeus_ingest_trigger tool (re-ingest a source)
- ZEUS-M02e: Add tool documentation and usage examples

### ZEUS-M03: MCP Integration Testing [Feature] [oracle]
- ZEUS-M03a: Test MCP tools from Claude Desktop / Cursor
- ZEUS-M03b: Verify auth and access control for MCP connections
- ZEUS-M03c: Load test — concurrent MCP requests
- ZEUS-M03d: Document MCP setup for external clients

---

## Project 8 — Observability & Admin

> Monitoring, metrics, and operational dashboards.

### ZEUS-X01: Metrics Collection [Feature] [oracle]
- ZEUS-X01a: Add query latency tracking to all API endpoints
- ZEUS-X01b: Track ingest pipeline metrics (chunks processed, errors, duration)
- ZEUS-X01c: Monitor Qdrant collection stats (vector count, memory usage)
- ZEUS-X01d: Track mem0 operation metrics (add/search latency, hit rates)

### ZEUS-X02: Admin API Routes [Feature] [oracle]
- ZEUS-X02a: Build /admin/metrics endpoint — JSON metrics export
- ZEUS-X02b: Build /admin/services endpoint — service health dashboard data
- ZEUS-X02c: Build /admin/ingest endpoint — ingest history and status
- ZEUS-X02d: Build /admin/memory endpoint — memory stats and recent operations

### ZEUS-X03: Admin Dashboard [Feature] [oracle]
- ZEUS-X03a: Build lightweight admin UI (static HTML or React)
- ZEUS-X03b: Display service health, memory stats, recent queries
- ZEUS-X03c: Add ingest pipeline status and trigger controls
- ZEUS-X03d: Show active agents and orchestration status

---

## Backlog — Future Phases

> Tracked but unscheduled. Plan in detail when closer.

### ZEUS-B01: VR Prototype [Feature] [orpheus]
- Coordinate with Brad — Zeus voice + avatar in Oculus environment

### ZEUS-B02: Meta AR Glasses Integration [Feature] [orpheus]
- Research OpenClaw API compatibility with Meta glasses
- Voice assistant in AR with visual avatar

### ZEUS-B03: Watch Vitals Integration [Feature] [iris]
- Health data integration — API TBD based on wearable hardware

### ZEUS-B04: Web Dashboard [Feature] [oracle]
- React UI — Zeus status, memory browser, conversation history, agent activity

### ZEUS-B05: Business Productization [Feature]
- Package Zeus as installable personal data center
- Professional services pilot (accounting firm, 10-20k per install)

### ZEUS-B06: Model Fine-Tuning [Feature] [mnemosyne]
- Fine-tune local model on personal data once conversation history is sufficient
- NemoClaw supports Nemotron fine-tuning path

### ZEUS-B07: Graph Memory (mem0g) [Feature] [mnemosyne]
- Enable graph memory variant once base mem0 is stable
- Relational memory for people, projects, tools, skills

### ZEUS-B08: Memory Decay Policy [Feature] [mnemosyne]
- Define decay rates for episodic vs semantic memories
- Implement automatic weight reduction for stale memories

---

## Summary

| Project | Parent Issues | Sub-Issues | Focus |
|---------|--------------|------------|-------|
| 0 — Foundation | 5 | 16 | Repo, infra, tooling |
| 1 — Data Brain | 6 | 26 | Ingest, memory, retrieval |
| 2 — Voice Loop | 5 | 20 | STT, TTS, wake word, pipeline |
| 3 — Ruflo Agents | 6 | 22 | Agents, safety, orchestration |
| 4 — Deploy to Olympus | 5 | 17 | Docker, server, always-on |
| 5 — Sessions & Chat | 2 | 10 | Multi-turn, text UI |
| 6 — Orchestration Runtime | 3 | 12 | Runtime, bus, hooks |
| 7 — MCP Server | 3 | 12 | MCP tools, integration |
| 8 — Observability | 3 | 12 | Metrics, admin, dashboard |
| Backlog | 8 | — | Future phases |
| **Total** | **46** | **147** | |
