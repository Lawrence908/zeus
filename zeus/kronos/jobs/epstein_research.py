# zeus/kronos/jobs/epstein_research.py — Overnight/scheduled Epstein research.
#
# Phase 4 of the Epstein researcher: unattended, cron-driven investigation of a
# question backlog. Each question runs the read-only research workflow
# (zeus/orchestration/epstein_research.run_research) with a GENEROUS poll budget
# so the slow async synthesis has time to finish overnight, writes a
# citation-backed markdown report to disk, and — when writes are enabled —
# persists the finding to mnemosyne with provenance.
#
# Multi-agent fan-out: a backlog of questions is researched concurrently under
# a small semaphore (each run is an independent researcher over the shared
# corpus API). Start as one; the bound keeps GPU contention on the epstein side
# manageable.
#
# SAFETY: read-only against the epstein service; the report keeps the corpus
# safety framing (mention != involvement, allegations stay labeled, no victim
# identities). Persistence is write-gated by ZEUS_MCP_ALLOW_WRITE.
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("zeus.kronos.epstein_research")

_REPORTS_DIR = Path(
    os.getenv("ZEUS_EPSTEIN_REPORT_DIR")
    or os.getenv("ZEUS_DEEP_RESEARCH_DIR", "/home/chris/zeus/docs/research")
)
# Cap concurrent researchers so an overnight backlog doesn't overwhelm the
# GPU-contended epstein synthesis backend.
_MAX_CONCURRENT = int(os.getenv("ZEUS_EPSTEIN_MAX_CONCURRENT", "2") or 2)
# Generous default so the async synthesis can complete unattended.
_DEFAULT_POLL_BUDGET = float(os.getenv("ZEUS_EPSTEIN_POLL_BUDGET", "600") or 600)


def _slug(text: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "untitled"


async def run_epstein_research(params: dict[str, Any]) -> dict[str, Any]:
    """Kronos built-in: research one question or a backlog against the corpus.

    Params:
      question:            single question, OR
      questions:           list of questions (multi-agent fan-out)
      doc_type:            optional doc_type filter
      date_mentioned:      optional date filter
      depth:               deep-research decomposition depth (default 3)
      poll_budget_seconds: seconds to wait for synthesis (default 600)
      persist:             persist findings to mnemosyne (default True; still
                           write-gated by ZEUS_MCP_ALLOW_WRITE)
      write_report:        write markdown report to disk (default True)
    """
    from zeus.orchestration.epstein_research import persist_findings, run_research

    questions: list[str] = []
    if params.get("questions"):
        questions = [str(q).strip() for q in params["questions"] if str(q).strip()]
    elif params.get("question"):
        questions = [str(params["question"]).strip()]
    if not questions:
        raise ValueError("epstein_research job requires 'question' or 'questions'")

    doc_type = params.get("doc_type")
    date_mentioned = params.get("date_mentioned")
    depth = int(params.get("depth") or 3)
    poll_budget = float(params.get("poll_budget_seconds") or _DEFAULT_POLL_BUDGET)
    persist = params.get("persist", True)
    write_report = params.get("write_report", True)

    sem = asyncio.Semaphore(_MAX_CONCURRENT)
    today = datetime.now(timezone.utc).date().isoformat()

    async def _one(question: str) -> dict[str, Any]:
        async with sem:
            result = await run_research(
                question,
                doc_type=doc_type,
                date_mentioned=date_mentioned,
                depth=depth,
                poll_budget_seconds=poll_budget,
            )
        entry: dict[str, Any] = {
            "question": question,
            "confidence": result.confidence,
            "citations": len(result.citations()),
            "job_id": result.job_id,
            "job_status": result.job_status,
            "error": result.error,
        }
        if write_report and not result.error:
            path = _REPORTS_DIR / f"{today}-epstein-{_slug(question)}.md"
            try:
                _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                path.write_text(result.to_markdown(), encoding="utf-8")
                entry["report_path"] = str(path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("epstein report write failed (%s): %s", path, exc)
                entry["report_path_error"] = str(exc)
        if persist:
            entry["persist"] = await persist_findings(result)
        return entry

    results = await asyncio.gather(*[_one(q) for q in questions])

    persisted = sum(1 for r in results if (r.get("persist") or {}).get("persisted"))
    return {
        "questions": len(questions),
        "reports_written": sum(1 for r in results if r.get("report_path")),
        "findings_persisted": persisted,
        "results": results,
    }
