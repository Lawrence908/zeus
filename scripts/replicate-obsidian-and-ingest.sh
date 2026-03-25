#!/usr/bin/env bash
# LiveSync CLI (sync + mirror) then Zeus markdown ingest for notes/obsidian-vault.
# Run from cron after headless vault + symlink are set up (see zeus/docs/obsidian-livesync-ingest.md).
#
# Environment:
#   ZEUS_ROOT      — repo root (default: /home/chris/zeus)
#   OBSIDIAN_SYNC  — path to sync-headless-vault.sh (default: apps/obsidian-livesync)
#   INGEST_DRY_RUN — set to 1 to pass --dry-run to ingest (no Qdrant writes)
set -euo pipefail

ZEUS_ROOT="${ZEUS_ROOT:-/home/chris/zeus}"
OBSIDIAN_SYNC="${OBSIDIAN_SYNC:-/home/chris/apps/obsidian-livesync/sync-headless-vault.sh}"

if [[ ! -x "$OBSIDIAN_SYNC" ]] && [[ -f "$OBSIDIAN_SYNC" ]]; then
  chmod +x "$OBSIDIAN_SYNC" 2>/dev/null || true
fi
"$OBSIDIAN_SYNC"

cd "$ZEUS_ROOT"
# shellcheck source=/dev/null
. .venv/bin/activate
set -a
[[ -f .env ]] && . ./.env
set +a

INGEST_ARGS=(
  python3 -m zeus.ingest.run
  --source markdown
  --glob "notes/obsidian-vault/**/*.md"
  --base-dir zeus/data/raw
)
if [[ "${INGEST_DRY_RUN:-0}" == "1" ]]; then
  INGEST_ARGS+=(--dry-run)
fi
"${INGEST_ARGS[@]}"
