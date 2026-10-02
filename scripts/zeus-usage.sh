#!/usr/bin/env bash
# scripts/zeus-usage.sh
# Answers one question: is anything actually using Zeus?
#
# Every MCP tool call that touches memory, profile, news, files or actions
# becomes an HTTP request to zeus-core. Docker's own healthcheck also hits
# /health ~100x/hour, which drowns out real traffic -- so /health is excluded
# and reported separately. Real traffic is the only number that matters.
#
# Usage: scripts/zeus-usage.sh [hours]   (default 336 = 14 days)
set -euo pipefail

HOURS="${1:-336}"
LOGS="$(docker logs zeus-core --since "${HOURS}h" 2>&1)"

real=$(grep -oE '"(GET|POST|PATCH|DELETE) [^ ]+ HTTP' <<<"$LOGS" \
  | sed 's/ HTTP//; s/"//' | sed 's/?.*//' | grep -v ' /health$' || true)

echo "Zeus usage, last ${HOURS}h (since $(date -Is -d "${HOURS} hours ago"))"
echo "  healthchecks : $(grep -c ' /health ' <<<"$LOGS" || true)  (ignore, Docker)"
echo "  real requests: $(grep -c . <<<"$real" || echo 0)"
echo
if [[ -n "$real" ]]; then
  echo "By endpoint:"
  sort <<<"$real" | uniq -c | sort -rn | sed 's/^/  /'
else
  echo "  Nothing but healthchecks. Zeus is idle."
fi
