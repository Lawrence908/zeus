# Token usage tracking

## Where the data lives

A single SQLite table — `zeus/data/small_llm_usage.db`, table `usage` — holds every model call's tokens, cost, latency, and outcome. Schema:

| column      | type    | notes |
|-------------|---------|-------|
| ts          | TEXT    | ISO 8601 UTC, indexed |
| caller      | TEXT    | e.g. `newsletter.summarize`, `chat.stream`, `kronos.deep_research` |
| provider    | TEXT    | `anthropic`, `anthropic_haiku`, `gemini_paid`, `groq`, `openrouter`, `ollama`, `cursor` (historical) |
| model       | TEXT    | exact model id |
| tier        | INTEGER | 1 = privacy-preserving, 2 = trains-on-input ok |
| tokens_in   | INTEGER | prompt tokens |
| tokens_out  | INTEGER | completion tokens |
| cost_usd    | REAL    | 0 for ollama, set per pricing for paid providers |
| latency_ms  | INTEGER | wall clock |
| ok          | INTEGER | 1/0 |
| error       | TEXT    | nullable |

Indexed on `ts` and `(provider, ts)`.

## Writers (current)

- `zeus/core/small_llm.py` — `_log_usage()` writes for every `small_llm_call()` (fact extraction, titles, classifiers, etc.).
- `zeus/core/query.py` — chat-path Claude / Ollama calls log here too (see `_log_chat_usage` helper). Caller is one of `chat.run_llm`, `chat.run_llm_stream`, `chat.run_llm_with_tools`.

## Reader (current)

- `GET /admin/llm_usage?bucket=day&since_days=30&provider=&caller=` returns time-series + per-provider / per-model / per-caller rollups + totals.

The Token Usage app at Zeus OS uses this endpoint exclusively.

## Historical import (TODO)

Drop CSVs into `~/.zeus/usage-imports/`:

```
~/.zeus/usage-imports/
  anthropic-2026-05.csv     # Anthropic Console → Usage → export
  cursor-2026-04.csv        # Cursor settings → Account → export (when supported)
```

Then call `POST /admin/llm_usage/import` (or eventually `python -m zeus.usage import`). Parser lives in `zeus/core/usage_import.py`.

### Anthropic CSV (verify on next export)

The Console's current Usage export columns are roughly:

```
workspace, model, api_key, usage_type, input_tokens, output_tokens,
cache_read_tokens, cache_write_tokens, start_time, end_time, cost_usd
```

Map to ledger:
- `start_time` → `ts`
- `'anthropic'` → `provider`
- `model` → `model`
- `1` → `tier`
- `input_tokens + cache_read_tokens` → `tokens_in` (cache reads are billed differently but count for the same purpose here)
- `output_tokens` → `tokens_out`
- `cost_usd` → `cost_usd`
- a synthetic caller like `historical.anthropic` so they're distinguishable from live calls

### Cursor

Cursor's per-call export format is unstable as of June 2026. Treat imported rows as monthly aggregates: `model='cursor-ide-aggregate'`, `provider='cursor'`, caller `historical.cursor`, one row per month.

## Productivity attribution (later)

Once local-model output starts producing actual code commits / PRs / docs, we want to correlate ollama tokens to outcomes. Sketch:
- Tag commits / file writes that originated from chat with `[zeus]` in a commit trailer or sidecar `.zeus-attribution.json`.
- A Kronos job rolls up `(period, local_tokens, lines_added, files_touched)`.
- Token Usage app gains a "productivity" panel showing tokens → output ratios.

Out of scope for Phase 2a — file this under future work in the Linear plan when ready.
