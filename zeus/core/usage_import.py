# zeus/core/usage_import.py — Scaffolding for historical LLM usage import.
#
# Status: NOT IMPLEMENTED. This file exists so the /admin/llm_usage/import
# endpoint and Zeus OS Token Usage app have a real module to talk to from
# day one. When historical Claude (anthropic.com console) and Cursor exports
# are available, fill in `import_anthropic_csv` and `import_cursor_csv` to
# parse them into the same `usage` table that the small-LLM router writes to.
#
# Expected on-disk layout (drop exports here):
#   ~/.zeus/usage-imports/
#     anthropic-YYYY-MM-DD.csv         Anthropic Console "Usage" CSV
#     cursor-YYYY-MM-DD.csv            Cursor settings → Account → export
#     <anything>.csv                   ignored unless prefix matches above
#
# Anthropic CSV columns (as of June 2026 console — verify on next export):
#   workspace, model, api_key, usage_type, input_tokens, output_tokens,
#   cache_read_tokens, cache_write_tokens, start_time, end_time, cost_usd
#
# Cursor: their console doesn't (yet) offer a structured per-call export.
# Likely workflows:
#   - Settings page → Usage → screenshot OCR (lossy, not pursuing)
#   - Best-effort manual CSV the user maintains
# Treat Cursor data as monthly totals tagged with provider='cursor' and a
# synthetic model='cursor-ide-aggregate' until the export improves.
#
# TODO when implementing:
#   1. Add a CLI subcommand `python -m zeus.usage import` for one-off runs.
#   2. Track which file basenames have been imported (idempotency) — use a
#      side table `usage_imports (path, mtime, sha256, imported_at)`.
#   3. Surface progress through the /admin/llm_usage/import endpoint (return
#      counts per file, errors, totals after).
#   4. Update zeus/docs/token-usage.md with the actual column mapping once
#      we confirm the current Anthropic CSV header.
from __future__ import annotations

import os
from pathlib import Path

IMPORT_DIR = Path(
    os.path.expanduser(os.getenv("ZEUS_USAGE_IMPORT_DIR", "~/.zeus/usage-imports"))
)


def list_pending() -> list[str]:
    """Return CSV basenames currently sitting in the import dir."""
    if not IMPORT_DIR.is_dir():
        return []
    return sorted(p.name for p in IMPORT_DIR.glob("*.csv"))


def import_anthropic_csv(path: Path) -> int:
    """Parse Anthropic Console Usage CSV → insert into the usage ledger.

    Returns the number of rows inserted. NOT IMPLEMENTED — see module
    docstring for the expected column set.
    """
    raise NotImplementedError(
        "Anthropic CSV importer not yet implemented. See zeus/docs/token-usage.md."
    )


def import_cursor_csv(path: Path) -> int:
    """Parse Cursor usage export → insert into the usage ledger.

    Returns rows inserted. NOT IMPLEMENTED. Cursor's export format is still
    in flux as of June 2026; revisit once they ship a stable structured one.
    """
    raise NotImplementedError(
        "Cursor importer not yet implemented. See zeus/docs/token-usage.md."
    )
