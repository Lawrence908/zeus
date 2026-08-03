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
from typing import Any

logger = logging.getLogger("zeus.kronos.epstein_research")

# Cap concurrent researchers so an overnight backlog doesn't overwhelm the
# GPU-contended epstein synthesis backend. Report routing + slugging now live in
# zeus.orchestration.epstein_research.write_research_report (shared with the tools).
_MAX_CONCURRENT = int(os.getenv("ZEUS_EPSTEIN_MAX_CONCURRENT", "2") or 2)
# Generous default so the async synthesis can complete unattended.
_DEFAULT_POLL_BUDGET = float(os.getenv("ZEUS_EPSTEIN_POLL_BUDGET", "600") or 600)


async def run_epstein_research(params: dict[str, Any]) -> dict[str, Any]:
    """Kronos built-in: research a backlog against the corpus in one of three
    modes (multi-agent fan-out under a concurrency bound in every mode).

    Common params:
      doc_type:            optional doc_type filter
      depth:               decomposition / graph depth
      write_report:        write markdown report(s) to disk (default True)

    mode="question" (default) — a question backlog:
      question / questions, date_mentioned, poll_budget_seconds,
      persist (mnemosyne; write-gated by ZEUS_MCP_ALLOW_WRITE)

    mode="entity_dossier" — a backlog of entities to profile:
      entity / entities  (list of names)

    mode="connection_map" — a backlog of entity groups to connect:
      names (one group), OR groups (list of name-lists)
    """
    from zeus.orchestration.epstein_research import (
        persist_findings,
        run_connection_map,
        run_entity_dossier,
        run_research,
        write_research_report,
    )

    mode = str(params.get("mode") or "question").strip()
    doc_type = params.get("doc_type")
    write_report = params.get("write_report", True)
    sem = asyncio.Semaphore(_MAX_CONCURRENT)

    def _emit(kind: str, subject: str, result: Any, extra: dict[str, Any]) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "subject": subject,
            "confidence": getattr(result, "confidence", None),
            "citations": len(result.citations()),
            "error": result.error,
            **extra,
        }
        if write_report and not result.error:
            sidecar = result.to_graph() if hasattr(result, "to_graph") else None
            try:
                path = write_research_report(kind, subject, result.to_markdown(), sidecar=sidecar)
                entry["report_path"] = str(path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("epstein report write failed (%s): %s", subject, exc)
                entry["report_path_error"] = str(exc)
        return entry

    # -- entity dossier backlog ---------------------------------------------
    if mode == "entity_dossier":
        entities = _as_list(params.get("entities"), params.get("entity"))
        if not entities:
            raise ValueError("entity_dossier mode requires 'entity' or 'entities'")
        depth = int(params.get("depth") or 1)

        async def _dossier(name: str) -> dict[str, Any]:
            async with sem:
                r = await run_entity_dossier(name, doc_type=doc_type, depth=depth)
            return _emit("entity_dossier", name, r, {"graph_available": r.graph_available})

        results = await asyncio.gather(*[_dossier(n) for n in entities])
        return {
            "mode": mode,
            "subjects": len(entities),
            "reports_written": sum(1 for r in results if r.get("report_path")),
            "results": results,
        }

    # -- connection map backlog ---------------------------------------------
    if mode == "connection_map":
        groups: list[list[str]] = []
        if params.get("groups"):
            groups = [[str(n).strip() for n in g if str(n).strip()] for g in params["groups"]]
        elif params.get("names"):
            groups = [[str(n).strip() for n in params["names"] if str(n).strip()]]
        groups = [g for g in groups if len(g) >= 2]
        if not groups:
            raise ValueError("connection_map mode requires 'names' or 'groups' (>=2 entities each)")
        depth = int(params.get("depth") or 2)

        async def _map(group: list[str]) -> dict[str, Any]:
            async with sem:
                r = await run_connection_map(group, depth=depth)
            return _emit("connection_map", "-".join(r.entities), r,
                         {"graph_available": r.graph_available})

        results = await asyncio.gather(*[_map(g) for g in groups])
        return {
            "mode": mode,
            "subjects": len(groups),
            "reports_written": sum(1 for r in results if r.get("report_path")),
            "results": results,
        }

    # -- question backlog (default) -----------------------------------------
    questions = _as_list(params.get("questions"), params.get("question"))
    if not questions:
        raise ValueError("question mode requires 'question' or 'questions'")
    date_mentioned = params.get("date_mentioned")
    depth = int(params.get("depth") or 3)
    poll_budget = float(params.get("poll_budget_seconds") or _DEFAULT_POLL_BUDGET)
    persist = params.get("persist", True)

    async def _one(question: str) -> dict[str, Any]:
        async with sem:
            result = await run_research(
                question,
                doc_type=doc_type,
                date_mentioned=date_mentioned,
                depth=depth,
                poll_budget_seconds=poll_budget,
            )
        entry = _emit("question", question, result,
                      {"job_id": result.job_id, "job_status": result.job_status})
        if persist:
            entry["persist"] = await persist_findings(result)
        return entry

    results = await asyncio.gather(*[_one(q) for q in questions])
    persisted = sum(1 for r in results if (r.get("persist") or {}).get("persisted"))
    return {
        "mode": mode,
        "subjects": len(questions),
        "reports_written": sum(1 for r in results if r.get("report_path")),
        "findings_persisted": persisted,
        "results": results,
    }


def _as_list(plural: Any, singular: Any) -> list[str]:
    """Normalize a plural-or-singular param into a clean list of strings."""
    if plural:
        return [str(x).strip() for x in plural if str(x).strip()]
    if singular:
        s = str(singular).strip()
        return [s] if s else []
    return []
