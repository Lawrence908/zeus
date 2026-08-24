# Retrieval improvements: what's live and how to finish the migration

This change reworks retrieval quality across the Knowledge (library) and
Mnemosyne (fact store) layers. It splits into **immediate wins** that need only
a restart, and **data migrations** that need a re-embed/re-index and are gated
off until you run them.

## Why
The baseline eval showed `recall@10 ~0.93` but `hit@1 ~0.60`: the right document
was almost always retrieved but not ranked first. That is a ranking problem, not
a recall problem, and it was made worse by two things:
1. The cross-encoder reranker was disabled (`ZEUS_KNOWLEDGE_RERANK=0`).
2. nomic-embed-text was called with no `search_query:` / `search_document:`
   prefixes, so the asymmetric model was used symmetrically.
The fact store was also dense-only (no BM25, no rerank), which hurts short,
keyword-heavy facts most.

## Live after a restart (no migration needed)
- **Knowledge reranking on** (`ZEUS_KNOWLEDGE_RERANK=1`) over a deeper candidate
  pool (`ZEUS_KNOWLEDGE_RERANK_CANDIDATES=40`).
- **Fact-store reranking on** (`ZEUS_MEMORY_RERANK=1`): the fact store now pulls
  a deeper dense pool and reorders it with the same cross-encoder. No re-index.
- First query downloads the reranker (~1 GB) to the HF cache and runs it on CPU.
  On the RTX 3080 prod box keep it on CPU; on the 5080 dev box you can set
  `ZEUS_RERANKER_DEVICE=cuda` and raise the candidate pools toward 100.

Restart, then re-run the eval to capture the rerank-only delta:
```bash
ZEUS_RUN_RETRIEVAL_EVAL=1 python3 -m zeus.memory.eval_suite   # or the pytest/Kronos harness
```

## Migration A: nomic task prefixes (`ZEUS_EMBED_PREFIXES=1`)
nomic-embed-text:v1.5 is asymmetric. Enabling prefixes changes the vector space,
so **every dense collection must be re-embedded** or stored docs and live queries
will disagree and quality will drop. Do not flip the flag without re-embedding.

1. Snapshot Qdrant first (safety):
   ```bash
   # per collection, via the Qdrant API or dashboard
   curl -X POST "$QDRANT_URL/collections/zeus_knowledge/snapshots"
   curl -X POST "$QDRANT_URL/collections/zeus_memories/snapshots"
   ```
2. Dry-run the re-embed to see counts:
   ```bash
   python3 scripts/reembed_retrieval.py --collection zeus_knowledge
   python3 scripts/reembed_retrieval.py --collection zeus_memories
   ```
3. Re-embed. For a **small** collection, in place is fine:
   ```bash
   ZEUS_EMBED_PREFIXES=1 python3 scripts/reembed_retrieval.py --collection zeus_memories --apply
   ```
   For a **large, live** collection (e.g. `zeus_knowledge` at ~307K points, a
   multi-hour job), do NOT rewrite it in place: that degrades live retrieval
   while it runs and breaks it at the end until the flag flips. Instead copy to a
   new collection with `--target`, leaving the live one serving unprefixed
   queries until an atomic cutover:
   ```bash
   ZEUS_EMBED_PREFIXES=1 python3 scripts/reembed_retrieval.py \
       --collection zeus_knowledge --target zeus_knowledge_prefixed --apply
   ```
4. Cut over: set `ZEUS_EMBED_PREFIXES=1` and point the collection at the rebuilt
   copy (`ZEUS_KNOWLEDGE_COLLECTION=zeus_knowledge_prefixed`), then **recreate**
   the container so the new env loads (`docker compose up -d zeus-core`; a plain
   `restart` does NOT reload `.env`). Re-run the eval. If it regresses, revert the
   two env values and `up -d` again; the original collection is untouched.
   New chunks ingested during the copy window are not in the rebuilt copy, so
   pause ingest during the run or re-ingest the gap after cutover.

Also applies to the news layer (`zeus_news`) and any other nomic collection if
you want prefixes everywhere; `news.py` still has its own un-prefixed embed path
and is intentionally left for a follow-up.

## Migration B: BM25 hybrid for the fact store (`ZEUS_MEMORY_HYBRID=1`)
The `zeus_memories` collection stores a single unnamed dense vector and has no
sparse vector config, so hybrid needs a **re-indexed collection** (named dense +
BM25 sparse), not just a flag.

1. Snapshot `zeus_memories` (as above).
2. Build a hybrid copy (non-destructive; writes `zeus_memories_hybrid`):
   ```bash
   python3 scripts/reembed_retrieval.py --collection zeus_memories --to-hybrid --apply
   ```
3. Verify counts match, then cut over with a Qdrant alias (atomic, reversible):
   ```bash
   # point the live name at the hybrid collection
   curl -X POST "$QDRANT_URL/collections/aliases" -H 'content-type: application/json' -d '{
     "actions": [{"create_alias": {"collection_name": "zeus_memories_hybrid", "alias_name": "zeus_memories"}}]
   }'
   ```
   (Or set `QDRANT_COLLECTION=zeus_memories_hybrid` and restart.)
4. Set `ZEUS_MEMORY_HYBRID=1`, restart, re-run the eval, keep the old collection
   until you are satisfied, then delete it.

## Order and measurement
Do these one at a time and re-run the eval between each so you can attribute the
delta: rerank (live now) -> prefixes (Migration A) -> fact-store BM25 (Migration
B). Grow the accepted query suite under `tests/retrieval_eval_queries/` toward
100+ first, or small deltas will be lost in the noise of a 30-query set.
