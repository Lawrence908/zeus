# Weekly Congressional Scrutiny Brief (Kronos job)

**Status: draft, ready to wire up.** A weekly Kronos job that turns CapitolScope
congressional-trading signals into an intelligence-style assessment connecting
this week's trading shifts to current global topics, synthesized on your local
Ollama.

- Executor: `zeus.kronos.jobs.congressional_scrutiny.run_congressional_scrutiny`
- Output: `zeus/data/briefings/YYYY-MM-DD-congressional-scrutiny.md` (override with
  `ZEUS_BRIEFINGS_DIR`)

## Pipeline

1. `capitolscope_context_pack(days=7)` - one call returns the week's activity
   plus week-over-week deltas and trend labels (sector rotation, newly-active
   tickers, member-count deltas, clusters, scrutiny movers).
2. `_gather_news(...)` - a short open-source news digest for the top-moving
   sectors/tickers (the "global topics" half CapitolScope does not have).
   Default uses Tavily (`TAVILY_API_KEY`); returns a graceful placeholder if
   unset. Swap for Brave, a canary query, or a Zeus reference call.
3. `small_llm_call(...)` - synthesizes the brief (BLUF, confidence-graded).
4. Writes the markdown brief to disk, then best-effort writeback (mirrors
   deep_research): a one-liner to the inbox (`POST {ZEUS_CORE_URL}/inbox/append`)
   and the brief ingested as a `KnowledgeChunk` (`source="congressional_scrutiny"`)
   so it is queryable later and future briefs/chats can cite it. Returns metadata
   (including per-target writeback status) for the JobRun summary.

## Environment

Already set for the MCP tools (reused here):

```
CAPITOLSCOPE_SIGNALS_URL=https://capitolscope.chrislawrence.ca   # or http://localhost:8120 on-host
CAPITOLSCOPE_SIGNALS_KEY=<the signals key>
```

Optional:

```
TAVILY_API_KEY=<key>        # for the news digest; without it the brief runs on signals + model knowledge
ZEUS_BRIEFINGS_DIR=/path    # output dir (default zeus/data/briefings)
```

## Keeping synthesis on Ollama

The job calls `small_llm_call(..., min_privacy_tier=1, model_hint="ollama")`.
Confirm your `DEFAULT_CHAIN` / tier config in `zeus/core/small_llm.py` routes
tier-1 (or `model_hint="ollama"`) to your local Ollama. Adjust the two params if
your chain uses different names. Congressional data is public, so tier 2 is also
acceptable if you prefer a stronger model.

## Register the weekly job

Via the `kronos_create_job` MCP tool (from chat or an agent):

```
kronos_create_job(
  name="Weekly Congressional Scrutiny Brief",
  description="CapitolScope trading shifts vs global topics, synthesized on Ollama",
  category="research",
  cron="0 8 * * 1",                     # Mondays 08:00 (your ZEUS_DEFAULT_TIMEZONE)
  executor="zeus.kronos.jobs.congressional_scrutiny.run_congressional_scrutiny",
  params={"days": 7, "max_tokens": 1800, "model_hint": "ollama"},
  safety_policy="standard",
  timeout_seconds=300,
  timezone="America/Toronto",
)
```

Or build the `JobDefinition` directly (see `zeus/kronos/models.py`) with the same
`executor` / `schedule` / `params` and register it through the Kronos registry/API.

Run it once on demand first (manual trigger or `days=14` for more content in a
thin week) and read the produced brief before enabling the schedule.

## The prompt

The system prompt (in the job file) frames an intelligence analyst with hard
rules: signals-not-proof, ground every claim in the provided data (no invented
trades/tickers), calibrated confidence (High/Moderate/Low), prefer deltas/trends
over raw levels, and a fixed BLUF markdown structure (BLUF -> notable shifts ->
global-topic hypotheses -> watch items -> caveats). Edit the constants
`SYSTEM_PROMPT` / `USER_TEMPLATE` to taste.

## Notes / limits

- Congressional disclosures lag (up to 45 days) and thin weeks happen; the
  prompt is instructed to say so rather than manufacture a narrative.
- This is a research/prioritisation aid built on public disclosures, not
  investment advice or insider-trading proof.
- Data-assembly (context-pack -> rendered prompt input) is verified live; the
  Ollama synthesis step runs in your environment.
