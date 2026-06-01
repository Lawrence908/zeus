# zeus/kronos/jobs/deep_research.py — Multi-agent deep research as a Kronos job.
#
# Mirrors the Claude Code /deep-research skill but runs autonomously inside
# Zeus. Pipeline per call:
#   1. Decompose the topic into N sub-questions via small_llm_call (structured).
#   2. Fan out parallel sub-research with asyncio.gather: each sub-question
#      runs Brave + Tavily searches in parallel, dedupes hits, fetches the top
#      K result pages as clean markdown via Jina Reader, then small_llm_call
#      synthesizes cited findings from snippets + full page content.
#   3. Optional gap pass: identify thin or unresolved areas and run 1-3
#      follow-up sub-questions (deep tier always; standard tier if gaps found).
#   4. Synthesize a global report with renumbered citations via small_llm_call.
#   5. Aegis post-filter the report (default policy) before disk write.
#   6. Write to /home/chris/zeus/docs/research/YYYY-MM-DD-<slug>.md.
#   7. Best-effort writeback: append a one-liner to /inbox/append and ingest
#      the report into the Zeus knowledge store so future runs can cite it.
#   8. Return a small metadata dict for the JobRun output_summary.
#
# Privacy tier 2: research topics are public, so the full provider chain
# (gemini_paid, groq, openrouter, anthropic_haiku, ollama) is in play.
#
# Search providers are independent. Both run in parallel per query; either
# one missing its key is non-fatal. Budgets:
#   - Brave free: 1 qps / 2000 queries/month
#   - Tavily free: 1000 queries/month
#   - Jina Reader: free without a key (rate-limited); higher limits with one
# A `deep` run does ~32 search calls per provider and up to 40 page fetches.
# The dedicated module-level semaphores pace these independently from the
# chat-path web_search tool so an overnight job and a chat session don't
# block each other.
from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from zeus.core.small_llm import small_llm_call
from zeus.safety.policy_engine import aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.kronos.deep_research")

REPORTS_DIR = Path(
    os.getenv("ZEUS_DEEP_RESEARCH_DIR", "/home/chris/zeus/docs/research")
)

# Per-depth budgets. `synth_tokens` caps the synthesis call's output size.
# `fetches` = number of result URLs to fetch as full pages via Jina Reader
# per sub-question (after dedupe across providers).
DEPTH_BUDGET: dict[str, dict[str, Any]] = {
    "quick":    {"subq": 3, "searches": 2, "results": 5, "fetches": 3, "gap": False,  "synth_tokens": 1500},
    "standard": {"subq": 5, "searches": 3, "results": 5, "fetches": 4, "gap": "auto", "synth_tokens": 2500},
    "deep":     {"subq": 8, "searches": 4, "results": 6, "fetches": 5, "gap": True,   "synth_tokens": 4000},
}

_BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
_BRAVE_TIMEOUT = 10.0
_brave_sem = asyncio.Semaphore(1)
_brave_last_ts: float = 0.0

_TAVILY_URL = "https://api.tavily.com/search"
_TAVILY_TIMEOUT = 15.0
_tavily_sem = asyncio.Semaphore(2)
_tavily_last_ts: float = 0.0
_TAVILY_MIN_INTERVAL = 0.5  # seconds — conservative against soft rate limits

_JINA_URL = "https://r.jina.ai/"
_JINA_TIMEOUT = 25.0
_JINA_MAX_CONTENT_CHARS = 6000  # ~1.5k tokens; keeps multi-page synth in budget
_jina_sem = asyncio.Semaphore(4)  # Jina Reader is HTTP-fetch-bound; a few in flight is fine


# --------------------------------------------------------------------------- #
# Structured-output models                                                    #
# --------------------------------------------------------------------------- #

class _Subquestion(BaseModel):
    question: str


class _Plan(BaseModel):
    subquestions: list[_Subquestion]


class _PacketLLMShape(BaseModel):
    """What the per-subquestion synthesis LLM returns."""
    findings: list[str] = Field(default_factory=list)
    gaps: str = ""


class _GapList(BaseModel):
    follow_ups: list[str] = Field(default_factory=list)


class _Source(BaseModel):
    title: str
    url: str
    accessed: str  # YYYY-MM-DD


class _Packet(BaseModel):
    """Internal packet collected per sub-question."""
    subquestion: str
    findings: list[str] = Field(default_factory=list)  # each ends with [n] markers
    sources: list[_Source] = Field(default_factory=list)
    gaps: str = ""
    error: str | None = None


# --------------------------------------------------------------------------- #
# Public entry point                                                          #
# --------------------------------------------------------------------------- #

async def run_deep_research(params: dict[str, Any]) -> dict[str, Any]:
    """
    Kronos built-in: orchestrate a multi-agent research run.

    Params:
      topic:    (required) what to research
      depth:    "quick" | "standard" (default) | "deep"
      format:   "markdown" (default) | "brief" | "outline" | "qa"
      out:      optional override for output file path
    """
    topic = str(params.get("topic") or "").strip()
    if not topic:
        raise ValueError("deep_research requires a 'topic' parameter")

    depth = str(params.get("depth") or "standard").lower()
    if depth not in DEPTH_BUDGET:
        depth = "standard"

    fmt = str(params.get("format") or "markdown").lower()
    if fmt not in {"markdown", "brief", "outline", "qa"}:
        fmt = "markdown"

    out_override = params.get("out")
    correlation = str(params.get("_correlation_id") or "manual")
    budget = DEPTH_BUDGET[depth]
    started = time.monotonic()

    # 1. Decompose
    plan = await _decompose(
        topic, n=int(budget["subq"]), caller=f"deep_research:{correlation}"
    )
    logger.info(
        "deep_research: %d sub-questions for topic=%r (depth=%s)",
        len(plan.subquestions), topic[:80], depth,
    )

    # 2. Fan out
    raw_results = await asyncio.gather(
        *[
            _research_one(topic, sq, budget, caller=f"deep_research:{correlation}:sub{i}")
            for i, sq in enumerate(plan.subquestions)
        ],
        return_exceptions=True,
    )
    valid_packets: list[_Packet] = []
    failed_packets = 0
    for r in raw_results:
        if isinstance(r, _Packet) and r.error is None and r.findings:
            valid_packets.append(r)
        else:
            failed_packets += 1
            if isinstance(r, BaseException):
                logger.warning("deep_research: subquestion errored: %s", r)

    # 3. Gap pass (deep always, standard if thin, quick never)
    follow_up_questions: list[str] = []
    if budget["gap"] is True or (
        budget["gap"] == "auto" and _has_thin_packets(valid_packets)
    ):
        max_followups = 3 if depth == "deep" else 2
        gap_qs = await _identify_gaps(
            topic, valid_packets, max_followups=max_followups,
            caller=f"deep_research:{correlation}:gap",
        )
        if gap_qs:
            follow_results = await asyncio.gather(
                *[
                    _research_one(
                        topic, _Subquestion(question=q), budget,
                        caller=f"deep_research:{correlation}:fu{i}",
                    )
                    for i, q in enumerate(gap_qs)
                ],
                return_exceptions=True,
            )
            for r in follow_results:
                if isinstance(r, _Packet) and r.error is None and r.findings:
                    valid_packets.append(r)
                    follow_up_questions.append(r.subquestion)

    # 4. Synthesize
    report_text = await _synthesize(
        topic=topic, depth=depth, fmt=fmt, packets=valid_packets,
        budget=budget,
        attempted=len(plan.subquestions) + len(follow_up_questions),
        failed=failed_packets,
        caller=f"deep_research:{correlation}:synth",
    )

    # 5. Aegis post-filter on the report content (explicit; the executor's
    #    post-hook only sees the metadata dict we return, not the file body).
    if aegis_enabled() and report_text:
        outcome = evaluate_text(report_text, policy_name="default")
        if outcome.status == "rejected":
            logger.warning(
                "deep_research: report blocked by Aegis: %s", outcome.message
            )
            report_text = (
                f"# {topic}\n\n"
                f"**Date:** {datetime.now(timezone.utc).date().isoformat()}\n\n"
                f"## Aegis blocked\n\n"
                f"The synthesized report was blocked by Aegis "
                f"({outcome.message or 'policy violation'}). "
                f"This usually means a fetched source contained content that "
                f"triggered a safety rule. Refine the topic or review the "
                f"policy and re-run.\n"
            )

    # 6. Write file
    out_path = _resolve_out_path(out_override, topic)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_text, encoding="utf-8")

    elapsed_ms = int((time.monotonic() - started) * 1000)
    headings = _extract_headings(report_text)[:20]
    source_count = _count_sources(report_text)

    logger.info(
        "deep_research: wrote report=%s sources=%d elapsed=%dms",
        out_path, source_count, elapsed_ms,
    )

    # 7. Best-effort writeback (skipped on empty runs; logged but not raised).
    writeback: dict[str, str] = {"inbox": "skipped", "library": "skipped"}
    if valid_packets:
        writeback = await _writeback_completion(
            topic=topic, out_path=out_path, depth=depth, fmt=fmt,
            source_count=source_count, headings=headings,
        )

    return {
        "status": "ok" if valid_packets else "empty",
        "topic": topic[:120],
        "depth": depth,
        "format": fmt,
        "out_path": str(out_path),
        "subquestions_attempted": len(plan.subquestions),
        "follow_ups": len(follow_up_questions),
        "subquestions_failed": failed_packets,
        "sources": source_count,
        "headings": headings,
        "duration_ms": elapsed_ms,
        "writeback": writeback,
    }


# --------------------------------------------------------------------------- #
# Decomposition                                                               #
# --------------------------------------------------------------------------- #

_DECOMPOSE_SYSTEM = (
    "You are a research planner. Given a research topic, decompose it into "
    "non-overlapping sub-questions a thorough investigator would explore to "
    "produce a referenced writeup. Each sub-question must be self-contained "
    "and answerable from public web sources. Avoid restating the topic; ask "
    "concrete questions whose answers compose into a full picture."
)


async def _decompose(topic: str, *, n: int, caller: str) -> _Plan:
    user = (
        f"Topic: {topic}\n\n"
        f"Generate exactly {n} sub-questions, ordered from foundational to "
        f"specific. Return strict JSON matching the schema."
    )
    try:
        res = await small_llm_call(
            system=_DECOMPOSE_SYSTEM,
            user=user,
            max_tokens=600,
            response_format=_Plan,
            min_privacy_tier=2,
            caller=caller,
        )
    except Exception as exc:
        logger.warning("deep_research: decomposition crashed: %s", exc)
        return _Plan(subquestions=[_Subquestion(question=topic)])

    if isinstance(res.parsed, _Plan) and res.parsed.subquestions:
        # Trim to n in case the LLM over-produced
        return _Plan(subquestions=res.parsed.subquestions[:n])

    logger.warning(
        "deep_research: decomposition unparsed (%s); using topic as single sub-question",
        (res.errors[-3:] if res.errors else "no errors"),
    )
    return _Plan(subquestions=[_Subquestion(question=topic)])


# --------------------------------------------------------------------------- #
# Per-subquestion research                                                    #
# --------------------------------------------------------------------------- #

_SUBQ_SYSTEM = (
    "You synthesize web search results into research findings with citations. "
    "Use ONLY the materials provided — snippets and (when present) full page "
    "content — do not invoke prior knowledge. Prefer citing claims from full "
    "page content over snippets when both are available; full content is more "
    "specific and verifiable. Each finding must end with one or more citation "
    "markers like [1] or [3][7] where the numbers index the source list "
    "provided in the user message. If sources disagree, surface the "
    "disagreement explicitly. If the materials are too thin to answer, return "
    "an empty 'findings' list and explain in 'gaps'. Output strict JSON "
    "matching the schema."
)


async def _research_one(
    topic: str, sq: _Subquestion, budget: dict[str, Any], *, caller: str,
) -> _Packet:
    today = datetime.now(timezone.utc).date().isoformat()

    queries = _build_queries(sq.question, topic, n=int(budget["searches"]))

    # Fan out across all configured providers in parallel per query.
    all_hits: list[dict[str, Any]] = []
    for q in queries:
        hits = await _search_all(q, count=int(budget["results"]))
        all_hits.extend(hits)

    # Deduplicate by URL while preserving first-seen order
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for h in all_hits:
        u = h.get("url", "").strip()
        if not u or u in seen:
            continue
        seen.add(u)
        unique.append(h)

    if not unique:
        return _Packet(
            subquestion=sq.question,
            gaps=f"No web results for any of {len(queries)} queries.",
            error="no_search_results",
        )

    # Fetch top K full pages via Jina Reader for grounded citations.
    fetch_count = min(int(budget.get("fetches", 3)), len(unique))
    if fetch_count > 0:
        top_hits = unique[:fetch_count]
        contents = await asyncio.gather(
            *[_fetch_page(h["url"]) for h in top_hits],
            return_exceptions=True,
        )
        for hit, content in zip(top_hits, contents):
            if isinstance(content, str) and content:
                hit["content_full"] = content

    sources = [
        _Source(title=(h.get("title") or "")[:200], url=h["url"], accessed=today)
        for h in unique
    ]

    snippets_block = "\n\n".join(
        _render_hit(i + 1, h) for i, h in enumerate(unique)
    )

    user = (
        f"Sub-question: {sq.question}\n"
        f"(Parent topic context: {topic[:200]})\n\n"
        f"Sources:\n{snippets_block}\n\n"
        f"Produce 3-6 short findings (each one sentence, each citing one or "
        f"more sources via [n]) and a 'gaps' field describing what could NOT "
        f"be answered from these sources. Use the same [n] indices as the "
        f"sources above. Return strict JSON."
    )

    try:
        res = await small_llm_call(
            system=_SUBQ_SYSTEM,
            user=user,
            max_tokens=900,
            response_format=_PacketLLMShape,
            min_privacy_tier=2,
            caller=caller,
        )
    except Exception as exc:
        logger.warning(
            "deep_research: subq synth failed sq=%r: %s", sq.question[:60], exc
        )
        return _Packet(
            subquestion=sq.question, sources=sources,
            gaps="LLM synthesis failed.",
            error=f"synth: {type(exc).__name__}",
        )

    if not isinstance(res.parsed, _PacketLLMShape):
        return _Packet(
            subquestion=sq.question, sources=sources,
            gaps="LLM returned unstructured output.",
            error="parse_failed",
        )

    return _Packet(
        subquestion=sq.question,
        findings=[f.strip() for f in res.parsed.findings if f.strip()],
        sources=sources,
        gaps=res.parsed.gaps,
    )


def _build_queries(sq: str, topic: str, *, n: int) -> list[str]:
    """Cheap deterministic query variations. Up to 4 distinct shapes."""
    base = sq.strip()
    qs = [base]
    if n > 1:
        qs.append(f"{base} {topic[:60]}".strip())
    if n > 2:
        qs.append(f"{base} review OR overview OR survey")
    if n > 3:
        qs.append(f"{base} 2026")
    return qs[:n]


def _render_hit(idx: int, h: dict[str, Any]) -> str:
    """Format a single search hit for inclusion in the per-subq synth prompt.

    Includes full page content (Jina Reader output) when available; falls
    back to the search snippet otherwise. The 'Full content' marker is what
    cues the LLM to prefer it over the snippet (see _SUBQ_SYSTEM).
    """
    title = (h.get("title") or "").strip()
    url = (h.get("url") or "").strip()
    desc = (h.get("description") or "").strip()[:500]
    full = (h.get("content_full") or "").strip()
    if full:
        return (
            f"[{idx}] {title}\n{url}\n"
            f"Snippet: {desc}\n\n"
            f"Full content (cite from this when possible):\n{full}"
        )
    return f"[{idx}] {title}\n{url}\n{desc}"


# --------------------------------------------------------------------------- #
# Gap pass                                                                    #
# --------------------------------------------------------------------------- #

_GAP_SYSTEM = (
    "You identify research follow-up questions. Given a list of unresolved "
    "gaps from completed sub-questions, propose at most N concrete, "
    "web-searchable follow-up questions that would resolve the most "
    "important gaps. Skip gaps that look unresolvable from public sources."
)


async def _identify_gaps(
    topic: str, packets: list[_Packet], *, max_followups: int, caller: str,
) -> list[str]:
    if not packets:
        return []
    gap_lines = [
        f"- Sub-question: {p.subquestion}\n  Gaps: {p.gaps}"
        for p in packets if p.gaps
    ]
    if not gap_lines:
        return []

    try:
        res = await small_llm_call(
            system=_GAP_SYSTEM,
            user=(
                f"Topic: {topic}\n\nGaps from completed sub-questions:\n"
                + "\n".join(gap_lines)
                + f"\n\nPropose at most {max_followups} follow-up questions. "
                + "If no useful follow-ups are possible, return an empty list."
            ),
            max_tokens=400,
            response_format=_GapList,
            min_privacy_tier=2,
            caller=caller,
        )
    except Exception as exc:
        logger.warning("deep_research: gap-pass crashed: %s", exc)
        return []

    if isinstance(res.parsed, _GapList):
        return [q.strip() for q in res.parsed.follow_ups[:max_followups] if q.strip()]
    return []


def _has_thin_packets(packets: list[_Packet]) -> bool:
    if not packets:
        return True
    thin = sum(1 for p in packets if len(p.findings) < 2 or p.gaps)
    return thin >= max(2, len(packets) // 3)


# --------------------------------------------------------------------------- #
# Synthesis                                                                   #
# --------------------------------------------------------------------------- #

_SYNTH_SYSTEM = (
    "You synthesize a research report from per-sub-question findings. "
    "Every claim in TL;DR, Key Findings, and Detailed Analysis must carry a "
    "[n] citation matching the global Sources list provided. Do not invent "
    "facts not present in the findings. If findings disagree across "
    "sub-questions, surface the disagreement rather than picking one. "
    "Output raw markdown — no JSON, no fences, no preamble."
)


async def _synthesize(
    *, topic: str, depth: str, fmt: str, packets: list[_Packet],
    budget: dict[str, Any], attempted: int, failed: int, caller: str,
) -> str:
    today = datetime.now(timezone.utc).date().isoformat()

    if not packets:
        return _empty_report(topic, depth, today, attempted, failed)

    # Build a global, deduplicated source list
    global_sources: list[_Source] = []
    url_to_idx: dict[str, int] = {}
    for p in packets:
        for s in p.sources:
            if s.url not in url_to_idx:
                url_to_idx[s.url] = len(global_sources) + 1
                global_sources.append(s)

    # Re-render each packet's findings with citations renumbered to global indices
    packet_blocks: list[str] = []
    for pi, p in enumerate(packets):
        local_to_global = {
            i: url_to_idx[s.url] for i, s in enumerate(p.sources, start=1)
        }
        rewritten = [_renumber(f, local_to_global) for f in p.findings]
        block = (
            f"### Sub-question {pi + 1}: {p.subquestion}\n"
            + "\n".join(f"- {f}" for f in rewritten)
            + (f"\n  Gaps: {p.gaps}" if p.gaps else "")
        )
        packet_blocks.append(block)

    sources_md = "\n".join(
        f"[{i + 1}] {s.title} — {s.url} — accessed {s.accessed}"
        for i, s in enumerate(global_sources)
    )

    user = (
        f"# Topic\n{topic}\n\n"
        f"# Depth\n{depth}\n\n"
        f"# Date\n{today}\n\n"
        f"# Per-sub-question findings (citations are GLOBAL indices)\n\n"
        + "\n\n".join(packet_blocks)
        + "\n\n# Global sources\n"
        + sources_md
        + "\n\n# Format\n"
        + _format_instructions(fmt)
        + "\n\nProduce the complete report now. Reproduce the Sources section "
        "verbatim at the end so citations are addressable."
    )

    try:
        res = await small_llm_call(
            system=_SYNTH_SYSTEM,
            user=user,
            max_tokens=int(budget["synth_tokens"]),
            response_format="text",
            min_privacy_tier=2,
            caller=caller,
        )
    except Exception as exc:
        logger.error("deep_research: synthesis failed: %s", exc)
        return _empty_report(topic, depth, today, attempted, failed)

    text = (res.text or "").strip()
    if not text:
        return _empty_report(topic, depth, today, attempted, failed)
    return text


def _format_instructions(fmt: str) -> str:
    if fmt == "brief":
        return (
            "One-page brief. Title (# heading), date line, TL;DR (3-5 bullets "
            "with [n]), Key Findings (5-8 numbered with [n]), Sources at end."
        )
    if fmt == "outline":
        return (
            "Hierarchical outline. Top-level subtopic headings (##), nested "
            "bullets for findings, each leaf bullet ends with [n]. TL;DR "
            "section above the outline; Sources at end."
        )
    if fmt == "qa":
        return (
            "Q&A. Top has TL;DR. Then for each sub-question render "
            "'## Q: <question>' followed by '**A:** <answer with [n] "
            "citations>'. End with Sources."
        )
    return (
        "Standard markdown report:\n"
        "# <Topic>\n\n"
        "**Date:** <YYYY-MM-DD>  \n"
        "**Depth:** <depth>  \n"
        "**Sources consulted:** <N>\n\n"
        "## TL;DR\n3-5 bullets, each with [n] citations.\n\n"
        "## Key Findings\nNumbered list, each item with [n] citations.\n\n"
        "## Detailed Analysis\nProse organized by sub-topic, inline [n] citations.\n\n"
        "## Open Questions / Gaps\nBullets; citations optional.\n\n"
        "## Method\nBrief: sub-questions explored, agent count, follow-ups.\n\n"
        "## Sources\nGlobal sources list rendered verbatim from the input."
    )


def _empty_report(topic: str, depth: str, date: str, attempted: int, failed: int) -> str:
    return (
        f"# {topic}\n\n"
        f"**Date:** {date}  \n**Depth:** {depth}\n\n"
        f"## Result\n\n"
        f"All {attempted} sub-question agents failed or returned no usable "
        f"sources ({failed} failed). Common causes: BRAVE_API_KEY missing or "
        f"rate-limited, topic too narrow, or all providers in the small_llm "
        f"chain unavailable. Re-run later or refine the topic.\n"
    )


# --------------------------------------------------------------------------- #
# Brave search (independent rate-limit from chat-path web_search)             #
# --------------------------------------------------------------------------- #

async def _search_all(query: str, *, count: int) -> list[dict[str, Any]]:
    """Run all configured providers in parallel and merge URL-deduped hits.

    Provider failures are absorbed (logged as warnings); a missing API key
    causes that provider to no-op rather than raise. Returns merged hits in
    first-seen order so each provider's top result keeps a slot near the top.
    """
    results = await asyncio.gather(
        _brave_search(query, count=count),
        _tavily_search(query, count=count),
        return_exceptions=True,
    )
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in results:
        if isinstance(r, BaseException):
            logger.warning(
                "deep_research: search provider failed q=%r: %s",
                query[:60], r,
            )
            continue
        for h in r:
            u = h.get("url", "").strip()
            if not u or u in seen:
                continue
            seen.add(u)
            merged.append(h)
    return merged


async def _brave_search(query: str, *, count: int = 5) -> list[dict[str, Any]]:
    global _brave_last_ts
    api_key = os.getenv("BRAVE_API_KEY", "").strip()
    if not api_key:
        return []  # Soft no-op so _search_all can still return Tavily results

    async with _brave_sem:
        wait = 1.0 - (time.monotonic() - _brave_last_ts)
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            async with httpx.AsyncClient(timeout=_BRAVE_TIMEOUT) as client:
                r = await client.get(
                    _BRAVE_URL,
                    params={"q": query, "count": count},
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": api_key,
                    },
                )
        finally:
            _brave_last_ts = time.monotonic()

    if r.status_code == 429:
        raise RuntimeError("brave 429 rate-limited")
    if r.status_code >= 400:
        raise RuntimeError(f"brave http {r.status_code}")

    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    results = ((data.get("web") or {}).get("results") or [])[:count]
    out: list[dict[str, Any]] = []
    for h in results:
        url = str(h.get("url") or "").strip()
        if not url:
            continue
        out.append({
            "title": str(h.get("title") or "").strip(),
            "url": url,
            "description": str(h.get("description") or "").strip(),
        })
    return out


async def _tavily_search(query: str, *, count: int = 5) -> list[dict[str, Any]]:
    """Tavily Search API. Soft no-op when TAVILY_API_KEY is unset.

    Free tier is 1000 queries/month. Tavily already returns AI-friendly
    snippets (`content` field) longer than Brave's, so this provider often
    surfaces complementary URLs Brave misses.
    """
    global _tavily_last_ts
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return []

    body = {
        "api_key": api_key,
        "query": query,
        "max_results": count,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }

    async with _tavily_sem:
        wait = _TAVILY_MIN_INTERVAL - (time.monotonic() - _tavily_last_ts)
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            async with httpx.AsyncClient(timeout=_TAVILY_TIMEOUT) as client:
                r = await client.post(_TAVILY_URL, json=body)
        finally:
            _tavily_last_ts = time.monotonic()

    if r.status_code == 429:
        raise RuntimeError("tavily 429 rate-limited")
    if r.status_code >= 400:
        raise RuntimeError(f"tavily http {r.status_code}: {r.text[:200]}")

    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    results = (data.get("results") or [])[:count]
    out: list[dict[str, Any]] = []
    for h in results:
        url = str(h.get("url") or "").strip()
        if not url:
            continue
        out.append({
            "title": str(h.get("title") or "").strip(),
            "url": url,
            "description": str(h.get("content") or "").strip(),
        })
    return out


# --------------------------------------------------------------------------- #
# Page fetcher (Jina Reader)                                                  #
# --------------------------------------------------------------------------- #

async def _fetch_page(url: str) -> str | None:
    """Fetch a clean-markdown rendering of a URL via Jina Reader.

    Free without an API key (rate-limited); a JINA_READER_API_KEY raises the
    limit. Returns None on any failure or empty body. Caps at
    _JINA_MAX_CONTENT_CHARS so a single huge page doesn't blow the synth
    prompt budget.
    """
    if not url:
        return None
    headers = {"Accept": "text/plain"}
    api_key = os.getenv("JINA_READER_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    async with _jina_sem:
        try:
            async with httpx.AsyncClient(timeout=_JINA_TIMEOUT) as client:
                r = await client.get(_JINA_URL + url, headers=headers)
        except Exception as exc:
            logger.warning(
                "deep_research: jina fetch failed url=%s: %s", url[:80], exc
            )
            return None

    if r.status_code >= 400:
        logger.info(
            "deep_research: jina returned %d for url=%s", r.status_code, url[:80]
        )
        return None
    text = (r.text or "").strip()
    if not text:
        return None
    return text[:_JINA_MAX_CONTENT_CHARS]


# --------------------------------------------------------------------------- #
# Completion writeback (inbox + library)                                      #
# --------------------------------------------------------------------------- #

async def _writeback_completion(
    *,
    topic: str,
    out_path: Path,
    depth: str,
    fmt: str,
    source_count: int,
    headings: list[str],
) -> dict[str, str]:
    """Best-effort post-run side effects. Errors are logged, not raised.

    Two effects:
      1. Append a one-line note to the user's inbox via /inbox/append so the
         user sees "research done" without polling /jobs.
      2. Ingest the report markdown as a single KnowledgeChunk into the Zeus
         knowledge store, keyed by file path. Lets future deep-research runs
         (and chat queries) cite previous research. Re-runs that overwrite
         the same path will create a second chunk; cleanup is left to the
         knowledge ingest pipeline rather than re-implemented here.
    """
    results = {"inbox": "skipped", "library": "skipped"}

    core_url = os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")
    inbox_text = (
        f"Research complete: \"{topic[:80]}\" "
        f"({depth}, {source_count} sources) -> {out_path}"
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{core_url}/inbox/append",
                json={"text": inbox_text, "tags": ["research", "auto"]},
            )
        results["inbox"] = "ok" if r.status_code < 400 else f"http_{r.status_code}"
    except Exception as exc:
        logger.warning("deep_research: inbox writeback failed: %s", exc)
        results["inbox"] = f"err: {type(exc).__name__}"

    try:
        report_text = out_path.read_text(encoding="utf-8")
        await asyncio.to_thread(
            _ingest_report_to_library,
            topic=topic,
            out_path=out_path,
            report_text=report_text,
            depth=depth,
            fmt=fmt,
            source_count=source_count,
            headings=headings,
        )
        results["library"] = "ok"
    except Exception as exc:
        logger.warning("deep_research: library writeback failed: %s", exc)
        results["library"] = f"err: {type(exc).__name__}"

    return results


def _ingest_report_to_library(
    *,
    topic: str,
    out_path: Path,
    report_text: str,
    depth: str,
    fmt: str,
    source_count: int,
    headings: list[str],
) -> None:
    """Add the report as one KnowledgeChunk. Sync; called via to_thread."""
    from zeus.memory.library import KnowledgeChunk, get_knowledge_store

    ks = get_knowledge_store()
    chunk = KnowledgeChunk(
        text=report_text,
        source="deep_research",
        source_id=str(out_path),
        source_path=str(out_path),
        chunk_index=0,
        user_id="user",
        metadata={
            "topic": topic[:300],
            "depth": depth,
            "format": fmt,
            "source_count": source_count,
            "headings": headings[:20],
            "kind": "deep_research_report",
            "generated_at_iso": datetime.now(timezone.utc).isoformat(),
        },
    )
    res = ks.add_chunks([chunk])
    if res.errors:
        # Surface first error so the caller's logger captures it.
        raise RuntimeError(res.errors[0])


# --------------------------------------------------------------------------- #
# Misc helpers                                                                #
# --------------------------------------------------------------------------- #

_CITATION_RE = re.compile(r"\[(\d+)\]")


def _renumber(text: str, mapping: dict[int, int]) -> str:
    def _swap(m: re.Match[str]) -> str:
        n = int(m.group(1))
        return f"[{mapping.get(n, n)}]"
    return _CITATION_RE.sub(_swap, text)


def _resolve_out_path(override: Any, topic: str) -> Path:
    if isinstance(override, str) and override.strip():
        return Path(override).expanduser()
    today = datetime.now(timezone.utc).date().isoformat()
    return REPORTS_DIR / f"{today}-{_slug(topic)}.md"


def _slug(topic: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return s[:max_len] or "untitled"


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def _extract_headings(report: str) -> list[str]:
    return [m.group(2).strip()[:80] for m in _HEADING_RE.finditer(report)]


_SOURCE_RE = re.compile(r"^\[\d+\]", re.MULTILINE)


def _count_sources(report: str) -> int:
    m = re.search(
        r"^##\s*Sources\s*$(.+?)(?=^##\s|\Z)",
        report, re.DOTALL | re.IGNORECASE | re.MULTILINE,
    )
    if not m:
        return len(_SOURCE_RE.findall(report))
    return len(_SOURCE_RE.findall(m.group(1)))


# Keep these importable for tests / future MCP wrappers
__all__ = ["run_deep_research", "REPORTS_DIR"]

# Expose internals for unit tests without making them de-facto public API.
_for_tests = {
    "_decompose": _decompose,
    "_research_one": _research_one,
    "_identify_gaps": _identify_gaps,
    "_synthesize": _synthesize,
    "_brave_search": _brave_search,
    "_tavily_search": _tavily_search,
    "_search_all": _search_all,
    "_fetch_page": _fetch_page,
    "_render_hit": _render_hit,
    "_writeback_completion": _writeback_completion,
    "_slug": _slug,
    "_renumber": _renumber,
    "_extract_headings": _extract_headings,
    "_count_sources": _count_sources,
}
