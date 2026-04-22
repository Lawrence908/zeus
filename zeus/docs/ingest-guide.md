# Iris Ingest Guide

What personal data to feed into Zeus, in what order, and how each source lands. Iris now writes to two collections:

- **Mnemosyne** (`zeus_memories`): curated profile sources pass through LLM fact extraction via `small_llm_call`. 100–500 items, tight signal. Sources: `context_pack`, `gcal`.
- **Library / Knowledge** (`zeus_knowledge`): bulk sources are embedded and upserted raw; no LLM on the write path. 10k–1M chunks, high recall. Sources: `markdown`, `obsidian`, `chatgpt`, `email`, `newsletter`, `bookmarks`, `git`.

Routing is declared in [zeus/ingest/config.yaml](../ingest/config.yaml) under each source's `target`. CLI flags override per-invocation:

```bash
python -m zeus.ingest.run --target memory      # curated only
python -m zeus.ingest.run --target knowledge   # bulk only
python -m zeus.ingest.run --target both        # full run (default)
```

All raw data lives in `zeus/data/raw/` which is gitignored. Never commit personal data to the repo.

## Priority order

### 1. `context_pack.md` (do this first)

The single highest-signal document you will ever ingest. Hand-written markdown covering identity, homelab, projects, goals, preferences, key people. Fact-extracted into `zeus_memories`.

Create at `zeus/data/raw/context_pack.md`. Template sections:

```markdown
# Chris — Personal Context Pack
# Last updated: YYYY-MM-DD

## Identity
## Homelab Infrastructure
## Current Projects (as of YYYY-MM-DD)
## Skills & Tools I Use Daily
## Goals (next 6 months)
## Preferences & Working Style
## Key People
## Things I'm Learning Right Now
## Recurring Commitments
```

Ingest:

```bash
python -m zeus.ingest.run --source context_pack
```

Re-run whenever you edit the file. Idempotent.

### 2. Obsidian vault

Offline RAG over daily notes, class notes, project journals. Bulk source to `zeus_knowledge`. See [obsidian-livesync-ingest.md](obsidian-livesync-ingest.md) for the LiveSync pipeline that keeps a headless mirror at `/home/chris/data/headless-obsidian-vault` in sync with CouchDB.

```bash
python -m zeus.ingest.run --source obsidian --dry-run
python -m zeus.ingest.run --source obsidian
```

### 3. Markdown under `zeus/data/raw/notes/`

Any tree of markdown: context-pack core, jobkit archive, engineering notes. Symlinks recommended; see [ingest-paths.md](ingest-paths.md).

```bash
python -m zeus.ingest.run --source markdown --dry-run
python -m zeus.ingest.run --source markdown
```

### 4. ChatGPT export

Years of conversational history. By default Iris indexes only your messages (`role: user`); flip `roles={"user","assistant"}` on `ChatGPTSource` if you want Claude's answers too.

Export: ChatGPT → Settings → Data Controls → Export. Drop the unzipped `conversations.json` at `zeus/data/raw/chat-history/` or set `CHATGPT_EXPORT_PATH`.

```bash
python -m zeus.ingest.run --source chatgpt --dry-run
python -m zeus.ingest.run --source chatgpt
```

Expect thousands to tens of thousands of chunks.

### 5. Secondary sources

| Source | Target | Notes |
|--------|--------|-------|
| `newsletter` | knowledge | IMAP fetch, see LAB-336 in ticket plan |
| `email` | knowledge | Starred / sent only by default |
| `bookmarks` | knowledge | Parses browser HTML export |
| `git` | knowledge | Commit messages from configured repos |
| `gcal` | memory | Calendar events, profile-shaped |

Each source has its own config block in `zeus/ingest/config.yaml`. Run with `--source <name>` or run all with no flag (respects per-source `target`).

## Fact extraction contract (memory layer)

Memory-layer sources go through `small_llm_call(response_format=FactExtraction, min_privacy_tier=1)` against the prompt in [zeus/core/prompts/memory_extract.md](../core/prompts/memory_extract.md). Hard constraints baked in:

- English only.
- Maximum 10 facts per chunk.
- Atomic claims, no speculation.
- `confidence < 0.6` facts are dropped.
- `contains_pii=true` is set on any fact containing names, emails, addresses.

Payloads use ISO-8601 strings for `created_at` / `updated_at`, `valid_from` / `valid_until`. Re-ingest is idempotent via `delete_by_source(source, source_id)`.

## Knowledge layer contract

Knowledge-layer sources embed with `nomic-embed-text:v1.5` (768-dim cosine) and upsert directly. With `ZEUS_KNOWLEDGE_HYBRID=1` (default), a named sparse BM25 vector is written alongside the dense vector so `search()` can fuse dense + sparse via RRF. Optional reranker (`ZEUS_KNOWLEDGE_RERANK=1`, `ZEUS_RERANKER_MODEL=BAAI/bge-reranker-v2-m3`) re-orders top-k candidates on CPU or the 5080.

No LLM is called on the knowledge write path; writes are fast and cheap. Idempotent via `KnowledgeStore.delete_by_source(source, source_id)`.

## Quality tips

- **Re-ingest whenever `context_pack.md` changes.** It is the tuning lever for grounded replies.
- **Chunk size default is 512 tokens with 64 overlap.** Drop to 128 for very short notes; raise for long-form writing.
- **Don't ingest**: chat logs with other people, work comms you don't own, credentials or tokens, any note marked `private: true` in frontmatter.
- **Watch the small-LLM usage DB** (`zeus/data/small_llm_usage.db`) after a memory-layer run; extraction cost should be a few cents at most per 100 chunks.

## Verifying a run

```bash
# Qdrant point counts
curl -s http://localhost:6333/collections/zeus_memories | jq '.result.points_count'
curl -s http://localhost:6333/collections/zeus_knowledge | jq '.result.points_count'

# Profile-shaped probe
curl -s -X POST localhost:8203/context/profile | jq '.facts[].text'

# Knowledge probe
curl -s -X POST localhost:8203/memory/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"hash tables class notes","limit":5}' | jq
```

## Retrieval eval

Baseline (30 hand-written queries on current knowledge corpus) lives at [tests/retrieval_eval_baseline.json](../../tests/retrieval_eval_baseline.json): hit@1=0.60, hit@5=0.867, hit@10=0.933, MRR@10=0.71.

Gate every retrieval-config change through the harness:

```bash
python -m zeus.memory.eval --query-set zeus/data/eval/queries.json --top-k 10
```

Tune `chunk_size`, `chunk_overlap`, `ZEUS_KNOWLEDGE_HYBRID`, `ZEUS_KNOWLEDGE_RERANK`, reranker device. Commit both the resulting JSON and the setting change together.

## Adding a new source

```python
# zeus/ingest/sources/<name>.py
from typing import AsyncIterator
from zeus.ingest.types import Chunk, chunk_text

class <Name>Source:
    target = "knowledge"   # or "memory"

    def __init__(self, ..., chunk_size=512, chunk_overlap=64, user_id="chris"):
        ...

    async def chunks(self) -> AsyncIterator[Chunk]:
        for item in self._load():
            for text in chunk_text(item.text, self.chunk_size, self.chunk_overlap):
                yield Chunk(
                    text=text,
                    source=f"<name>:{item.identifier}",
                    metadata={"type": "<name>", ...},
                    user_id=self.user_id,
                )
```

Register in `zeus/ingest/run.py:build_sources()` and add a block in `zeus/ingest/config.yaml`. Class-level `target` decides which store receives chunks.
