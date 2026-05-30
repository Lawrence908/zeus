# zeus/kronos/jobs/ingest.py — Kronos built-in for the nightly knowledge ingest.
#
# Wraps zeus.ingest.pipeline.IngestPipeline.run_all_sources() so the Iris
# pipeline runs on a Kronos cron tick. APScheduler (zeus/ingest/scheduler.py)
# stays in place for now; the two run side-by-side until this job has proven
# itself, then the APScheduler block can be retired from main.py.
#
# Params:
#   sources:      list of source names to ingest (default: all bulk knowledge
#                 sources from ingest config). Matches zeus.ingest.run source
#                 names: markdown, obsidian, chatgpt, email, newsletter,
#                 bookmarks, git, gcal, context_pack.
#   incremental:  passed to run_all_sources (currently a no-op in that layer,
#                 but forward-compatible).
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("zeus.kronos.ingest")

# Default to the bulk knowledge sources. Curated profile sources (context_pack,
# gcal) can be added per-job via params.sources if you want the LLM fact
# extraction to run on a schedule.
_DEFAULT_SOURCES: tuple[str, ...] = (
    "markdown",
    "obsidian",
    "chatgpt",
    "bookmarks",
    "git",
)


async def run_nightly_ingest(params: dict[str, Any]) -> dict[str, Any]:
    from zeus.ingest.pipeline import IngestPipeline
    from zeus.ingest.run import build_sources_for_trigger

    source_names = params.get("sources") or list(_DEFAULT_SOURCES)
    incremental = bool(params.get("incremental", True))

    built: list = []
    skipped: list[dict[str, str]] = []
    for name in source_names:
        try:
            built.extend(build_sources_for_trigger(name))
        except ValueError as exc:
            # Source is configured in YAML but missing an env var / export file.
            # This is normal (not every source is active in every environment);
            # record and keep going instead of failing the whole run.
            logger.info("kronos ingest: skipping %s — %s", name, exc)
            skipped.append({"source": name, "reason": str(exc)})
        except Exception as exc:
            logger.warning("kronos ingest: failed to build %s — %s", name, exc)
            skipped.append({"source": name, "reason": f"build error: {exc}"})

    if not built:
        return {
            "status": "skipped",
            "reason": "no ingest sources resolvable in this environment",
            "requested": source_names,
            "skipped": skipped,
        }

    pipeline = IngestPipeline(sources=built)
    results = await pipeline.run_all_sources(incremental=incremental)

    total_stored = sum(r.chunks_stored for r in results)
    by_source = [
        {
            "source": r.source,
            "chunks_seen": r.chunks_seen,
            "chunks_stored": r.chunks_stored,
            "chunks_skipped": r.chunks_skipped,
            "elapsed_seconds": round(r.elapsed_seconds, 2),
        }
        for r in results
    ]
    return {
        "status": "ok",
        "incremental": incremental,
        "total_chunks_stored": total_stored,
        "sources_run": len(results),
        "results": by_source,
        "skipped_unresolved": skipped,
    }
