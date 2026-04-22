# Zeus Memory Architecture Rework: Planning & TODO

Status: **Phase 1 shipped, MemoryStore live, migration task K landed on `frontend-improvements`**
Owner: Chris
Last updated: 2026-04-18

> **Context (2026-04-18):** mem0 was removed in April 2026 and replaced by the hand-rolled [`zeus/memory/store.py`](../zeus/memory/store.py) (`MemoryStore`). The memory layer now calls `small_llm_call` for fact extraction; the knowledge layer in [`zeus/memory/library.py`](../zeus/memory/library.py) uses dense + BM25 RRF hybrid with an optional BGE-reranker. The reference layer (Phase 2) shipped as [`zeus/memory/reference.py`](../zeus/memory/reference.py) with `KiwixClient` and `NomadClient`. This doc remains the authoritative narrative for **why** the split happened; for current code layout see [`CLAUDE.md`](../CLAUDE.md) and [`zeus/docs/architecture.md`](../zeus/docs/architecture.md). mem0 references below are historical.

This doc is the working plan for splitting Zeus's single `zeus_memories` collection into a three-layer retrieval architecture. It is written so multiple chats can pick up discrete pieces of Phase 1 in parallel without stepping on each other. Update the task checklist inline as work lands.

## Why we're doing this

The current `zeus_memories` collection (396 points in Qdrant) was populated by running `zeus.ingest.run` over bulk sources (Obsidian vault, class notes, jobkit archive, chatgpt exports, newsletters) through mem0's `Memory.add()`. mem0 runs an LLM fact-extraction pass on every chunk and produces atomic claims. That is the right shape for conversational memory ("Chris prefers plain text in Telegram") and the wrong shape for bulk documents, we ended up with thousands of disconnected trivia statements like `byte = 8 bits`, `A graph with no cycles is acyclic or a forest`, plus a chunk of garbled Chinese characters that are almost certainly OCR errors from screenshot-based notes (Chris only writes in English).

Result: `QueryEngine` retrieves five "memories" per turn and none of them are useful profile context, so the chat model keeps answering "I don't have that in memory."

We also want to be able to ingest much larger bulk corpora later (Wikipedia ZIM, Project NOMAD data) without polluting the memory layer further.

## Target architecture (three layers)

| Layer | Collection | Writer | Retrieval shape | Typical size | What lives here |
|---|---|---|---|---|---|
| **Mnemosyne / Memory** | `zeus_memories` (rebuilt) | `mem0.Memory.add()`, LLM fact extraction | Atomic facts, profile-shaped | 100–500 items | Curated context pack, chat-extracted preferences, KAIROS observations |
| **Library / Knowledge** | `zeus_knowledge` (new) | `KnowledgeStore.add_chunks()`, raw embed+store, **no LLM** | Full chunks with source metadata | 10k–1M chunks | Obsidian vault, jobkit archive, chatgpt exports, newsletters, email, bookmarks, git |
| **Reference / Live** | `zeus_cache_reference` (Phase 2, optional) | Live HTTP proxy (kiwix, NOMAD) with optional cached re-embed | Passage snippets | Unbounded, not indexed | Wikipedia ZIM via kiwix, Project NOMAD |

The Memory layer stays small and high-signal. The Knowledge layer is a dumb but fast RAG store, no extraction, no dedup pass, just chunk → embed → upsert. The Reference layer hits authoritative external sources at retrieval time so we never re-index them.

`QueryEngine.query()` retrieves from all layers in parallel and renders them as **separately labelled blocks** in the system prompt: `Profile`, `Memories`, `Knowledge`, `Reference`. The model is told which block is which so it stops confusing a class-note fragment for a fact about Chris.

### Token budget

Existing split in `SessionManager.get_context_window()`: ⅓ retrieved, ⅔ session. The retrieved third is sub-budgeted:

| Sub-block | Share of retrieval budget | Notes |
|---|---|---|
| Profile facts | 20% | From `get_profile_facts()` (mem0 with profile filter) |
| Memory results | 25% | mem0 search, top-k=5 |
| Knowledge results | 45% | KnowledgeStore search, top-k=5, truncated to fit |
| Reference snippets | 10% | Phase 2 only; unused until then, reallocated to knowledge |

These are starting numbers, we tune after Phase 3 eval.

## Source reclassification

| Source | Today | Target | Notes |
|---|---|---|---|
| `context_pack` (`zeus/data/raw/context_pack.md`) | memory | **memory** | The only curated profile source. Keep running through mem0 fact extraction. |
| `markdown` (context-pack-core, jobkit-archive, notes) | memory | **knowledge** | Bulk docs, no extraction |
| `chatgpt` | memory | **knowledge** | Historical chat logs; RAG, not facts |
| `obsidian` | memory | **knowledge** | User explicitly wants offline RAG over vault |
| `email` | memory | **knowledge** | |
| `newsletter` | memory | **knowledge** | |
| `bookmarks` | memory | **knowledge** | |
| `git` | memory | **knowledge** | |
| `gcal` | memory | **memory** | Events are profile-shaped (future-looking, small volume) |
| (future) `kiwix` Wikipedia | N/A | **reference** | Live proxy only, no ingest |
| (future) NOMAD | N/A | **reference** | Already has its own Qdrant RAG; proxy it |

## `ingest/config.yaml` schema

New file: `zeus/ingest/config.yaml`. Declarative per-source routing and per-folder include/exclude rules. Merged with CLI args; CLI wins on explicit overrides.

```yaml
# zeus/ingest/config.yaml
defaults:
  user_id: chris
  chunk_size: 512
  chunk_overlap: 64

sources:
  context_pack:
    target: memory
    path: zeus/data/raw/context_pack.md

  markdown:
    target: knowledge
    roots:
      - base_dir: zeus/data/raw/context-pack-core
        globs: ["**/*.md"]
      - base_dir: zeus/data/raw/jobkit-archive
        globs: ["**/*.md"]
      - base_dir: zeus/data/raw/notes
        globs: ["**/*.md"]
        exclude:
          - "archive/old-classes/**"  # example — trim rotted class notes

  obsidian:
    target: knowledge
    vault_path: ${OBSIDIAN_VAULT_PATH}
    exclude:
      - ".trash/**"
      - "templates/**"

  chatgpt:
    target: knowledge
    path: zeus/data/raw/chat-history

  email:
    target: knowledge
    limit: 200

  newsletter:
    target: knowledge

  bookmarks:
    target: knowledge
    path: zeus/data/raw/bookmarks.html

  git:
    target: knowledge
    max_commits: 500

  gcal:
    target: memory
    days_back: 90
    days_forward: 30
```

Rules:
- `target` is required and must be `memory` or `knowledge` (Phase 1). `reference` accepted in schema but rejected by pipeline until Phase 2.
- `exclude` globs are matched against the relative path under the source's root.
- Env-var interpolation (`${OBSIDIAN_VAULT_PATH}`) via `os.path.expandvars` after load.
- `zeus/ingest/run.py` loads this file when present; CLI args override individual source fields.

## Phase 1: concrete work

### File-level changes

1. **`zeus/memory/library.py`** (new)
   ```python
   class KnowledgeStore:
       def __init__(self, qdrant_client, embedder, collection="zeus_knowledge"):
           ...
       def ensure_collection(self) -> None: ...
       def add_chunks(self, chunks: list[KnowledgeChunk]) -> AddResult: ...
       def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[KnowledgeHit]: ...
       def delete_by_source(self, source: str, source_id: str) -> int: ...
   ```
   - `KnowledgeChunk` carries: `text`, `source`, `source_id`, `source_path`, `chunk_index`, `created_at`, `metadata`.
   - `ensure_collection()` creates `zeus_knowledge` with 768-dim vectors (`nomic-embed-text`), cosine distance, same `indexing_threshold` as `zeus_memories`.
   - `add_chunks()` batches embeddings (reuse whatever client `zeus/memory/search.py` uses), upserts to Qdrant. No mem0 involvement, no LLM calls.
   - `delete_by_source()` enables idempotent re-ingest.

2. **`zeus/ingest/config.py`** (new)
   - `load_ingest_config(path="zeus/ingest/config.yaml") -> IngestConfig` with pydantic models for `SourceConfig` and root-level `IngestConfig`.
   - Resolves env vars, validates targets.

3. **`zeus/ingest/pipeline.py`** (modify)
   - Each `IngestSource` gains a `target: Literal["memory", "knowledge"]` attribute (default `"memory"` for back-compat).
   - `run_ingest()` routes per-chunk: `target == "memory"` → existing mem0 path; `target == "knowledge"` → `KnowledgeStore.add_chunks()`.
   - Summary/stats split into `memory_ops` and `knowledge_ops`.

4. **`zeus/ingest/run.py`** (modify)
   - Load `zeus/ingest/config.yaml` if present; merge into `build_sources`.
   - Honour per-source `target` from config when constructing sources.
   - New CLI flag `--target {memory,knowledge,both}` to filter which layers run in a given invocation.

5. **`zeus/memory/search.py`** (modify)
   - Add `search_knowledge(query, top_k=5)` that delegates to `KnowledgeStore`.
   - Keep `search_memories()` and `get_profile_facts()` unchanged (still use mem0).

6. **`zeus/core/query.py`** (modify)
   - `QueryEngine.query()` fans out: profile (existing), memory (existing), knowledge (new).
   - Build system prompt with four labelled blocks. Update `zeus/core/prompts/chat_system.md` to describe each block.
   - Apply sub-budget token allocation from the table above.

7. **`zeus/core/prompts/chat_system.md`** (modify)
   - Replace the single `Relevant Context` block with labelled `Profile`, `Memories`, `Knowledge` (and `Reference` placeholder for Phase 2).
   - Add one-liner telling the model: Memories are curated facts about the user; Knowledge is retrieved from their personal document library (may be outdated or tangential); cite which block an answer came from when ambiguous.

### Migration (Option A, confirmed): task K runbook

Run these in order from the repo root on the host. `zeus-core` must be restarted between steps 2 and 3 so `KnowledgeStore` ensures its new collection on first write.

**1. Backup Qdrant**
```bash
docker exec zeus-qdrant tar czf - /qdrant/storage \
  > /tmp/qdrant-backup-$(date +%Y%m%d-%H%M).tgz
ls -lh /tmp/qdrant-backup-*.tgz      # sanity check — should be tens of MB
```

**2. Drop the old memories collection**
```bash
curl -X DELETE http://localhost:6333/collections/zeus_memories
curl -s http://localhost:6333/collections | jq '.result.collections'
# Expect: zeus_memories is gone. zeus_knowledge appears only after step 3.
```

**3. Restart zeus-core so it picks up the new code paths**
```bash
docker compose restart zeus-core
docker compose logs -f zeus-core | head -50     # watch for clean boot
```
(Full rebuild is not required, `compose.override.yaml` bind-mounts `./zeus` into the container. A plain `restart` is enough for Python edits. Only rebuild if dependencies changed, which they did not in Phase 1.)

**4. Re-run ingest with the new routing**

With `ZEUS_LLM=claude` so the memory layer's fact extraction uses Claude (not Qwen, prevents the CJK hallucination flagged in task J).

```bash
# Memory layer — curated profile sources. Runs mem0 fact extraction.
ZEUS_LLM=claude python -m zeus.ingest.run --target memory

# Knowledge layer — bulk sources. No LLM, just embed + Qdrant upsert.
python -m zeus.ingest.run --target knowledge
```

`zeus/ingest/config.yaml` now declares the routing; `--target` filters which layer runs. Both commands default to `--source all`.

**5. Verify the two collections exist and are populated**
```bash
curl -s http://localhost:6333/collections/zeus_memories | jq '.result.points_count'
curl -s http://localhost:6333/collections/zeus_knowledge | jq '.result.points_count'
```
Expect: `zeus_memories` ≈ 100–500 points (curated context pack + gcal), `zeus_knowledge` in the thousands.

**6. Spot-check via Telegram or chat**

Profile-shaped questions (should hit `Profile` / `Memories` blocks):
- "What am I working on this week?"
- "What's my current role?"
- "What newsletters do I subscribe to?"

Knowledge-shaped questions (should hit the `Knowledge` block):
- "What did I write about hash tables in my class notes?"
- Something from a specific Obsidian note title you remember
- A newsletter headline from the last week

Watch `docker compose logs -f zeus-core` for `retrieval.parallel` timing and confirm knowledge hits come back from `_collect_retrieval_context()`.

**7. If something is wrong**: rollback
```bash
docker compose stop zeus-core zeus-qdrant
docker run --rm -v qdrant_storage:/qdrant/storage -v /tmp:/backup alpine \
  sh -c "rm -rf /qdrant/storage/* && tar xzf /backup/qdrant-backup-YYYYMMDD-HHMM.tgz -C /"
docker compose start zeus-qdrant zeus-core
```

## Parallelisable work breakdown

Pieces that can be picked up by independent chats without collision. Dependencies listed.

| # | Task | Touches | Depends on |
|---|---|---|---|
| A | Implement `KnowledgeStore` (`zeus/memory/library.py`) with unit test that round-trips a chunk | new file only | N/A |
| B | Write `zeus/ingest/config.py` loader + pydantic models + unit test | new file only | N/A |
| C | Draft `zeus/ingest/config.yaml` with current raw layout | new file only | N/A |
| D | Add `target` attribute to each `IngestSource` subclass | `zeus/ingest/sources/*.py` | N/A |
| E | Route `run_ingest()` by target | `zeus/ingest/pipeline.py` | A, D |
| F | Wire config loader into `zeus/ingest/run.py` + `--target` flag | `zeus/ingest/run.py` | B, D |
| G | Extend `zeus/memory/search.py` with `search_knowledge()` | `zeus/memory/search.py` | A |
| H | Update `QueryEngine` to four-block retrieval + sub-budgets | `zeus/core/query.py` | G |
| I | Rewrite `chat_system.md` prompt with labelled blocks | `zeus/core/prompts/chat_system.md` | N/A |
| J | Chinese-character ingest bug: find which source produces them and fix (likely an OCR/PDF/image path in markdown or obsidian source) | `zeus/ingest/sources/*.py` | N/A |
| K | Migration runbook + ops check (backup, drop, re-run, verify) | `docs/memory-architecture-plan.md` (this file) | E, F, H |

Good parallel splits: A+B+C+I+J in parallel first; D unblocks E,F; E+F unblock K; G unblocks H.

## Phase 1 TODO checklist

- [x] A, `KnowledgeStore` class + ensure_collection + add_chunks + search + delete_by_source (`zeus/memory/library.py`)
- [x] B, `load_ingest_config()` with pydantic validation (`zeus/ingest/config.py`)
- [x] C, `zeus/ingest/config.yaml` matching current raw layout
- [x] D, `target` attribute on every `IngestSource` subclass
- [x] E, `run_ingest()` routes memory vs knowledge chunks correctly (`zeus/ingest/pipeline.py`)
- [x] F, `zeus/ingest/run.py` loads config and supports `--target`, `--config`, `--no-config`
- [x] G, `search_knowledge()` helper in `zeus/memory/search.py`
- [x] H, `QueryEngine` retrieves four blocks with sub-budgeted tokens via `_collect_retrieval_context()` (profile 20% / memory 25% / knowledge 55%, reference Phase 2)
- [x] I, `chat_system.md` updated with labelled blocks + usage rules
- [x] J, Chinese-character bug root-caused: **not an ingest parser bug**: Qwen2.5-7B hallucinates CJK tokens during mem0 fact extraction on short/garbled chunks. Routing bulk sources to Knowledge (no LLM extraction) eliminates it structurally; remaining memory-layer sources should run with `--llm claude`. No source exclusion needed.
- [ ] K, Qdrant backup taken, `zeus_memories` dropped, re-ingest completed, spot-checks pass

## Phase 2: Reference layer (after Phase 1 lands)

- Live HTTP proxy to kiwix-serve for Wikipedia ZIM lookups at retrieval time.
- Live HTTP proxy to Project NOMAD's Qdrant RAG (see `zeus/docs/project-nomad-integration.md`).
- Optional `zeus_cache_reference` collection for re-embedding frequently-hit snippets.
- Add `Reference` block to QueryEngine with its 10% sub-budget.
- New Linear ticket; not started until Phase 1 ships and eval shows Knowledge recall is healthy.

## Phase 3: Retrieval eval (LAB-61 child)

- Extend `tests/retrieval_eval.py` with labelled ground-truth queries:
  - `profile_questions.yaml`, expected to hit Profile/Memory
  - `knowledge_questions.yaml`, expected to hit Knowledge (pull from known Obsidian notes / newsletters)
- Measure recall@5 per layer, log to `zeus/data/retrieval_eval.json`.
- Use results to retune sub-budget percentages.

## Open questions / notes

- **Chinese characters**: user confirmed all notes are English. Almost certainly from a PDF/image screenshot being passed through a parser that invented CJK glyphs, or from a source that mis-detects encoding. Suspect first: any markdown file generated by screenshot-OCR tooling under `zeus/data/raw/notes/`. Task J should grep the raw files for CJK codepoints and trace back.
- **Wikipedia ZIM**: compressed is ~100GB; decompressed index would be huge. Do NOT ingest. Reference layer only.
- **NOMAD**: has its own Qdrant RAG already. Reference layer proxies it; we do not duplicate.
- **Back-compat**: once Phase 1 lands, the old single-block prompt is gone. No migration flag, we commit to the new shape.

## Linear tickets to file

- `LAB-XXX` Memory/Knowledge layer split (Phase 1 parent)
- `LAB-XXX` Declarative ingest config (`ingest/config.yaml`)
- `LAB-XXX` Reference layer proxy (Phase 2)
- `LAB-XXX` Retrieval eval extension (Phase 3, child of LAB-61)
- `LAB-XXX` Chinese-character ingest bug (Phase 1, task J)

File these when Phase 1 work actually starts, don't pre-create empty tickets.
