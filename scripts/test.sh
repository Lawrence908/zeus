#!/usr/bin/env bash
# scripts/test.sh — run the exact gate CI runs (ruff lint + pytest), locally.
#
# Mirrors the `backend` job in .github/workflows/ci.yml so you can reproduce a
# CI failure before pushing. The suite is fully mocked — no Qdrant/Ollama needed.
#
# Usage:
#   scripts/test.sh            # lint + full test suite
#   scripts/test.sh -k pattern # extra args are forwarded to pytest
set -euo pipefail

cd "$(dirname "$0")/.."

# Prefer the repo venv if present, else whatever's on PATH.
if [[ -x .venv/bin/ruff ]]; then
  RUFF=.venv/bin/ruff
  PYTEST=.venv/bin/pytest
else
  RUFF=ruff
  PYTEST=pytest
fi

echo "==> ruff check ."
"$RUFF" check .

echo "==> pytest"
"$PYTEST" -q "$@"

echo "==> OK: lint + tests passed"
