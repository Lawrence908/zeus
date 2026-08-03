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
import itertools
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
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


# Common role / non-name tokens the person extraction emits as if they were
# people (seen live: "Prosecutor", "My", "unknown"). Co-occurrence is already a
# weak signal; these are noise on top of it, so drop them from connection lists.
_ROLE_STOPWORDS = {
    "prosecutor", "defendant", "plaintiff", "the court", "court", "government",
    "my", "unknown", "victim", "witness", "attorney", "judge", "counsel",
    "defense", "petitioner", "respondent", "appellant", "appellee", "affiant",
    "agent", "officer", "detective", "minor", "jane doe", "john doe",
}


def _related_names(name_a: str, name_b: str) -> bool:
    """True if two names are near-duplicates (one contains the other), e.g.
    'Maxwell' vs 'Ghislaine Maxwell'. Used to avoid listing an entity as its
    own connection."""
    a, b = name_a.strip().lower(), name_b.strip().lower()
    return a == b or a in b or b in a


def _graph_people(
    subgraph: dict[str, Any], *, exclude: str, doc_type_keys: set[str]
) -> list[str]:
    """Named Person nodes from a subgraph, de-noised: drop the subject and its
    near-duplicates, role stopwords, and implausible names. Co-occurrence only."""
    out: list[str] = []
    seen: set[str] = set()
    for n in subgraph.get("nodes", []) or []:
        nm = n.get("name")
        if not nm or n.get("type") not in (None, "Person"):
            # Person nodes carry type == "Person"; event nodes have no name.
            if n.get("type") not in (None, "Person"):
                continue
        if not nm:
            continue
        nm = str(nm).strip()
        low = nm.lower()
        if low in seen or low in _ROLE_STOPWORDS:
            continue
        if _related_names(nm, exclude):
            continue
        if not _plausible_entity(nm, doc_type_keys):
            continue
        seen.add(low)
        out.append(nm)
    return out


def _graph_events(
    subgraph: dict[str, Any], *, limit: int = 20, per_bucket: int = 2
) -> list[dict[str, str]]:
    """Dated events from a subgraph's event nodes (event_date_iso + description),
    sorted chronologically and de-noised. Graph-derived, so weakly cited:
    presented as a timeline scaffold, with the cited search evidence carrying the
    real sourcing.

    OCR chunks overlap, so one underlying passage surfaces as several event nodes
    with near-identical text (observed live: 6x the same 2020-07-02 line). Dedupe
    on a whitespace-normalized description prefix, and cap events per
    (date, event_type) bucket so no single document floods the timeline."""
    evs: list[dict[str, str]] = []
    seen_prefix: set[str] = set()
    bucket_count: dict[tuple[str, str], int] = {}
    raw: list[dict[str, str]] = []
    for n in subgraph.get("nodes", []) or []:
        if n.get("name") or "event_id" not in n:
            continue
        date = str(n.get("event_date_iso") or "").strip()
        desc = str(n.get("description") or "").strip()
        if not (date or desc):
            continue
        raw.append({
            "date": date,
            "event_type": str(n.get("event_type") or "").strip(),
            "description": desc,
        })
    raw.sort(key=lambda e: e["date"] or "9999-99-99")
    for e in raw:
        norm = re.sub(r"\s+", " ", e["description"]).strip().lower()
        prefix = norm[:60]
        if prefix and prefix in seen_prefix:
            continue
        bucket = (e["date"], e["event_type"])
        if bucket_count.get(bucket, 0) >= per_bucket:
            continue
        seen_prefix.add(prefix)
        bucket_count[bucket] = bucket_count.get(bucket, 0) + 1
        evs.append(e)
        if len(evs) >= limit:
            break
    return evs


# Generic investigative angles appended to the entity name. Never search the
# bare name: live, a bare-entity query timed out against the 1.2M-doc store
# while these narrower variants returned fast (prototype finding 2026-07-27).
_DOSSIER_ANGLES = [
    "role and relationship",
    "testimony deposition statement",
    "travel flights schedule properties",
    "court filing charges indictment",
    "financial records payments transactions",
    "correspondence emails communication",
]


# The search backend serializes embeddings; firing the whole fan-out at once
# trips 500s / read-timeouts (observed live 2026-07-27). Bound concurrency and
# retry once on a transient failure.
_SEARCH_CONCURRENCY = int(os.getenv("ZEUS_EPSTEIN_SEARCH_CONCURRENCY", "3") or 3)


async def _search_one(
    client: EpsteinClient,
    query: str,
    *,
    doc_type: str | None = None,
    n_results: int = 8,
    retries: int = 1,
) -> list[EpsteinHit]:
    for attempt in range(retries + 1):
        try:
            r = await client.search(query, doc_type=doc_type, n_results=n_results)
            return [EpsteinHit.from_api(x) for x in r.get("results", []) or []]
        except EpsteinError as exc:
            if attempt < retries:
                await asyncio.sleep(1.0 + attempt)
                continue
            logger.warning("epstein search failed (%s): %s", query, exc)
    return []


async def _search_fanout(
    client: EpsteinClient,
    queries: list[str],
    *,
    doc_type: str | None = None,
    n_results: int = 8,
    concurrency: int | None = None,
) -> list[EpsteinHit]:
    """Run searches under a concurrency bound so the embedding backend keeps up."""
    sem = asyncio.Semaphore(concurrency or _SEARCH_CONCURRENCY)

    async def _guard(q: str) -> list[EpsteinHit]:
        async with sem:
            return await _search_one(client, q, doc_type=doc_type, n_results=n_results)

    batches = await asyncio.gather(*[_guard(q) for q in queries])
    return [h for b in batches for h in b]


def _dossier_subqueries(name: str, connections: list[str], max_subqueries: int) -> list[str]:
    """Entity name crossed with generic angles first, then the strongest graph
    connections. Deterministic and dependency-free."""
    subs = [f"{name} {angle}".strip() for angle in _DOSSIER_ANGLES]
    for conn in connections:
        subs.append(f"{name} {conn}".strip())
    # Dedupe preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for s in subs:
        if s.lower() in seen:
            continue
        seen.add(s.lower())
        ordered.append(s)
    return ordered[:max_subqueries]


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


# ------------------------------------------------------------------------- #
# Component B: entity dossier
# ------------------------------------------------------------------------- #
@dataclass
class DossierResult:
    """Structured entity dossier. `to_markdown()` renders the cited profile;
    raw fields let Kairos / persistence / tests inspect the evidence."""

    entity: str
    safety_rules: str
    base_url: str | None
    graph_available: bool
    subqueries: list[str] = field(default_factory=list)
    evidence: list[EpsteinHit] = field(default_factory=list)
    connections: list[str] = field(default_factory=list)
    timeline: list[dict[str, str]] = field(default_factory=list)
    doc_types: list[str] = field(default_factory=list)
    confidence: str = "low"
    gaps: list[str] = field(default_factory=list)
    error: str | None = None

    def citations(self) -> list[dict[str, str]]:
        seen: set[str] = set()
        out: list[dict[str, str]] = []
        for h in self.evidence:
            if h.document_id and h.document_id not in seen:
                seen.add(h.document_id)
                out.append({"document_id": h.document_id, "source_label": h.source_label})
        return out

    def to_markdown(self) -> str:
        lines: list[str] = [f"# Entity Dossier: {self.entity}", ""]
        lines.append(
            "> Sensitive legal corpus (victims + unproven allegations). Name "
            "co-occurrence is a signal about where to read, NOT an accusation or "
            "a relationship. Allegations remain allegations; victim identities "
            "and redacted content are never inferred. Every substantive statement "
            "is cited by document_id."
        )
        lines.append("")
        if self.error:
            lines.append(f"**Error:** {self.error}")
            return "\n".join(lines)

        access = "graph + search" if self.graph_available else "search-only (graph unavailable)"
        lines.append(f"- **Access mode:** {access}")
        lines.append(f"- **Evidence:** {len(self.evidence)} deduped excerpts; "
                     f"doc_types: {', '.join(self.doc_types) or 'n/a'}")
        lines.append(f"- **Confidence:** {self.confidence}")
        lines.append("")

        if self.timeline:
            lines.append("## Timeline (graph-derived; corroborate against cited evidence)")
            for e in self.timeline:
                date = e["date"] or "undated"
                etype = f" ({e['event_type']})" if e["event_type"] else ""
                desc = e["description"][:240].replace("\n", " ").strip()
                lines.append(f"- **{date}**{etype}: {desc}")
            lines.append("")

        if self.connections:
            lines.append("## Connections (co-occurrence signal — NOT involvement)")
            lines.append(", ".join(self.connections))
            lines.append("")

        if self.evidence:
            lines.append("## Notable excerpts (cited)")
            for i, h in enumerate(self.evidence[:15], 1):
                lines.append(f"{i}. [{h.citation()}] {h.text[:280].strip()}")
            lines.append("")

        cits = self.citations()
        if cits:
            lines.append("## Citations")
            for i, c in enumerate(cits, 1):
                lines.append(f"[{i}] {c['document_id']} ({c['source_label'] or 'corpus'})")
            lines.append("")

        if self.gaps:
            lines.append("## Gaps / caveats")
            for g in self.gaps:
                lines.append(f"- {g}")
        return "\n".join(lines)


async def run_entity_dossier(
    name: str,
    *,
    depth: int = 1,
    doc_type: str | None = None,
    n_results: int = 8,
    max_subqueries: int = 8,
    max_connections: int = 15,
    client: EpsteinClient | None = None,
) -> DossierResult:
    """Build a cited dossier for one entity: graph neighborhood (degrade on 503)
    -> planned sub-queries (never the bare name) -> fan-out search -> timeline
    from graph events -> confidence + gaps. Read-only."""
    client = client or get_epstein_client()
    if client is None:
        return DossierResult(
            entity=name, safety_rules=_FALLBACK_SAFETY, base_url=None,
            graph_available=False,
            error="Epstein research capability disabled (ZEUS_EPSTEIN_ENABLED=0).",
        )

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
    connections: list[str] = []
    timeline: list[dict[str, str]] = []

    # 1. graph neighborhood (best-effort; degrade on 503).
    if graph_available:
        try:
            d = await client.entity(name, depth=depth)
            sg = d.get("subgraph", {}) or {}
            connections = _graph_people(
                sg, exclude=name, doc_type_keys=doc_type_keys
            )[:max_connections]
            timeline = _graph_events(sg)
        except EpsteinError as exc:
            if exc.status == 503:
                gaps.append("Entity graph unavailable (503); connections/timeline "
                            "are search-derived only.")
                graph_available = False
            else:
                logger.warning("epstein entity failed (%s): %s", name, exc)
    else:
        gaps.append("Graph not available; connections/timeline are search-derived only.")

    # 2. plan sub-queries (name x angles, then top connections) and fan out
    # under a concurrency bound so the embedding backend keeps up.
    subqueries = _dossier_subqueries(name, connections, max_subqueries)
    all_hits = await _search_fanout(
        client, subqueries, doc_type=doc_type, n_results=n_results
    )
    evidence = _dedupe_hits(all_hits)[: n_results * 2]

    if not evidence:
        gaps.append("No excerpts retrieved; the name may be absent or spelled "
                    "differently in the corpus.")

    doc_types = sorted({h.doc_type for h in evidence if h.doc_type})
    distinct_docs = len({h.document_id for h in evidence if h.document_id})
    top_score = max((h.score for h in evidence), default=0.0)
    gaps.append("Co-occurrence in documents is not proof of involvement.")

    return DossierResult(
        entity=name,
        safety_rules=safety_rules,
        base_url=client.resolved_base,
        graph_available=graph_available,
        subqueries=subqueries,
        evidence=evidence,
        connections=connections,
        timeline=timeline,
        doc_types=doc_types,
        confidence=_confidence(distinct_docs, top_score, graph_available and bool(connections)),
        gaps=gaps,
    )


def _write_allowed() -> bool:
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


async def submit_corpus_finding(
    *,
    kind: str,
    subject: str,
    body_md: str,
    citations: list[dict[str, Any]],
    confidence: str | None = None,
    gaps: list[str] | None = None,
    job_id: str | None = None,
    client: EpsteinClient | None = None,
) -> dict[str, Any]:
    """Second sink: POST a finding to the epstein service's gated
    /api/research/findings as a `proposed` case-context proposal.

    Best-effort and never raises. Gated twice: by ZEUS_MCP_ALLOW_WRITE (the same
    switch as mnemosyne persistence) AND by the client carrying a write key
    (ZEUS_EPSTEIN_WRITE_API_KEY); without both, this is a no-op. Requires at least
    one citation. The finding never mutates the corpus; a human accepts it before
    any context/claims reflection."""
    if not _write_allowed():
        return {"submitted": False, "reason": "ZEUS_MCP_ALLOW_WRITE is false"}
    if not citations:
        return {"submitted": False, "reason": "no citations; nothing to submit"}
    client = client or get_epstein_client()
    if client is None:
        return {"submitted": False, "reason": "epstein client disabled"}
    if not client.write_enabled:
        return {"submitted": False, "reason": "no write key (ZEUS_EPSTEIN_WRITE_API_KEY unset)"}
    provenance = {"agent": "epstein_research", "job_id": job_id or "", "base_url": client.resolved_base or ""}
    try:
        row = await client.submit_finding(
            kind=kind, subject=subject, body_md=body_md, citations=citations,
            confidence=confidence, gaps=gaps, provenance=provenance,
        )
    except EpsteinError as exc:
        logger.warning("submit_corpus_finding failed: %s", exc)
        return {"submitted": False, "reason": f"submit failed: {exc}"}
    return {"submitted": True, "finding_id": row.get("finding_id"), "status": row.get("status")}


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

    # Second sink: also submit to the epstein service's gated /findings, if a
    # write key is configured. Best-effort; a failure here does not undo the
    # mnemosyne persistence above.
    corpus = await submit_corpus_finding(
        kind="question",
        subject=result.question,
        body_md=body,
        citations=citations,
        confidence=result.confidence,
        gaps=result.gaps,
        job_id=result.job_id,
    )
    return {
        "persisted": True,
        "source_id": source_id,
        "citations": len(citations),
        "corpus_finding": corpus,
    }


# ------------------------------------------------------------------------- #
# Component C: connection map
# ------------------------------------------------------------------------- #
@dataclass
class ConnectionMapResult:
    """How two or more entities connect through the corpus graph + evidence.
    `to_markdown()` renders the writeup; `to_graph()` emits a neutral
    {nodes, edges} export. Every relation is co-occurrence or explicitly cited;
    the corpus graph has no contradiction edge, so none is implied."""

    entities: list[str]
    safety_rules: str
    base_url: str | None
    graph_available: bool
    pairs: list[dict[str, Any]] = field(default_factory=list)
    confidence: str = "low"
    gaps: list[str] = field(default_factory=list)
    error: str | None = None

    def citations(self) -> list[dict[str, str]]:
        seen: set[str] = set()
        out: list[dict[str, str]] = []
        for p in self.pairs:
            for h in p.get("evidence", []) or []:
                if h.document_id and h.document_id not in seen:
                    seen.add(h.document_id)
                    out.append({"document_id": h.document_id, "source_label": h.source_label})
        return out

    def to_graph(self) -> dict[str, Any]:
        node_ids: dict[str, dict[str, Any]] = {}
        for e in self.entities:
            node_ids[e] = {"id": e, "role": "subject"}
        edges: list[dict[str, Any]] = []
        for p in self.pairs:
            for mid in p.get("intermediaries", []) or []:
                node_ids.setdefault(mid, {"id": mid, "role": "intermediary"})
            edges.append({
                "source": p["a"],
                "target": p["b"],
                "connected": bool(p.get("connected")),
                "relation": "co-occurrence",
                "intermediaries": p.get("intermediaries", []),
                "evidence": [
                    {"document_id": h.document_id, "source_label": h.source_label}
                    for h in (p.get("evidence", []) or [])
                ],
                "events": p.get("events", []),
            })
        return {"nodes": list(node_ids.values()), "edges": edges}

    def to_markdown(self) -> str:
        lines: list[str] = [f"# Connection Map: {' <-> '.join(self.entities)}", ""]
        lines.append(
            "> Sensitive legal corpus (victims + unproven allegations). Edges are "
            "document CO-OCCURRENCE or explicitly-cited relations, NEVER "
            "accusations. Allegations remain allegations; victim identities and "
            "redacted content are never inferred."
        )
        lines.append("")
        if self.error:
            lines.append(f"**Error:** {self.error}")
            return "\n".join(lines)

        access = "graph + search" if self.graph_available else "search-only (graph unavailable)"
        lines.append(f"- **Access mode:** {access}")
        lines.append(f"- **Confidence:** {self.confidence}")
        lines.append("")

        for p in self.pairs:
            state = "connected" if p.get("connected") else "no graph path found"
            lines.append(f"## {p['a']} <-> {p['b']} — {state}")
            mids = p.get("intermediaries", []) or []
            if mids:
                lines.append(f"- **Intermediaries (co-occurrence):** {', '.join(mids)}")
            for ev in (p.get("events", []) or [])[:5]:
                date = ev.get("date") or "undated"
                desc = (ev.get("description") or "")[:200].replace("\n", " ").strip()
                lines.append(f"- **{date}**: {desc}")
            evidence = p.get("evidence", []) or []
            if evidence:
                lines.append("- **Cited evidence:**")
                for h in evidence[:5]:
                    lines.append(f"  - [{h.citation()}] {h.text[:200].strip()}")
            else:
                lines.append("- No excerpt retrieved for this pair (graph "
                             "co-occurrence only, if any).")
            lines.append("")

        cits = self.citations()
        if cits:
            lines.append("## Citations")
            for i, c in enumerate(cits, 1):
                lines.append(f"[{i}] {c['document_id']} ({c['source_label'] or 'corpus'})")
            lines.append("")

        if self.gaps:
            lines.append("## Gaps / caveats")
            for g in self.gaps:
                lines.append(f"- {g}")
        return "\n".join(lines)


def _connection_people(connection: dict[str, Any], *, a: str, b: str,
                       doc_type_keys: set[str]) -> list[str]:
    """Named intermediaries on a connection path, excluding the two endpoints."""
    out: list[str] = []
    seen: set[str] = set()
    for n in connection.get("nodes", []) or []:
        nm = n.get("name")
        if not nm:
            continue
        nm = str(nm).strip()
        low = nm.lower()
        if low in seen or low in _ROLE_STOPWORDS:
            continue
        if _related_names(nm, a) or _related_names(nm, b):
            continue
        if not _plausible_entity(nm, doc_type_keys):
            continue
        seen.add(low)
        out.append(nm)
    return out


async def run_connection_map(
    names: list[str],
    *,
    depth: int = 2,
    n_results: int = 6,
    client: EpsteinClient | None = None,
) -> ConnectionMapResult:
    """Map how 2+ entities connect: pairwise graph paths (co-occurrence) plus
    scoped cited evidence per pair. Read-only; degrades to evidence-only when the
    graph is down."""
    clean = [str(n).strip() for n in names if str(n).strip()]
    # Dedupe preserving order.
    entities = list(dict.fromkeys(clean))
    if len(entities) < 2:
        return ConnectionMapResult(
            entities=entities, safety_rules=_FALLBACK_SAFETY, base_url=None,
            graph_available=False,
            error="A connection map needs at least two distinct entities.",
        )

    client = client or get_epstein_client()
    if client is None:
        return ConnectionMapResult(
            entities=entities, safety_rules=_FALLBACK_SAFETY, base_url=None,
            graph_available=False,
            error="Epstein research capability disabled (ZEUS_EPSTEIN_ENABLED=0).",
        )

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
    graph_down_noted = False
    sem = asyncio.Semaphore(_SEARCH_CONCURRENCY)

    async def _pair(a: str, b: str) -> dict[str, Any]:
        nonlocal graph_down_noted
        async with sem:
            connected = False
            intermediaries: list[str] = []
            events: list[dict[str, str]] = []
            if graph_available:
                try:
                    d = await client.entity(a, depth=depth, related_to=b)
                    conn = d.get("connection") or {}
                    connected = bool(conn.get("connected"))
                    intermediaries = _connection_people(
                        conn, a=a, b=b, doc_type_keys=doc_type_keys
                    )
                    events = _graph_events(conn, limit=5)
                except EpsteinError as exc:
                    if exc.status == 503 and not graph_down_noted:
                        gaps.append("Entity graph unavailable (503); pairs rely on "
                                    "scoped search evidence only.")
                        graph_down_noted = True
                    elif exc.status != 503:
                        logger.warning("connection %s<->%s failed: %s", a, b, exc)
            # Scoped cited evidence for the pair (independent of the graph).
            evidence = _dedupe_hits(
                await _search_one(client, f"{a} {b}", n_results=n_results)
            )
        return {
            "a": a, "b": b, "connected": connected,
            "intermediaries": intermediaries, "events": events, "evidence": evidence,
        }

    pairs = await asyncio.gather(
        *[_pair(a, b) for a, b in itertools.combinations(entities, 2)]
    )

    if not graph_available and not graph_down_noted:
        gaps.append("Graph not available; edges are scoped-search co-occurrence only.")
    gaps.append("Edges are document co-occurrence, not proof of a relationship or "
                "involvement.")

    connected_pairs = sum(1 for p in pairs if p["connected"])
    distinct_docs = len({
        h.document_id for p in pairs for h in p["evidence"] if h.document_id
    })
    top_score = max(
        (h.score for p in pairs for h in p["evidence"]), default=0.0
    )
    confidence = _confidence(distinct_docs, top_score, connected_pairs > 0)

    return ConnectionMapResult(
        entities=entities,
        safety_rules=safety_rules,
        base_url=client.resolved_base,
        graph_available=graph_available,
        pairs=list(pairs),
        confidence=confidence,
        gaps=gaps,
    )


# ------------------------------------------------------------------------- #
# Component D: shared report-to-disk writer (used by tools + the Kronos job)
# ------------------------------------------------------------------------- #
_REPORT_SUBDIRS = {
    "question": "",
    "entity_dossier": "dossiers",
    "connection_map": "maps",
}


def _slug(text: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "untitled"


def _reports_root() -> Path:
    return Path(
        os.getenv("ZEUS_EPSTEIN_REPORT_DIR")
        or os.getenv("ZEUS_DEEP_RESEARCH_DIR", "/home/chris/zeus/docs/research")
    )


def write_research_report(
    kind: str,
    subject: str,
    markdown: str,
    *,
    sidecar: dict[str, Any] | None = None,
    when: str | None = None,
) -> Path:
    """Write a report to `ZEUS_EPSTEIN_REPORT_DIR/<subdir>/<date>-epstein-<slug>.md`,
    routed by kind (question -> root, entity_dossier -> dossiers/, connection_map
    -> maps/). An optional `sidecar` dict is written alongside as .json (used for
    the connection-map graph export). Returns the markdown path."""
    day = when or datetime.now(timezone.utc).date().isoformat()
    sub = _REPORT_SUBDIRS.get(kind, "")
    root = _reports_root() / sub if sub else _reports_root()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{day}-epstein-{_slug(subject)}.md"
    path.write_text(markdown, encoding="utf-8")
    if sidecar is not None:
        path.with_suffix(".json").write_text(
            json.dumps(sidecar, indent=2, default=str), encoding="utf-8"
        )
    return path
