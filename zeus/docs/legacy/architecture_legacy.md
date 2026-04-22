> **Legacy (March 2026).** Preserved for decision history only. Superseded by [zeus/docs/architecture.md](../architecture.md) and [CLAUDE.md](../../../CLAUDE.md). References to mem0, `context-pack`, and the original Sprint 0–4 plan do not reflect current code.

⚡
ZEUS
Personal AI Assistant, Architecture & Stack

Zeus is a self-hosted personal AI assistant/agent system. It connects fragmented personal data stores, runs local models for privacy, and provides a voice-first interface. Built on proven open-source repos, composed into a unified stack.

1. Confirmed Stack Decisions

Layer	Technology	Reason
Orchestration	Ruflo v3.5 (Claude Code)	Stable, swarm agents, 60+ specialized agents, native MCP
Safety / Sandbox	NemoClaw + OpenShell	Policy-based guardrails, sandboxed execution for local agents
STT (voice in)	WhisperLiveKit	SOTA 2025 real-time, SimulStreaming backend, AlignAtt low latency
TTS (voice out)	Voicebox API → LuxTTS	150x RT, 1GB VRAM, voice cloning, REST API from Voicebox studio
Memory Layer	mem0 (self-hosted)	Hybrid vector+graph+KV, 91% lower latency vs full-context
Vector DB	Qdrant	Self-hosted, Docker, fast semantic search
Local Inference (dev)	Ollama + Claude API	5080 tower during dev/testing
Local Inference (prod)	Ollama on 3080 server	Qwen2.5-7B or Mistral-7B Q4/Q5, 10GB VRAM fit
Data Ingestion	Zeus Ingest Pipeline	Custom: .md files, ChatGPT export, context-pack API
API Bus	FastAPI	Routes between all services, exposes context-pack compatible API
Wake Word / VAD	openWakeWord	Fully open, passive trigger before WhisperLiveKit activates

2. Architecture Overview
Zeus is structured as layered services communicating over a FastAPI bus. Each layer is independently deployable and replaceable.

⚡ INTERFACE	Voice (Mic) → openWakeWord → WhisperLiveKit STT Voicebox TTS (LuxTTS) → Speaker  |  Web UI (optional)

🧠 ZEUS CORE	FastAPI Bus  ←→  Ruflo Orchestration  ←→  NemoClaw / OpenShell

🗄️ MEMORY	mem0 (hybrid: vector + graph + KV)  ←→  Qdrant Vector DB

📥 DATA INGESTION	Zeus Ingest Pipeline: ChatGPT export | .md files | context-pack API | email | notes

🤖 MODELS	Dev: Claude API via 5080 tower  |  Prod: Ollama (3080 server, Qwen2.5-7B Q4)

🛡️ SAFETY	NemoClaw OpenShell, sandboxed execution, privacy router, policy guardrails


3. Component Breakdown
3.1 Orchestration, Ruflo
Ruflo (formerly Claude-Flow) is the task orchestration brain for Zeus. It runs as a Claude Code-native layer coordinating specialized agents in parallel swarms.
•	Version: v3.5.0 (first stable release, March 2026)
•	60+ specialized agents across 16 categories, each scoped to a role
•	Hooks system auto-routes tasks to the right agents in background
•	215 MCP tools available; lazy-loaded so startup stays fast
•	SQLite-backed swarm memory at .swarm/memory.db
•	Dual-mode: Claude Code (primary) + OpenAI Codex (secondary) worker support

3.2 Safety Layer, NemoClaw + OpenShell
NemoClaw is NOT an alternative to Ruflo, it is the security sandbox layer beneath it. Released at GTC 2026, it wraps OpenClaw agents with policy-based guardrails, sandboxed execution, and a privacy router.
KEY INSIGHT	Ruflo handles orchestration (what agents do). NemoClaw handles containment (what agents are allowed to do and touch).

•	OpenShell: kernel-level sandboxing + policy enforcement runtime
•	Privacy Router: monitors outbound data, blocks unauthorized transmissions
•	Policy-based guardrails: PII detection, topic control, jailbreak prevention
•	Supports mixing local Nemotron models + cloud frontier models via privacy router
•	Single-command install: layered over OpenClaw/OpenShell runtime
For Zeus, NemoClaw is especially valuable because you are feeding personal data (emails, ChatGPT history, .md files). Having a sandboxed runtime means local agents cannot accidentally exfiltrate sensitive data.

3.3 Voice Pipeline
STT: WhisperLiveKit
Real-time speech-to-text optimized for conversational use. Uses SimulStreaming (SOTA 2025) with AlignAtt policy for ultra-low latency.
•	Auto-selects best backend: faster-whisper (GPU), mlx-whisper (Apple Silicon), or vanilla Whisper
•	Voice Activity Detection built-in, reduces overhead when silent
•	Speaker diarization available via Diart integration
•	Works on the 3080 server (10GB VRAM) without issue

TTS: Voicebox → LuxTTS Engine
Voicebox is the local TTS service (REST API). LuxTTS is the selected engine inside it, chosen for voice cloning to build a consistent "Zeus voice".
•	Voicebox exposes REST API, Zeus calls it like any microservice
•	LuxTTS: 150x realtime on GPU, 1GB VRAM, 48kHz audio output
•	Voice cloning from reference audio: record a few seconds → consistent voice
•	Voicebox supports 5 engines, can switch per-generation if needed
•	"Compose the voice from unhinged Australians", feed reference clips to LuxTTS encode_prompt

Wake Word: openWakeWord
Passive listener that activates WhisperLiveKit on trigger. Fully open-source, runs on CPU, negligible resource cost.

3.4 Memory, mem0 + Qdrant
mem0 is the memory orchestration layer. It sits between Zeus agents and the underlying storage systems, managing the full memory lifecycle.
WHY MEM0 OVER RAG ALONE	RAG retrieves from static knowledge bases. mem0 stores evolving user-specific facts. Zeus needs both: RAG for document knowledge, mem0 for personal context that grows with every interaction.

•	Hybrid storage: vector DB (semantic search) + graph DB (relationships) + KV store (fast facts)
•	91% lower latency vs full-context approaches, 90% token savings
•	Auto-extracts key facts from conversations and stores them
•	Supports Ollama local models, critical for offline operation on the server
•	Works with Claude API during cloud dev phase
•	Qdrant as the vector DB backend: self-hosted Docker, production-grade

3.5 Data Ingestion, Zeus Ingest Pipeline
A custom pipeline to ingest all fragmented personal data stores into the Zeus knowledge base. This is one of the most important components, the quality of Zeus intelligence depends on it.
Data Sources (Phase 1)
•	ChatGPT export (JSON), years of conversation history
•	.md files from server context stores, existing knowledge packs
•	context-pack API, existing API interface, will be extended
•	Dev project READMEs, notes, and docs from various repos
Data Sources (Phase 2)
•	Email (IMAP), processed via privacy-filtered ingestion
•	Watch vitals (if wearable integration added)
•	Browser history (optional, opt-in)
Pipeline Architecture
•	Ingest → Chunk → Embed → Store in Qdrant + mem0
•	Deduplication: hash-based to avoid re-processing unchanged files
•	Metadata tagging: source, date, topic category
•	Zeus Context API: FastAPI endpoint that exposes the knowledge base (successor to context-pack)

3.6 Model Strategy
Development Phase (Now)
•	Primary: Claude API (Sonnet 4.6) called via Ruflo from 5080 tower
•	Memory: mem0 with Claude as the extraction LLM
•	Advantage: best quality during initial build and RAG pipeline tuning
Production Phase (Server)
•	Primary: Ollama serving Qwen2.5-7B-Instruct Q4_K_M on 3080 (10GB VRAM)
•	Alternative: Mistral-7B Q5_K_M if more factual accuracy needed
•	Fallback: Claude API for complex tasks via privacy router (NemoClaw)
•	Embed: nomic-embed-text or bge-m3, both run easily on 3080

4. Hardware Map
Machine	Role	Key Specs
Tower PC	Dev & test, larger models, Claude API	RTX 5080 (16GB), 14B models comfortable
Server	Production deployment, always-on Zeus	RTX 3080 (10GB), 7B models Q4/Q5
Laptop	Claude Code development, Ruflo orchestration	Dev environment, no local model inference

5. Zeus Repo Structure (github.com/[you]/zeus)
Recommended initial structure for the zeus repo:

Path	Purpose
zeus/	Root, CLAUDE.md, README, docker-compose.yml
zeus/core/	FastAPI bus, main entry point, routing logic
zeus/orchestration/	Ruflo config, CLAUDE.md, agent definitions
zeus/memory/	mem0 setup, Qdrant config, embedding utilities
zeus/ingest/	Data ingestion pipeline, all source parsers
zeus/ingest/sources/	chatgpt.py, markdown.py, email.py, context_pack.py
zeus/voice/	STT (WhisperLiveKit), TTS (Voicebox client), VAD
zeus/safety/	NemoClaw / OpenShell config and policies
zeus/api/	Zeus Context API, successor to context-pack
zeus/models/	Ollama model configs, prompt templates
zeus/data/	Raw exports (gitignored), processed chunks
zeus/docs/	Architecture docs (these files)

6. Open Decisions & Next Steps
Decisions Still to Make
•	VR/AR interface: Brad consultation on feasibility, Oculus + avatar + Zeus voice is the vision
•	Email integration: IMAP parser for ingestion, privacy-first, local only
•	Watch vitals: API integration for health data feed into Zeus context
•	NemoClaw policy definitions: what is Zeus allowed to do autonomously vs require approval
•	UI: headless voice-only to start, lightweight web dashboard later
Immediate Next Steps
•	Initialize zeus repo, set up CLAUDE.md for Ruflo
•	Get Qdrant running in Docker on server
•	Build ChatGPT export parser (ingest/sources/chatgpt.py)
•	.md file walker for existing context stores on server
•	Get Voicebox + LuxTTS running on tower, pick a voice
•	Wire WhisperLiveKit STT on laptop for voice dev loop
•	Test mem0 with Ollama backend on 3080
