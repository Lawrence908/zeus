# Kronos Job Catalog

A brainstorm of useful scheduled jobs for this Zeus deployment, with the tools each one needs, what's already wired, and what to build next. Use this as a planning surface - pick a job, follow the references, ship it.

Companions:
- How to author a job: [`../zeus/docs/kronos-job-guide.md`](../zeus/docs/kronos-job-guide.md)
- Subsystem invariants: [`../zeus/kronos/CLAUDE.md`](../zeus/kronos/CLAUDE.md)
- Tool catalogs: [`../zeus/core/tools/`](../zeus/core/tools/) (chat-path), [`../zeus/mcp/tools.py`](../zeus/mcp/tools.py) (MCP)

## Tool inventory (current state)

What's already built:

| Tool | Surface | Read/Write | Notes |
|------|---------|-----------|-------|
| `current_time` | chat | R | UTC + local timestamp |
| `server_health` | chat + MCP (`olympian_server_health`) | R | `/admin/system` |
| `status_read` | chat + MCP | R | `~/.zeus/status.md` |
| `file_read` | chat + MCP | R | Allowlist-rooted vault read |
| `file_search` | chat + MCP | R | ripgrep over allowlist |
| `web_search` | chat | R | Configured-only |
| `calendar_today` | chat + MCP (`zeus_calendar_today`) | R | Today's gcal events |
| `newsletter_latest` | chat + MCP (`zeus_newsletter_latest`) | R | Most recent digest |
| `inbox_append` | chat + MCP (`olympian_inbox_append`) | W | One-line note to inbox.md |
| `action_run` / `action_list` | chat + MCP (`olympian_action_run/list`) | W | Allowlisted shell scripts |
| `zeus_query` | MCP | R | RAG over all four context layers |
| `zeus_profile` | MCP | R | Curated profile facts |
| `zeus_memory_search` | MCP | R | Vector search over memories |
| `zeus_remember` | MCP | W | Add to MemoryStore |
| `zeus_ingest_trigger` | MCP | W | Run a single Iris source |
| `kronos_create_job` | MCP | W | Self-scheduling |

Built-in Kronos executors (in `zeus/kronos/jobs/`):

| Path | Status |
|------|--------|
| `newsletter.run_morning_digest` | Live |
| `health_check.run_service_health` | Live |
| `ingest.run_nightly_ingest` | Wraps `IngestPipeline.run_all_sources`; works as soon as source env is set |
| `memory_review.run_weekly_review` | Live (Qdrant scroll, no LLM) |

## How to read each job spec

Each entry below has the same shape:

> **`<id>`** - one-line purpose
> **When**: cron + tz · **Mode**: built-in / agent / shell · **Executor**: dotted path
> **Tools**: what it uses (or would use)
> **Build status**: ✅ ship now / 🟡 needs new built-in / 🔴 needs new tool
> **Notes**: trade-offs, prereqs

---

## 1. Daily routines

### `morning-news-briefing` - composite morning digest

**When**: `0 7 * * *` America/Los_Angeles · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.briefing.run_morning_briefing` (new)
**Tools used**: `zeus_newsletter_latest`, `zeus_calendar_today`, `olympian_inbox_append`, `small_llm_call`
**Build status**: 🟡 new built-in; composes existing tools
**Notes**: pulls latest newsletter digest + today's calendar + last 24h inbox additions; runs `small_llm_call(min_privacy_tier=1)` to write a 5-bullet daily brief; appends to `~/.zeus/status.md` so the chat tool `status_read` surfaces it. Optional: also push to Telegram (needs new tool below).

### `evening-recap` - what happened today

**When**: `30 21 * * *` America/Los_Angeles · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.briefing.run_evening_recap` (new)
**Tools used**: git log (new tool), `zeus_memory_search`, `olympian_inbox_append`
**Build status**: 🟡 new built-in + 🔴 new `zeus_git_recent` tool
**Notes**: counts commits + summarises memory adds + lists tomorrow's first three calendar events. Output → inbox so morning-you sees it.

### `monday-week-ahead` - Monday morning planning

**When**: `0 8 * * 1` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.briefing.run_week_ahead` (new)
**Tools used**: `zeus_calendar_today` (extended to range, see new tools), `zeus_query` for project context
**Build status**: 🟡 new built-in + 🔴 needs `zeus_calendar_range(days)`
**Notes**: full week calendar + open task themes. Could chain into `kronos_create_job` to schedule one-off prep jobs for big meetings.

### `daily-intention` - morning prompt

**When**: `0 7 * * *` (right after briefing) · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.notify.run_intention_prompt` (new, tiny)
**Tools used**: `olympian_inbox_append`
**Build status**: 🟡 new built-in (~20 LOC)
**Notes**: appends "Today's intention: __" template line to inbox; meant to be filled in by hand.

---

## 2. Memory hygiene

### `weekly-memory-review` - already shipped (stub-grade)

**When**: `0 18 * * 0` · **Mode**: built-in · **Executor**: `zeus.kronos.jobs.memory_review.run_weekly_review`
**Build status**: ✅ live
**Upgrade idea**: chain into `small_llm_call` (tier 1) to synthesize a weekly narrative from the category groups, then `zeus_remember(namespace="weekly_review")` so the next week's memory-review can spot trends.

### `memory-drift-check` - flag contradictions

**When**: `0 4 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.memory_review.run_drift_check` (new)
**Tools used**: direct `MemoryStore` access (Qdrant scroll); `small_llm_call` to compare candidate-pair facts
**Build status**: 🟡 new built-in
**Notes**: scans facts added in the last 7 days against existing high-confidence facts in the same category, looks for contradictions ("user lives in X" vs "user lives in Y"), and writes a flagged-pairs report to `kronos_execution_log` namespace. Caller decides what to do; this is observation, not action.

### `stale-memory-audit` - surface expired facts

**When**: `0 3 * * 1` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.memory_review.run_stale_audit` (new)
**Tools used**: Qdrant scroll filtered by `valid_until <= now`
**Build status**: 🟡 new built-in
**Notes**: lists facts whose `valid_until` has passed but are still in the collection. Doesn't delete (that's irreversible) - appends list to inbox for review.

### `pii-audit` - count PII-bearing facts

**When**: `0 4 * * 0` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.memory_review.run_pii_audit` (new)
**Tools used**: Qdrant scroll filtered by `contains_pii=true`
**Build status**: 🟡 new built-in
**Notes**: weekly PII census; sanity check that PII facts aren't accidentally being widened. Output to inbox.

---

## 3. Ingest & library

### `nightly-knowledge-ingest` - already seeded

**When**: `0 2 * * *` · **Mode**: built-in · **Executor**: `zeus.kronos.jobs.ingest.run_nightly_ingest`
**Build status**: ✅ wires through `IngestPipeline.run_all_sources`; activate by enabling the seed job.

### `obsidian-livesync-watcher` - re-ingest changed notes

**When**: `*/30 * * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.ingest.run_obsidian_recent` (new)
**Tools used**: filesystem (find files modified in last 30 min); `IngestPipeline` for just those files
**Build status**: 🟡 new built-in (or run as `zeus_ingest_trigger(source="obsidian")` via the existing endpoint)
**Notes**: cheaper than the nightly bulk run for a constantly-edited vault. Requires `OBSIDIAN_VAULT_PATH`.

### `bookmark-fetch-and-ingest` - fetch new bookmarked URLs

**When**: `0 3 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.bookmarks.run_fetch_recent` (new)
**Tools used**: bookmarks export reader, web fetch (new tool), `KnowledgeStore.add_chunks`
**Build status**: 🔴 needs `zeus_web_fetch(url)` tool + 🟡 new built-in
**Notes**: bookmarks source currently reads URL + title only. Adding fetched-page-text to the knowledge layer makes RAG over bookmarks actually useful.

### `git-commit-ingest` - capture recent commits

**When**: `0 */6 * * *` · **Mode**: agent
**Agent**: `iris` · **Endpoint**: `/iris/ingest` (already declared in `iris.yaml`, needs a real route)
**Params**: `{ source: "git", since: "6h" }`
**Build status**: 🟡 needs `/iris/ingest` actually wired in `zeus/orchestration/bus.py` or a built-in wrapper that calls the existing CLI path
**Notes**: keeps the knowledge layer current with the codebase narrative.

### `newsletter-imap-poll` - only digest when new mail arrives

**When**: `0 */2 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.newsletter.run_poll_then_digest` (new)
**Tools used**: existing `NewsletterSource.fetch_newsletters_raw`, then `kronos_create_job` (or direct call) to fire `run_morning_digest` only if new newsletters
**Build status**: 🟡 new built-in (small)
**Notes**: avoids the daily 7am digest summarising the same TLDR twice. Better signal-to-noise.

---

## 4. Health & observability

### `hourly-service-health` - already seeded

**When**: `0 * * * *` · **Mode**: built-in · **Executor**: `zeus.kronos.jobs.health_check.run_service_health`
**Build status**: ✅ live; extend `params.targets` to add voicebox + whisper.

### `disk-space-monitor` - warn before disk fills

**When**: `0 */4 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.disk_check.run_disk_audit` (new)
**Tools used**: `shutil.disk_usage()`; `olympian_inbox_append` if any mount > threshold
**Build status**: 🟡 new built-in (~30 LOC)
**Notes**: cap at /, /home, and `zeus/data` usage. Threshold from params.

### `qdrant-collection-stats` - track growth

**When**: `0 5 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.health_check.run_qdrant_stats` (new)
**Tools used**: `MemoryStore._client` reach-through (same admin pattern as `/admin/ingest/stats`)
**Build status**: 🟡 new built-in
**Notes**: writes daily {memories_count, knowledge_count, vectors_count} to `kronos_execution_log` namespace; growth curve queryable via `zeus_memory_search`.

### `kronos-overdue-alarm` - meta-watchdog

**When**: `*/30 * * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.health_check.run_kronos_overdue` (new)
**Tools used**: `GET /admin/metrics` `kronos.overdue` field; `olympian_inbox_append` if nonzero
**Build status**: 🟡 new built-in (tiny)
**Notes**: Kronos watching itself. Cheap insurance.

### `small-llm-cost-summary` - daily spend tally

**When**: `0 23 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.small_llm.run_cost_summary` (new)
**Tools used**: read `zeus/data/small_llm_usage.db`, group by provider for the day, append to inbox
**Build status**: 🟡 new built-in + 🔴 optional `zeus_small_llm_usage(period)` MCP tool for chat queries
**Notes**: surfaces overrun risk before the next-day cap kicks in. Trivial since the DB schema is already there.

### `model-benchmark-refresh` - keep tok/s data current

**When**: `0 4 * * 0` · **Mode**: shell (one-shot CLI)
**Executor**: `shell:python -m zeus.bench`
**Build status**: ✅ shell mode ships; needs `ZEUS_KRONOS_SHELL_ALLOWLIST` to include `^python -m zeus\\.bench$`
**Notes**: refreshes `zeus/data/benchmarks.json` so the Settings UI graphs stay accurate after model swaps.

---

## 5. Calendar & meetings

### `daily-calendar-brief` - morning calendar push

**When**: `30 7 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.calendar.run_daily_brief` (new)
**Tools used**: `zeus_calendar_today`, `olympian_inbox_append`
**Build status**: 🟡 new built-in (small)
**Notes**: trivial wrapper; explicit so it's queryable from the dashboard.

### `meeting-prep-15` - 15min-before-meeting context pull

**When**: dynamic, scheduled by another job · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.calendar.run_meeting_prep` (new)
**Tools used**: `zeus_query` to RAG against the meeting title + attendees
**Build status**: 🔴 needs `zeus_calendar_next_meeting(within_minutes)` tool + 🟡 new built-in + a parent job that scans gcal hourly and `kronos_create_job`s a one-off `run_at` for 15min before each meeting
**Notes**: most ambitious entry on this list - chains four pieces. Probably best deferred until other jobs are stable.

### `weekly-calendar-review` - Sunday evening look-ahead

**When**: `0 19 * * 0` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.calendar.run_weekly_review` (new)
**Tools used**: extended calendar tool (range), `small_llm_call` for narrative
**Build status**: 🔴 needs `zeus_calendar_range` + 🟡 new built-in

---

## 6. Notifications & inbox flow

### `telegram-good-morning` - push briefing to phone

**When**: `5 7 * * *` (just after morning briefing) · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.notify.send_telegram` (new)
**Tools used**: 🔴 new `zeus_telegram_send(text, chat_id?)` tool
**Build status**: 🔴 needs the tool first (Telegram bot exists, just no MCP/chat tool wraps it)
**Notes**: piggybacks on existing `zeus/integrations/telegram/bot.py` - add a thin send wrapper, register as both chat-path tool and MCP tool, then job fires it with the morning brief text.

### `inbox-watcher` - turn "remind me" notes into one-off jobs

**When**: `*/15 * * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.inbox.run_remind_parser` (new)
**Tools used**: read `~/.zeus/inbox.md`, regex/LLM-extract reminder lines, `kronos_create_job` for each
**Build status**: 🟡 new built-in (medium)
**Notes**: lets you write "remind me 2026-04-30 14:00 buy birthday cake" into your inbox and have Kronos auto-schedule it. Mark processed lines with a checkmark to avoid re-firing.

### `birthday-watcher` - surface upcoming birthdays from contacts

**When**: `0 6 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.notify.run_birthday_check` (new)
**Tools used**: contacts source (doesn't exist yet) or gcal birthday calendar via `zeus_calendar_range(7)`
**Build status**: 🔴 needs calendar range tool, possibly contacts ingest source
**Notes**: low priority; nice if other calendar work lands.

---

## 7. Web / external watchers

### `hn-top-fetch` - daily Hacker News top stories

**When**: `0 8 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.watchers.run_hn_top` (new)
**Tools used**: 🔴 `zeus_web_fetch(url)` (new), `KnowledgeStore.add_chunks`
**Build status**: 🔴 needs web fetch tool + 🟡 new built-in
**Notes**: hits the HN Algolia API, fetches top 30 story titles + scores. No need for full-text initially.

### `arxiv-keyword-watch` - academic feed

**When**: `0 9 * * 1` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.watchers.run_arxiv` (new)
**Tools used**: arxiv API (httpx), `KnowledgeStore.add_chunks`
**Build status**: 🟡 new built-in (no new tool - direct httpx)
**Notes**: keywords from `params.keywords`; one source of fresh research material.

### `cloudflare-uptime-check` - public-site availability

**When**: `*/10 * * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.health_check.run_uptime_check` (new) - or extend `run_service_health` with external URLs
**Build status**: ✅ trivially handled by extending `run_service_health` params with `{ "zeus.chrislawrence.ca": "https://zeus.chrislawrence.ca/health" }`
**Notes**: don't even need a new built-in if the existing health check is parameterised correctly.

### `github-starred-fetch` - weekly recap of new starred repos

**When**: `0 10 * * 0` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.watchers.run_github_starred` (new)
**Tools used**: GitHub API (httpx), `KnowledgeStore.add_chunks`
**Build status**: 🟡 new built-in (needs `GITHUB_TOKEN` env)

---

## 8. Code & dev workflows

### `daily-commit-narrative` - yesterday's commits as a paragraph

**When**: `0 9 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.code.run_commit_narrative` (new)
**Tools used**: 🔴 `zeus_git_recent(since_hours)` tool, `small_llm_call` (tier 1)
**Build status**: 🔴 needs git tool + 🟡 new built-in
**Notes**: writes "yesterday I committed X across Y repos: {narrative}" to inbox. Good for offloading tracking from your head.

### `outdated-deps-scan` - weekly Python dep check

**When**: `0 11 * * 1` · **Mode**: shell
**Executor**: `shell:pip list --outdated --format=json`
**Tools used**: shell mode + Aegis post-filter
**Build status**: ✅ shell mode ships; allowlist `^pip list `
**Notes**: writes the JSON to a file; companion built-in could parse it and alert on major bumps.

### `todo-fixme-scan` - weekly repo audit

**When**: `0 12 * * 1` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.code.run_todo_scan` (new)
**Tools used**: `olympian_file_search` (already has ripgrep)
**Build status**: 🟡 new built-in (small) - search for `TODO|FIXME|XXX`, count by file, tally.

---

## 9. AI / LLM ops

### `provider-chain-probe` - verify small_llm fallback works

**When**: `0 6 * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.small_llm.run_chain_probe` (new)
**Tools used**: directly calls `small_llm_call` with a trivial prompt against each provider individually
**Build status**: 🟡 new built-in
**Notes**: catches "OpenRouter changed their auth" before it hits a real digest. Result → inbox if any provider fails.

### `ollama-warm-up` - keep model resident in VRAM

**When**: `*/15 * * * *` · **Mode**: built-in
**Executor**: `zeus.kronos.jobs.small_llm.run_ollama_warmup` (new)
**Tools used**: httpx → `/api/generate` with single token
**Build status**: 🟡 new built-in (trivial)
**Notes**: only on prod; voice latency suffers when Ollama unloads the chat model. Cheap enough to fire frequently.

---

## 10. Voice & Phaos

### `voice-pipeline-health` - TTS + STT probes

**When**: `*/15 * * * *` · **Mode**: built-in
**Executor**: extend `run_service_health` with `{ "voicebox": "${VOICEBOX_URL}/health", "whisper": "http://localhost:9090/health" }`
**Build status**: ✅ pure config; no new code.

---

## New tools to build (consolidated)

If you only build a few, build these - they unlock the most jobs:

| Tool | Surface | Effort | Unlocks |
|------|---------|--------|---------|
| `zeus_web_fetch(url, max_chars=10000)` | chat + MCP | small (httpx + readability/trafilatura) | bookmark fetch, HN watcher, arxiv watcher, ad-hoc URL grabs in chat |
| `zeus_telegram_send(text, chat_id?)` | chat + MCP | tiny (existing bot already has connection) | morning briefing push, any notification job, drift alerts |
| `zeus_calendar_range(days_ahead=7)` | chat + MCP | tiny (extend existing endpoint) | week ahead, meeting prep, birthday watcher |
| `zeus_calendar_next_meeting(within_minutes=30)` | chat + MCP | tiny | meeting prep job, "what's next?" voice query |
| `zeus_git_recent(since_hours=24, repo_path=".")` | chat + MCP | small (gitpython already a dep) | daily commit narrative, evening recap, code workflow jobs |
| `zeus_disk_usage(paths=["/", "/home", "zeus/data"])` | chat + MCP | tiny (`shutil.disk_usage`) | disk monitor job |
| `zeus_small_llm_usage(period="today")` | chat + MCP | small (read `small_llm_usage.db`) | cost summary job; queryable in chat ("how much did I spend today?") |

Each would be a chat-path `ToolSpec` in `zeus/core/tools/<name>.py` mirrored as an MCP wrapper in `zeus/mcp/tools.py` (same dual-registration pattern as `inbox_append`, `calendar_today`, etc.).

## New built-in jobs to build (consolidated)

By module path, in priority order:

```
zeus/kronos/jobs/
  briefing.py
    run_morning_briefing       # composite (newsletter + calendar + inbox)
    run_evening_recap          # commits + memory + tomorrow's calendar
    run_week_ahead             # Monday week-ahead summary

  notify.py
    send_telegram              # generic Telegram push (needs the new tool)
    run_intention_prompt       # morning intention template

  calendar.py
    run_daily_brief
    run_weekly_review
    run_meeting_prep           # parameterised; one-offs scheduled by another job

  inbox.py
    run_remind_parser          # parse "remind me ..." lines into kronos one-offs

  code.py
    run_commit_narrative
    run_todo_scan

  watchers.py
    run_hn_top
    run_arxiv
    run_github_starred

  small_llm.py
    run_cost_summary
    run_chain_probe
    run_ollama_warmup

  disk_check.py
    run_disk_audit

  memory_review.py    # extend existing module
    run_drift_check
    run_stale_audit
    run_pii_audit

  health_check.py     # extend existing module
    run_kronos_overdue
    run_qdrant_stats
```

## Recommended build order (highest leverage first)

1. **`zeus_telegram_send`** + **`send_telegram`** - every notification job depends on this; one MCP tool unlocks five jobs.
2. **`zeus_web_fetch`** + **`bookmarks.run_fetch_recent`** + **`watchers.run_hn_top`** - three useful jobs, one tool.
3. **`zeus_calendar_range`** + **`calendar.run_daily_brief`** + **`calendar.run_weekly_review`** - calendar surface stays useful for chat too.
4. **`small_llm.run_cost_summary`** + **`small_llm.run_chain_probe`** - operational hygiene; 0 new tools.
5. **`disk_check.run_disk_audit`** + **`health_check.run_kronos_overdue`** - cheap insurance; 0 new tools.
6. **`briefing.run_morning_briefing`** - payoff job; needs items 1 + 3 first.
7. **`memory_review.run_drift_check`** - once the trivial weekly review proves itself.

After (1)–(7), most of the other entries become 30–50 LOC each.

## Things to avoid

- **Don't schedule jobs that themselves call `_run_llm` (chat path).** Use `small_llm_call(min_privacy_tier=1)` instead - keeps the chat LLM free for the user during cron-driven work. The newsletter swap (Phase 2) is the precedent.
- **Don't widen `ZEUS_KRONOS_SHELL_ALLOWLIST` casually.** Each entry is a regex; a typo silently rejects everything (or, worse, allows more than you intended). Test with a manual `POST /kronos/jobs/{id}/run` before letting any new pattern on the schedule.
- **Don't write to memory from a job without going through Aegis.** All built-ins already pass through the executor's pre/post hooks, but if you reach for `MemoryStore` directly from a job, you bypass the post-hook. Use `zeus_remember` (HTTP) which goes through the chat-path safety stack.
- **Don't fan out a single cron tick to many subprocesses.** `ZEUS_KRONOS_MAX_CONCURRENT` defaults to 3; if a job kicks off five sub-jobs via `kronos_create_job`, you'll queue them across ticks. Acceptable, just don't be surprised by the cadence.
- **Don't rely on sub-minute cron precision.** Tick floor is 30s. Anything tighter belongs in a real event loop, not Kronos.
