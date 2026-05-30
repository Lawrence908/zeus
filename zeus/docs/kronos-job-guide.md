# Kronos Job Guide

How to create a scheduled job in Zeus, what every field means, and which dispatch mode to pick. Use this as context when you (or an agent) construct a new job. Subsystem invariants and what-not-to-do live in [`../kronos/CLAUDE.md`](../kronos/CLAUDE.md); this doc is the user-facing companion.

## What a Kronos job is

A single declarative record (`JobDefinition` in `zeus/kronos/models.py`) describing **when** to fire and **what** to call. The scheduler ticks every `ZEUS_KRONOS_TICK_SECONDS` (default 30s), finds enabled jobs whose next fire time has passed, and dispatches them through the executor with Aegis hooks on input and output. Each execution writes a `JobRun` row with status, duration, output, and a correlation id.

Anything time-anchored in Zeus belongs here: morning briefings, nightly ingest, weekly memory reviews, daily news, one-off reminders. Free-form, agent-created, or hand-written.

## Three ways to create a job

All three paths land in the same DB row via `POST /kronos/jobs`. Pick by audience.

### 1. UI — the `/jobs` page

Click **+ New Job** in the header. Fill the form. Submit. Drawer opens on the new job. Best for human authoring.

Fields are explained below; the form auto-derives a slug-style `id` from the name and provides a cron preset dropdown plus a live next-5-fires preview.

Requires `ZEUS_KRONOS_ALLOW_WRITE=1`.

### 2. Chat — the `kronos_create_job` MCP tool

Tell Zeus "remind me", "every Friday at 5", "schedule a", "each morning". The model will call `kronos_create_job(name, cron|run_at, executor|agent, params, ...)`. See `zeus/mcp/tools.py` for the full signature.

Requires `ZEUS_MCP_ALLOW_WRITE=1` and (for the action runner family) `ZEUS_KRONOS_ALLOW_WRITE=1` server-side.

### 3. HTTP — `POST /kronos/jobs`

```bash
curl -X POST http://localhost:8203/kronos/jobs \
  -H 'Content-Type: application/json' \
  -d @job.json
```

Body is the full `JobDefinition` JSON. Returns 201 with the created row, 409 if the id already exists. Use this for scripts, CI, agents that aren't routed through MCP.

### Bonus — seed YAML

Edit `zeus/data/kronos.yaml` and restart `zeus-core`. The registry runs **insert-or-skip by id** on every boot, so existing jobs are never clobbered. Seed YAML is the right place for the canonical "this environment always wants these jobs" set; live edits should go through the API.

## JobDefinition fields

| Field | Required | Notes |
|-------|----------|-------|
| `id` | yes | Stable URL-safe slug. Locked after creation. The UI derives this from `name` if you don't pick one. |
| `name` | yes | Human-readable. |
| `description` | no | Free text. Shows in the UI drawer. |
| `category` | no | One of `briefing`, `ingest`, `memory_review`, `maintenance`, `research`, `job_search`, `health`, `custom`. Drives the colour badge and groups the timeline view. Default `custom`. |
| `schedule.cron` | one of | Standard 5- or 6-field cron. Required unless `run_at` is set. |
| `schedule.run_at` | one of | ISO datetime for one-off jobs. Job auto-disables after firing. Required unless `cron` is set. |
| `schedule.timezone` | no | IANA TZ name (`America/Los_Angeles`, `UTC`, …). Default `UTC`. Cron is interpreted in this TZ. |
| `executor` | one of | Dotted Python path for built-in mode (`zeus.kronos.jobs.x.y`) or `shell:<cmd>` for shell mode. Required unless `agent` is set. |
| `agent` | one of | Olympian agent name for agent-bus mode. Required unless `executor` is set. |
| `endpoint` | only with agent | Agent endpoint path. Default `/run`. Must be declared in the agent's YAML manifest. |
| `params` | no | Arbitrary JSON object passed to the executor. Validated against `safety_policy` by Aegis pre-hook. |
| `safety_policy` | no | Aegis policy name (matches a YAML in `zeus/safety/policies/`). Default `standard`. |
| `timeout_seconds` | no | Hard kill after this many seconds. Default 300. |
| `max_retries` | no | Retries on transient HTTP errors (Ollama blip, network reset). Default 1. |
| `tags` | no | Free-form list. Shown in the drawer. |
| `enabled` | no | Default true. Disabled jobs sit in the DB but never fire. |

Cross-field rules:
- Exactly one of `cron` / `run_at`.
- Exactly one of `executor` / `agent`.

## Picking a schedule

`croniter` 5-field cron, evaluated in the job's timezone. Quick reference:

```
"0 7 * * *"      Daily at 7:00
"0 */6 * * *"    Every 6 hours, on the hour
"*/15 * * * *"   Every 15 minutes
"0 9 * * 1-5"    Weekdays at 9:00
"0 18 * * 0"     Sundays at 18:00
"0 0 1 * *"      First of every month at 0:00
```

**Sub-minute precision is not supported.** Tick is 30s; a `* * * * *` cron fires somewhere in seconds 0–30 of each minute. If you need second-level precision, you're using the wrong tool.

**DST**: cron values that fall in the spring-forward gap (e.g. `30 2` on the day clocks jump from 02:00 to 03:00 local) fire once at 03:30 instead of being skipped. Don't rely on cron for transactions that must happen at exactly one wall-clock moment per day across DST boundaries.

For one-offs, `run_at` is an ISO 8601 datetime. The job disables itself after firing, so re-enabling it has no effect (delete and re-create instead).

## Picking a dispatch mode

### Built-in (recommended default)

`executor: zeus.kronos.jobs.<module>.<callable>`. The executor `importlib.import_module`s and awaits it with `params` as the single argument. Aegis pre-hook scans `params`; post-hook scans the output before it's written to the DB.

Available built-ins (see `zeus/kronos/jobs/`):

| Path | Purpose | Params |
|------|---------|--------|
| `zeus.kronos.jobs.newsletter.run_morning_digest` | Fetch newsletters, summarize via `small_llm_call` (tier-1), generate audio | `{ newsletter_type: "all" \| <type>, num_recent: 1..10 }` |
| `zeus.kronos.jobs.ingest.run_nightly_ingest` | Wrap `IngestPipeline.run_all_sources` for selected sources | `{ sources: ["markdown","obsidian", ...], incremental: true }` |
| `zeus.kronos.jobs.memory_review.run_weekly_review` | Group MemoryStore additions in the last N days by category and source | `{ days: 7, max_samples_per_category: 3, user_id: "user" }` |
| `zeus.kronos.jobs.health_check.run_service_health` | Probe configured services with httpx | `{ targets: { name: url, ... }, timeout_seconds: 5 }` |

Discover the live list by hitting `GET /kronos/executors` (the `JobForm` dropdown does this). Add a new built-in by dropping a module in `zeus/kronos/jobs/` exposing an `async def run_*(params: dict)`.

### Agent (via the bus)

`agent: <name>`, `endpoint: <path>`. The executor POSTs to `/orchestration/call` on the local bus, which forwards to the named agent. Agent must be RUNNING and must declare the endpoint in its YAML manifest under `zeus/orchestration/agents/<name>.yaml`. Aegis pre/post run on the bus side; the executor does not double-scan.

Use this when the work logically belongs to an existing olympian (e.g., have `iris` re-ingest a particular source).

### Shell (last resort)

`executor: shell:<command>`. Double-gated:

1. `ZEUS_KRONOS_SHELL_ENABLED=1`
2. `ZEUS_KRONOS_SHELL_ALLOWLIST` is a comma-separated list of regex patterns; the command must match at least one.

Hard kill on timeout. Aegis post-filter on stdout. **Test new allowlist patterns with a manual `POST /kronos/jobs/{id}/run` before letting them on the schedule** — `re.search` is used (anchored fullmatch is your responsibility) and a typo in the regex silently rejects everything.

## Recipes

### Daily morning briefing (built-in)

```json
{
  "id": "morning-news-briefing",
  "name": "Morning News Briefing",
  "description": "HN + tech newsletters, summarized and read aloud at 7am.",
  "category": "briefing",
  "schedule": { "cron": "0 7 * * *", "timezone": "America/Los_Angeles" },
  "executor": "zeus.kronos.jobs.newsletter.run_morning_digest",
  "params": { "newsletter_type": "all", "num_recent": 5 },
  "safety_policy": "standard",
  "timeout_seconds": 600,
  "max_retries": 1,
  "tags": ["news", "morning"]
}
```

### One-off reminder

```json
{
  "id": "remind-call-mom",
  "name": "Call Mom",
  "category": "custom",
  "schedule": { "run_at": "2026-04-26T17:00:00-07:00" },
  "executor": "zeus.kronos.jobs.health_check.run_service_health",
  "params": { "targets": { "self": "http://localhost:8203/health" } }
}
```

(There's no native "notify Chris" built-in yet; pair with `olympian_inbox_append` via an agent job for a real reminder, or build a `zeus.kronos.jobs.inbox.run_inbox_note` that calls `/inbox/append`.)

### Hourly service health probe

```json
{
  "id": "hourly-service-health",
  "name": "Hourly Service Health",
  "category": "health",
  "schedule": { "cron": "0 * * * *" },
  "executor": "zeus.kronos.jobs.health_check.run_service_health",
  "safety_policy": "standard",
  "timeout_seconds": 30
}
```

### Nightly ingest, knowledge sources only

```json
{
  "id": "nightly-knowledge-ingest",
  "name": "Nightly Knowledge Ingest",
  "category": "ingest",
  "schedule": { "cron": "0 2 * * *" },
  "executor": "zeus.kronos.jobs.ingest.run_nightly_ingest",
  "params": { "sources": ["markdown","obsidian","chatgpt","bookmarks","git"] },
  "safety_policy": "ingest",
  "timeout_seconds": 1800
}
```

### Agent-routed task

```json
{
  "id": "weekly-memory-prune",
  "name": "Weekly Memory Prune",
  "category": "memory_review",
  "schedule": { "cron": "0 3 * * 1" },
  "agent": "mnemosyne",
  "endpoint": "/maintenance/prune",
  "params": { "older_than_days": 365 },
  "safety_policy": "memory"
}
```

(Only works once `mnemosyne` ships an `/maintenance/prune` endpoint declared in its YAML.)

## What can go wrong

| Symptom | Cause | Fix |
|---------|-------|-----|
| Job created but never fires | Disabled, or `ZEUS_KRONOS_ENABLED=0` | Toggle the row, or set the env and restart `zeus-core` |
| `validation` error on create | Cross-field rule (cron+run_at, executor+agent) violated, or invalid cron | Read the response body; the form catches most of these client-side |
| Run shows `failed` with `aegis:` prefix | Aegis pre or post rejected the payload/output | Inspect `params`/output; loosen `safety_policy` or fix the data |
| Run shows `timeout` | Job exceeded `timeout_seconds` | Increase the timeout, or fix the slow path |
| Run shows `lost` after a restart | Scheduler crashed mid-execute; the orphan reaper marked the row | No action needed; the next scheduled tick will re-fire |
| Agent-mode run shows 503 in `error` | Target agent isn't RUNNING | Start it via `/orchestration/agents/<name>/action` |
| Shell job rejected | Command doesn't match `ZEUS_KRONOS_SHELL_ALLOWLIST` | Add a matching pattern; test with `POST /jobs/{id}/run` |
| Built-in import error in `error` | Bad dotted path or executor module not in container | Check `GET /kronos/executors` for the live list |

## Inspecting after the fact

| Where | What |
|-------|------|
| `/jobs` UI table | Per-job last-run badge + next-fire countdown |
| `/jobs` UI drawer History tab | Last 20 runs with expandable detail |
| `/jobs` UI Output tab | Full text of the latest run (with copy) |
| `/jobs` UI Timeline | Next-fires-by-category for the next 24h or 7d |
| `GET /kronos/runs?job_id=…` | Recent runs JSON |
| `GET /kronos/runs/{run_id}` | Single run with `correlation_id` |
| `GET /admin/metrics` → `kronos` block | Counts, by-status, by-category avg duration, overdue count |
| `sqlite3 zeus/data/kronos.db` | Source of truth for jobs + runs |

Every run carries a `correlation_id` (12-char hex) that's logged by both the scheduler and the executor. Grep logs by it to follow a single execution end-to-end.

## Quick env reference

| Env | Default | Purpose |
|-----|---------|---------|
| `ZEUS_KRONOS_ENABLED` | `0` | Master switch — start the scheduler in lifespan |
| `ZEUS_KRONOS_DB_PATH` | `zeus/data/kronos.db` | SQLite path |
| `ZEUS_KRONOS_TICK_SECONDS` | `30` | Scheduler tick |
| `ZEUS_KRONOS_MAX_CONCURRENT` | `3` | Semaphore for concurrent dispatched jobs |
| `ZEUS_KRONOS_ALLOW_WRITE` | `0` | Gate for POST/PATCH/DELETE on `/kronos/*` |
| `ZEUS_KRONOS_SHELL_ENABLED` | `0` | Shell-mode master switch |
| `ZEUS_KRONOS_SHELL_ALLOWLIST` | `""` | Shell-mode regex allowlist |
| `ZEUS_MCP_ALLOW_WRITE` | `0` | Gate the `kronos_create_job` MCP tool |

Backend design: [`../../docs/kronos-backend-plan.md`](../../docs/kronos-backend-plan.md). Frontend design: [`../../docs/kronos-frontend-plan.md`](../../docs/kronos-frontend-plan.md). Subsystem invariants: [`../kronos/CLAUDE.md`](../kronos/CLAUDE.md). Catalog of *what* to schedule (tools each needs, what to build): [`../../docs/kronos-job-catalog.md`](../../docs/kronos-job-catalog.md).
