#!/usr/bin/env bash
# scripts/check-docs.sh
# Pre-commit / pre-push doc freshness check for Zeus.
#
# Rules enforced:
#   1. No forbidden package names in current docs (mem0ai, litellm).
#      Historical mentions are allowed inside zeus/docs/legacy/ only.
#   2. Every .md file under docs/ and zeus/docs/ must be listed in docs/INDEX.md.
#   3. Emdashes in prose are warned (not fatal). Code fences and legacy/ are skipped.
#
# Install as a git hook:
#   ln -sf ../../scripts/check-docs.sh .git/hooks/pre-commit

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

fail=0

# --- 1. Forbidden package-name strings ------------------------------------
# These indicate stale claims that the repo still depends on mem0 or LiteLLM.
for needle in mem0ai litellm LiteLLM; do
    matches=$(
        grep -rn --include='*.md' -E "\\b${needle}\\b" docs/ zeus/docs/ CLAUDE.md README.md 2>/dev/null \
            | grep -v 'legacy/' \
            || true
    )
    if [[ -n "$matches" ]]; then
        # Allow lines that explicitly frame the mention as historical / forbidden / absent.
        filtered=$(echo "$matches" | grep -vE '(forbidden|removed|historical|retrospective|supply-chain|was removed|not in the chain|do not install|excluded|no (mem0|litellm|LiteLLM))' || true)
        if [[ -n "$filtered" ]]; then
            echo "ERROR: forbidden token '$needle' outside a historical framing:"
            echo "$filtered" | sed 's/^/  /'
            fail=1
        fi
    fi
done

# --- 2. INDEX.md coverage -------------------------------------------------
# Every current .md under docs/ and zeus/docs/ must appear by filename in docs/INDEX.md.
index_text="$(cat docs/INDEX.md)"
while IFS= read -r path; do
    case "$path" in
        */legacy/*) continue ;;
        docs/research/*) continue ;;  # generated research artifacts, not indexed docs
        docs/INDEX.md) continue ;;
    esac
    filename="$(basename "$path")"
    if ! grep -q -F "$filename" <<<"$index_text"; then
        echo "ERROR: $path not listed in docs/INDEX.md"
        fail=1
    fi
done < <(find docs zeus/docs -name '*.md' -type f | sort)

# Also ensure legacy files are indexed in the legacy section.
while IFS= read -r path; do
    filename="$(basename "$path")"
    if ! grep -q -F "$filename" <<<"$index_text"; then
        echo "ERROR: legacy $path not listed in docs/INDEX.md"
        fail=1
    fi
done < <(find zeus/docs/legacy -name '*.md' -type f 2>/dev/null | sort)

# --- 3. Emdash warnings ---------------------------------------------------
# Non-fatal. Fenced code blocks and legacy/ are skipped.
emdash_hits=0
while IFS= read -r path; do
    case "$path" in
        */legacy/*) continue ;;
        docs/research/*) continue ;;  # generated research artifacts, not curated prose
        # Ticket plan keeps emdashes inside ticket-title table cells by design.
        docs/ZEUS_LINEAR_TICKET_PLAN.md) continue ;;
    esac
    # Strip fenced code blocks (```...```).
    prose="$(awk 'BEGIN{fence=0} /^```/{fence=!fence; next} !fence' "$path")"
    if grep -q -- '—' <<<"$prose"; then
        lines=$(grep -n -- '—' <<<"$prose" | head -3)
        echo "WARN: emdash in prose: $path"
        echo "$lines" | sed 's/^/    /'
        emdash_hits=$((emdash_hits + 1))
    fi
done < <(find docs zeus/docs -name '*.md' -type f | sort)

if [[ "$fail" -eq 0 && "$emdash_hits" -eq 0 ]]; then
    echo "docs: clean"
fi

exit "$fail"
