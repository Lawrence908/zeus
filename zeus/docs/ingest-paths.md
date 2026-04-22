# Zeus ingest paths (Iris / Mnemosyne)

Where personal context lives, how it links into Zeus, and how to run ingest.

## Raw data directory

From the **Zeus repo root** (`…/zeus/`), all local exports and mirrors live under:

- `zeus/data/raw/`

This tree is **gitignored**. Do not commit exports, vault copies, or secrets here.

## Curated baseline

- **`zeus/data/raw/context_pack.md`**: single markdown file you maintain. Highest signal. Routes to the memory layer (LLM fact extraction). Ingest first via the `context_pack` source.

## Optional layout

| Path | Purpose |
|------|---------|
| `zeus/data/raw/context_pack.md` | Identity, homelab, projects, goals (hand-curated) |
| `zeus/data/raw/notes/` | Symlinks or copies from other repos / vaults |
| `zeus/data/raw/chat-history/` | ChatGPT export dir (conversations-NNN.json files) |

**Rule of thumb:** Curated facts → `context_pack.md`. Bulk notes → predictable subfolders under `zeus/data/raw/` so glob patterns stay stable.

**Obsidian (Self-hosted LiveSync):** Keep a vault directory on disk (Obsidian app or [LiveSync CLI](https://github.com/vrtmrz/obsidian-livesync)), symlink it under `notes/`, then schedule markdown ingest. Full steps: [obsidian-livesync-ingest.md](obsidian-livesync-ingest.md).

## Symlinks on this machine

`zeus/data/raw/` is ignored by git, so symlinks are **local only**. After a fresh clone, recreate them (adjust paths if your home layout differs):

```bash
RAW="zeus/data/raw"
mkdir -p "$RAW/notes"
ln -sfn /home/chris/services/context-pack/core       "$RAW/notes/context-pack-core"
ln -sfn /home/chris/services/context-pack/writing    "$RAW/notes/context-pack-writing"
ln -sfn /home/chris/apps/jobkit/archive/data         "$RAW/notes/jobkit-archive"
ln -sfn /home/chris/data/headless-obsidian-vault     "$RAW/notes/obsidian-vault"
```

| Link | Target |
|------|--------|
| `notes/context-pack-core` | `/home/chris/services/context-pack/core` |
| `notes/context-pack-writing` | `/home/chris/services/context-pack/writing` |
| `notes/jobkit-archive` | `/home/chris/apps/jobkit/archive/data` (JobKit **archive** only, not `apps/jobkit/data/demo/`) |
| `notes/obsidian-vault` | `/home/chris/data/headless-obsidian-vault` (LiveSync CLI mirror target on daedalus; see [obsidian-livesync-ingest.md](obsidian-livesync-ingest.md)) |

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

**Obsidian-linked vault** (after symlink above):

```bash
python3 -m zeus.ingest.run --source markdown \
  --glob "notes/obsidian-vault/**/*.md" \
  --base-dir zeus/data/raw \
  --dry-run
```

## Scheduled ingest (cron)

For sources that change on disk without you running the CLI (e.g. LiveSync updates), run the same ingest command on a timer. Example: every three hours, from repo root with venv and `.env` loaded. Adapt paths to your machine:

```cron
10 */3 * * * cd /path/to/zeus-repo && . .venv/bin/activate && set -a && . ./.env && set +a && python3 -m zeus.ingest.run --source markdown --glob "notes/obsidian-vault/**/*.md" --base-dir zeus/data/raw
```

If you use the headless LiveSync CLI, run **sync then ingest** in order (one wrapper script or two cron entries). Details: [obsidian-livesync-ingest.md](obsidian-livesync-ingest.md).

**N.O.M.A.D.:** catalogs or exports under `zeus/data/raw/nomad/` (or symlinks) can use the same cron pattern with a different `--glob`. See [project-nomad-integration.md](project-nomad-integration.md).

## Markdown vs YAML under `notes/`

The `markdown` source is tuned for `.md` (heading-aware splits, YAML frontmatter stripping). YAML files (e.g. `resume_base.yml`, `profile.yml`) are still read as text and chunked, but without markdown headings you get larger, less structured chunks; usually acceptable for factual baselines.
