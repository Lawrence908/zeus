# zeus/kronos/jobs/retrieval_eval.py — Nightly retrieval-eval scoring (Themis).
#
# Runs the accepted retrieval-eval suite against the live stack via the shared
# core in zeus/memory/eval_suite.py, persists the full report to
# zeus/data/retrieval_eval.json, and returns the summary as the JobRun output
# (which the Kronos run store records). Read-heavy: the only write is the JSON
# report path. It never touches the accepted baseline or the query suite files
# (see docs/themis-spec.md: the baseline is append-only + human-accepted).
#
# Regression alerting and query minting are separate concerns (Themis action
# items 5 and 6); this job only scores and persists.
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("zeus.kronos.retrieval_eval")

_DEFAULT_OUT = "zeus/data/retrieval_eval.json"


async def run_retrieval_eval(params: dict[str, Any]) -> dict[str, Any]:
    from zeus.memory.eval_suite import DEFAULT_TOP_K, load_suite, score_suite

    top_k = int(params.get("top_k") or DEFAULT_TOP_K)
    out_path = str(params.get("out_path") or os.getenv("ZEUS_RETRIEVAL_EVAL_OUT") or _DEFAULT_OUT)

    suite = load_suite()
    if not suite:
        return {"status": "error", "reason": "no accepted queries under tests/retrieval_eval_queries/"}

    # Scoring is sync (search helpers are sync) and slow (embedding per query);
    # keep the event loop free.
    summary, per_query = await asyncio.to_thread(score_suite, suite, top_k=top_k)

    scored_at = datetime.now(timezone.utc).isoformat()
    report = {"scored_at": scored_at, "summary": summary, "per_query": per_query}

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    overall = summary["overall"]
    logger.info(
        "retrieval_eval scored=%s error=%s overall_hit@5=%s layer_miss=%s -> %s",
        overall["n_scored"],
        overall["n_error"],
        overall["hit@5"],
        overall["layer_miss"],
        out_path,
    )

    # Compact JobRun output: full detail is on disk, this is the run-store row.
    return {
        "status": "ok",
        "scored_at": scored_at,
        "out_path": out_path,
        "overall": overall,
        "per_layer": summary["per_layer"],
        "config": summary["config"],
    }
