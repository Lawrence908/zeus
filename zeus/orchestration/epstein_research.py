# zeus/orchestration/epstein_research.py — Epstein research workflow (Phase 2).
#
# Given a question, this orchestrates a citation-backed investigation over the
# external epstein corpus (via the read-only reference client in
# zeus/memory/epstein.py — Zeus ingests nothing):
#
#   1. capabilities  — fetch the live manifest (doc_types + safety_rules).
#   2. plan          — derive sub-queries from the question, augmented with the
#                      top co-occurring entities discovered in a first search.
#   3. retrieve      — fan out FAST searches for the sub-queries in parallel,
#                      dedupe by (document_id, chunk_index), keep citations.
#   4. entities      — best-effort graph dossiers for the top entities (the
#                      graph may be down; degrade gracefully).
#   5. synthesize    — start an ASYNC deep-research job (preferred over the slow
#                      synchronous /ask) and, if a poll budget is given, poll it
#                      to completion. Retrieval + citations are the floor; the
#                      synthesized prose is best-effort (may time out).
#   6. assemble      — a structured result with inline citations, an explicit
#                      confidence label, and named gaps.
#
# SAFETY (non-negotiable, echoed into the assembled answer + the agent prompt):
#   - Mention is not involvement; co-occurrence is a signal, never an accusation.
#   - Allegations stay labeled as allegations.
#   - Never surface, infer, or reconstruct victim identities or redacted content.
#   - Every claim is grounded in a returned excerpt and cited; gaps are stated.
# The manifest's `safety_rules` string is the source of truth and is carried
# through on every result.
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

from zeus.memory.epstein import EpsteinClient, EpsteinError, EpsteinHit, get_epstein_client

logger = logging.getLogger("zeus.orchestration.epstein_research")

_FALLBACK_SAFETY = (
    "Mention is not involvement; co-occurrence is a signal, never an accusation. "
    "Allegations stay labeled as allegations. Never surface or infer victim "
    "identities or redacted content. Ground every claim in a cited excerpt."
)


@dataclass
class ResearchResult:
    """Structured outcome of a research run. `to_markdown()` renders the
    citation-backed answer; the raw fields let callers (Kairos, memory
    persistence, tests) inspect the evidence directly."""

    question: str
    safety_rules: str
    base_url: str | None
    graph_available: bool
    subqueries: list[str] = field(default_factory=list)
    evidence: list[EpsteinHit] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    job_id: str | None = None
    job_status: str | None = None
    report: str = ""
    job_citations: list[dict[str, Any]] = field(default_factory=list)
    confidence: str = "low"
    gaps: list[str] = field(default_factory=list)
    error: str | None = None

    def citations(self) -> list[dict[str, str]]:
        """Deduplicated citation list (document_id + source_label) drawn from
        both the fast retrieval and the async job."""
        seen: set[str] = set()
        out: list[dict[str, str]] = []
        for h in self.evidence:
            if h.document_id and h.document_id not in seen:
                seen.add(h.document_id)
                out.append({"document_id": h.document_id, "source_label": h.source_label})
        for c in self.job_citations:
            did = str(c.get("document_id", ""))
            if did and did not in seen:
                seen.add(did)
                out.append(
                    {"document_id": did, "source_label": str(c.get("source_label", ""))}
                )
        return out

    def to_markdown(self) -> str:
        lines: list[str] = [f"## Research: {self.question}", ""]
        lines.append(
            "> Sensitive legal corpus (victims + unproven allegations). "
            "Mention is not involvement; allegations remain allegations; "
            "victim identities and redacted content are never inferred."
        )
        lines.append("")
        if self.error:
            lines.append(f"**Error:** {self.error}")
            return "\n".join(lines)

        # Synthesized prose (best-effort) or a clear note when unavailable.
        prose = self.report.strip()
        if prose and "Synthesis failed" not in prose:
            lines.append(prose)
        else:
            lines.append(
                "_Deep synthesis is unavailable or still running; the findings "
                "below are the retrieved evidence with citations._"
            )
        lines.append("")

        # Evidence with inline citations.
        if self.evidence:
            lines.append("### Evidence")
            for i, h in enumerate(self.evidence, 1):
                lines.append(f"{i}. [{h.citation()}] {h.text[:280]}")
            lines.append("")

        # Entity signals (explicitly framed).
        named = [e for e in self.entities if e.get("names")]
        if named:
            lines.append("### Entity signals (co-occurrence only — NOT accusations)")
            for e in named:
                names = ", ".join(e["names"][:15])
                lines.append(f"- **{e['entity']}**: {names}")
            lines.append("")

        # Full citation list.
        cits = self.citations()
        if cits:
            lines.append("### Citations")
            for i, c in enumerate(cits, 1):
                label = c["source_label"] or "corpus"
                lines.append(f"[{i}] {c['document_id']} ({label})")
            lines.append("")

        lines.append(f"**Confidence:** {self.confidence}")
        if self.gaps:
            lines.append("**Gaps / caveats:**")
            for g in self.gaps:
                lines.append(f"- {g}")
        if self.job_id:
            lines.append("")
            lines.append(
                f"_Deep-research job `{self.job_id}` (status: {self.job_status}). "
                f"Poll epstein_research_result for the synthesized report._"
            )
        return "\n".join(lines)


def _dedupe_hits(hits: list[EpsteinHit]) -> list[EpsteinHit]:
    seen: set[tuple[str, str]] = set()
    out: list[EpsteinHit] = []
    for h in sorted(hits, key=lambda x: -x.score):
        key = (h.document_id, h.chunk_index)
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


def _plausible_entity(name: str, doc_type_keys: set[str]) -> bool:
    """Filter the /search `entities` keys down to real person/org names.

    On this corpus the search graph-expansion sometimes keys `entities` by
    source label (e.g. "primary", "2025-dec-DOJ-release") rather than a named
    node. Those are not entities: drop known doc_type keys, obvious slugs
    (hyphenated/lowercase), and anything without an initial capital.
    """
    n = name.strip()
    if not (3 <= len(n) <= 60):
        return False
    if n in doc_type_keys or n.lower() in doc_type_keys:
        return False
    if "-" in n and any(c.isdigit() for c in n):  # date-tagged source slugs
        return False
    # Require an uppercase initial somewhere (proper noun), and reject
    # all-lowercase single tokens.
    if not any(c.isupper() for c in n):
        return False
    return True


def _plan_subqueries(question: str, entities: list[str], max_subqueries: int) -> list[str]:
    """Heuristic planner: the question plus entity-augmented variants. The async
    job does its own LLM decomposition server-side; this fan-out is purely to
    gather immediate, broad evidence fast. Deterministic and dependency-free."""
    subs = [question]
    for ent in entities:
        if len(subs) >= max_subqueries:
            break
        subs.append(f"{question} {ent}".strip())
    return subs[:max_subqueries]


def _confidence(distinct_docs: int, top_score: float, synth_ok: bool) -> str:
    if distinct_docs >= 5 and top_score >= 0.6:
        return "high" if synth_ok else "medium"
    if distinct_docs >= 2:
        return "medium"
    return "low"


async def run_research(
    question: str,
    *,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    depth: int = 3,
    n_results: int = 8,
    max_subqueries: int = 3,
    max_entities: int = 2,
    start_job: bool = True,
    poll_budget_seconds: float = 0.0,
    poll_interval_seconds: float = 5.0,
    client: EpsteinClient | None = None,
) -> ResearchResult:
    """Run the plan -> retrieve -> entity -> job workflow.

    Chat callers use `poll_budget_seconds=0` (return fast evidence + a job
    handle immediately). Overnight/Kairos callers pass a generous budget to
    poll the deep-research job to completion.
    """
    client = client or get_epstein_client()
    if client is None:
        return ResearchResult(
            question=question,
            safety_rules=_FALLBACK_SAFETY,
            base_url=None,
            graph_available=False,
            error="Epstein research capability disabled (ZEUS_EPSTEIN_ENABLED=0).",
        )

    # 1. capabilities (safety_rules + graph availability). Non-fatal on failure.
    safety_rules = _FALLBACK_SAFETY
    graph_available = False
    doc_type_keys: set[str] = set()
    try:
        cap = await client.capabilities()
        safety_rules = str(cap.get("safety_rules") or _FALLBACK_SAFETY)
        graph_available = bool(cap.get("graph_available"))
        doc_type_keys = {str(k) for k in (cap.get("doc_types") or {})}
    except EpsteinError as exc:
        logger.warning("epstein capabilities failed: %s", exc)

    gaps: list[str] = []

    # 2. first search with graph expansion to discover candidate entities.
    entity_names: list[str] = []
    all_hits: list[EpsteinHit] = []
    try:
        first = await client.search(
            question,
            doc_type=doc_type,
            date_mentioned=date_mentioned,
            n_results=n_results,
            expand_graph=graph_available,
        )
        all_hits.extend(EpsteinHit.from_api(r) for r in first.get("results", []) or [])
        ents = first.get("entities") or {}
        entity_names = [
            str(k) for k in ents if _plausible_entity(str(k), doc_type_keys)
        ][:max_entities]
    except EpsteinError as exc:
        return ResearchResult(
            question=question,
            safety_rules=safety_rules,
            base_url=client.resolved_base,
            graph_available=graph_available,
            error=f"Initial retrieval failed: {exc}",
        )

    # 3. plan + fan out remaining sub-queries in parallel.
    subqueries = _plan_subqueries(question, entity_names, max_subqueries)

    async def _sub(q: str) -> list[EpsteinHit]:
        try:
            d = await client.search(
                q, doc_type=doc_type, date_mentioned=date_mentioned, n_results=n_results
            )
            return [EpsteinHit.from_api(r) for r in d.get("results", []) or []]
        except EpsteinError as exc:
            logger.warning("epstein sub-query failed (%s): %s", q, exc)
            return []

    if len(subqueries) > 1:
        extra = await asyncio.gather(*[_sub(q) for q in subqueries[1:]])
        for batch in extra:
            all_hits.extend(batch)

    evidence = _dedupe_hits(all_hits)[: n_results * 2]

    # 4. entity dossiers (best-effort; graph may be down).
    entities: list[dict[str, Any]] = []
    for name in entity_names:
        try:
            d = await client.entity(name, depth=1)
            sg = d.get("subgraph", {}) or {}
            names = [str(n["name"]) for n in sg.get("nodes", []) or [] if n.get("name")]
            entities.append({"entity": d.get("entity", name), "names": names})
        except EpsteinError as exc:
            if exc.status == 503:
                if "Entity graph unavailable (503)." not in gaps:
                    gaps.append("Entity graph unavailable (503).")
            else:
                logger.warning("epstein entity failed (%s): %s", name, exc)

    # 5. deep-research job (async, preferred). Optionally poll to completion.
    job_id: str | None = None
    job_status: str | None = None
    report = ""
    job_citations: list[dict[str, Any]] = []
    synth_ok = False
    if start_job:
        try:
            started = await client.start_job(
                question, doc_type=doc_type, date_mentioned=date_mentioned, depth=depth
            )
            job_id = str(started.get("job_id") or "") or None
            job_status = str(started.get("status") or "") or None
        except EpsteinError as exc:
            gaps.append(f"Could not start deep-research job: {exc}")

    if job_id and poll_budget_seconds > 0:
        deadline = time.monotonic() + poll_budget_seconds
        while time.monotonic() < deadline:
            try:
                j = await client.get_job(job_id)
            except EpsteinError as exc:
                gaps.append(f"Job polling failed: {exc}")
                break
            job_status = str(j.get("status") or job_status)
            if job_status in ("done", "error"):
                report = str(j.get("report") or "")
                job_citations = j.get("citations") or []
                synth_ok = job_status == "done" and "Synthesis failed" not in report
                break
            await asyncio.sleep(poll_interval_seconds)
        else:
            gaps.append("Deep synthesis did not complete within the poll budget.")

    if job_id and not synth_ok and job_status not in ("done", "error"):
        gaps.append("Deep synthesis still running; report will follow (poll the job).")

    # 6. assemble.
    distinct_docs = len({h.document_id for h in evidence if h.document_id})
    top_score = max((h.score for h in evidence), default=0.0)
    if distinct_docs < 2:
        gaps.append("Few matching documents; treat conclusions as tentative.")
    gaps.append(
        "Evidence reflects document co-occurrence, not proof of involvement."
    )

    return ResearchResult(
        question=question,
        safety_rules=safety_rules,
        base_url=client.resolved_base,
        graph_available=graph_available,
        subqueries=subqueries,
        evidence=evidence,
        entities=entities,
        job_id=job_id,
        job_status=job_status,
        report=report,
        job_citations=job_citations,
        confidence=_confidence(distinct_docs, top_score, synth_ok),
        gaps=gaps,
    )


def _write_allowed() -> bool:
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


async def persist_findings(
    result: ResearchResult, *, user_id: str = "user"
) -> dict[str, Any]:
    """Phase 3: persist a notable finding to Zeus memory (mnemosyne) with full
    provenance. WRITE-GATED by ZEUS_MCP_ALLOW_WRITE.

    Stored as a RAW payload (extract_facts=False — no LLM, no fact mangling of
    a sensitive corpus) in `zeus_memories`, tagged source=`epstein_research`
    with the question, citations, confidence, and resolved base URL so a future
    turn can trace every claim back to a document_id. Does NOT write anything
    back to the epstein service (that write path is deliberately absent; a
    future authenticated /findings endpoint would be gated the same way).
    """
    if result.error:
        return {"persisted": False, "reason": f"result had error: {result.error}"}
    if not _write_allowed():
        return {
            "persisted": False,
            "reason": "ZEUS_MCP_ALLOW_WRITE is false; finding not persisted",
        }
    citations = result.citations()
    if not citations:
        return {"persisted": False, "reason": "no citations; nothing to persist"}

    from zeus.memory.store import get_memory_store

    # Deterministic id so re-persisting the same question is idempotent.
    digest = hashlib.sha256(result.question.strip().lower().encode()).hexdigest()[:12]
    source_id = f"epstein_research:{result.job_id or digest}"

    cite_lines = "\n".join(
        f"- {c['document_id']} ({c['source_label'] or 'corpus'})" for c in citations
    )
    body = (
        f"Epstein corpus finding (confidence: {result.confidence}).\n"
        f"Question: {result.question}\n"
        f"Citations:\n{cite_lines}\n"
        f"Note: co-occurrence in documents, not proof of involvement; "
        f"allegations remain allegations."
    )
    try:
        store = get_memory_store()
        await store.add_text(
            body,
            source="epstein_research",
            source_id=source_id,
            user_id=user_id,
            extract_facts=False,
            metadata={
                "category": "research_finding",
                "question": result.question,
                "confidence": result.confidence,
                "job_id": result.job_id or "",
                "base_url": result.base_url or "",
                "citations": [c["document_id"] for c in citations],
                "provenance": "epstein_research",
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("persist_findings failed: %s", exc)
        return {"persisted": False, "reason": f"store error: {exc}"}
    return {"persisted": True, "source_id": source_id, "citations": len(citations)}
