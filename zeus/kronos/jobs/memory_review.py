# zeus/kronos/jobs/memory_review.py — Weekly memory review (Phase 2 wires up).
#
# The seed job `weekly-memory-review` is disabled in kronos.yaml for Phase 1.
# This stub lets the import resolve if a developer enables it early.
from __future__ import annotations


async def run_weekly_review(params: dict) -> dict:
    return {
        "status": "stub",
        "note": (
            "run_weekly_review is a Phase 1 stub. Phase 2 surfaces patterns "
            "from the week's memory additions."
        ),
    }
