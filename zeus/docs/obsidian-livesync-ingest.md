# Obsidian Self-hosted LiveSync → Zeus (Iris)

Recommended pipeline: **CouchDB ↔ local vault directory ↔ symlink under `zeus/data/raw/notes/` ↔ scheduled markdown ingest** into mnemosyne (mem0 + Qdrant). Zeus does not connect to CouchDB; it only reads **files on disk** that LiveSync keeps current.

Upstream: [vrtmrz/obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync) (Obsidian plugin and **official CLI** for headless sync).

## Why this shape

- One pipeline to reason about: sync produces a normal tree of `.md` files; Iris already chunks markdown well.
- No manual “export this week” step if cron (or a timer) re-runs ingest after sync.
- `zeus/data/raw/` is gitignored; vault content and CouchDB credentials stay out of the repo.

## 1. Local vault directory

Pick a **fixed path** for the vault root on this machine, for example:

- `~/obsidian-vault`

That folder should look like an Obsidian vault (markdown notes, optional `.obsidian/` config). You may never open Obsidian there; it still works as the mirror target.

## 2. Keep it in sync with CouchDB

### Option A — Obsidian on this machine

1. Install Obsidian.
2. Open or create a vault at your chosen path (e.g. `~/obsidian-vault`).
3. Enable **Self-hosted LiveSync** and point it at the **same CouchDB** you use elsewhere.

Notes are written to disk by the plugin; Zeus only needs read access to that tree.

### Option B — Headless (no Obsidian UI)

1. Install and configure the **LiveSync CLI** from [vrtmrz/obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync) (sync, then mirror into your vault directory).
2. Use the **same** fixed path as your mirror root so paths in this doc stay stable.

Follow upstream docs for credentials, passphrase, and non-interactive use; do not store secrets in the Zeus repo.

## 3. Link the vault into Zeus raw data

From the **Zeus repo root** (the directory that contains `zeus/data/raw/`):

```bash
RAW="zeus/data/raw"
mkdir -p "$RAW/notes"
ln -sfn "$HOME/obsidian-vault" "$RAW/notes/obsidian-vault"
```

Adjust `obsidian-vault` symlink name or target if your path differs. See also [ingest-paths.md](ingest-paths.md) for the full symlink table.

## 4. Ingest (manual first)

Activate your venv, load `.env`, then preview:

```bash
python3 -m zeus.ingest.run --source markdown \
  --glob "notes/obsidian-vault/**/*.md" \
  --base-dir zeus/data/raw \
  --dry-run
```

If the preview is too noisy or picks up plugin noise, narrow the glob (e.g. a `notes/obsidian-vault/Notes/**/*.md` subfolder) or exclude paths via a dedicated subfolder you only use for Zeus-facing notes.

Remove `--dry-run` when the chunks look right.

## 5. Schedule sync + ingest

Typical pattern:

1. **Sync** — Obsidian stays running, or CLI runs on a schedule to refresh the mirror.
2. **Ingest** — Cron every hour or few hours calls the same `python3 -m zeus.ingest.run …` command after sync.

Example cron entry (runs ingest at minute 10 past every 3rd hour; edit paths and user):

```cron
10 */3 * * * cd /home/chris/zeus && . .venv/bin/activate && set -a && . ./.env && set +a && python3 -m zeus.ingest.run --source markdown --glob "notes/obsidian-vault/**/*.md" --base-dir zeus/data/raw
```

If you use the CLI for sync, chain **sync then ingest** in one script or two cron lines in order.

## Large attachments and non-markdown files

The markdown source ingests `.md` per your glob. Binary attachments (PDFs, images) are skipped unless you add another source. If the vault is huge, prefer a **dedicated subfolder** of high-signal notes for Zeus, or a narrower glob, to control embedding cost and noise.

## Related

- [ingest-paths.md](ingest-paths.md) — raw layout and symlink conventions
- [ingest-guide.md](ingest-guide.md) — ordering and source priorities
- [project-nomad-integration.md](project-nomad-integration.md) — parallel integration for N.O.M.A.D.
