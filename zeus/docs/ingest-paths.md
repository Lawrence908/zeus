# Zeus ingest paths (Iris / Mnemosyne)

Where personal context lives, how it links into Zeus, and how to run ingest.

## Raw data directory

From the **Zeus repo root** (`…/zeus/`), all local exports and mirrors live under:

- `zeus/data/raw/`

This tree is **gitignored**. Do not commit exports, vault copies, or secrets here.

## Curated baseline

- **`zeus/data/raw/context_pack.md`** — Single markdown file you maintain. Highest signal; ingest this first via the `context_pack` source.

## Optional layout

| Path | Purpose |
|------|---------|
| `zeus/data/raw/context_pack.md` | Identity, homelab, projects, goals (hand-curated) |
| `zeus/data/raw/notes/` | Symlinks or copies from other repos / vaults |
| `zeus/data/raw/chatgpt_export.json` | ChatGPT export (if used) |

**Rule of thumb:** Curated facts → `context_pack.md`. Bulk notes → predictable subfolders under `zeus/data/raw/` so glob patterns stay stable.

## Symlinks on this machine

`zeus/data/raw/` is ignored by git, so symlinks are **local only**. After a fresh clone, recreate them (adjust paths if your home layout differs):

```bash
RAW="zeus/data/raw"
mkdir -p "$RAW/notes"
ln -sfn /home/chris/services/context-pack/core       "$RAW/notes/context-pack-core"
ln -sfn /home/chris/services/context-pack/writing    "$RAW/notes/context-pack-writing"
ln -sfn /home/chris/apps/jobkit/archive/data         "$RAW/notes/jobkit-archive"
```

| Link | Target |
|------|--------|
| `notes/context-pack-core` | `/home/chris/services/context-pack/core` |
| `notes/context-pack-writing` | `/home/chris/services/context-pack/writing` |
| `notes/jobkit-archive` | `/home/chris/apps/jobkit/archive/data` (JobKit **archive** only — not `apps/jobkit/data/demo/`) |

The JobKit link covers `resume_base.yml`, `profile.yml`, `projects/*.md`, and the rest of that archive tree in one place.

## Ingest commands

From Zeus repo root, with venv activated and `.env` loaded:

**Context pack file**

```bash
python3 -m zeus.ingest.run --source context_pack
```

**Markdown under raw (dry-run first)**

```bash
python3 -m zeus.ingest.run --source markdown \
  --glob "notes/**/*.md" \
  --base-dir zeus/data/raw \
  --dry-run
```

Remove `--dry-run` when the preview looks right.

## Markdown vs YAML under `notes/`

The `markdown` source is tuned for `.md` (heading-aware splits, YAML frontmatter stripping). YAML files (e.g. `resume_base.yml`, `profile.yml`) are still read as text and chunked, but without markdown headings you get larger, less structured chunks — usually acceptable for factual baselines.
