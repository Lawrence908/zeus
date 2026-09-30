#!/usr/bin/env bash
# scripts/zeus-mcp.sh
# stdio launcher for the Zeus MCP server, for MCP clients (Claude Code, Cursor).
#
# Why a wrapper rather than invoking `python -m zeus.mcp` directly: the server
# calls load_dotenv() with no path, so it only picks up .env when cwd is the
# repo root. MCP clients launch servers from the *client's* cwd, which is
# whatever project the user happens to be in. Without the cd, every tool that
# needs a key from .env fails, and the core-backed tools fall back to the
# ZEUS_CORE_URL default (:8203) instead of this host's published port.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PY="$REPO_ROOT/.venv/bin/python"
[[ -x "$PY" ]] || { echo "zeus-mcp: no venv at $PY" >&2; exit 1; }

exec "$PY" -m zeus.mcp
