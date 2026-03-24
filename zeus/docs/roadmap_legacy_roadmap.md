🗺️
ZEUS
Build Roadmap & Decisions Log

This is a living document. Decisions get logged here as they are made. Roadmap phases track what is built and when. This is the single source of truth for where Zeus stands and where it is going.

1. Decisions Log
All major stack and design decisions — current and open.

Core Stack
Decision	Status	Choice / Notes
Orchestration engine	DECIDED	Ruflo v3.5 — Claude Code native, stable, 60+ agents, MCP tools
Safety / sandbox layer	DECIDED	NemoClaw + OpenShell — stacks under Ruflo, not a replacement
STT engine	DECIDED	WhisperLiveKit — SimulStreaming SOTA 2025, works on 3080
TTS service	DECIDED	Voicebox (REST API) with LuxTTS engine selected
Voice cloning approach	DECIDED	Compose reference audio → LuxTTS encode_prompt for consistent voice
Memory layer	DECIDED	mem0 self-hosted — hybrid vector+graph+KV, Ollama support
Vector database	DECIDED	Qdrant — self-hosted Docker, production-grade
API bus	DECIDED	FastAPI — routes all services, exposes Zeus Context API
Repo name	DECIDED	zeus — fits Greek mythology naming scheme
Wake word / VAD	DECIDED	openWakeWord — fully open, CPU only, passive trigger

Models
Decision	Status	Choice / Notes
Dev model (cloud)	DECIDED	Claude API (Sonnet 4.6) — best quality during dev/RAG tuning phase
Prod model (server)	DECIDED	Ollama: Qwen2.5-7B-Instruct Q4_K_M on 3080 (10GB VRAM fit)
Backup prod model	DECIDED	Mistral-7B Q5_K_M — swap in for factual tasks if needed
Embed model	DECIDED	nomic-embed-text via Ollama — fast, good quality, free
Embed model alt	OPEN	bge-m3 — evaluate if nomic-embed-text retrieval quality is insufficient
14B model testing	OPEN	Tower 5080 (16GB) — test Qwen2.5-14B during dev, decide if worth server upgrade
Model fine-tuning	FUTURE	Train on personal data later — NemoClaw supports Nemotron fine-tuning

Data & Memory
Decision	Status	Choice / Notes
ChatGPT history strategy	DECIDED	Index user messages only; include assistant replies in curated threads only
Privacy levels	DECIDED	public / personal / sensitive / private — tagged on every chunk
Context-pack migration	DECIDED	Migrate + extend; Zeus Context API becomes new endpoint
Email ingestion	OPEN	IMAP parser — decide on scope: all mail vs starred/sent only
Calendar ingestion	OPEN	Key metadata only (event titles, attendees) — no full content
Watch/vitals integration	FUTURE	Depends on hardware (Shamus to test); API to be determined
Memory decay policy	OPEN	Define decay rates for episodic vs semantic memories in mem0
Graph memory (mem0g)	OPEN	Enable graph memory variant once base mem0 is stable

Interface & Future Vision
Decision	Status	Choice / Notes
Initial interface	DECIDED	Voice-only to start — openWakeWord → STT → Zeus → TTS
Web dashboard	OPEN	Lightweight status/query UI — defer until voice loop is working
VR integration	OPEN	Consult Brad — Oculus + avatar + Zeus voice; prototype concept
AR glasses (Meta)	FUTURE	End goal — Zeus talking in Meta glasses with visual avatar
Swarm visualization	FUTURE	Dashboard showing active agents, memory queries, voice pipeline status
Business productization	FUTURE	Personal data center installs for professional services — 10-20k per install model

2. Build Roadmap
Organized into sprints. Each sprint has a clear deliverable. School finishes in ~5 weeks — plan accordingly.

Sprint 0 — Foundation (This Week)
Sprint 0 — Foundation
☐	zeus repo init	mkdir zeus, git init, create CLAUDE.md for Ruflo, README, docker-compose scaffold
☐	Qdrant up	docker run -p 6333:6333 qdrant/qdrant — verify admin UI at localhost:6333/dashboard
☐	Ollama setup	ollama pull nomic-embed-text + qwen2.5:7b on tower — verify running
☐	mem0 init	pip install mem0ai — test basic add/search with local Ollama backend
☐	Get ChatGPT export	ChatGPT Settings → Data Controls → Export Data — download when ready
☐	Voice test	Install Voicebox on tower, pick LuxTTS engine, record reference audio for Zeus voice

Sprint 1 — Data Brain (Week 1–2)
Sprint 1 — Data Brain
☐	ChatGPT parser	zeus/ingest/sources/chatgpt.py — parse conversations.json, chunk, embed, store in Qdrant
☐	.md walker	zeus/ingest/sources/markdown.py — walk server context dirs, ingest all .md files
☐	Context-pack migration	zeus/ingest/sources/context_pack.py — pull and migrate existing API data
☐	Zeus Context API v1	FastAPI /query and /status endpoints — test with curl queries
☐	mem0 integration	Connect mem0 to Qdrant, verify search returns personal memories correctly
☐	Query test	Run test queries against your own data — verify relevance and retrieval quality

Sprint 2 — Voice Loop (Week 2–3)
Sprint 2 — Voice Loop
☐	WhisperLiveKit setup	Install on laptop/tower, test real-time STT from mic — verify latency
☐	openWakeWord	Configure wake word (pick one — "Hey Zeus"?) — trigger WhisperLiveKit on detect
☐	Voicebox API client	zeus/voice/tts_client.py — send text, receive audio, play via sounddevice
☐	Voice loop end-to-end	Wake word → STT → Zeus Core → TTS → speaker — full loop working
☐	Zeus Core v1	zeus/core/main.py — FastAPI that takes text input, queries mem0+Qdrant, calls LLM, returns response
☐	Voice test session	Have a full voice conversation with Zeus — identify pain points

Sprint 3 — Ruflo Agents (Week 3–4)
Sprint 3 — Ruflo Agents
☐	Ruflo init in zeus/	npx ruflo@latest init in repo — configure CLAUDE.md for Zeus-specific agents
☐	Personal agent	Define "Zeus Personal" agent — system prompt with personal context, RAG access
☐	Dev agent	Define "Zeus Dev" agent — code assistant with project context from vector DB
☐	Research agent	Define "Zeus Research" agent — web search + memory write-back
☐	NemoClaw setup	Install NemoClaw, configure OpenShell policies — define what agents can/cannot do
☐	Multi-agent test	Test parallel agent execution — complex task using 2+ agents simultaneously

Sprint 4 — Deploy to Server (Post-school, Week 5+)
Sprint 4 — Deploy to Server
☐	Docker compose	Full zeus docker-compose.yml — Qdrant, mem0 backend, Zeus Core, Voicebox, Ollama
☐	Server deploy	Deploy to 3080 server — test all services running stable
☐	Ollama on 3080	Pull Qwen2.5-7B Q4_K_M on server — benchmark latency vs tower
☐	Always-on mode	Zeus running as systemd service — wakes on keyword, sleeps otherwise
☐	Server voice	Move WhisperLiveKit to server — test STT latency over LAN
☐	Phase 2 ingestion	Email IMAP parser — filtered ingestion of mail into knowledge base

Backlog — Future Phases
Future / Backlog
☐	VR prototype	Coordinate with Brad — Zeus voice + avatar in Oculus environment
☐	Meta glasses	Research OpenClaw API compatibility with Meta glasses — voice assistant in AR
☐	Watch vitals	Health data integration — Shamus lead on this, share API spec when ready
☐	Web dashboard	React UI — Zeus status, memory browser, conversation history, agent activity
☐	Business template	Package Zeus as installable personal data center — accounting firm pilot
☐	Model fine-tuning	Fine-tune local model on personal data once enough conversation history accumulated

3. Naming Conventions
Zeus follows the Greek mythology theme throughout the codebase.

Component	Codename	Reason
Main repo / system	zeus	King of gods — the overarching personal AI OS
Memory layer	mnemosyne	Goddess of memory — mother of the Muses
Ingest pipeline	hermes	Messenger god — moves data between worlds
Voice interface	apollo	God of music/communication — voice of Zeus
Safety / guardrails	aegis	Shield of Zeus — protection layer
Agent swarm	olympians	The specialized agents that serve Zeus
Server hardware	olympus	Home of the gods — your always-on server
Context API	oracle	Knowledge endpoint — the oracle others query

4. Key Repos & Links
Decision	Status	Choice / Notes
Ruflo (orchestration)	DECIDED	github.com/ruvnet/ruflo — npm install -g ruflo@latest
NemoClaw	DECIDED	nvidia.com/en-us/ai/nemoclaw — single-command install
WhisperLiveKit (STT)	DECIDED	github.com/QuentinFuxa/WhisperLiveKit — pip install whisper-live-kit
Voicebox (TTS)	DECIDED	github.com/jamiepine/voicebox — voicebox.sh for install
LuxTTS engine	DECIDED	github.com/ysharma3501/LuxTTS — inside Voicebox as engine
mem0 (memory)	DECIDED	github.com/mem0ai/mem0 — pip install mem0ai
Qdrant (vector DB)	DECIDED	qdrant.tech — docker pull qdrant/qdrant
Ollama (model serving)	DECIDED	ollama.com — ollama pull qwen2.5:7b
openWakeWord	DECIDED	github.com/dscripka/openWakeWord

