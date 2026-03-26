# Obsidian Self-hosted LiveSync → Zeus (Iris)

Recommended pipeline: **CouchDB ↔ local vault directory ↔ symlink under `zeus/data/raw/notes/` ↔ scheduled markdown ingest** into mnemosyne (mem0 + Qdrant). Zeus does not connect to CouchDB; it only reads **files on disk** that LiveSync keeps current.

Upstream: [vrtmrz/obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync) (Obsidian plugin and **official CLI** for headless sync).

## Why this shape

- One pipeline to reason about: sync produces a normal tree of `.md` files; Iris already chunks markdown well.
- No manual “export this week” step if cron (or a timer) re-runs ingest after sync.
- `zeus/data/raw/` is gitignored; vault content and CouchDB credentials stay out of the repo.

## 1. Local vault directory

Pick a **fixed path** for the vault root on this machine. On daedalus the headless mirror is:

- `/home/chris/data/headless-obsidian-vault`

That folder should look like an Obsidian vault (markdown notes, optional `.obsidian/` config, and `.livesync/settings.json` for the CLI). You may never open Obsidian there; it still works as the mirror target.

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

1. **Sync** — CLI (or Obsidian) replicates CouchDB into the local DB.
2. **Mirror** — CLI writes DB → files on disk.
3. **Ingest** — Zeus indexes `.md` into mnemosyne.

Use the wrapper **`scripts/replicate-obsidian-and-ingest.sh`** (sync + mirror + ingest). Cron setup is in [Cron: how to install the job](#cron-how-to-install-the-job) below.

## What you should see on disk

- **Markdown and attachments** — After a successful **`mirror`**, notes appear as normal paths under your vault root, e.g. `…/headless-obsidian-vault/SomeNote.md`, `…/headless-obsidian-vault/ASTR311/…`, etc.
- **Folder like `headless-obsidian-vault-fa1dd4bf-…-livesync-v2/`** — That is the CLI’s **local LevelDB / PouchDB** store (internal). It is **not** your notes tree. Ignore it for Zeus; ingest globs should target `**/*.md` alongside it, not inside it.

## If `sync` fails (no `.md` files yet)

`mirror` only materializes files after the local DB has been filled by replication. If the CLI prints `[Error] Command 'sync' failed`:

1. **Capture the real reason** — Notices often go to stderr and are easy to miss. Run:
   ```bash
   LIVESYNC_DEBUG=1 /home/chris/apps/obsidian-livesync/sync-headless-vault.sh 2>&1 | tee /tmp/livesync-sync.log
   ```
   Then search the log for `Notice`, `Failed`, `denied`, `corrupted`, `PBKDF2`, `VersionUpFlash`, `Pending`, `Locked`.
2. **Use loopback CouchDB on daedalus** — In `.livesync/settings.json`, set `couchDB_URI` to `http://127.0.0.1:5984` (same DB as Docker on this host). Re-copy from Obsidian or edit the plaintext fields if you are not relying only on `encryptedCouchDBConnection`. Hairpin via Tailscale to yourself can be flaky.
3. **Clear plugin “changelog / version” gate** — If Obsidian had `versionUpFlash` set, copy a fresh `data.json` from the PC or clear that field after plugin updates (see LiveSync docs).
4. **Remote lock / fetch** — If the desktop app says the remote is locked or asks to **Fetch** again, resolve that in Obsidian first; then retry CLI sync.

When `sync` succeeds, run `mirror` (or the wrapper script); you should then see real folders and `.md` files next to the `*-livesync-v2` directory.

### Remote database locked (`NODE_LOCKED`) and `Method not implemented`

If the log shows:

`The remote database has been rebuilt or corrupted…` then `Error: Method not implemented` at `HeadlessConfirm.askSelectStringDialogue`, the CouchDB **milestone** is **locked** and this headless device’s node ID is not yet in `accepted_nodes`. Obsidian would show a three-button dialog; the CLI had no way to answer it until you set a non-interactive choice.

**After rebuilding the LiveSync CLI** from a tree that includes the headless `askSelectStringDialogue` implementation, run **one** of:

```bash
# Prefer for a brand-new headless copy: reset local sync state and fetch from remote (button order: Fetch, Unlock, Dismiss)
LIVESYNC_HEADLESS_DIALOG_INDEX=0 /home/chris/apps/obsidian-livesync/sync-headless-vault.sh
```

Or add this device without wiping local state (only if you understand the plugin warning—usually use Fetch for an empty headless vault):

```bash
LIVESYNC_HEADLESS_DIALOG_INDEX=1 /home/chris/apps/obsidian-livesync/sync-headless-vault.sh
```

Substring match (works across locales if the label contains the word):

```bash
LIVESYNC_HEADLESS_DIALOG_CHOICE=reset /home/chris/apps/obsidian-livesync/sync-headless-vault.sh   # Fetch / reset sync
LIVESYNC_HEADLESS_DIALOG_CHOICE=unlock /home/chris/apps/obsidian-livesync/sync-headless-vault.sh
```

**After a successful Unlock** you should see: `The remote database has been unlocked. Please retry the operation.` The process still exits with `[Error] Command 'sync' failed` — that only means “no replication ran *this* invocation.” **Run `sync` again immediately** (no `LIVESYNC_HEADLESS_*` needed unless the dialog appears again):

```bash
/home/chris/apps/obsidian-livesync/sync-headless-vault.sh
```

Then let **`mirror`** run (same script does both).

**Fetch (dialog index 0) in headless mode:** Choosing “Reset Synchronisation…” schedules a fetch that normally opens another **Svelte wizard** in the app. In the CLI that path is **not** fully headless; you may get `flag_fetch.md` and a failed `sync` exit. For a dedicated headless replica, **Unlock (index 1)** once, then **retry `sync`**, is usually the right sequence. If you tried Fetch and have a stale flag file, remove it:

`rm -f /home/chris/data/headless-obsidian-vault/flag_fetch.md /home/chris/data/headless-obsidian-vault/redflag3.md`

**Alternative:** Resolve the lock entirely in **Obsidian** on a trusted device (same vault / CouchDB), then retry headless `sync`.

## Cron: how to install the job

1. On daedalus: `crontab -e`
2. Add one line (adjust minute/path/log dir):

   ```cron
   12 * * * * /home/chris/zeus/scripts/replicate-obsidian-and-ingest.sh >> /home/chris/logs/zeus-obsidian-ingest.log 2>&1
   ```

3. Ensure the log directory exists: `mkdir -p /home/chris/logs`

Cron uses **your user’s** environment; the script activates `/home/chris/zeus/.venv` and loads `/home/chris/zeus/.env` itself, so you do not need to duplicate that in the crontab.

## Large attachments and non-markdown files

The markdown source ingests `.md` per your glob. Binary attachments (PDFs, images) are skipped unless you add another source. If the vault is huge, prefer a **dedicated subfolder** of high-signal notes for Zeus, or a narrower glob, to control embedding cost and noise.

## Related

- [ingest-paths.md](ingest-paths.md) — raw layout and symlink conventions
- [ingest-guide.md](ingest-guide.md) — ordering and source priorities
- [project-nomad-integration.md](project-nomad-integration.md) — parallel integration for N.O.M.A.D.
