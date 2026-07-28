#!/usr/bin/env bash
# scripts/aletheia-post-receive.sh — git post-receive hook for Aletheia.
#
# Install into a server-side bare repo (or symlink from .git/hooks/post-receive
# on a non-bare working repo you push to) to fire an *incremental* Aletheia sweep
# scoped to the docs whose referenced paths intersect the pushed change set.
#
# It computes the changed paths for each pushed ref and POSTs them to the
# Aletheia API. The endpoint only ever triggers a read-only investigation, so
# this hook cannot start a writing run. If the POST is inconvenient to wire, the
# nightly Kronos sweep covers the same ground on a delay.
#
# Env:
#   ZEUS_ALETHEIA_URL   base URL of the zeus-core API (default http://127.0.0.1:8203)
set -euo pipefail

ZEUS_URL="${ZEUS_ALETHEIA_URL:-http://127.0.0.1:8203}"

# post-receive reads "<oldrev> <newrev> <refname>" lines on stdin.
changed=""
while read -r oldrev newrev _refname; do
  if [[ "$oldrev" =~ ^0+$ ]]; then
    # New branch: diff against the newrev's parent, or list its tree.
    files=$(git diff-tree --no-commit-id --name-only -r "$newrev" 2>/dev/null || true)
  else
    files=$(git diff --name-only "$oldrev" "$newrev" 2>/dev/null || true)
  fi
  changed+=$'\n'"$files"
done

# De-dup, drop blanks, JSON-encode as an array.
paths_json=$(printf '%s\n' "$changed" | sed '/^$/d' | sort -u | \
  awk 'BEGIN{printf "["} {printf "%s\"%s\"", (NR>1?",":""), $0} END{printf "]"}')

if [[ "$paths_json" == "[]" ]]; then
  exit 0
fi

curl -fsS -X POST "$ZEUS_URL/aletheia/runs" \
  -H 'Content-Type: application/json' \
  -d "{\"mode\":\"incremental\",\"changed_paths\":$paths_json}" \
  >/dev/null 2>&1 || echo "aletheia: notify failed (is zeus-core up?)" >&2

exit 0
