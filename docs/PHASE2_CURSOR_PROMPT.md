# Zeus Phase 2 Implementation Prompt for Cursor

**Copy this entire prompt into Cursor's AI assistant to get context-aware help building Phase 2.**

---

## Project Context

I'm building **Zeus**, a self-hosted personal AI assistant that ingests your data, remembers context across conversations, and answers questions with voice or text.

### Architecture Overview
- **zeus/core/** — FastAPI entry point, session management, query handler
- **zeus/api/** — REST API for semantic search (Oracle subsystem)
- **zeus/ingest/** — Data pipeline (Iris subsystem) — parsers for ChatGPT, Markdown, context-pack
- **zeus/memory/** — mem0 + Qdrant integration (Mnemosyne subsystem)
- **zeus/models/** — Ollama configs, prompt templates
- **zeus/voice/** — Voice interface stubs (Orpheus subsystem)
- **zeus/safety/** — Policy templates (Aegis subsystem)
- **zeus/orchestration/** — Ruflo agent configs (Olympians subsystem)

### Tech Stack
- **Vector DB:** Qdrant (Docker, port 6333)
- **LLM:** Ollama running Qwen2.5-7B-Instruct Q4_K_M (port 11434)
- **HTTP API:** FastAPI (Zeus Core, port 8203)
- **Embeddings:** nomic-embed-text via Ollama
- **Memory:** mem0 + Qdrant for hybrid storage
- **Dev LLM:** Claude API (Sonnet 4.6) for rapid iteration
- **Container:** Docker Compose for reproducible setup

### Code Standards
- Python 3.11+ only
- FastAPI for all HTTP endpoints
- Type hints everywhere
- Async where it matters (I/O bound)
- No comments unless the code can't express intent
- Prefer composition over inheritance
- Each service independently startable for testing
- File paths as comments at top of each file

### Greek Naming Convention (REQUIRED)
All subsystems use Greek mythology names:
- **zeus** = main system
- **mnemosyne** = memory layer (mem0 + Qdrant)
- **iris** = ingest pipeline (data sources → chunks)
- **orpheus** = voice interface (STT, TTS, wake word)
- **aegis** = safety layer (policy enforcement)
- **olympians** = agent swarm (Ruflo tasks)
- **oracle** = Context API (structured context serving)
- **olympus** = production server (RTX 3080)

Use these names consistently in code, configs, docs, PRs, and commit messages.

---

## Phase 2: Data Brain — Current Status

### ✓ Already Implemented
1. **LAB-45 (ChatGPT Export Parser)** — `zeus/ingest/sources/chatgpt.py`
   - Parses conversations.json from ChatGPT export
   - User-message-only filtering with optional assistant inclusion
   - Date-based temporal tagging and topic auto-categorization
   - Wired into ingest pipeline

2. **LAB-46 (Markdown File Walker)** — `zeus/ingest/sources/markdown.py`
   - Recursive .md file walker
   - Heading-aware chunking (split at heading boundaries)
   - YAML frontmatter extraction (title, tags, date)
   - .gitignore pattern respect

3. **LAB-47 (Context-Pack Migration)** — `zeus/ingest/sources/context_pack.py`
   - Pull from existing context-pack API
   - Re-chunk with standardized Zeus chunking
   - Re-embed and load into Qdrant

4. **LAB-48 (Zeus Context API v1 / Oracle)** — `zeus/api/main.py`
   - POST `/context/query` — semantic search endpoint
   - POST `/memory/add` and `/memory/search` — memory endpoints
   - POST `/ingest/trigger` — trigger ingest for a source
   - GET `/status` — index stats and health
   - GET `/context/profile` — structured personal context
   - Backward-compat endpoint `/context-pack/query`

5. **LAB-49 (Zeus Query Engine)** — `zeus/core/query.py`
   - Text in → semantic search (Qdrant) → LLM response
   - System prompt with personal context injection
   - LLM provider switching (Claude API dev / Ollama prod)
   - Response quality testing framework

6. **Ingest Pipeline** — `zeus/ingest/pipeline.py` and `zeus/ingest/run.py`
   - Unified CLI: `python -m zeus.ingest.run --source chatgpt`
   - Chunk → embed → store orchestration
   - Hash-based deduplication

### ▶ In Progress / Needs Work

**LAB-61 (mem0 Integration & Retrieval Quality)** — `zeus/memory/` directory
- **Done:** mem0 client + Qdrant connector (`memory/config.py`)
- **Done:** Memory search with token budgeting (`memory/search.py`)
- **Needs:** Retrieval quality evaluation harness
- **Needs:** Tune chunk size, overlap, embedding params for relevance
- **Needs:** Build context block formatting for LLM consumption

**LAB-56 (Privacy & Data Governance)** — `zeus/safety/` directory
- **Status:** Policy templates exist, no enforcement layer yet
- **To implement:**
  - Privacy level tagging (public/personal/sensitive/private)
  - PII scanner for stripping secrets from .md files
  - Hash-based deduplication
  - Collection versioning for Qdrant migrations

**LAB-64 (Email Ingest)** — Phase 2 Data Sources
- **Status:** Not started
- **To implement:** `zeus/ingest/sources/email.py`
  - IMAP email parser
  - Privacy-filtered ingestion (starred/sent only vs all)
  - Email-specific metadata tagging (sender, subject, thread)

---

## Phase 2 Implementation Tasks

### Immediate Priority (This Sprint)

1. **Validate Retrieval Quality (LAB-127)**
   - Build ground-truth query set against personal ChatGPT data
   - Expected sources for each query
   - Measure recall@5, recall@10, MRR
   - Identify tuning gaps

2. **Tune Retrieval Parameters (LAB-126)**
   - Vary chunk size (256, 512, 1024 tokens)
   - Vary overlap (0, 50%, 100% of chunk)
   - Vary embedding model params (if applicable)
   - Rerun eval suite for each config

3. **Build Retrieval Eval Suite (LAB-127)**
   - Load ground-truth queries from JSON
   - Run against current Qdrant index
   - Compare retrieved docs to expected sources
   - Generate report (recall, precision, MRR)
   - File: `zeus/memory/eval.py`

4. **Implement Context Block Formatting (LAB-123)**
   - Format retrieved chunks for LLM consumption
   - Token budgeting (stay under context limit)
   - Metadata formatting (source, date, tags)
   - File: `zeus/memory/formatting.py`

### Secondary Priority (Next 2 Weeks)

5. **Email Ingest (LAB-64, LAB-136, LAB-138, LAB-139, LAB-143)**
   - IMAP parser for email ingestion
   - Privacy filtering (scope: starred/sent only vs all)
   - Metadata tagging (sender, subject, thread)
   - Test with real email accounts

6. **Privacy & Data Governance (LAB-56 — blocked until email ingest)**
   - Privacy level tagging per document
   - PII scanner for .md files
   - Deduplication strategy
   - Collection versioning for migrations

---

## Key Files to Work On

```
zeus/
├── memory/
│   ├── config.py          ← mem0 client setup (done)
│   ├── search.py          ← token-budgeted search (done)
│   ├── eval.py            ← NEW: retrieval eval suite
│   └── formatting.py      ← NEW: context block formatting
├── ingest/
│   ├── sources/
│   │   ├── chatgpt.py     ← done
│   │   ├── markdown.py    ← done
│   │   ├── context_pack.py ← done
│   │   └── email.py       ← NEW: IMAP parser
│   ├── pipeline.py        ← may need updates for eval
│   └── run.py
├── core/
│   ├── query.py           ← integrate formatting.py here
│   └── main.py
└── models/
    └── prompt_templates/  ← update system prompt for context injection
```

---

## Testing & Validation

### Unit Tests
- Test memory search with real Qdrant index
- Test email parser with sample IMAP mailbox
- Test context block formatting with various chunk sizes

### Integration Tests
- End-to-end ingest: raw data → chunks → embed → store
- End-to-end query: text in → search → format → LLM → response
- Eval suite against ground-truth queries

### Smoke Tests
```bash
# Start services
docker compose up -d

# Run ingest
python -m zeus.ingest.run --source chatgpt

# Test query endpoint
curl -X POST http://localhost:8203/context/query \
  -H "Content-Type: application/json" \
  -d '{"q": "what did i discuss about memory systems?", "max_results": 5}'

# Test retrieval eval
python -m zeus.memory.eval --query-set queries.json --output report.json
```

---

## Environment & Dependencies

### .env Variables
```env
ZEUS_ENV=dev           # or 'prod' for Ollama
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434
CLAUDE_API_KEY=sk-...  # only needed if ZEUS_ENV=dev
```

### Docker Services (docker compose up -d)
- **qdrant** (port 6333) — vector DB
- **ollama** (port 11434) — local LLM
- **zeus-core** (port 8203) — FastAPI app

### Python Packages (in requirements.txt or pyproject.toml)
- mem0-ai
- qdrant-client
- fastapi
- pydantic
- httpx (for Ollama/Claude API calls)
- python-dotenv

---

## Implementation Notes

### About mem0 Integration
mem0 handles hybrid storage (vector + graph + KV). When you add to memory:
```python
from zeus.memory.config import memo_client
memo_client.add("key", "value", metadata={"source": "chatgpt"})
```

When you search:
```python
from zeus.memory.search import semantic_search
results = semantic_search("query", max_results=5, token_budget=2000)
```

The token_budget parameter limits how many tokens of context you get back.

### About Chunk Formatting
Retrieved chunks need to be formatted for the LLM:
```
[ChatGPT | 2024-03-15]
User: how do you implement...
Assistant: you can implement...

---

[Markdown | notes/ai.md]
# Memory Systems
Vector databases store...
```

### About Retrieval Eval
Your eval suite should:
1. Load query set with expected source documents
2. Run each query against Qdrant
3. Compare returned docs to expected
4. Calculate recall@K, MRR, precision
5. Report which queries fail (false negatives)

---

## Commit Message Format

Use Linear ticket numbers in branch and commit messages:

```bash
git checkout -b chrislawrencedev/LAB-127-build-retrieval-eval-suite
git commit -m "Build retrieval eval suite with ground-truth queries

- Load eval set from JSON
- Measure recall@5, recall@10, MRR
- Generate report with failure analysis

(LAB-127)"
```

---

## Questions to Ask While Implementing

1. **For retrieval tuning:** What chunk size / overlap gives best recall with acceptable latency?
2. **For email ingest:** Should we default to "starred/sent only" or make it configurable?
3. **For privacy:** What metadata should we preserve vs strip during ingest?
4. **For formatting:** How many tokens should we reserve for context in typical queries?

---

## Reference Docs

- **Architecture & Code Standards:** `CLAUDE.md` (root)
- **Full Roadmap & Status:** `docs/zeus_linear_ticket_plan.md`
- **Project README:** `README.md`
- **System Prompt Template:** `docs/SYSTEM_PROMPT.md`

---

## How to Use This in Cursor

1. Copy this entire prompt
2. Open Cursor → New Chat
3. Paste the prompt
4. Ask specific questions like:
   - "I need to build the retrieval eval suite. What should the query set JSON look like?"
   - "Help me implement email ingest with privacy filtering"
   - "How should I structure the context block formatting?"
   - "Review this code for compliance with the code standards"
   - "Explain how mem0 search works with token budgeting"

Cursor will have full context and can provide implementation-ready code.

---

**Last Updated:** 2026-03-25
**Target Completion:** ~2 weeks (evaluation → tuning → email ingest → privacy layer)