# zeus/kronos/ — Scheduler subsystem

Deterministic, cron-driven scheduler and job executor. Owns anything time-based in Zeus: newsletter digests, nightly ingest, weekly memory reviews, daily briefings, and any user-created recurring job. The "measured time" sibling to Kairos's autonomous "opportune moment" daemon — they run as parallel lifespan tasks.

Root brief: [`../../CLAUDE.md`](../../CLAUDE.md). Full design: [`../../docs/kronos-backend-plan.md`](../../docs/kronos-backend-plan.md). User-facing job-author guide: [`../docs/kronos-job-guide.md`](../docs/kronos-job-guide.md).

## Layout

| File | Role |
|------|------|
| `models.py` | `JobStatus`, `JobCategory`, `JobSchedule`, `JobDefinition`, `JobRun` (Pydantic v2) |
| `storage.py` | `JobStorage` Protocol + `SQLiteJobStorage` (stdlib sqlite3 + `asyncio.to_thread`, no new deps) |
| `registry.py` | `KronosRegistry`: CRUD over storage + idempotent YAML seed |
| `executor.py` | `KronosExecutor`: built-in / agent dispatch, Aegis pre/post, timeout, retry |
| `scheduler.py` | `KronosScheduler`: asyncio tick loop, croniter next-fire, concurrency cap |
| `api.py` | `/kronos/*` FastAPI router |
| `jobs/` | Built-in job implementations (`newsletter.py`, etc.) |

Data: `zeus/data/kronos.db` (jobs + job_runs), `zeus/data/kronos.yaml` (seed).

## Invariants

- **Every execution passes through Aegis.** Built-in-mode executor runs `AegisPolicyEngine(policy=job.safety_policy).evaluate_payload(job.params)` pre-dispatch and `evaluate_text(output_summary)` post-dispatch. Agent-mode dispatches through `/orchestration/call`, which already applies pre/post hooks — executor does **not** re-scan to avoid double-filtering.
- **Atomic fire-intent + last_fired_at.** The scheduler INSERTs a `PENDING` `JobRun` and UPDATEs `jobs.last_fired_at` in the same transaction, before dispatching. A mid-execute crash leaves a `PENDING` row; on boot, `reap_orphans()` marks stale `PENDING`/`RUNNING` runs as `LOST` and resumes scheduling. This supersedes the spec's plain "set last_fired_at before dispatch".
- **Timeouts are hard.** Every dispatch wraps in `asyncio.wait_for(..., timeout=job.timeout_seconds)`. No open-ended runs.
- **Retry on transient HTTP only.** Uses `zeus.core.retry.is_transient_http_error` (extracted from `zeus/ingest/pipeline.py`). Exponential backoff (0.5s, 1s, 2s), cap at `job.max_retries`.
- **YAML seed is insert-or-skip by id.** On every boot, missing ids from `kronos.yaml` are inserted; existing ids are left alone. Users edit live jobs via the API; the YAML is the fresh-environment fallback.
- **One-off jobs auto-disable after firing.** `JobSchedule.run_at` (ISO datetime) fires once, then the scheduler flips `enabled=False` on the row.
- **Correlation IDs are mandatory.** Generated on every run (uuid4 hex[:12]); every log line carries it. Same shape as the bus.

## Env flags

| Env | Default | Effect |
|-----|---------|--------|
| `ZEUS_KRONOS_ENABLED` | `0` | Start the scheduler in FastAPI lifespan. Off by default; flip to `1` per environment once seed jobs are reviewed. |
| `ZEUS_KRONOS_DB_PATH` | `zeus/data/kronos.db` | SQLite file path |
| `ZEUS_KRONOS_TICK_SECONDS` | `30` | Scheduler tick interval. Sub-minute cron precision is not supported. |
| `ZEUS_KRONOS_MAX_CONCURRENT` | `3` | Semaphore size for concurrent dispatched jobs |
| `ZEUS_KRONOS_ALLOW_WRITE` | `0` | Gate POST/PATCH/DELETE routes on `/kronos/*` |
| `ZEUS_KRONOS_SHELL_ENABLED` | `0` | Shell executor mode (Phase 3, not implemented yet) |
| `ZEUS_KRONOS_SHELL_ALLOWLIST` | `""` | Regex allowlist for shell-mode commands |
| `ZEUS_KRONOS_MEMORY_NAMESPACE` | `kronos_execution_log` | Namespace for audit-trail writes via `zeus_remember` |

## Executor dispatch modes

| Mode | Job field | Behaviour |
|------|-----------|-----------|
| Built-in | `executor: zeus.kronos.jobs.<module>.<fn>` | `importlib` + await. Aegis pre/post run in-executor. |
| Agent | `agent: <name>` | HTTP POST to `/orchestration/call` on the local bus; target agent + endpoint in `params`. Bus runs Aegis pre/post. |
| Shell | `executor: shell:<cmd>` | Double-gated by `ZEUS_KRONOS_SHELL_ENABLED=1` + non-empty `ZEUS_KRONOS_SHELL_ALLOWLIST` (comma-separated regex). Hard-killed on timeout. Aegis post-filter on stdout. |

## What not to do

- Don't call `_internal_bus_call` from the scheduler. The scheduler runs outside a FastAPI request; use `app.state.http_client` to POST `/orchestration/call` instead.
- Don't widen `ZEUS_KRONOS_SHELL_ALLOWLIST` without an Aegis policy review note in the PR.
- Don't bypass the PENDING-run write. It's the only mechanism that recovers a crashed scheduler.
- Don't switch from `asyncio.sleep` to `await stop_event.wait_for(...)` — the scheduler uses the latter specifically so shutdown is instant; don't regress it.
- Don't duplicate the newsletter router logic in `jobs/newsletter.py`. Import the helpers (`_summarize_newsletters`, `_generate_audio`) directly.
- Don't replace croniter with APScheduler. APScheduler stays for the legacy ingest job until that migrates; Kronos wants the "next fire time given last_fired_at" semantics croniter provides directly.
