# Zeus Phase 9-10 Implementation Prompt for Cursor

**Copy this entire prompt into Cursor's AI assistant to get context-aware help building Phase 9-10.**

---

## Quick Context

This assumes you've completed **Sprints 1–8** — memory, voice, sessions, text chat, and MCP server are all working. Sprint 5 (agent runtime) is also complete: `GET /orchestration/status` returns all agents.

### Key Reference
- Project Architecture: `CLAUDE.md`
- Full Roadmap: `docs/zeus_linear_ticket_plan.md` and `zeus/docs/roadmap.md`
- Phase 5-6 Context: `docs/PHASE5_6_CURSOR_PROMPT.md`

---

## Phase Overview

**Sprint 9: Observability + Continuous Ingest** — Day-2 operations: know what Zeus is doing and keep memory fresh automatically.
- Query logging (latency, source count, prompt hash)
- Admin API: ingest stats, system metrics
- Minimal admin dashboard at `/admin`
- Scheduled periodic Iris runs
- Memory consolidation job (dedup / merge overlapping chunks)

**Sprint 10: Additional Ingest Sources** — Expand memory coverage with high-signal personal data.
- Obsidian vault parser
- Git history parser
- Google Calendar parser
- Browser bookmarks parser
- Register all sources in `zeus/ingest/run.py` and `orchestration/agents/iris.yaml`

**Why Together?** Sprint 9 gives you visibility into what's in memory and how it's being queried. Sprint 10 feeds more signal in. Running them together means you can immediately see the impact of new ingest sources in the admin dashboard.

---

## Current Status

### ✓ Complete

- `zeus/core/sessions.py` — session lifecycle, multi-turn continuity
- `zeus/core/chat.py` — text chat routes, SSE streaming
- `zeus/core/query.py` — query engine with LLM + Oracle context
- `zeus/mcp/server.py` + `zeus/mcp/tools.py` — MCP server with tools
- `zeus/orchestration/runtime.py` — agent lifecycle engine
- `zeus/orchestration/bus.py` — inter-agent FastAPI router
- `zeus/orchestration/hooks.py` — pre/post hook registry
- `zeus/ingest/sources/` — chatgpt, markdown, context_pack, email parsers
- `zeus/api/main.py` — Oracle context API (`/context/query`, `/context/profile`)

### ⧬ Not Started (Sprint 9)

- Query logging middleware (request_id, prompt_hash, latency_ms, source_count)
- `/admin/ingest/stats` endpoint
- `/admin/metrics` endpoint
- `/admin` dashboard HTML
- Scheduled ingest via `zeus/ingest/scheduler.py`
- Memory consolidation job `zeus/memory/consolidate.py`

### ⧬ Not Started (Sprint 10)

- `zeus/ingest/sources/obsidian.py`
- `zeus/ingest/sources/git.py`
- `zeus/ingest/sources/gcal.py`
- `zeus/ingest/sources/bookmarks.py`
- Registration in `zeus/ingest/run.py`

---

## Sprint 9: Observability + Continuous Ingest

### Architecture

```
User Query
    ↓
Zeus Core (chat / voice)
    ↓  ← QueryLoggingMiddleware records latency + metadata
Oracle / Query Engine
    ↓
Response → User

                    ┌─────────────────────────┐
                    │  Admin Dashboard /admin  │
                    │  - Live query log        │
                    │  - Ingest stats          │
                    │  - Agent swarm status    │
                    │  - Memory collection info│
                    └─────────────────────────┘
                                 ↑
                    GET /admin/metrics
                    GET /admin/ingest/stats

Scheduler (APScheduler)
    ├─ Every 6h: run Iris ingest (new files only)
    └─ Every 24h: run memory consolidation
```

### Task Breakdown

#### Sprint 9a: Query Logging (LAB-147)

**Goal:** Every query through Oracle/query-engine gets a log entry with enough fields to diagnose latency and retrieval quality issues.

**Key File:** `zeus/core/middleware.py`

```python
import hashlib, time, uuid, logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("zeus.query")

class QueryLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not request.url.path.startswith(("/chat/message", "/context/query")):
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start = time.monotonic()

        response = await call_next(request)

        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.info(
            "query",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "latency_ms": latency_ms,
                "status": response.status_code,
            },
        )
        response.headers["X-Request-Id"] = request_id
        return response
```

**Wire into `main.py`:**
```python
from zeus.core.middleware import QueryLoggingMiddleware
app.add_middleware(QueryLoggingMiddleware)
```

#### Sprint 9b: Ingest Stats Endpoint (LAB-148)

**Goal:** `GET /admin/ingest/stats` returns counts, last-run time, and per-source summaries.

**Key File:** `zeus/core/admin.py`

```python
from fastapi import APIRouter, Request
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/ingest/stats")
async def ingest_stats(request: Request) -> dict:
    """Return collection size and per-source chunk counts from Qdrant."""
    memory = request.app.state.memory
    # Query Qdrant collection info
    ...

@router.get("/metrics")
async def metrics(request: Request) -> dict:
    """Return uptime, agent swarm status, recent query count."""
    runtime = request.app.state.agent_runtime
    return {
        "uptime_seconds": ...,
        "agents": runtime.get_status(),
        "recent_queries": ...,
    }
```

#### Sprint 9c: Admin Dashboard (LAB-149)

**Goal:** Minimal HTML dashboard at `/admin` — no external JS framework, just server-rendered HTML + a little vanilla JS for auto-refresh.

**Key File:** `zeus/core/static/admin.html`

Contents:
- Agent swarm status table (name, status, model)
- Ingest stats table (source, chunk count, last run)
- Recent queries table (timestamp, latency, path, status)
- Auto-refreshes every 30s via `fetch("/admin/metrics")`

**Route:** `GET /admin` → serves `admin.html`

#### Sprint 9d: Scheduled Ingest (LAB-148 extension)

**Goal:** Iris runs automatically every N hours so memory stays fresh without manual intervention.

**Key File:** `zeus/ingest/scheduler.py`

```python
# Uses APScheduler (add to requirements.txt: apscheduler>=3.10)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zeus.ingest.pipeline import IngestPipeline

def build_scheduler(pipeline: IngestPipeline) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    # Incremental ingest every 6 hours
    scheduler.add_job(
        pipeline.run_all_sources,
        "interval",
        hours=6,
        id="iris_ingest",
        kwargs={"incremental": True},
    )
    return scheduler
```

**Wire into lifespan in `main.py`:**
```python
scheduler = build_scheduler(ingest_pipeline)
scheduler.start()
app.state.ingest_scheduler = scheduler
# In yield cleanup:
scheduler.shutdown()
```

**New env vars:**
```env
INGEST_SCHEDULE_HOURS=6      # how often Iris runs
INGEST_INCREMENTAL=true      # skip already-ingested content
```

#### Sprint 9e: Memory Consolidation (backlog item)

**Goal:** Periodically dedup and merge near-duplicate memory chunks to keep Qdrant lean.

**Key File:** `zeus/memory/consolidate.py`

```python
class MemoryConsolidator:
    def __init__(self, memory_client, similarity_threshold: float = 0.95):
        ...

    async def run(self) -> dict:
        """Find near-duplicate chunks, merge, delete originals."""
        # 1. Scroll all chunks from Qdrant
        # 2. Find pairs with cosine similarity > threshold
        # 3. Merge text, keep highest-quality source metadata
        # 4. Delete originals, write merged chunk
        ...
```

**Scheduled:** every 24h via APScheduler

---

## Sprint 10: Additional Ingest Sources

### Architecture

```
zeus/ingest/sources/
    ├── chatgpt.py        ← existing
    ├── markdown.py       ← existing
    ├── context_pack.py   ← existing
    ├── email.py          ← existing
    ├── obsidian.py       ← NEW: Obsidian vault (.md with frontmatter + [[links]])
    ├── git.py            ← NEW: git log --all --format=... → commit messages + diffs
    ├── gcal.py           ← NEW: Google Calendar API → events as text chunks
    └── bookmarks.py      ← NEW: browser bookmark HTML export
```

Each source implements the same interface as existing sources:
```python
class SourceParser:
    def parse(self, path: str | Path) -> list[Chunk]:
        """Return list of Chunk(text, metadata) ready for embed + store."""
```

### Task Breakdown

#### Sprint 10a: Obsidian Parser (LAB in backlog)

**Key File:** `zeus/ingest/sources/obsidian.py`

**What it handles:**
- Standard Markdown files in Obsidian vault
- YAML frontmatter (`---` blocks) → metadata
- `[[WikiLink]]` references → resolved to source file links in metadata
- `#tag` extraction → stored as chunk tags
- Daily notes detected by filename pattern (`YYYY-MM-DD.md`)

**Config in `iris.yaml`:**
```yaml
- type: obsidian
  vault_path: "${OBSIDIAN_VAULT_PATH}"
  exclude_dirs: [".obsidian", "templates", "archive"]
```

**New env var:** `OBSIDIAN_VAULT_PATH`

#### Sprint 10b: Git History Parser (LAB in backlog)

**Key File:** `zeus/ingest/sources/git.py`

**What it handles:**
- `git log` output: commit hash, author, date, message
- Generates one chunk per commit: `"[date] commit: [message] (files: [changed files])`
- Optionally includes `git diff --stat` per commit (file change summaries)
- Filters by author email to keep only your own commits
- Configurable depth (last N commits, or since date)

**Config in `iris.yaml`:**
```yaml
- type: git
  repo_path: "${ZEUS_REPO_PATH}"
  author_email: "${GIT_AUTHOR_EMAIL}"
  max_commits: 500
```

**New env vars:** `GIT_AUTHOR_EMAIL`, `ZEUS_REPO_PATH`

#### Sprint 10c: Google Calendar Parser (LAB in backlog)

**Key File:** `zeus/ingest/sources/gcal.py`

**What it handles:**
- Google Calendar API v3 (OAuth2)
- Fetches events from primary calendar (past 90 days + next 30 days)
- Generates chunks: `"[date] [title]: [description] (attendees: [list])"`
- Recurring events deduplicated
- Private events skipped (configurable)

**Auth:** OAuth2 token stored in `zeus/data/gcal_token.json` (gitignored)

**Config in `iris.yaml`:**
```yaml
- type: gcal
  credentials_path: "zeus/data/gcal_credentials.json"
  token_path: "zeus/data/gcal_token.json"
  days_back: 90
  days_forward: 30
```

**New deps:** `google-api-python-client>=2.0`, `google-auth-oauthlib>=1.0`

#### Sprint 10d: Bookmarks Parser (LAB in backlog)

**Key File:** `zeus/ingest/sources/bookmarks.py`

**What it handles:**
- Netscape Bookmark HTML format (exported from Chrome/Firefox/Safari)
- Extracts: title, URL, ADD_DATE, folder path
- Generates chunks: `"Bookmark: [title] — [url] (folder: [path], added: [date])"`
- Deduplicates by URL
- Optionally fetches page content for top-N bookmarks (configurable, slow)

**Config in `iris.yaml`:**
```yaml
- type: bookmarks
  export_path: "zeus/data/raw/bookmarks.html"
  fetch_content: false   # set true to fetch page text (slow)
```

#### Sprint 10e: Source Registration

**`zeus/ingest/run.py` additions:**
```python
from zeus.ingest.sources.obsidian import ObsidianParser
from zeus.ingest.sources.git import GitParser
from zeus.ingest.sources.gcal import GoogleCalendarParser
from zeus.ingest.sources.bookmarks import BookmarksParser

SOURCE_REGISTRY = {
    "markdown": MarkdownParser,
    "chatgpt": ChatGPTParser,
    "context_pack": ContextPackParser,
    "email": EmailParser,
    "obsidian": ObsidianParser,       # NEW
    "git": GitParser,                  # NEW
    "gcal": GoogleCalendarParser,      # NEW
    "bookmarks": BookmarksParser,      # NEW
}
```

**`orchestration/agents/iris.yaml` additions:**
```yaml
config:
  sources:
    - type: obsidian
      vault_path: "${OBSIDIAN_VAULT_PATH}"
    - type: git
      repo_path: "."
      author_email: "${GIT_AUTHOR_EMAIL}"
    - type: gcal
      credentials_path: "zeus/data/gcal_credentials.json"
    - type: bookmarks
      export_path: "zeus/data/raw/bookmarks.html"
```

---

## Key Files to Work On

### Sprint 9

```
zeus/
├── core/
│   ├── admin.py              ← NEW: /admin/ingest/stats, /admin/metrics, /admin dashboard
│   ├── middleware.py         ← NEW: QueryLoggingMiddleware
│   ├── main.py               ← wire in admin router, middleware, scheduler
│   └── static/
│       └── admin.html        ← NEW: minimal admin dashboard
├── ingest/
│   └── scheduler.py          ← NEW: APScheduler for periodic Iris runs
└── memory/
    └── consolidate.py        ← NEW: dedup + merge near-duplicate chunks
```

### Sprint 10

```
zeus/ingest/sources/
    ├── obsidian.py           ← NEW
    ├── git.py                ← NEW
    ├── gcal.py               ← NEW
    └── bookmarks.py          ← NEW
zeus/ingest/run.py            ← register new sources in SOURCE_REGISTRY
zeus/orchestration/agents/iris.yaml  ← add new source entries
```

---

## Environment Variables

### Sprint 9

```env
# Observability
ZEUS_LOG_LEVEL=info          # debug | info | warning | error
ZEUS_LOG_FORMAT=text         # text (dev) | json (prod)

# Scheduled ingest
INGEST_SCHEDULE_HOURS=6
INGEST_INCREMENTAL=true

# Memory consolidation
CONSOLIDATE_SCHEDULE_HOURS=24
CONSOLIDATE_SIMILARITY_THRESHOLD=0.95
```

### Sprint 10

```env
# Obsidian
OBSIDIAN_VAULT_PATH=/path/to/your/vault

# Git
GIT_AUTHOR_EMAIL=you@example.com

# Google Calendar (file paths, not secrets)
GCAL_CREDENTIALS_PATH=zeus/data/gcal_credentials.json
GCAL_TOKEN_PATH=zeus/data/gcal_token.json
```

---

## New Dependencies

### Sprint 9

```
# requirements.txt additions
apscheduler>=3.10.0         # scheduler for periodic ingest
```

### Sprint 10

```
# requirements.txt additions
google-api-python-client>=2.0.0
google-auth-oauthlib>=1.2.0
beautifulsoup4>=4.12.0      # bookmarks HTML parser
gitpython>=3.1.0            # git history parser (or subprocess)
```

---

## Testing & Validation

### Sprint 9: Exit Criterion

```bash
uvicorn zeus.core.main:app --reload

# Admin metrics
curl -s localhost:8000/admin/metrics | python3 -m json.tool

# Ingest stats (requires at least one ingest run)
curl -s localhost:8000/admin/ingest/stats | python3 -m json.tool

# Admin dashboard
open http://localhost:8000/admin
# Should render table of agent swarm status + ingest stats

# Verify query logging fires
curl -s -X POST localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"what are my projects"}' | python3 -m json.tool
# Server logs should show: zeus.query INFO query latency_ms=... path=/chat/message
```

### Sprint 10: Exit Criterion

```bash
# Dry-run all sources (no writes)
python -m zeus.ingest.run --source all --dry-run

# Should list chunks from every registered source without errors:
# ✓ markdown: N chunks
# ✓ chatgpt: N chunks
# ✓ obsidian: N chunks
# ✓ git: N chunks
# ✓ gcal: N chunks  (requires credentials)
# ✓ bookmarks: N chunks

# Live run single new source
python -m zeus.ingest.run --source obsidian
curl -s localhost:6333/collections/zeus_memories | python3 -m json.tool
# vectors_count should increase
```

---

## Implementation Notes

### Sprint 9 Decisions

**Why APScheduler over a cron job?**
- Runs inside the FastAPI process — no separate daemon to manage
- Respects `ZEUS_ENV` (different schedules for dev/prod)
- Introspectable via the admin API (next run time, last run time, errors)
- Easy to pause/resume via API if needed

**Why a custom admin dashboard (not Grafana/Prometheus)?**
- Zero external dependencies for a personal assistant
- Grafana is overkill for one user on a homelab
- Simple HTML + fetch is sufficient, and stays within the Greek naming convention
- Can always add Prometheus metrics exporter later if needed

**Structured logging in prod:**
- Set `ZEUS_LOG_FORMAT=json` in prod
- Use Python's `logging` with a JSON formatter
- Fields: `timestamp`, `level`, `logger`, `message`, `request_id`, `latency_ms`

### Sprint 10 Decisions

**Why Obsidian first?**
- Highest signal-to-noise — Obsidian notes are deliberate, curated knowledge
- Already markdown-compatible with the existing `markdown.py` parser
- `[[WikiLink]]` graph structure is valuable metadata for retrieval ranking

**Why Git history?**
- Captures what you've actually built, debugged, and shipped
- Commit messages are dense, high-quality text about your work
- Very low friction to ingest (no auth, already on disk)

**Why not fetch bookmark page content by default?**
- Fetching 1000+ URLs at ingest time is slow (minutes to hours)
- Page content goes stale (URLs change, pages disappear)
- Title + URL + folder path is usually enough for retrieval
- Power users can enable `fetch_content: true` for curated bookmark sets

**Google Calendar auth:**
- Use OAuth2 "installed application" flow (not service account)
- First-time setup: run `python -m zeus.ingest.sources.gcal --auth` to generate token
- Token refresh is automatic via google-auth-oauthlib
- Credentials file stays gitignored (`zeus/data/`)

---

## Dependency Chain

```
Sprint 1 (Memory) + Sprint 2 (Voice) + Sprint 5 (Runtime)
    ↓
Sprint 9a (Query Logging)
    ↓
Sprint 9b (Ingest Stats + /admin/metrics)
    ↓
Sprint 9c (Admin Dashboard)
    ├─ Sprint 9d (Scheduled Ingest) — parallel
    └─ Sprint 9e (Memory Consolidation) — parallel

Sprint 1 (Memory) + Sprint 9 (Observability)
    ↓
Sprint 10 (each source is independent, can be done in parallel):
    ├─ Sprint 10a (Obsidian)
    ├─ Sprint 10b (Git)
    ├─ Sprint 10c (Google Calendar)
    └─ Sprint 10d (Bookmarks)
        ↓
Sprint 10e (Source Registration — wire all into run.py + iris.yaml)
```

---

## Tickets (from zeus_linear_ticket_plan.md)

### Sprint 9 — Project 8: Observability + Admin

| Ticket | Title | Key File |
|--------|-------|----------|
| LAB-147 | Metrics Collection | `zeus/core/middleware.py` |
| LAB-148 | Admin API Routes | `zeus/core/admin.py` + scheduler |
| LAB-149 | Admin Dashboard | `zeus/core/static/admin.html` |

### Sprint 10 — Project: Additional Ingest Sources (Backlog)

| Ticket | Title | Key File |
|--------|-------|----------|
| (new) | Obsidian Parser | `zeus/ingest/sources/obsidian.py` |
| (new) | Git History Parser | `zeus/ingest/sources/git.py` |
| (new) | Google Calendar Parser | `zeus/ingest/sources/gcal.py` |
| (new) | Bookmarks Parser | `zeus/ingest/sources/bookmarks.py` |
| (new) | Source Registration | `zeus/ingest/run.py` updates |

---

## How to Use This in Cursor

1. Copy this entire prompt
2. Open Cursor → New Chat
3. Paste the prompt
4. Ask specific questions like:
   - "Implement the QueryLoggingMiddleware for Zeus"
   - "Build the /admin/ingest/stats endpoint using Qdrant collection info"
   - "Write the admin.html dashboard with agent status and ingest stats"
   - "Implement the Obsidian vault parser with WikiLink handling"
   - "Set up APScheduler for periodic Iris ingest in the FastAPI lifespan"
   - "Build the Git history ingest source for Zeus"

Cursor will have full context and can provide implementation-ready code.

---

**Last Updated:** 2026-03-26
**Depends On:** Sprints 1–8 complete, Sprint 5 (agent runtime) complete
**Critical Path:** Sprint 9a (logging) → 9b (stats endpoint) → 9c (dashboard). Sprint 10 sources are all parallel.
