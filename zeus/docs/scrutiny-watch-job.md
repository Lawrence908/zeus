# Daily Scrutiny Watch (Kronos job)

**Status: live (enabled 2026-07-26 after end-to-end validation).** The always-on funnel
under the weekly [Congressional Scrutiny Brief](congressional-scrutiny-job.md).
Every morning it *catches* fresh CapitolScope scrutiny + herding-cluster signals,
*triages* which are genuinely new or intensifying, and *escalates* only the
standouts into real multi-agent `deep_research` runs for web verification.

- Executor: `zeus.kronos.jobs.scrutiny_watch.run_scrutiny_watch`
- Output: `zeus/data/briefings/YYYY-MM-DD-scrutiny-watch.md` (override `ZEUS_BRIEFINGS_DIR`)
- Persistence: `zeus/data/scrutiny_watch.db` (override `ZEUS_SCRUTINY_WATCH_DB`)

## How it differs from the weekly brief

| | Weekly brief (`congressional_scrutiny`) | Daily watch (`scrutiny_watch`) |
|---|---|---|
| Cadence | Monday | Every morning |
| Output | Human-readable narrative assessment | Triage + escalation log |
| LLM | One synthesis call | One structured triage call |
| Persistence | none (stateless) | `scrutiny_watch.db` dedup + cooldown |
| Web research | headline news digest only | spawns full `deep_research` on standouts |

Run both: the brief is what you read on Monday; the watch is what keeps the
interesting signals from slipping past mid-week and turns the best ones into
verified research automatically.

## Pipeline

1. `capitolscope_context_pack(days)` - the week's activity + deltas.
2. `_build_candidates()` flattens it into fingerprinted signals:
   - `cluster:<ticker>:<direction>:<window_start>` (herding clusters)
   - `member:<member>` (top scrutiny movers)
   - `newticker:<ticker>` (newly-active tickers)
3. **Dedup** against `scrutiny_watch.db`: upsert every candidate, keep the set
   that is *new this cycle*. By default (`only_new=true`) only new signals are
   triaged, so the same cluster is never re-worked day after day.
4. **Triage** - one `small_llm_call` with a structured `TriageResult` schema
   scores each new signal 0-10 for research-worth and returns a hypothesis, a
   confirm/refute test, and a concrete `deep_research` topic sentence.
5. **Escalate** - for items with `score >= escalate_threshold` (and not in
   cooldown), up to `max_escalations`, POST a one-off `deep_research` Kronos job
   (`run_at` ~now) exactly like the chat tool. This decouples the heavy research
   run from the watch job's short timeout - each runs under its own. The job id +
   expected report path are recorded in the db and the brief. Everything below
   the bar is *flagged* with a ready-to-run topic.
6. Write the watch brief to disk; best-effort inbox + knowledge writeback
   (`source="scrutiny_watch"`), mirroring the brief job.

## Params

| Param | Default | Effect |
|---|---|---|
| `days` | `7` | context-pack window |
| `escalate_threshold` | `8` | triage score at/above which `deep_research` auto-fires |
| `max_escalations` | `2` | hard cap on research runs per cycle (cost guard) |
| `max_candidates` | `12` | cap on signals sent to triage |
| `cooldown_days` | `14` | don't re-escalate the same fingerprint within N days |
| `depth` | `standard` | `deep_research` depth for escalations (`quick`/`standard`/`deep`) |
| `only_new` | `true` | triage only signals unseen before this run |
| `providers` | `[ollama]` | hard-pin the small_llm chain (keeps triage local/free); `null` = `DEFAULT_CHAIN` |
| `model_hint` | `ollama` | model within the pinned provider |

> **Local by default.** Triage is pinned to Ollama via `providers=["ollama"]`, so
> the daily cron spends nothing from the `$2/day` small-LLM cap. `model_hint`
> alone is *not* enough - it only selects the model within whichever provider the
> default chain reaches first (anthropic, in this env), which is why the pin
> exists. Set `providers: null` to fall back to `DEFAULT_CHAIN` if you want a
> stronger model (congressional data is public, so tier-2 is acceptable).

## Environment

Reuses the CapitolScope MCP env:

```
CAPITOLSCOPE_SIGNALS_URL=https://capitolscope.chrislawrence.ca   # or http://localhost:8120 on-host
CAPITOLSCOPE_SIGNALS_KEY=<the signals key>
```

Escalation POSTs a job to `/kronos/jobs`, so the server needs:

```
ZEUS_KRONOS_ALLOW_WRITE=1     # else escalations are flagged, not spawned
```

Optional: `ZEUS_BRIEFINGS_DIR`, `ZEUS_SCRUTINY_WATCH_DB`,
`ZEUS_DEEP_RESEARCH_DIR`, `TAVILY_API_KEY`/`BRAVE_API_KEY` (used by the spawned
`deep_research` runs, not this job directly).

> **Deployment gotcha (daedalus / any bind-mounted deploy).** In the container,
> `/app/zeus` is bind-mounted **read-only** (dev hot-edit) and the code's default
> output paths (`/home/chris/zeus/docs/...`, and the watch DB) resolve to
> **ephemeral container-internal** dirs. Only `/app/zeus/data` (rw, = host
> `zeus/zeus/data`, gitignored) survives container recreation. `compose.yaml`
> therefore sets, on `zeus-core`:
> ```
> ZEUS_BRIEFINGS_DIR=/app/zeus/data/briefings
> ZEUS_DEEP_RESEARCH_DIR=/app/zeus/data/research
> ZEUS_SCRUTINY_WATCH_DB=/app/zeus/data/scrutiny_watch.db
> ```
> The watch DB default is now **relative** (`zeus/data/scrutiny_watch.db`) so it
> lands on the writable mount even without the env override. The knowledge-store
> ingest is durable regardless of these paths. Restart `zeus-core` after editing
> `small_llm.py`/job code - the server runs without `--reload`.

## Enable / disable

Seeded **enabled** in `zeus/data/kronos.yaml` (fires `0 8 * * *`
America/Los_Angeles). To re-validate or toggle:

```bash
# 1. Manual run (via the API, once zeus-core is up with ZEUS_KRONOS_ENABLED=1):
curl -X POST localhost:8203/kronos/jobs/daily-scrutiny-watch/run

# 2. Read the brief it wrote:
cat zeus/data/briefings/$(date -u +%F)-scrutiny-watch.md

# 3. Toggle the daily schedule:
curl -X POST localhost:8203/kronos/jobs/daily-scrutiny-watch/enable
curl -X POST localhost:8203/kronos/jobs/daily-scrutiny-watch/disable
```

To trial escalation cheaply, set `escalate_threshold: 11` (nothing escalates -
triage + flag only) or `depth: quick` for shorter research runs, then tighten.

## Notes / limits

- Signals, not proof. STOCK Act disclosures lag up to 45 days; hypotheses are
  research prompts, not insider-trading proof and not investment advice. The
  triage prompt enforces this.
- Escalations are threshold-gated and hard-capped so a busy week can't fan out
  an unbounded number of paid research runs. Cooldown stops the same signal from
  re-escalating for `cooldown_days`.
- The spawned `deep_research` reports land in `zeus/docs/research/` and are
  independently ingested into knowledge by that job's own writeback.
