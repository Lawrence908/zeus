# Epstein Researcher - corpus investigation via live proxy

The Epstein researcher lets Zeus agents investigate a large external document
corpus (~1.3M DOJ/court records on Jeffrey Epstein) and reach
**citation-backed** conclusions, on demand ("research question X") or
unattended. It follows Zeus's live-HTTP-proxy Reference pattern (the same shape
as kiwix/NOMAD in `zeus/memory/reference.py`): Zeus queries a purpose-built
external API **at request time and stores nothing**. The corpus, all
retrieval/graph/LLM logic, and the deep-research synthesizer live in the
SEPARATE `epstein` service.

> **Safety (non-negotiable).** The corpus involves victims and unproven
> allegations. Every tool description, the agent system prompt, and every
> rendered answer carry the same framing: mention is not involvement
> (co-occurrence is a signal, never an accusation); allegations stay labeled as
> allegations; victim identities and redacted content are never surfaced,
> inferred, or reconstructed; claims are grounded in returned excerpts and
> cited, and missing evidence is stated. The live manifest's `safety_rules`
> string is echoed through on every call and is the source of truth.

## The contract (read it at runtime - do not hardcode)

`GET /api/research/capabilities` is the authoritative, evolving manifest:
`doc_types` (with counts), `filter_fields`, `endpoints`, `graph_available`,
`auth`, and `safety_rules`. Call it first. The rest of the API:

| Endpoint | Use | Speed |
|---|---|---|
| `POST /api/research/search` | dense retrieval (+optional graph expansion) | fast |
| `GET /api/research/document/{id}` | reconstructed full text + metadata | fast |
| `GET /api/research/entity/{name}` | graph dossier (`depth`, `related_to`) | fast; 503 if graph down |
| `POST /api/research/ask` | synchronous grounded answer | SLOW (minutes) |
| `POST /api/research/jobs` | start async deep-research job | fast to start |
| `GET /api/research/jobs/{id}` | poll status/steps/report/citations | fast |
| `GET /api/research/jobs` | recent jobs | fast |

**Known infra caveat:** `ask` and the synthesis step of a job are GPU-contended
and often time out - the job still returns real retrieval + citations with the
prose noted as failed (`"Synthesis failed: timed out"`). Always lead with fast
retrieval, treat synthesis as best-effort, and surface citations even when the
prose is missing.

## Zeus-side layout

| Piece | File |
|---|---|
| Reference client (read + findings-write endpoints, base-URL probe, read/write bearers) | `zeus/memory/epstein.py` |
| Chat-path tools (9) | `zeus/core/tools/epstein.py` |
| MCP tools (9) | `zeus/mcp/tools.py` (+ `zeus/mcp/server.py`) |
| Research workflow + write-gated persistence | `zeus/orchestration/epstein_research.py` |
| Agent manifest | `zeus/orchestration/agents/epstein_researcher.yaml` |
| Kairos dispatch arms (read-only) | `zeus/orchestration/daemon.py` |
| Overnight Kronos job | `zeus/kronos/jobs/epstein_research.py` |

### Tools (all read-only; no write path to the epstein service)

`epstein_capabilities`, `epstein_search`, `epstein_document`, `epstein_entity`,
`epstein_research_start`, `epstein_research_result`, the one-shot orchestrated
`epstein_research` (plan → fast cited retrieval → entity signals → async job →
answer with confidence + gaps), plus two investigation flows:

- `epstein_entity_dossier`, cited profile of one entity: graph neighborhood
  (co-occurrence connections + a de-noised dated timeline) plus a bounded,
  concurrency-limited search fan-out, confidence, and gaps. Degrades to
  search-only when the graph is down. `write_report` saves markdown to
  `<report-dir>/dossiers/`.
- `epstein_connection_map`, how 2+ entities connect: pairwise graph paths
  (co-occurrence), named intermediaries, and scoped cited evidence per pair.
  `write_report` saves markdown + a `{nodes, edges}` JSON export to
  `<report-dir>/maps/`. Edges are co-occurrence or explicitly-cited relations
  only; there is no contradiction edge in the corpus graph.

Each is exposed on all three surfaces (MCP clients, the chat path when
`ZEUS_TOOLS_ENABLED=1`, and Kairos) and gated by `ZEUS_EPSTEIN_ENABLED`. The two
flows and the shared `write_research_report` writer live in
`zeus/orchestration/epstein_research.py`; the Kronos job dispatches them via a
`mode` param (`question` | `entity_dossier` | `connection_map`).

**Search fan-out is concurrency-bounded** (`ZEUS_EPSTEIN_SEARCH_CONCURRENCY`,
default 3) with one retry: firing a whole fan-out at once trips the embedding
backend into 500s (observed live 2026-07-27; a full unbounded burst can wedge
the backend's ONNX embedder until `docker restart epstein-backend`).

## Config (mirrors `ZEUS_KIWIX_*` / `ZEUS_NOMAD_*`)

| Env | Default | Effect |
|---|---|---|
| `ZEUS_EPSTEIN_ENABLED` | `0` | Master gate for the whole capability |
| `ZEUS_EPSTEIN_BASE_URL` | (probe) | Skip probing; use this base verbatim |
| `ZEUS_EPSTEIN_API_KEY` | (unset) | Optional read bearer token (read API is open today) |
| `ZEUS_EPSTEIN_WRITE_API_KEY` | (unset) | Write bearer for findings write-back; must match the server's `RESEARCH_WRITE_API_KEY` |
| `ZEUS_EPSTEIN_ASK_TIMEOUT` | `300` | Cap for the slow synchronous `/ask` |
| `ZEUS_EPSTEIN_POLL_BUDGET` | `600` | Overnight-job seconds to wait for synthesis |
| `ZEUS_EPSTEIN_MAX_CONCURRENT` | `2` | Concurrent researchers in the backlog job |
| `ZEUS_EPSTEIN_SEARCH_CONCURRENCY` | `3` | Concurrent searches within a dossier/map fan-out |
| `ZEUS_EPSTEIN_REPORT_DIR` | `docs/research` | Reports land here; dossiers in `dossiers/`, maps in `maps/` |

**Base-URL resolution.** When `ZEUS_EPSTEIN_BASE_URL` is unset, the client
probes `/api/research/capabilities` in order and uses the first 200:
`http://epstein-backend:8000` (docker `homelab-web` net), then
`http://192.168.50.128:8170` (LAN), then `https://epstein.chrislawrence.ca`.
The resolved base is logged and cached.

## Phase 3 - persistence (write-gated)

`persist_findings(result)` writes a notable finding to mnemosyne
(`zeus_memories`) as a **raw** payload (no LLM) with full provenance:
`source=epstein_research`, the question, the deduped citation list, confidence,
and the resolved base URL. Gated by `ZEUS_MCP_ALLOW_WRITE`.

**Second sink (write-back to the epstein service).** `persist_findings` also
calls `submit_corpus_finding(...)`, which POSTs the finding to the epstein
service's gated `POST /api/research/findings` as a `proposed` case-context
proposal. Any flow can call `submit_corpus_finding` directly. It is a no-op
unless BOTH `ZEUS_MCP_ALLOW_WRITE` is on AND the client carries a write key
(`ZEUS_EPSTEIN_WRITE_API_KEY`); the server also refuses (403) without its own
`RESEARCH_WRITE_API_KEY`. A finding never mutates corpus documents; reflecting an
`accepted` finding into `context/*.md` or the claims ledger is a later human
step. Client methods: `submit_finding`, `list_findings`, `set_finding_status`.

## Phase 4 - unattended research

`zeus.kronos.jobs.epstein_research.run_epstein_research` researches one question
or a **backlog** (multi-agent fan-out under a concurrency bound), polls each
deep-research job to completion with a generous budget, writes a cited markdown
report per question, and (write-gated) persists findings. Seed it as a Kronos
job:

```yaml
- id: epstein-overnight
  name: "Epstein overnight research backlog"
  category: research
  schedule: { cron: "0 3 * * *" }
  executor: zeus.kronos.jobs.epstein_research.run_epstein_research
  params:
    questions:
      - "What do the documents reveal about flight logs and passenger manifests?"
      - "What financial entities recur across the correspondence?"
    depth: 3
    poll_budget_seconds: 600
  safety_policy: citation_required
  timeout_seconds: 3600
  enabled: false
```

Kairos (the autonomous daemon) can also investigate on its own initiative once
the read-only epstein tools are added to `ZEUS_KAIROS_TOOL_ALLOWLIST` - see
`zeus/orchestration/CLAUDE.md`.

---

## Epstein-side evolution notes (keep the two services in contract)

Zeus reads the contract at runtime, but a few coordinated changes on the
`epstein` service would make the pair more robust as both evolve:

1. **Add a `version` field to `/api/research/capabilities`.** This is the sync
   handshake: Zeus can log/branch on the manifest version and warn when the
   remote contract moves ahead of what Zeus was built against. (Zeus already
   tolerates new `doc_types`/`filter_fields` because it never hardcodes them.)

2. **DONE: the authenticated `POST /api/research/findings` write endpoint.**
   Zeus contributes a cited finding back into the case context as a `proposed`
   proposal. It requires a **separate** write bearer (`RESEARCH_WRITE_API_KEY`
   server-side / `ZEUS_EPSTEIN_WRITE_API_KEY` client-side, distinct from the read
   key), is closed by default (403 without a key), and on the Zeus side is gated
   behind `ZEUS_MCP_ALLOW_WRITE` exactly like `persist_findings`. Reflecting an
   `accepted` finding into `context/*.md` / the claims ledger remains a human step
   and is not yet automated.

3. **Fix synthesis speed + the healthcheck.** The `ask`/job synthesis GPU
   contention is the main quality limiter today (prose times out; citations
   survive). Separately, the container's curl-based healthcheck reports
   unhealthy while retrieval works - worth fixing so orchestration can trust
   the health signal.

## Verifying end-to-end

```bash
# 1. contract reachable, doc types present
curl -s http://192.168.50.128:8170/api/research/capabilities | jq '.doc_types'

# 2. tools + workflow round-trip (offline-safe unit tests)
.venv/bin/python -m pytest tests/test_epstein.py -q

# 3. live smoke of the chat tool (returns cited excerpts + safety framing)
ZEUS_EPSTEIN_ENABLED=1 .venv/bin/python - <<'PY'
import asyncio
from zeus.core.tools.epstein import register
from zeus.core.tools import registry
register()
_, h = registry.get("epstein_search")
print(asyncio.run(h({"query": "flight logs", "n_results": 3})).content[:600])
PY
```

As of the last run, the base resolved to `http://192.168.50.128:8170`, the
entity graph was **available**, and job synthesis was **slow/timing out** (real
retrieval + citations still returned) - the documented infra caveat.
