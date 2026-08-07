# Themis: Retrieval Eval Harness Worker

**Status:** Planned (action items 1 to 2 built)
**Owner:** Chris
**Last updated:** 2026-07-29
**Depends on:** nothing in the swarm. Scoring runs as a Kronos/Kairos source; minting runs as a `small_llm_call` batch; the baseline guard is a CI check. (Earlier drafts listed Argo P0/P1; the runtime decision below removes that dependency.)
**Related existing work:** `tests/retrieval_eval.py`, `tests/retrieval_eval_baseline.json`, `zeus/memory/eval.py`, LAB-NEW-D (retrieval eval extension, Phase 3 of the memory architecture plan)
**Naming:** Themis, divine order and right measure. Role-domain fit: this agent's job is to hold retrieval to a standard and report when it slips.

---

## Resolved design decisions (2026-07-29)

Three ambiguities in the original draft were closed before building. They govern
everything below; where the prose and these decisions ever disagree, these win.

1. **Match oracle: keyword gate plus LLM-judge audit.** Nightly scoring stays
   keyword-based, because it is deterministic, free, and reads no personal text
   on the hot path. An LLM-judge does not drive the nightly number; it runs only
   over the held-back human control set, to detect the keyword oracle drifting
   upward as the suite grows. The judge reads personal content, so it is a
   `small_llm_call(min_privacy_tier=1)`, the same as minting. Consequence: the
   control set is a prerequisite, not a late add. It moves up next to minting.

2. **Ground-truth anchor: document identity (`source` plus `source_id`), never a
   raw chunk id.** Knowledge is re-ingested idempotently through
   `delete_by_source` then re-add, which can renumber chunk ids. Anchoring to the
   source document survives that cycle; a raw chunk id does not. A hit is any
   chunk from the expected document appearing in top-k. Minting therefore
   identifies the source document that answers a query, not a specific chunk.

3. **Runtime: split, not a swarm worker.** Scoring is a read-heavy Kronos/Kairos
   source whose only writes are `zeus/data/retrieval_eval.json` and the run
   store. Minting is a `small_llm_call` batch, not an agent with a tool loop.
   The append-only baseline is protected by a pre-commit / CI check, not by a
   coordinator diff inspection. This keeps `ZEUS_KAIROS_TOOL_ALLOWLIST` from
   widening for minting, and it drops the Argo dependency entirely.

---

## Purpose

The retrieval sub-budgets in `QueryEngine._collect_retrieval_context()` (profile
20%, memory 25%, knowledge 45%, reference 10%) are documented as starting
guesses. The current baseline sits at hit@1 0.60, hit@5 0.867, hit@10 0.933,
MRR@10 0.71 over 30 hand-written queries. Thirty queries is enough to detect a
catastrophic regression and not enough to tune anything.

Themis is the compounding worker: it grows the ground-truth suite over time and
scores retrieval against it on a schedule. Unlike the other two workers, its
value is almost entirely cumulative. A single run is nearly worthless; a hundred
runs give you a suite large enough to trust a sub-budget change, plus a time
series showing which ingest change hurt recall.

Two distinct jobs, deliberately separated:

| Job | Cadence | What it does |
|---|---|---|
| **Scoring** | Nightly | Runs the existing suite, compares to baseline, flags regressions |
| **Minting** | Weekly batch | Proposes new ground-truth queries from recently ingested content |

---

## The integrity problem, and the rule that solves it

An agent that can both generate the test suite and edit the baseline it is scored
against will, sooner or later, make the numbers look good. This is the same class
of problem as a coding worker being able to edit its own Aegis policy.

**Rule: the baseline is append-only and human-accepted.** Themis may propose a
new baseline; it may never write `tests/retrieval_eval_baseline.json`. Accepting a
new baseline is a human action, the same as approving a merge.

Write scope, enforced by tool allowlist and by a pre-commit / CI check on the
committed diff (decision 3: there is no swarm coordinator in this design, so the
CI check is the enforcer):

| Path | Themis access |
|---|---|
| `tests/retrieval_eval_queries/pending/*.yaml` | write (proposed queries land here, in the `pending/` subdirectory) |
| `zeus/data/retrieval_eval.json` | write (run results) |
| `tests/retrieval_eval_queries/{profile,knowledge}_questions.yaml` | **denied** (promotion out of `pending/` is a human action) |
| `tests/retrieval_eval_baseline.json` | **denied** |
| `zeus/core/query.py` (sub-budget constants) | **denied** |
| everything else | read only |

That last denial matters: Themis reports that the budgets should change, and
proposes numbers. It does not apply them. Retuning retrieval is a decision, not a
maintenance task.

**CI guard.** A check in `scripts/` (sibling to `check-docs.sh`) fails the commit
if the diff touches `tests/retrieval_eval_baseline.json` or the active
`*_questions.yaml` files without a human-author commit, or if any file under
`pending/` was promoted without a corresponding review. This is the concrete
mechanism that makes "human-accepted" real under a non-swarm runtime.

---

## Scoring run

Nightly. Straightforward and cheap.

1. Load the accepted query suite (`tests/retrieval_eval_queries/*.yaml`,
   excluding `pending/`).
2. Run each query against the live retrieval stack. Record which layer answered,
   rank of the expected document, and per-layer hit rates.
3. Compare against the current accepted baseline.
4. Persist the full result to `zeus/data/retrieval_eval.json` and a row to the
   run store.

### The oracle (decision 1)

A query is scored with a keyword gate: the expected keywords must appear in a
retrieved chunk's text (substring for phrases, word-boundary for single tokens).
Document identity (decision 2) disambiguates a genuine hit from an accidental
token match: a hit is credited when the keyword gate passes on a chunk whose
`source` plus `source_id` matches the expected document, when that anchor is
recorded. Keyword-only rows (no anchor) still score, at coarser confidence.

The keyword gate is the whole nightly signal. The LLM-judge does not run nightly.
It runs only over the held-back control set (see below) so that a slow upward
drift in keyword scores can be caught against a semantically judged reference.

### Per-layer metrics

The current baseline is aggregate. The whole reason the memory layer was split
was that profile retrieval was being polluted by bulk chunks, so aggregate
numbers hide the failure mode that actually mattered. Score per layer:

- `profile_questions.yaml`: expected to be answered from the Profile or Memories
  block.
- `knowledge_questions.yaml`: expected to be answered from the Knowledge block.
- A query answered from the *wrong layer* is a distinct failure category from a
  query not answered at all. Track it separately as `layer_miss`, because it is
  the specific signal that sub-budgets or routing need attention.

This is built: `tests/retrieval_eval.py` runs every query against both the
Knowledge layer and the Profile/Memories layer, scores rank within the expected
layer, and classifies each query as `hit`, `miss`, `layer_miss`, or `error`.

### Regression alerting

Immediate Telegram message only when a threshold is crossed. Otherwise silence,
and the number rolls into the weekly digest.

- `ZEUS_THEMIS_REGRESSION_THRESHOLD`, default: hit@5 drops more than 5 percentage
  points against baseline, or `layer_miss` rate rises more than 5 points.
- The alert must name the most likely cause: which queries newly failed, and what
  changed since the last passing run (last ingest run, last commit touching
  `zeus/memory/**` or `zeus/core/query.py`). A regression alert without a suspect
  list is just anxiety.

**Open risk kept in view: corpus drift versus config regression.** New ingest
legitimately shifts recall, so a threshold crossing does not by itself mean a
config regressed. Until scoring can run against a fixed corpus snapshot, the
suspect list must foreground the last ingest run, and the alert should be read as
"something moved," not "the config broke." A first live run on 2026-07-28 already
showed knowledge hit@5 at 0.667 against a committed 0.867 baseline with the
scoring path unchanged, which is most plausibly corpus drift and a stale baseline
rather than a regression.

**Open risk kept in view: small-suite noise.** Five percentage points is roughly
1.5 queries on a 30-query suite, below the run-to-run noise floor of embedding
plus HNSW nondeterminism. The 5-point threshold should be gated on a minimum
suite size, or widened early and tightened as the suite grows past ~100 queries.

### Configuration sweep (optional, later)

Once the suite is large enough to be statistically meaningful, the scoring job can
run the suite under several configurations in one pass: hybrid on/off, reranker
on/off, candidate sub-budget splits. This is the run that actually earns the
retune, and it belongs on the 5080 because of the BGE reranker. Do not build this
until the suite is big enough that the numbers mean something. Keep nightly
scoring single-host; treat the sweep as a separate same-host experiment so
hardware differences are never mistaken for retrieval differences.

---

## Minting run

Weekly. This is the part that needs care.

### The bias trap

The obvious implementation is: pick a chunk from `zeus_knowledge`, ask an LLM to
write a question that chunk answers, store `(query, expected document)`. This
produces a suite that is trivially easy, because the question is generated *from*
the answer text and will share its vocabulary. Recall against such a suite
measures lexical overlap, not retrieval quality, and it will drift upward over
time while real-world retrieval stays flat or gets worse. This is the same
lexical-overlap risk the keyword oracle carries, which is exactly why decision 1
puts an LLM-judge audit on the control set.

Mitigations, in order of preference:

1. **Mint from the document, not the chunk.** Read a whole source document, write
   a question a person would plausibly ask about it, and *then* identify which
   document holds the answer as a separate step, recorded as `source` plus
   `source_id` (decision 2). The question is no longer a paraphrase of a single
   target chunk.
2. **Reject queries that share too much vocabulary with the target text.** A cheap
   Jaccard threshold on content words filters the worst offenders.
3. **Mint some queries from real usage.** Queries that appear in the query-log
   ring buffer, where you followed up with a correction or a rephrase, are the
   highest-signal ground truth available, because they are real questions that
   retrieval got wrong. This is probably the single most valuable source and
   worth prioritising over synthetic minting. It has an unbuilt prerequisite: the
   ring buffer is in-process and not persisted, so a persisted query log must
   exist first (see open questions).

### Human review queue

Proposed queries land in `tests/retrieval_eval_queries/pending/<date>.yaml`, not
in the active suite. Promotion is a human action. Batch size stays small enough
to review in a few minutes, `ZEUS_THEMIS_MINT_BATCH_SIZE`, default 10.

The weekly digest includes the pending batch inline so review can happen from the
Telegram link without opening an editor.

**Privacy of the artifact, not just the call.** Minted questions can encode
personal facts, and `pending/*.yaml` is a committed path. The `min_privacy_tier`
gate protects the LLM call, not where its output lands. Keep `pending/`
gitignored until a human promotes a query, or redact personal specifics at mint
time, so personal-data-derived questions are not committed by default.

### Privacy

Minting reads personal content: Obsidian notes, ChatGPT exports, newsletters,
email. This is exactly the material the privacy-tier gate exists for.

- Minting runs through `small_llm_call(..., min_privacy_tier=1)`, **not** through
  a Claude Code worker. It is a structured-output task over personal text, which
  is the small-LLM layer's purpose. There is no reason to hand it to an agent
  with a tool loop.
- The LLM-judge audit (decision 1) over the control set runs the same way,
  `small_llm_call(min_privacy_tier=1)`, for the same reason.
- No swarm worker is used anywhere in Themis (decision 3). The scoring job's
  code-level work (harness changes, per-layer metric additions) is ordinary
  development, done by a human or a normal coding session, not an autonomous
  worker with write access to the suite.

---

## Control set (validity guard, built alongside minting)

A small held-back set of human-written queries, never minted and never promoted
from `pending/`, kept as the reference the minting loop is checked against. Two
uses:

1. **Suite-inflation detection.** Watch whether the gap between control-set recall
   and full-suite recall widens over time. A widening gap means the minted suite
   is getting easier than reality, the exact failure mode of the bias trap.
2. **Oracle audit (decision 1).** The LLM-judge runs over the control set to
   confirm the keyword gate still agrees with a semantic judgment. Disagreement
   is the signal that the keyword oracle has drifted.

This was action item 9 in the original draft. Under decision 1 it is a
prerequisite for trusting either the oracle or the minting loop, so it is built
with minting, not after it.

---

## Delivery

| Event | Delivery |
|---|---|
| Nightly scoring, no regression | Silent. Persisted only. |
| Nightly scoring, regression past threshold | Immediate Telegram: metric, delta, newly failing queries, suspect list. |
| Weekly digest | Markdown report: metric time series, per-layer breakdown, `layer_miss` trend, pending minted queries for review, and any proposed sub-budget change with its evidence. Telegram summary plus link. |

Weekly report to `zeus/data/research/themis/weekly-<iso-week>.md`, ingested with
`source="themis"`, `source_id=<iso-week>`.

---

## Budget and failure behaviour

- Scoring runs are cheap and mostly local: embedding calls plus optional reranker.
  Budget is dominated by minting and by the control-set judge audit.
- `ZEUS_THEMIS_MAX_USD_PER_WEEK` covering the minting batch and the judge audit,
  drawn against the existing small-LLM daily cap rather than a new ledger.
- **Fail-open per query.** A query that errors during scoring is recorded as
  `error`, excluded from the metric denominator, and reported in the digest. It
  does not abort the run and it does not silently count as a miss, because a
  scoring bug masquerading as a recall regression is the worst possible outcome
  here. Guard against denominator collapse: if the error rate crosses a floor,
  alert on that rather than reporting a rate computed over a handful of survivors,
  and always surface `n_scored` next to every rate.

---

## Why this one is worth building early

Every other retrieval decision on the roadmap is currently unfalsifiable. The
sub-budget percentages, whether the reranker earns its latency, whether hybrid
fusion helps on your actual corpus, whether the next ingest source improved or
degraded things: none of these can be answered against 30 queries. Themis is the
instrument that makes the rest of the memory work measurable, which is why the
memory architecture plan already flags the eval harness as the mandatory first
spike.

It is also the lowest-risk worker to build first: read-mostly, cheap, no merge
path, and its failure mode is a bad number in a report rather than a bad commit in
a repo.

---

## Open questions

- [ ] **Minting bias.** Which of the three mitigations to implement first, and how
  to validate that the suite is not getting easier over time. The control set is
  the chosen instrument: hold back a human-written set and watch whether the gap
  between control-set recall and full-suite recall widens.
- [ ] How to extract candidate queries from the query-log ring buffer, given it is
  in-process and not persisted. This needs a persisted query log first, which is
  now an explicit prerequisite of minting mitigation 3.
- [ ] Whether the configuration sweep runs on the 5080 on a separate cadence from
  nightly scoring on daedalus, and how results from two hosts are compared without
  confusing hardware differences for retrieval differences.
- [ ] Suite size target before a sub-budget retune is considered credible. Working
  assumption: 100 queries as a floor, 200 to trust a sub-budget move.
- [ ] Fixed-corpus snapshot for scoring, so a recall change can be attributed to
  config rather than to the corpus growing between runs.

---

## Action items

1. [x] Split the existing 30 queries into `profile_questions.yaml` and
   `knowledge_questions.yaml` under `tests/retrieval_eval_queries/` (all 30 are
   knowledge-layer; `profile_questions.yaml` seeded with unverified queries
   pending human validation).
2. [x] Per-layer metrics plus `layer_miss` category in `tests/retrieval_eval.py`,
   with fail-open per query.
3. [ ] Nightly scoring job as a Kronos/Kairos source, results to
   `zeus/data/retrieval_eval.json` and the run store.
4. [ ] Baseline and active-suite denylist enforced at tool allowlist and by a CI
   check (decision 3), sibling to `scripts/check-docs.sh`.
5. [ ] Regression threshold plus suspect-list Telegram alert, gated on a minimum
   suite size, with the corpus-drift caveat surfaced in the suspect list.
6. [ ] Minting job as a `small_llm_call(min_privacy_tier=1)` batch,
   document-level not chunk-level, anchored to `source` plus `source_id`, with
   vocabulary-overlap rejection.
7. [ ] `pending/` review queue plus promotion flow; keep `pending/` gitignored or
   redacted until promotion.
8. [ ] Weekly digest generator with metric time series and Knowledge-layer
   ingest.
9. [ ] Held-back human control set, built alongside minting (item 6), driving both
   suite-inflation detection and the LLM-judge oracle audit.
10. [ ] Rebaseline: the committed `tests/retrieval_eval_baseline.json` predates
    recent ingest and is in the old flat shape. Capture a new-shape baseline once
    the corpus-drift question is settled.
11. [ ] (Later) Multi-configuration sweep on the 5080.

---

## Linear tickets to file

Placeholder IDs only. Not minted Linear identifiers; replace after creation. Note
that this work overlaps LAB-NEW-D in the memory architecture plan and should
probably be filed as children of LAB-61 rather than as a new parent.

- `LAB-NEW-THEMIS-1` Themis parent: retrieval eval harness worker
- `LAB-NEW-THEMIS-2` Per-layer metrics and query file split (done)
- `LAB-NEW-THEMIS-3` Nightly scoring job plus regression alerting
- `LAB-NEW-THEMIS-4` Query minting via small-LLM with bias mitigations and control set
- `LAB-NEW-THEMIS-5` Pending review queue and baseline integrity CI guard
- `LAB-NEW-THEMIS-6` Weekly digest and time series
