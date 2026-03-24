# Zeus Development Guide

Zeus is a self-hosted personal AI assistant system built with Python/FastAPI. See `docs/SYSTEM_PROMPT.md` for architecture, stack details, and code standards.

## Cursor Cloud specific instructions

### Project overview

Zeus is a greenfield Python project — a personal AI for RAG and agent orchestration. The core service is a FastAPI "API bus" at `zeus/core/app.py` that will route to planned subsystems (memory, ingest, voice, safety, orchestration, context API).

### Running the application

- **Dev server**: `source .venv/bin/activate && uvicorn zeus.core.app:app --host 0.0.0.0 --port 8000 --reload`
- **Swagger docs**: available at `http://localhost:8000/docs`
- The `--reload` flag enables hot-reloading on code changes.

### Lint, test, build

- **Lint**: `source .venv/bin/activate && ruff check zeus/ tests/`
- **Format check**: `source .venv/bin/activate && ruff format --check zeus/ tests/`
- **Auto-fix lint**: `source .venv/bin/activate && ruff check --fix zeus/ tests/`
- **Tests**: `source .venv/bin/activate && pytest tests/ -v`
- **Type check**: `source .venv/bin/activate && mypy zeus/`

### Environment notes

- Python 3.12 is available; the project requires Python 3.11+.
- The virtual environment lives at `.venv/` in the repo root. Always activate it before running commands.
- `python3.12-venv` system package is required to create venvs (pre-installed via update script).
- Dependencies are managed via `pyproject.toml` — install with `pip install -e ".[dev]"`.
