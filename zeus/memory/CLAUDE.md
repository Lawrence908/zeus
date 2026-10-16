# zeus/memory/ — Mnemosyne, Library, Reference

Three retrieval layers share this directory. Root brief: [`../../CLAUDE.md`](../../CLAUDE.md). Full plan: [`../../docs/memory-architecture-plan.md`](../../docs/memory-architecture-plan.md).

## Layer map

| Layer | File | Qdrant collection | Writer | Retrieval |
|-------|------|-------------------|--------|-----------|
| Mnemosyne / Memory | `store.py` (`MemoryStore`) | `zeus_memories` | `add_text(extract_facts=True)` via `small_llm_call(FactExtraction)` | vector, filterable by category / valid_as_of / contains_pii |
| Library / Knowledge | `library.py` (`KnowledgeStore`) | `zeus_knowledge` | `add_chunks()` raw embed, no LLM | dense + BM25 RRF hybrid, optional BGE-rerank |
| Reference | `reference.py` | (none; live proxy) | n/a | HTTP to kiwix-serve + NOMAD at query time |

Search helpers (`search.py`) return mem0-shaped dicts so `format_context_block` in `zeus/core/query.py` renders all three through one code path.

## Invariants

- **ISO-8601 strings** for `created_at`, `updated_at`, `valid_from`, `valid_until`. Never floats. This is what broke mem0.
- **`confidence >= ZEUS_MEMORY_MIN_CONFIDENCE`** (default `0.6`) on every extracted fact. Lower-confidence facts are dropped at the store.
- **`contains_pii` flag** is advisory; PII-bearing write paths must pass `min_privacy_tier=1` to `small_llm_call`.
- **Idempotent re-ingest** via `delete_by_source(source, source_id)`. Re-running `zeus.ingest.run` for the same source must not create duplicate points.
- **Single embed dimension (768)** across both collections (`nomic-embed-text:v1.5`). Do not mix embedders in one collection.
- **No LLM on the knowledge write path.** If you reach for `small_llm_call` here, you are building memory, not knowledge; put the source in the memory target instead.

## Feature flags

| Env | Default | Effect |
|-----|---------|--------|
| `ZEUS_KNOWLEDGE_HYBRID` | `1` | Adds named sparse BM25 vector at write; uses `FusionQuery(RRF)` at read |
| `ZEUS_KNOWLEDGE_RERANK` | `0` (but **`1` in prod**, see below) | Reranks top-k candidates via `rerank-gateway` |
| `ZEUS_RERANKER_URL` | `http://rerank-gateway:8191` | Gateway base URL |
| `ZEUS_RERANKER_TIMEOUT` | `25.0` | Must stay **above** the gateway's `RERANK_REQUEST_TIMEOUT` (15s), or a truncated read replaces the gateway's error text with a bare timeout |
| `ZEUS_RERANKER_MODEL` | `BAAI/bge-reranker-v2-m3` | Advisory only — the checkpoint is the pool's, reported by the gateway's `/healthz` |
| `ZEUS_RERANKER_DEVICE` | — | **Deprecated, ignored.** Device selection belongs to the pool |
| `ZEUS_RERANKER_FP16` | — | **Deprecated, ignored.** Same reason |
| `ZEUS_MEMORY_MIN_CONFIDENCE` | `0.6` | Drop facts below this |
| `ZEUS_KIWIX_ENABLED` | `1` | Toggle kiwix proxy |
| `ZEUS_KIWIX_URL` | cf-tunnel | kiwix-serve base URL |
| `ZEUS_KIWIX_CF_ACCESS_CLIENT_ID` / `_SECRET` | (unset) | Cloudflare Access credentials when behind tunnel |
| `ZEUS_NOMAD_ENABLED` | `0` | Toggle NOMAD proxy |
| `ZEUS_NOMAD_URL` | (unset) | NOMAD base URL |
| `ZEUS_KNOWLEDGE_SEARCH_TOP_K` | `5` | KnowledgeStore top-k |
| `ZEUS_REFERENCE_SEARCH_TOP_K` | `5` | Reference top-k |
| `ZEUS_MEMORY_SEARCH_TOP_K` | `8` | MemoryStore top-k |

## Common patterns

**Adding to memory (extracted facts):**

```python
from zeus.memory.store import get_memory_store
store = get_memory_store()
await store.add_text(
    "The user prefers plain text in Telegram.",
    source="context_pack",
    source_id="context_pack:telegram_pref",
    user_id="user",
    extract_facts=True,
)
```

**Adding to knowledge (raw chunk):**

```python
from zeus.memory.library import get_knowledge_store, KnowledgeChunk
ks = get_knowledge_store()
await ks.add_chunks([KnowledgeChunk(text=..., source="obsidian:daily", source_id="obsidian:2026-04-18", ...)])
```

**Searching (use helpers, not the stores directly):**

```python
from zeus.memory.search import search_memories, search_knowledge, search_reference, get_profile_facts
```

All four return the same shape so `QueryEngine` can render them into labelled blocks without special-casing.

## Retrieval eval

Baseline: hit@1=0.60, hit@5=0.867, hit@10=0.933, MRR@10=0.71 on 30 hand-written queries. Stored in `tests/retrieval_eval_baseline.json`.

Gate every retrieval-config change through:

```bash
python -m zeus.memory.eval --query-set zeus/data/eval/queries.json --top-k 10
```

Commit the resulting JSON alongside the flag change so the baseline moves deliberately.

## What not to do

- Don't add a graph database. Bi-temporal payloads + category filters give KG-like queries without Neo4j.
- Don't add mem0, LiteLLM, LangChain, or LlamaIndex back in. The whole point of the hand-rolled stores is owning the Qdrant payload shape.
- Don't load the reranker **in-process**, on any device. It lives in `services/rerank-gateway/` (TEI, `POST /rerank`) and Zeus reaches it over HTTP via `ZEUS_RERANKER_URL`. Re-adding `sentence-transformers` or `FlagEmbedding` here puts torch and the CUDA wheels back into a 22 GB image in order to duplicate a service that already exists — `reranker.py` was this tree's only torch consumer, which is the whole reason the extraction was worth doing.
- Don't put the reranker on the daedalus 3080, and don't read its free VRAM as headroom. Measured 2026-08-28: 2,985 MiB free, with `zeus-ollama` holding 752 + 3,650 MiB (`OLLAMA_KEEP_ALIVE=24h`, both model slots in use), a `canary-worker` holding 2,136 MiB, and `zeus-comfyui` idle at 332 MiB. That last one is the disqualifier: it is the `--lowvram` SDXL fallback behind comfyui-gateway, it only renders when Apollo is asleep, and `--disable-smart-memory` pages a 6.9 GB checkpoint through VRAM per job. A resident ~2 GB TEI turns those renders into OOMs, and comfyui-gateway's VRAM floor deliberately does not apply to non-FLUX nodes, so it keeps submitting to a node that then hangs for its full 480 s poll timeout. Apollo's 5080 is the GPU for this; the gateway pool puts it first and falls back to a daedalus CPU node.
- Don't ingest Wikipedia or NOMAD into Qdrant. They stay live-proxied.
- Don't conflate `zeus_memories` and `zeus_knowledge` in search. `QueryEngine` renders them as separate labelled blocks; mixing them defeats the whole split.
