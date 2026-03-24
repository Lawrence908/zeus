🗄️
ZEUS
Data Ingestion & Memory Playbook

This document covers how Zeus ingests, processes, and stores your personal data to build a persistent, evolving AI knowledge base — your "second brain" that grows smarter with every interaction.

1. The Strategy: RAG + mem0 Together
KEY DISTINCTION	RAG retrieves from static knowledge (your documents). mem0 stores evolving facts from conversations. Zeus uses BOTH: RAG for what you've written, mem0 for what Zeus learns about you over time.

Your existing personal data (ChatGPT history, .md files, context-packs) feeds the RAG pipeline — it becomes the static knowledge base. Every Zeus conversation adds to mem0 — preferences, decisions, patterns. Over months, Zeus stops needing you to re-explain context.

The Zeus Context API (successor to your context-pack API) exposes both layers over a single HTTP interface — other tools can query it just like your current context-pack setup.

2. Data Sources & Ingestion Phases

Phase	Timeline	Data Sources
Phase 1 — Seed	Immediately	ChatGPT export (JSON) .md context files from server Existing context-pack data Dev project notes & READMEs
Phase 2 — Grow	Weeks 2–4	Email (IMAP, privacy-filtered) Calendar events (key metadata only) Browser bookmarks (curated) Job application history
Phase 3 — Live	Ongoing	All new Zeus conversations (auto-stored via mem0) Project files as created/updated Watch vitals (if wearable) New .md files added to server stores

3. Memory Architecture
Zeus uses mem0's hybrid datastore architecture. Different memory types are stored in the optimal storage backend:

Memory Type	Storage	What Zeus Stores Here
Episodic	Vector (Qdrant)	What happened — conversations, events, decisions made
Semantic	Vector (Qdrant)	What you know — facts, preferences, expertise, projects
Relational	Graph (mem0g)	Who/what connects to what — people, projects, tools, skills
Procedural	KV Store	How things are done — workflows, templates, code patterns
Temporal	KV + metadata	When things happened — timestamps, recency weighting

MEM0 + OLLAMA	mem0 uses an LLM to extract key facts from conversations. During dev: Claude API. During prod: Ollama (Qwen2.5-7B) on the 3080. This keeps memory extraction entirely local and private.

4. Ingest Pipeline Design
The Zeus ingest pipeline lives in zeus/ingest/ and follows a consistent pattern for all data sources.

4.1 Pipeline Flow
Every source goes through the same stages:

1. Load	2. Clean	3. Chunk	4. Hash	5. Embed	6. Store	7. Tag	8. Index

•	Load: Read raw file or API response
•	Clean: Strip metadata noise, normalize encoding, remove duplicates
•	Chunk: Split into ~512 token segments with 64 token overlap
•	Hash: SHA-256 per chunk — skip if already in Qdrant (deduplication)
•	Embed: nomic-embed-text or bge-m3 via Ollama
•	Store: Upsert into Qdrant with payload metadata
•	Tag: source, date, topic_category, confidence, privacy_level
•	Index: Update mem0 with any entity-level facts extracted

4.2 ChatGPT Export Parser
The ChatGPT export is a JSON file (conversations.json) containing your entire history. This is the richest data source — years of your thinking, questions, and problem-solving patterns.

# zeus/ingest/sources/chatgpt.py
# Input:  conversations.json (from ChatGPT Settings → Export)
# Output: chunks in Qdrant + entity facts in mem0

Key processing decisions:
•	Only index YOUR messages (user role), not ChatGPT responses — you want YOUR knowledge patterns, not generic AI output
•	Exception: include assistant responses in topic threads where you clearly agreed or saved the content
•	Date-tag each conversation for temporal weighting (recent = higher weight)
•	Auto-categorize by conversation title into topic clusters (dev, career, projects, ideas, etc.)
•	Strip any PII you wouldn't want in a local index (NemoClaw policy can handle this)

4.3 Markdown File Walker
Your server context stores are .md files. The walker recursively processes all .md files in configured directories.

# zeus/ingest/sources/markdown.py
# Input:  directory path(s) from config
# Output: chunks in Qdrant, preserving file path as source metadata

•	Frontmatter extraction: title, tags, date from YAML frontmatter if present
•	Header-aware chunking: prefer to split at heading boundaries
•	File watcher mode: inotify on Linux to auto-ingest new/modified files
•	Respect .gitignore patterns for exclusion

4.4 Context-Pack Migration
Your existing context-pack API is a source that can be directly queried and its data migrated into Qdrant.

# zeus/ingest/sources/context_pack.py
# Input:  existing context-pack API endpoint
# Output: migrated chunks + Zeus Context API replaces it

•	One-time migration: pull all context-pack entries via API
•	Re-chunk and re-embed with standardized Zeus chunking
•	Zeus Context API becomes the new endpoint other tools point to
•	Backward-compatible: expose same query interface as context-pack for existing integrations

5. Zeus Context API
The Zeus Context API is a FastAPI service that exposes your entire knowledge base over HTTP. It replaces your context-pack API and serves as the single integration point for other tools.

5.1 Endpoints
Endpoint	Method	Description
/query	POST	Semantic search across all ingested knowledge
/memory/add	POST	Store a new memory or fact via mem0
/memory/search	POST	Search personal memories (episodic + semantic)
/ingest/trigger	POST	Trigger re-ingestion of a source
/status	GET	Health check + index stats
/context-pack/query	POST	Backward-compat endpoint (same as /query)

5.2 Query Response Format
POST /query
{ "query": "my react experience", "limit": 5, "sources": ["chatgpt", "md"] }

Response:
{ "results": [
    { "text": "...", "source": "chatgpt/2024-03", "score": 0.92, "tags": ["dev","react"] },
    ...
  ],
  "memories": [ "Prefers functional React components", "Worked on context-pack API" ]
}

6. Privacy & Data Governance
PRINCIPLE	Zeus only stores what you control. All data stays on your hardware. NemoClaw OpenShell enforces this at the runtime level — agents cannot exfiltrate data to unauthorized destinations.

Privacy Levels (tag on every chunk)
•	public — general knowledge, shareable
•	personal — your content, local only, never sent to cloud without explicit trigger
•	sensitive — PII, health data, financial info — encrypted at rest, mem0 graph excluded
•	private — not indexed at all, excluded from all queries

Data Excluded by Default
•	Banking and financial account data
•	Passwords, tokens, API keys (scanner strips these from .md files before ingest)
•	Content marked private in frontmatter (private: true)
•	Messages from contacts who haven't consented to being part of your AI index

Retention & Decay
•	mem0 supports automatic decay — stale memories lose weight over time
•	Manual purge: /memory/delete endpoint for removing specific facts
•	Full reset: nuke Qdrant collection + mem0 DB and re-ingest from scratch

7. Getting Started — Ingest Quickstart
Step-by-step to get your data into Zeus for the first time:

1.	Get ChatGPT export: ChatGPT → Settings → Data Controls → Export → wait for email
2.	Start Qdrant: docker run -p 6333:6333 qdrant/qdrant
3.	Start Ollama with embed model: ollama pull nomic-embed-text
4.	Run ChatGPT ingest: python zeus/ingest/sources/chatgpt.py --input conversations.json
5.	Run .md walker: python zeus/ingest/sources/markdown.py --dir /path/to/context/stores
6.	Migrate context-pack: python zeus/ingest/sources/context_pack.py --api http://your-api
7.	Start Zeus Context API: uvicorn zeus.api.main:app --port 8000
8.	Verify: curl http://localhost:8000/status
