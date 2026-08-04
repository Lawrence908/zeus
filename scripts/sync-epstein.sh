#!/usr/bin/env bash
# scripts/sync-epstein.sh — pull mainline work into the private `epstein` branch.
#
# The `epstein` branch is a long-lived PRIVATE branch that must never merge to
# main. Mainline (`zeus-os`) carries the commit that REMOVES Epstein from the
# mainline, so a plain `git merge zeus-os` would replay that deletion and wipe
# this branch's reason to exist. Instead, this script cherry-picks the mainline
# commits that are NOT yet on `epstein` (by patch-id, so already-shared commits
# like the original voice/themis work are skipped) and NOT in the exclude list.
#
# Usage:
#   scripts/sync-epstein.sh [--dry-run] [MAINLINE]
#     MAINLINE   branch to sync FROM (default: zeus-os)
#     --dry-run  show what would be picked/skipped, change nothing
#
# On a conflict the script stops mid-cherry-pick. Resolve it, then:
#   git cherry-pick --continue   (or: git cherry-pick --skip)
#   scripts/sync-epstein.sh      (re-run to finish the rest)
#
# Excludes: scripts/epstein-sync-exclude.txt (hashes), or a "[epstein-sync-skip]"
# line in a mainline commit message.
set -euo pipefail

PRIVATE_BRANCH="epstein"
SKIP_MARKER="[epstein-sync-skip]"

DRY_RUN=0
MAINLINE="zeus-os"
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    -*) echo "unknown option: $arg" >&2; exit 2 ;;
    *) MAINLINE="$arg" ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
EXCLUDE_FILE="$repo_root/scripts/epstein-sync-exclude.txt"

# Always address branches via refs/heads/ — the working tree has a `zeus-os/`
# directory, so a bare `zeus-os` is ambiguous to git.
mainline_ref="refs/heads/${MAINLINE}"
private_ref="refs/heads/${PRIVATE_BRANCH}"

die() { echo "sync-epstein: $*" >&2; exit 1; }

git rev-parse --verify --quiet "$mainline_ref" >/dev/null || die "no such branch: ${MAINLINE}"
git rev-parse --verify --quiet "$private_ref" >/dev/null || die "no such branch: ${PRIVATE_BRANCH}"

current="$(git rev-parse --abbrev-ref HEAD)"
[ "$current" = "$PRIVATE_BRANCH" ] || die "checkout ${PRIVATE_BRANCH} first (currently on ${current})"

if [ -n "$(git status --porcelain)" ]; then
  die "working tree is dirty — commit or stash first"
fi

# Build the set of excluded full-hashes from the exclude file.
declare -A EXCLUDED=()
if [ -f "$EXCLUDE_FILE" ]; then
  while IFS= read -r line; do
    line="${line%%#*}"; line="${line//[[:space:]]/}"
    [ -z "$line" ] && continue
    if full="$(git rev-parse --verify --quiet "${line}^{commit}")"; then
      EXCLUDED["$full"]=1
    else
      echo "sync-epstein: WARNING exclude entry not found, ignoring: $line" >&2
    fi
  done < "$EXCLUDE_FILE"
fi

# Mainline commits not already on epstein (patch-id aware), oldest first.
mapfile -t CANDIDATES < <(git rev-list --reverse --right-only --cherry-pick \
  "${private_ref}...${mainline_ref}")

if [ "${#CANDIDATES[@]}" -eq 0 ]; then
  echo "sync-epstein: already up to date with ${MAINLINE}."
  exit 0
fi

picked=0 skipped=0
echo "sync-epstein: ${#CANDIDATES[@]} candidate commit(s) from ${MAINLINE}:"
for sha in "${CANDIDATES[@]}"; do
  subject="$(git log -1 --format='%s' "$sha")"
  reason=""
  if [ -n "${EXCLUDED[$sha]:-}" ]; then
    reason="exclude-list"
  elif git log -1 --format='%B' "$sha" | grep -qF "$SKIP_MARKER"; then
    reason="skip-marker"
  fi

  if [ -n "$reason" ]; then
    printf '  SKIP  %s %s  (%s)\n' "${sha:0:9}" "$subject" "$reason"
    skipped=$((skipped + 1))
    continue
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    printf '  PICK  %s %s\n' "${sha:0:9}" "$subject"
    picked=$((picked + 1))
    continue
  fi

  printf '  PICK  %s %s\n' "${sha:0:9}" "$subject"
  if ! git cherry-pick -x "$sha"; then
    echo >&2
    echo "sync-epstein: CONFLICT on ${sha:0:9}. Resolve it, then run:" >&2
    echo "  git cherry-pick --continue   # or: git cherry-pick --skip / --abort" >&2
    echo "  scripts/sync-epstein.sh      # re-run to finish the rest" >&2
    exit 1
  fi
  picked=$((picked + 1))
done

if [ "$DRY_RUN" -eq 1 ]; then
  echo "sync-epstein: dry run — would pick ${picked}, skip ${skipped}. Nothing changed."
else
  echo "sync-epstein: done — picked ${picked}, skipped ${skipped}."
fi
