# Pheme - News Consolidation & Analysis

Pheme (personification of rumor and public report) is the Zeus news subsystem:
it consolidates news from **Canary** (OSINT platform) and **CapitolScope**
(congressional-trading signals) into a dedicated Qdrant collection, runs a
staged local-only analytical pipeline to surface non-obvious cross-source
signal, and delivers a daily digest plus rate-capped breaking alerts.

Root brief: [`../../CLAUDE.md`](../../CLAUDE.md). Sibling layers:
[`../memory/CLAUDE.md`](../memory/CLAUDE.md), scheduler:
[`../kronos/CLAUDE.md`](../kronos/CLAUDE.md).

## Architecture

```
Canary ─────┐                             ┌─ Telegram push (proactive, PHEME_TELEGRAM_CHAT_ID)
            ├─ Iris sources ─> zeus_news ─┤
CapitolScope┘   (NewsStore)               └─ Twitter (gated, approval-first)
                     │
               Pheme pipeline (local Ollama, staged, cached)
               extract -> cluster -> thread -> correlate -> rank -> synthesize
                     │
               daily digest (Kronos)  +  breaking alert (KAIROS observer)
```

## Components

| Piece | File | Notes |
|---|---|---|
| NewsStore | `zeus/memory/news.py` | `zeus_news` collection, 768-dim dense, no LLM on writes. Deterministic uuid5 point ids from `(source, source_id)` make re-ingest an in-place upsert. Payload indexes: source, topics, entities, published_at, ingested_at, pinned, significance. `sweep_expired()` enforces `NEWS_RETENTION_DAYS` (default 45); `pinned=True` survives. |
| Ingest sources | `zeus/ingest/sources/canary.py`, `capitolscope.py` | `target = "news"`. Canary: JWT login as the `zeus@canary.local` analyst service user, processed articles only, HTML stripped, `full_grade` stored as `bias`. CapitolScope: Signals context pack decomposed into headline / notable-trade / cluster / scrutiny items with tickers and members pre-seeded as entities. |
| Pipeline | `zeus/pheme/pipeline.py` | Six stages, every LLM call local (`pheme_llm_call`, provider pinned to `ollama`), every stage cached under `zeus/data/pheme/<run>/`. |
| Local LLM wrapper | `zeus/pheme/llm.py` | `small_llm_call(providers=["ollama"], min_privacy_tier=1)` + 3-attempt validate-and-retry (reflection pattern). Cloud providers are unreachable from Pheme by construction. |
| Daily trigger | `zeus/kronos/jobs/pheme.py` + `zeus/data/kronos.yaml` (`pheme-daily-digest`) | Ingest both sources -> retention sweep -> pipeline -> delivery. Cron seeded from `PHEME_DIGEST_HOUR` (kronos seed YAML now supports `${VAR:-default}`); edit the live job via `/kronos` afterwards. |
| Breaking trigger | `zeus/pheme/observer.py` (`PhemeBreakingObserver`) | KAIROS `ObservationSource`, registered only when `PHEME_BREAKING_ENABLED=1`. Fires on an entity burst (>= `PHEME_BREAKING_MIN_ITEMS` fresh items, cross-source or larger single-source), runs a scoped breaking pipeline, delivers, and reports what it sent. Hard-capped by `PHEME_MAX_ALERTS_PER_DAY` (default 3); an entity alerts at most once per day. No tools, so the KAIROS allowlist is untouched. |
| Telegram push | `zeus/pheme/delivery.py` + `zeus/integrations/telegram/bot.py` | Proactive `Bot.send_message` to `PHEME_TELEGRAM_CHAT_ID`, Aegis `evaluate_text` (policy `pheme`) before send, plain-text via `markdown_to_plaintext`. Inline **Tweet it / Skip** keyboard when Twitter is enabled and autopost is off; the long-polling bot answers the callback and fires/drops the pending tweet. |
| Twitter poster | `zeus/integrations/twitter/poster.py` | `post_news_thread(lead, thread)` is the single choke point to `POST /2/tweets`: `PHEME_TWITTER_ENABLED` gate + Aegis `evaluate_payload` (policy `pheme`) on every tweet. OAuth2 user-context bearer with refresh (`/2/oauth2/token`), rotated tokens persisted to `zeus/data/pheme/twitter_token.json`. Ports the posting path from `~/services/api-clients/resources/PF/Integrations/twitter/` (the PF module depends on that app's DB stack, so the two HTTP calls are mirrored, not imported; the older `clients/twitter` client never implemented posting). |
| MCP tools | `zeus/mcp/tools.py` / `server.py` / `catalog.py` | `zeus_news_search` (read) and `olympian_twitter_post` (double-gated write: `ZEUS_MCP_ALLOW_WRITE` + `PHEME_TWITTER_ENABLED`). |
| Chat tool | `zeus/core/tools/news_search.py` | `zeus_news_search` ToolSpec mirror; registered in `main.py`. |
| Query surface | `zeus/memory/search.py` `search_news()` | Shared context-block dict shape. Opt-in `ZEUS_NEWS_IN_CONTEXT=1` folds top news hits into the chat knowledge block; default off - the tool is the primary path. |
| Safety policy | `zeus/safety/policies/pheme.yaml` | Rejects prompt-injection artifacts, credential-shaped strings, personal identifiers, shell payloads, and trading-advice phrasing on outbound content. |

## Pipeline stages

1. **Extract** (LLM, per item, skipped when payload already has entities+claim):
   entities (incl. tickers for public companies - this is what lets stage 4 key
   CapitolScope tickers against Canary prose), 2-4 topics, one neutral claim.
   Written back to Qdrant via `set_analysis` (no re-embed).
2. **Cluster** (non-LLM): union-find over entity-overlap edges (>=2 shared or
   Jaccard >= 0.34) plus Qdrant recommend-by-id neighbours (k=12,
   score >= `PHEME_CLUSTER_SIM`). A second pass merges same-story clusters
   that exact-phrase entity overlap missed: candidate pairs share >= 2 salient
   entity tokens (stopworded, so "police" alone never links stories) and merge
   only on an embedding bridge >= `PHEME_CLUSTER_MERGE_SIM` (0.78; measured on
   the 2026-07-26 Berlin split, where cross-outlet same-story pairs score
   0.80-0.90). LLM only names multi-item clusters.
3. **Thread** (non-LLM query + light LLM): prior-coverage lookup with
   `until=<window start>`; "development" vs "new" plus a one-line
   what-changed note.
4. **Correlate** (LLM, targeted): only CapitolScope x Canary pairs that share
   an entity, strongest overlap first, capped at
   `PHEME_MAX_CORRELATION_PAIRS`. Kept when connected, confidence >= 0.5.
5. **Rank** (heuristic + one LLM call): heuristic (cluster size, cross-source,
   development, correlation participation) blended 50/50 with a single
   profile-relevance scoring call over `get_profile_facts()`. Significance is
   written back to `zeus_news`.
6. **Synthesize**: LLM writes the lead paragraph plus a 2-4 bullet **Insights**
   section (cross-story observations: shared drivers, tensions, what to watch);
   body, item list, links, and the public trim are composed deterministically.
   The digest is mirrored into the newsletter manifest as
   `newsletter_type="pheme"` so the `/newsletters` UI and
   `zeus_newsletter_latest` surface it.

Telegram delivery renders the digest as Telegram HTML (`format_digest_html`):
bold headers with date, insights and connections sections, per-story meta line
(`N articles · new/developing`), one titled link per story with a `+N more`
count. Aegis evaluates the URL-stripped text (article URLs are data and long
query tokens would trip the credential rule); a failed HTML send falls back to
plain text automatically.

Public Twitter trim (distinct output, not a copy of the Telegram text): lead
tweet = strongest cross-source connection (or top story), then up to 3
"headline plus one-line take" tweets with links.

## Env reference

See the Pheme block in `.env.example`. The non-obvious ones:

- `PHEME_TWITTER_AUTOPOST=0` - the human gate. At `0`, posting happens only on
  Telegram **Tweet it**; at `1` the pipeline posts directly after Aegis passes.
- `PHEME_DIGEST_HOUR` - read at Kronos **seed time** only (first boot);
  afterwards the live `pheme-daily-digest` job owns the schedule.
- `TWITTER_OAUTH2_*` - user-context OAuth2 app credentials with
  `tweet.write` + `offline.access` scopes. Do a one-time authorization-code
  flow to obtain the initial access/refresh tokens; the poster rotates them.

## Operations

```bash
# Manual ingest (idempotent; source_id-keyed upserts)
python -m zeus.ingest.run --source canary --target news --news-days-back 3
python -m zeus.ingest.run --source capitolscope --target news --news-days-back 2

# Manual pipeline run (stages cached under zeus/data/pheme/<date>/)
python - <<'PY'
import asyncio
from dotenv import load_dotenv; load_dotenv(".env")
from zeus.pheme.pipeline import run_pheme_pipeline
print(asyncio.run(run_pheme_pipeline("daily")).body)
PY

# Unit tests (live Qdrant + Ollama, throwaway collection)
python -m pytest tests/test_news_store.py
```

Canary side note: Zeus authenticates as the `zeus@canary.local` analyst user
(created 2026-07-26 directly in the Canary DB; password in `zeus/.env`). Only
`processing_status=processed` articles are ingested - if the digest looks
thin, check Canary's NLP worker backlog (`/articles/pipeline-status`).

## What not to do

- Don't route any Pheme analytical stage onto the cloud `small_llm_call`
  chain. `pheme_llm_call` pins `providers=["ollama"]`; keep it that way.
- Don't call `post_news_thread` from anywhere new without going through its
  built-in Aegis pre-hook (there is no bypass parameter on purpose).
- Don't add `olympian_twitter_post` to the KAIROS tool allowlist.
- Don't change `_POINT_NAMESPACE` in `zeus/memory/news.py` - it is what makes
  re-ingest idempotent.
- Don't brute-force all correlation pairs; candidates come from entity
  overlap only.
