# Iris Ingest Guide — Data Sources and Ordering

This guide covers what personal data to feed into mnemosyne, in what order, and how to prepare each source before running Iris. The order matters — start with the highest-signal data so you have a useful Zeus after the first ingest, then add volume.

All raw data lives in `zeus/data/raw/` which is gitignored. Never commit personal data to the repo.

---

## Ingest Order (Priority)

### 1. `context_pack.md` — Hand-written personal context (do this first)

This is a single markdown file you write by hand. It is the most valuable thing you can ingest because it contains structured, accurate facts about you that Zeus will use as baseline context for every query.

**Why first:** Sparse personal data + lots of ChatGPT noise = bad recall. The context pack gives Zeus a clean foundation before any noisy source is added.

**Create it at:** `zeus/data/raw/context_pack.md`

**Template — fill in all sections:**

```markdown
# Chris — Personal Context Pack
# Last updated: YYYY-MM-DD
# This file is hand-curated. Update it monthly or when major things change.

## Identity
- Full name: Chris Lawrence
- Location: [city, country]
- Timezone: [e.g. America/Toronto]
- Occupation: CS student + self-hosted homelab operator
- School: [institution], graduating [date]

## Homelab Infrastructure
- Olympus: RTX 3080 server, 10GB VRAM, Proxmox host, production workloads
- Apollo (tower): RTX 5080, 16GB VRAM, dev/test machine
- Hermes (NAS): [storage specs], runs [services]
- Network: [any relevant topology notes]
- Key services running: [list what's self-hosted]

## Current Projects (as of [date])
- Zeus: self-hosted personal AI assistant — currently in Sprint 1 (memory layer)
- [other projects with brief status]

## Skills & Tools I Use Daily
- Languages: Python (primary), [others]
- Infra: Proxmox, Docker, [others]
- AI/ML: Claude API, Ollama, [others]

## Goals (next 6 months)
- [list 3-5 concrete goals]

## Preferences & Working Style
- [e.g. I prefer CLI tools over GUIs]
- [e.g. I self-host everything possible for privacy]
- [e.g. I work best in the evenings]

## Key People
- [family / colleagues / collaborators and brief context]

## Things I'm Learning Right Now
- [list topics actively studying]

## Recurring Commitments
- [classes, meetings, deadlines]
```

**Ingest command:**
```bash
python -m zeus.ingest.run --source markdown --glob "context_pack.md" --base-dir zeus/data/raw --dry-run
# Check output looks sensible
python -m zeus.ingest.run --source markdown --glob "context_pack.md" --base-dir zeus/data/raw
```

---

### 2. Notes / Markdown files

Any notes you've written over time: Obsidian vault, Bear exports, Notion exports, plain `.md` files, engineering notes, project journals.

**Prepare:**
- Export from your notes app as markdown (most support this)
- Place in `zeus/data/raw/notes/`
- No special formatting required — Iris strips frontmatter and splits on headings automatically

**Filter before ingesting:**
- Remove anything you don't want Zeus to reference (meeting notes with other people's PII, sensitive info)
- Iris doesn't filter content — it stores what you give it

**Ingest command:**
```bash
# Preview first
python -m zeus.ingest.run --source markdown --glob "notes/**/*.md" --base-dir zeus/data/raw --dry-run

# Check chunk count and spot-check some chunks look coherent
# Then go live
python -m zeus.ingest.run --source markdown --glob "notes/**/*.md" --base-dir zeus/data/raw
```

**Chunk size note:** The default 512-word chunks work well for notes. If your notes are very short (tweet-length), consider dropping `--chunk-size` to 128 so you don't merge unrelated notes.

---

### 3. ChatGPT Export

Your conversation history with ChatGPT contains a lot of signal about how you think, what you've worked on, and what you've asked for help with.

**Export:**
1. ChatGPT → Settings → Data Controls → Export Data
2. You'll receive an email with a download link (can take up to an hour)
3. Unzip → rename `conversations.json` → place at `zeus/data/raw/chatgpt_export.json`

**What gets ingested:** By default, only your messages (role: `user`). This captures your questions, preferences, and context without also ingesting all the AI's responses, which adds noise without adding personal signal.

**Optionally include assistant responses:** If you want to capture answers you've relied on (e.g. you asked for an explanation of something and memorised it), edit `ChatGPTSource` default to `roles={"user", "assistant"}`. Not recommended for first ingest — see how user-only performs first.

**Ingest command:**
```bash
python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chatgpt_export.json --dry-run
# This will log chunk count — can be large (thousands of chunks)
python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chatgpt_export.json
```

**Expect:** A large ChatGPT export (years of history) will produce 5,000–30,000 chunks. This is fine — Qdrant handles it easily and mem0's hybrid search will surface the relevant ones.

---

### 4. Engineering Notes & Project Docs

Markdown files specific to ongoing projects: architecture decisions, setup notes, debugging notes, TODO lists.

**Example paths to ingest:**
```bash
# If you have notes in the zeus repo itself
python -m zeus.ingest.run --source markdown --glob "docs/**/*.md" --base-dir zeus

# Project notes outside the repo
python -m zeus.ingest.run --source markdown --glob "**/*.md" --base-dir ~/projects/notes
```

---

### 5. Future Sources (Sprint 1 → Sprint 2)

These require writing a new source parser following the `IngestSource` protocol.

**Obsidian vault** (`zeus/ingest/sources/obsidian.py`):
- Obsidian uses standard markdown with `[[wikilinks]]` syntax
- The markdown parser handles most of it; strip `[[` / `]]` from links before chunking
- Daily notes are especially valuable — they're a log of what you actually did

**Git commit messages** (`zeus/ingest/sources/git.py`):
- `git log --all --pretty=format:"%H %ai %s%n%b"` gives you date + subject + body
- Filter to repos you want Zeus to know about
- Useful for "what did I work on last week"

**Calendar events** (`zeus/ingest/sources/gcal.py`):
- Google Calendar API → export recurring commitments and one-off events
- Focus on past events for context, upcoming events for task awareness
- Store as structured text: `2024-03-15 10:00: Meeting with [person] about [topic]`

**Browser bookmarks** (`zeus/ingest/sources/bookmarks.py`):
- Export from browser → parse the HTML bookmark file
- Include title + URL + folder path
- Gives Zeus insight into what tools/sites you use and reference

---

## Source Parser Template

To add a new source, create `zeus/ingest/sources/<name>.py` following this pattern:

```python
# zeus/ingest/sources/<name>.py — Iris <Name> source parser
from typing import AsyncIterator
from zeus.ingest.pipeline import Chunk, chunk_text


class <Name>Source:
    def __init__(self, ..., chunk_size: int = 512, chunk_overlap: int = 64, user_id: str = "chris"):
        ...

    async def chunks(self) -> AsyncIterator[Chunk]:
        # Parse your source format here
        for item in self._load():
            for text in chunk_text(item.text, self.chunk_size, self.chunk_overlap):
                yield Chunk(
                    text=text,
                    source=f"<name>:{item.identifier}",
                    metadata={"type": "<name>", ...},
                    user_id=self.user_id,
                )
```

Then add it to `zeus/ingest/run.py`'s `build_sources()` function and to `zeus/orchestration/agents/iris.yaml`'s `config.sources` list.

---

## Memory Quality Tips

**Re-ingest frequently:** mnemosyne deduplicates by content hash (mem0 handles this), so re-running ingest on the same files is safe. Run it weekly to pick up new notes.

**Context pack is your tuning lever:** If Zeus gives bad answers, check if the context pack is stale. Update it and re-ingest — it takes 30 seconds and often fixes the problem.

**Chunk size tradeoffs:**
- Large chunks (512+ words): better semantic coherence, fewer results returned per query
- Small chunks (128 words): higher recall granularity, but may fragment context
- Default 512 is the right starting point; tune down if you're getting irrelevant results

**What not to ingest:**
- Chat logs with other people (privacy)
- Work communications unless fully self-owned
- Credentials, keys, secrets (check your notes for these before ingesting)
- Large binary descriptions (PDFs of textbooks, etc.) — too much noise relative to signal

---

## Checking Ingest Quality

After each source ingest, spot-check with a few queries through Oracle:

```bash
# Start oracle if not running
uvicorn zeus.api.main:app --port 8001 --reload

# Test queries
curl -s -X POST localhost:8001/context/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what homelab servers do I run", "top_k": 3}' | python3 -m json.tool

curl -s -X POST localhost:8001/context/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what am I currently working on", "top_k": 5}' | python3 -m json.tool
```

Good results: relevant chunks with high scores, diverse sources. Bad results: irrelevant chunks, very low scores, all from the same source. If quality is poor, check your context pack first, then look at chunk sizes.
