# zeus/kronos/jobs/ingest.py — Nightly knowledge-ingest job (Phase 2 wires up).
#
# The seed job `nightly-knowledge-ingest` is disabled in kronos.yaml for Phase 1.
# This stub exists so the import path resolves and the job round-trips through
# the API without a 500 when a developer flips enabled=true before Phase 2 lands.
from __future__ import annotations


async def run_nightly_ingest(params: dict) -> dict:
    return {
        "status": "stub",
        "note": (
            "run_nightly_ingest is a Phase 1 stub. Phase 2 wires this into "
            "IngestPipeline.run_all_sources(incremental=True)."
        ),
        "requested_targets": params.get("targets", []),
    }
