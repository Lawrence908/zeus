# zeus/kronos/jobs/congressional_scrutiny.py
# Weekly congressional-trading scrutiny briefing.
#
# DRAFT for review. Mirrors the deep_research / newsletter job pattern:
#   1. Pull the CapitolScope context-pack (week-over-week deltas + trend labels)
#      via the MCP tool function directly (no MCP round-trip needed in-process).
#   2. Gather a short open-source news digest for the sectors/tickers that moved
#      most this week (the "global topics" half CapitolScope does not have).
#      Pluggable: default is Tavily; swap in Brave, canary, or Zeus reference.
#   3. small_llm_call synthesizes an intelligence-style assessment connecting the
#      trading shifts to current global topics (BLUF, confidence-graded).
#   4. Write markdown to docs/briefings/, best-effort inbox append + knowledge
#      ingest, and return metadata for the JobRun output_summary.
#
# Privacy: congressional disclosures are public. Set min_privacy_tier / model_hint
# to keep synthesis on your local Ollama (see the small_llm_call call below).
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from zeus.core.small_llm import small_llm_call
from zeus.mcp.tools import capitolscope_context_pack

logger = logging.getLogger("zeus.kronos.congressional_scrutiny")

# Relative, gitignored default (under the writable data mount, NOT the indexed
# docs/ tree the check-docs hook scans). Overridden in-container by ZEUS_BRIEFINGS_DIR.
BRIEFINGS_DIR = Path(os.getenv("ZEUS_BRIEFINGS_DIR", "zeus/data/briefings"))


# ---------------------------------------------------------------- prompt
SYSTEM_PROMPT = """\
You are an intelligence analyst producing a weekly assessment for a private
research reader. Your primary source is CapitolScope: structured signals derived
from public U.S. congressional stock-trading disclosures (STOCK Act filings),
plus a short open-source news digest. Your job is to identify how this week's
congressional-trading shifts may connect to current global topics and events,
and to flag what is worth watching for stock research.

Hard rules:
- These are SIGNALS, not proof. Congressional trades are lagged public
  disclosures; any link to an event is a hypothesis, never insider-trading proof
  and never investment advice. State this.
- Ground every claim in the provided data. Cite the specific signal you reason
  from (a sector's trend label, a cluster, a ticker, a member, a delta). Do NOT
  invent trades, members, tickers, or figures. If the week is thin, say so
  plainly rather than manufacturing a narrative.
- Use calibrated confidence: High / Moderate / Low. Most event-linkage
  hypotheses are Low-to-Moderate; reserve High only for direct, well-evidenced
  alignment between a clear trading shift and a concrete, current event.
- Prefer the DELTAS and trend labels (accelerating_inflow, cooling_outflow,
  new_this_week, member_delta) over raw levels: the story is what CHANGED.
- Be concise and decision-useful. No filler.

Output strictly this markdown structure:

# Congressional Scrutiny Brief — {period}

**BLUF:** 2-4 sentences. The single most important shift this week and its most
plausible global-topic linkage, with a confidence level.

## Notable shifts
- 3-6 bullets: the most significant moves (sector rotation with its trend label,
  herding clusters, newly-active tickers, high-scrutiny members). Each bullet
  names the exact signal it comes from.

## Global-topic hypotheses
For each meaningful linkage (0-4 of them; fewer is fine):
- **<topic or event>** — <which signal> -> <hypothesized connection>.
  Confidence: <High/Moderate/Low>. Confirm/refute: <what evidence would settle it>.

## Watch items
- 2-5 specific things to monitor next week (a ticker, a sector trend, a member,
  an upcoming catalyst such as an earnings print).

## Caveats
- One short paragraph: restate the signals-not-proof framing and note data
  limits for this week (disclosure lag, thin activity, unmatched assets)."""

USER_TEMPLATE = """\
Reporting period (this week): {period}
Prior comparison window: {prior}

== CapitolScope context pack (structured signals; deltas are this-week vs the prior equal week) ==
{context}

== Open-source news digest (for global-topic linkage; may be sparse) ==
{news}

Produce the weekly Congressional Scrutiny Brief per your instructions. Reason
only from the signals above; connect shifts to the news where the evidence
supports it, and be explicit about confidence."""


# ---------------------------------------------------------------- rendering
def _fmt_money(n) -> str:
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "n/a"
    a = abs(n)
    if a >= 1e9:
        return f"${n/1e9:.1f}B"
    if a >= 1e6:
        return f"${n/1e6:.1f}M"
    if a >= 1e3:
        return f"${n/1e3:.0f}K"
    return f"${n:.0f}"


def _render_context(cp: dict[str, Any]) -> str:
    h = cp.get("headline", {})
    lines = [
        f"Headline: {h.get('tickers_active','?')} tickers active, "
        f"{h.get('buys','?')} buys / {h.get('sells','?')} sells, "
        f"net bias {h.get('net_bias','?')}, {h.get('new_tickers_vs_prior',0)} new tickers vs prior.",
        "",
        "Sector rotation (net $, trend vs prior week):",
    ]
    for s in cp.get("sector_rotation", []):
        lines.append(
            f"  - {s['sector']}: {s['trend']} | net {_fmt_money(s['net_notional'])} "
            f"(prior {_fmt_money(s['prior_net_notional'])}, delta {_fmt_money(s['delta'])}), "
            f"{s['members']} members"
        )
    lines += ["", "Active tickers (member delta vs prior week):"]
    for t in cp.get("active_tickers", []):
        tag = " NEW" if t.get("new_this_week") else ""
        lines.append(
            f"  - {t['ticker']} [{t.get('sector','?')}]: {t['net_direction']}, "
            f"{t['members']} members (delta {t['member_delta']:+d}){tag}, {_fmt_money(t['notional'])}"
        )
    clusters = cp.get("notable_clusters", [])
    if clusters:
        lines += ["", "Herding clusters (N members, same ticker+side, short window):"]
        for c in clusters[:6]:
            ret = c.get("avg_return_30d")
            ret_s = "n/a" if ret is None else f"{ret*100:+.1f}%"
            lines.append(
                f"  - {c['member_count']} members {c['direction']} {c['ticker']} "
                f"({c['window_start']}..{c['window_end']}), avg 30d ret {ret_s}, "
                f"lead {c.get('lead_member','?')}"
            )
    movers = cp.get("scrutiny_movers", [])
    if movers:
        lines += ["", "Top scrutiny-score members (composite signal):"]
        for m in movers[:8]:
            lines.append(f"  - {m['member']} ({m.get('party','?')}) score {m['scrutiny_score']}, leading factor {m.get('leading_factor','?')}")
    return "\n".join(lines)


# ---------------------------------------------------------------- news (pluggable)
async def _gather_news(cp: dict[str, Any], max_topics: int = 4) -> str:
    """Short news digest for the sectors/tickers that moved most. Default uses
    Tavily (TAVILY_API_KEY); returns '' if unavailable. Swap for Brave, a canary
    query, or a Zeus reference call as preferred."""
    key = os.getenv("TAVILY_API_KEY", "")
    # Build a few targeted queries from the biggest shifts.
    topics: list[str] = []
    for s in cp.get("sector_rotation", [])[:2]:
        topics.append(f"{s['sector']} sector news this week")
    for t in cp.get("active_tickers", [])[:2]:
        topics.append(f"{t['ticker']} stock news")
    topics = topics[:max_topics]
    if not key or not topics:
        return "(no news source configured; assess from the signals and your own knowledge of current events)"

    out: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            for q in topics:
                r = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": key, "query": q, "max_results": 3, "search_depth": "basic"},
                )
                if r.status_code != 200:
                    continue
                results = (r.json() or {}).get("results", [])
                if results:
                    out.append(f"[{q}]")
                    for it in results:
                        out.append(f"  - {it.get('title','')} ({it.get('url','')})")
    except Exception as e:  # noqa: BLE001
        logger.warning("news gather failed: %s", e)
        return "(news fetch failed; assess from the signals and your own knowledge)"
    return "\n".join(out) or "(no relevant news found)"


# ---------------------------------------------------------------- executor
async def run_congressional_scrutiny(params: dict[str, Any]) -> dict[str, Any]:
    days = int(params.get("days", 7))

    cp = await capitolscope_context_pack(days=days)
    if not cp or "error" in cp:
        return {"status": "error", "error": (cp or {}).get("error", "no data")}

    period = f"{cp.get('this_week',{}).get('start','?')} to {cp.get('this_week',{}).get('end','?')}"
    prior = f"{cp.get('prior_week',{}).get('start','?')} to {cp.get('prior_week',{}).get('end','?')}"
    context = _render_context(cp)
    news = await _gather_news(cp)

    user = USER_TEMPLATE.format(period=period, prior=prior, context=context, news=news)
    result = await small_llm_call(
        system=SYSTEM_PROMPT,
        user=user,
        max_tokens=int(params.get("max_tokens", 1800)),
        response_format="text",
        # Public data, but keep synthesis local on your Ollama:
        min_privacy_tier=1,
        model_hint=params.get("model_hint", "ollama"),
        caller="kronos.congressional_scrutiny",
    )
    briefing = (result.text or "").strip()
    if not briefing:
        return {"status": "error", "error": "empty synthesis"}

    # Write the brief to disk.
    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = BRIEFINGS_DIR / f"{stamp}-congressional-scrutiny.md"
    path.write_text(briefing + "\n", encoding="utf-8")

    sectors = [s["sector"] for s in cp.get("sector_rotation", [])][:6]
    tickers = [t["ticker"] for t in cp.get("active_tickers", [])][:8]

    # Best-effort writeback: a one-liner to the inbox + the brief as a
    # KnowledgeChunk so it is queryable later (and future briefs/chats can cite
    # it). Failures are logged, not raised.
    writeback = await _writeback_brief(out_path=path, period=period, sectors=sectors, tickers=tickers)

    return {
        "status": "ok",
        "path": str(path),
        "period": period,
        "sectors_covered": sectors,
        "tickers_covered": tickers,
        "chars": len(briefing),
        "provider": result.provider_used,
        "writeback": writeback,
    }


# ---------------------------------------------------------------- writeback
async def _writeback_brief(*, out_path: Path, period: str, sectors: list[str],
                           tickers: list[str]) -> dict[str, str]:
    """Append an inbox note and ingest the brief into the Zeus knowledge store.
    Mirrors deep_research's writeback. Best-effort; errors are logged."""
    results = {"inbox": "skipped", "library": "skipped"}
    core_url = os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")

    note = f"Congressional scrutiny brief ({period}): {', '.join(tickers[:5]) or 'thin week'} -> {out_path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{core_url}/inbox/append",
                json={"text": note, "tags": ["capitolscope", "scrutiny", "auto"]},
            )
        results["inbox"] = "ok" if r.status_code < 400 else f"http_{r.status_code}"
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrutiny brief: inbox writeback failed: %s", exc)
        results["inbox"] = f"err: {type(exc).__name__}"

    try:
        text = out_path.read_text(encoding="utf-8")
        await asyncio.to_thread(_ingest_brief_to_library, out_path=out_path, text=text,
                                period=period, sectors=sectors, tickers=tickers)
        results["library"] = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrutiny brief: library writeback failed: %s", exc)
        results["library"] = f"err: {type(exc).__name__}"

    return results


def _ingest_brief_to_library(*, out_path: Path, text: str, period: str,
                             sectors: list[str], tickers: list[str]) -> None:
    """Add the brief as one KnowledgeChunk. Sync; called via to_thread."""
    from zeus.memory.library import KnowledgeChunk, get_knowledge_store

    ks = get_knowledge_store()
    chunk = KnowledgeChunk(
        text=text,
        source="congressional_scrutiny",
        source_id=str(out_path),
        source_path=str(out_path),
        chunk_index=0,
        user_id="user",
        metadata={
            "kind": "congressional_scrutiny_brief",
            "period": period,
            "sectors": sectors,
            "tickers": tickers,
            "generated_at_iso": datetime.now(timezone.utc).isoformat(),
        },
    )
    res = ks.add_chunks([chunk])
    if res.errors:
        raise RuntimeError(res.errors[0])
