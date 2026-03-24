# AGENTS.md

## Project overview

Zeus is a self-hosted, privacy-preserving, voice-first personal AI assistant. See `docs/SYSTEM_PROMPT.md` for full architecture and stack details. Python 3.11+ / FastAPI monorepo.

## Cursor Cloud specific instructions

### Services

| Service | Entry point | Default port | Command |
|---------|------------|--------------|---------|
| Zeus Core (API bus) | `zeus.core.main:app` | 8000 | `uvicorn zeus.core.main:app --host 0.0.0.0 --port 8000 --reload` |
| Oracle (Context API) | `zeus.api.main:app` | 8001 | `uvicorn zeus.api.main:app --host 0.0.0.0 --port 8001 --reload` |

### Dev commands

- **Install deps**: `pip install -e ".[dev]"` (from venv at `.venv`)
- **Lint**: `ruff check zeus/ tests/`
- **Lint fix**: `ruff check --fix zeus/ tests/`
- **Test**: `python -m pytest tests/ -v`
- **Run core**: `uvicorn zeus.core.main:app --reload`
- **Run oracle**: `uvicorn zeus.api.main:app --port 8001 --reload`

### Gotchas

- The venv is at `.venv` — always activate it before running commands: `. .venv/bin/activate`
- `python3.12-venv` system package is required and may not be pre-installed; the update script handles venv creation.
- The project uses `pyproject.toml` with setuptools as the build backend. Install in editable mode (`-e`) to get hot-reloading of source changes.
- Both FastAPI apps have Swagger docs at `/docs` (useful for interactive testing).
- Config is via env vars with `ZEUS_` prefix (see `zeus/core/config.py`). Defaults work for local dev.
