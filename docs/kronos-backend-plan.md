# Kronos: Scheduler Subsystem (Backend Plan)

## Context

Kronos is a new Zeus subsystem: a deterministic, cron-driven scheduler and job executor. It is the "measured time" counterpart to Kairos's "opportune moment." Kairos remains the autonomous observe-decide-act daemon; Kronos runs jobs at declared times, on schedules users set.

Kronos is the single source of truth for anything time-based in Zeus: newsletter digests, nightly ingest, weekly memory reviews, daily briefings, scheduled research, and any user-created recurring task. Chat can create jobs on the fly; a `/jobs` dashboard shows everything running.

## Scope

In scope:

- Persistent job registry with cron-like and one-off schedules
- Asyncio scheduler loop that dispatches due jobs
- Executor with three dispatch modes: built-in Python, agent-via-bus, gated shell
- REST API under `/kronos/*`
- MCP tool for chat-initiated job creation
- Aegis safety on every execution path
- Absorbs LAB-341 and LAB-343 (newsletter scheduling moves here)

Out of scope:

- Replacing Kairos (stays as the autonomous observer)
- Visual DAG/workflow editor (jobs can chain by calling agents, no graph UI)
- Distributed/multi-host scheduling (single process, single host)

## Greek naming

**Kronos**: titan of sequential, measured time. Deterministic execution at declared moments. Parallel to **Kairos** (opportune moment, reactive), not a replacement.

## File layout

```text
zeus/
  kronos/
    __init__.py
    models.py          # JobDefinition, JobRun, JobSchedule, JobStatus, JobCategory
    storage.py         # JobStorage Protocol + SQLiteJobStorage
    scheduler.py       # KronosScheduler asyncio loop
    executor.py        # KronosExecutor with built-in/agent/shell modes
    registry.py        # get/list/add/update/delete; loads seed from YAML
    api.py             # FastAPI router mounted at /kronos
    jobs/              # Built-in job implementations
      __init__.py
      newsletter.py    # replaces LAB-343 KAIROS observer
      ingest.py        # scheduled ingest runs
      memory_review.py
      briefing.py      # daily news, weekly summary, etc.
      health_check.py
      job_search.py    # Phase 2, forwards to external app
  data/
    kronos.db          # SQLite: jobs + job_runs tables
    kronos.yaml        # Declarative seed jobs (loaded on empty DB)
```

## Job model

`zeus/kronos/models.py` defines the Pydantic shapes. Key ideas:

- `JobDefinition` carries identity, schedule, executor target, params, safety policy, timeout, retry policy.
- `JobSchedule` holds either a cron expression + timezone, or a one-off `run_at` datetime. One-offs fire once then auto-disable.
- `JobCategory` is an enum: `briefing`, `ingest`, `memory_review`, `maintenance`, `research`, `job_search`, `health`, `custom`.
- `JobRun` records every execution: status, started_at, finished_at, duration_ms, output_summary, error, correlation_id.
- `JobStatus` enum: `pending`, `running`, `success`, `failed`, `timeout`, `cancelled`.

## Storage

Mirror the `SessionStorage` pattern from LAB-329. `JobStorage` Protocol with `SQLiteJobStorage` as the default implementation. `asyncio.to_thread` plus stdlib `sqlite3`, no new deps. Tables: `jobs` (one row per definition), `job_runs` (one row per execution, indexed by `job_id` and `started_at`). DB path from `ZEUS_KRONOS_DB_PATH` (default `zeus/data/kronos.db`). Persists across container restarts via the existing `zeus_data` volume.

## Scheduler engine

Use `croniter` (tiny dep, does one thing) for cron expression parsing. The scheduler is an asyncio loop:

1. Tick every `ZEUS_KRONOS_TICK_SECONDS` (default 30).
2. On each tick, query enabled jobs and compute whether their next fire time has passed since `last_fired_at` (stored on the job row).
3. For each due job, spawn `asyncio.create_task(executor.run(job))`.
4. Update `last_fired_at` before dispatching to prevent double-fires.
5. One-off jobs (`run_at` set) disable themselves after firing.

Concurrency cap via `ZEUS_KRONOS_MAX_CONCURRENT` (default 3). Excess jobs queue and fire on the next tick.

Scheduler lifespan is a single `asyncio.create_task` registered in `zeus/core/main.py`, same pattern as the newsletter digest runner and (future) Kairos daemon. Graceful shutdown via `asyncio.Event`.

## Executor

Three dispatch modes selected by the job definition:

1. **Built-in**. `executor` is a dotted Python import path (`zeus.kronos.jobs.newsletter.run_morning_digest`). Called directly with `params`.
2. **Agent**. `agent` field set to an olympian agent name. Executor calls `bus_call(target=agent, endpoint=..., payload=params, correlation_id=...)`. Reuses LAB-145 bus infrastructure.
3. **Shell**. `executor` prefixed with `shell:`. Gated by `ZEUS_KRONOS_SHELL_ENABLED` and a regex allowlist (`ZEUS_KRONOS_SHELL_ALLOWLIST`). Mirrors `olympian_shell` safety (LAB-349). Last resort.

Every execution, regardless of mode:

1. Create a `JobRun` row with `PENDING` status and a new correlation_id.
2. Run Aegis pre-hook on `params` via `evaluate_payload()` (LAB-343). Reject raises and records `FAILED`.
3. Dispatch under `asyncio.wait_for(..., timeout=job.timeout_seconds)`.
4. On success: run Aegis post-hook on `output_summary` before writing to memory.
5. Write `JobRun` with final status, duration, output, error.
6. On failure: retry up to `max_retries` with exponential backoff (0.5s, 1s, 2s). Reuse the `_is_transient_error` helper from `zeus/ingest/pipeline.py` (extract to `zeus/core/retry.py` per the backlog note).
7. Write summary via `zeus_remember(namespace=ZEUS_KRONOS_MEMORY_NAMESPACE)` (default `kronos_execution_log`). Keeps a queryable audit trail in memory.

## Safety

Every job execution passes through Aegis:

- Pre-hook validates `params` before dispatch.
- Post-hook filters any output before it lands in memory.
- Built-in tool allowlist per `JobCategory`. For example, `memory_review` jobs only get read-only tools.
- Shell executor double-gated: env flag plus regex allowlist.
- Per-job `safety_policy` maps to a policy file in `zeus/safety/policies/` (same registration as agents).
- Timeouts are hard kills; no open-ended runs.

## API surface

FastAPI router at `/kronos`, mounted in `zeus/core/main.py`. All write routes gated by `ZEUS_KRONOS_ALLOW_WRITE`.

```
GET    /kronos/jobs                    # list; filter by category, status, enabled, search
GET    /kronos/jobs/{job_id}           # single job + last 20 runs
POST   /kronos/jobs                    # create
PATCH  /kronos/jobs/{job_id}           # partial update
DELETE /kronos/jobs/{job_id}           # remove (soft by default; hard with ?hard=1)
POST   /kronos/jobs/{job_id}/run       # manual trigger, returns correlation_id
POST   /kronos/jobs/{job_id}/enable
POST   /kronos/jobs/{job_id}/disable
GET    /kronos/runs                    # recent runs across all jobs; filter by status, job_id, since
GET    /kronos/runs/{run_id}           # full run detail
GET    /kronos/schedule/upcoming       # next N jobs to fire, computed from croniter
GET    /kronos/health                  # scheduler tick count, last tick, error count, queue depth
GET    /kronos/executors               # list known built-in executors (for the frontend form)
GET    /kronos/categories              # enum values (for frontend dropdowns)
```

## Chat integration

Add an MCP tool in `zeus/mcp/tools.py`:

```python
@mcp.tool()
async def kronos_create_job(
    name: str,
    description: str,
    category: str,
    cron: str | None,
    run_at: str | None,           # ISO datetime for one-offs
    executor: str,
    params: dict,
    timezone: str = "UTC",
) -> dict:
    """Create a Kronos scheduled job. Proxies to POST /kronos/jobs."""
```

Gated by `ZEUS_MCP_ALLOW_WRITE` (same flag as existing write tools).

Update `zeus/core/prompts/chat_system.md` to surface the capability: when the user says "remind me", "every Friday", "schedule a", "each morning", etc., the model may call `kronos_create_job`. Keep examples sparse, let the capability speak for itself.

## Config file (seed jobs)

`zeus/data/kronos.yaml` loaded on first boot when the DB is empty. Subsequent boots honour DB state and ignore YAML changes (users edit via API or dashboard). YAML stays as a backup and for fresh environments.

Example shape:

```yaml
jobs:
  - id: daily-news-briefing
    name: Daily News Briefing
    description: Morning news digest, summarized and read aloud.
    category: briefing
    schedule:
      cron: "0 9 * * *"
      timezone: America/Los_Angeles
    executor: zeus.kronos.jobs.briefing.run_news_briefing
    params:
      sources: [hackernews, techcrunch]
      voice_output: true
    safety_policy: standard
    timeout_seconds: 300
    max_retries: 1
    tags: [news, morning]

  - id: weekly-memory-review
    name: Weekly Memory Review
    description: Surface patterns from the week's memory additions.
    category: memory_review
    schedule:
      cron: "0 18 * * 0"
      timezone: America/Los_Angeles
    executor: zeus.kronos.jobs.memory_review.run_weekly_review
    safety_policy: memory
    timeout_seconds: 600

  - id: nightly-knowledge-ingest
    name: Nightly Knowledge Ingest
    description: Re-run bulk knowledge ingest sources overnight.
    category: ingest
    schedule:
      cron: "0 2 * * *"
    agent: iris
    params:
      targets: [knowledge]
    timeout_seconds: 1800

  - id: newsletter-morning-digest
    name: Newsletter Morning Digest
    description: Replaces LAB-343 KAIROS newsletter observer.
    category: briefing
    schedule:
      cron: "0 7 * * *"
    executor: zeus.kronos.jobs.newsletter.run_morning_digest
    safety_policy: standard
```

## Migration of existing scheduled work

- **LAB-343 (Newsletter via KAIROS)**: moves to Kronos job `newsletter-morning-digest`. Kairos stays autonomous, no newsletter logic there.
- **LAB-341 newsletter manifest** (`zeus/data/newsletters/*.json`): Kronos becomes the scheduling source of truth. On first Kronos boot, if legacy manifest exists and no matching job is in DB, seed a Kronos job from it and mark the manifest deprecated. Keep the manifest readable for one release, then drop.
- **Ad-hoc ingest cron on the host**: fold into a Kronos job (`nightly-knowledge-ingest` above).

Kairos remains untouched. Both run as parallel lifespan tasks.

## Observability

- Extend `/admin/metrics` with Kronos section: total jobs, enabled count, runs in last 24h (success/failed), avg duration per category, overdue count.
- In-process ring buffer `app.state.kronos_recent_runs` (last 100 runs) for fast dashboard loads without hitting SQLite.
- Structured logs per run: INFO on start/success (with correlation_id), WARNING on retry, ERROR on final failure.
- `GET /kronos/health` exposes scheduler liveness (tick count, last tick age) so the dashboard can show a green/red indicator.

## Environment variables

```
ZEUS_KRONOS_ENABLED=1
ZEUS_KRONOS_DB_PATH=zeus/data/kronos.db
ZEUS_KRONOS_TICK_SECONDS=30
ZEUS_KRONOS_MAX_CONCURRENT=3
ZEUS_KRONOS_ALLOW_WRITE=1
ZEUS_KRONOS_SHELL_ENABLED=0
ZEUS_KRONOS_SHELL_ALLOWLIST=""
ZEUS_KRONOS_MEMORY_NAMESPACE=kronos_execution_log
```

Add to `.env.example` with brief comments. Default to `enabled=1` for dev, off by default on a fresh prod boot until jobs are reviewed.

## Dependencies on existing work

- **LAB-329** (session persistence): storage follows the same Protocol + SQLite pattern.
- **LAB-332** (TaskRunner): multi-step jobs can delegate to TaskRunner rather than implementing their own step loops.
- **LAB-326** (Aegis pre-hook): Kronos reuses `evaluate_payload()` before dispatch.
- **LAB-328** (olympian tool pack): agent-executed jobs rely on these tools.
- **LAB-343** (KAIROS newsletter): superseded; absorb and close.

## Linear ticket structure

**New Project 11: Kronos (Scheduler)**

Parent tickets:

- Kronos Core Scheduler: models, storage, `KronosScheduler` loop, lifespan wiring
- Kronos Executor: built-in, agent, shell dispatch modes with Aegis integration
- Kronos REST API: full `/kronos/*` surface, write gating, error shapes
- Built-in Job Library: briefing, ingest, memory-review, health-check, newsletter migration
- Chat Integration: `kronos_create_job` MCP tool, `chat_system.md` update
- Kronos Observability: admin metrics, ring buffer, `/kronos/health`
- Phase 2, Kronos Job-Search Bridge: forwards scraped listings to your external app via HTTP

## Phase 1 deliverable

Smallest working system:

1. Models, SQLite storage, scheduler loop, built-in executor with Aegis pre/post.
2. `GET /kronos/jobs`, `GET /kronos/runs`, `GET /kronos/jobs/{id}`, `POST /kronos/jobs/{id}/run`.
3. One real job wired end-to-end (newsletter morning digest migration).
4. Seed YAML with three jobs (newsletter, nightly ingest, weekly memory review).

Dashboard work can begin in parallel against this API contract.
