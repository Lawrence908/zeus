"""zeus/mcp/tools.py — MCP tool implementations calling Zeus Core HTTP APIs."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


def _allow_write() -> bool:
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in {"1", "true", "yes", "y"}


async def zeus_query(*, query: str, top_k: int = 8, max_tokens: int = 1024) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/context/query",
            json={"query": query, "top_k": top_k, "max_tokens": max_tokens},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json() or {}
        sources = data.get("sources") or []
        source_strings = []
        for s in sources:
            src = (s or {}).get("source")
            if src:
                source_strings.append(str(src))
        return {
            "context": str(data.get("context") or ""),
            "sources": source_strings,
            "token_estimate": int(data.get("token_estimate") or 0),
        }


async def zeus_profile() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/context/profile", timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        summary = str(data.get("summary") or "")
        facts = data.get("facts") or []
        profile = summary
        if facts:
            profile = summary + "\n" + "\n".join(f"- {str(f)}" for f in facts[:12])
        return {"profile": profile.strip(), "updated_at": ""}


async def zeus_remember(*, text: str, namespace: str = "general", tags: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; zeus_remember disabled")

    payload = {"text": text, "namespace": namespace, "tags": tags or []}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{_core_url()}/memory/add", json=payload, timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        return {"memory_id": str(data.get("memory_id") or ""), "status": str(data.get("status") or "ok")}


async def zeus_ingest_trigger(*, source: str = "all") -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; zeus_ingest_trigger disabled")

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/ingest/trigger",
            json={"source": source},
            timeout=120.0,
        )
        r.raise_for_status()
        data = r.json() or {}
        return {
            "status": str(data.get("status") or "ok"),
            "chunks_indexed": int(data.get("chunks_indexed") or 0),
            "sources_run": list(data.get("sources_run") or []),
        }


async def kronos_create_job(
    *,
    name: str,
    description: str = "",
    category: str = "custom",
    cron: str | None = None,
    run_at: str | None = None,
    executor: str | None = None,
    agent: str | None = None,
    endpoint: str = "/run",
    params: dict[str, Any] | None = None,
    timezone: str = "UTC",
    safety_policy: str = "standard",
    timeout_seconds: int = 300,
    max_retries: int = 1,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Create a Kronos scheduled job. Proxies to POST /kronos/jobs.

    Provide exactly one of cron/run_at, and exactly one of executor/agent.
    Returns the created job_id and the next scheduled fire time.
    """
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; kronos_create_job disabled")

    if (cron is None) == (run_at is None):
        raise ValueError("kronos_create_job: pass exactly one of cron or run_at")
    if (executor is None) == (agent is None):
        raise ValueError("kronos_create_job: pass exactly one of executor or agent")

    # Derive a stable id from the name when caller doesn't pick one.
    if not job_id:
        slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
        job_id = slug[:60] or "job"

    payload: dict[str, Any] = {
        "id": job_id,
        "name": name,
        "description": description,
        "category": category,
        "schedule": {"cron": cron, "run_at": run_at, "timezone": timezone},
        "executor": executor,
        "agent": agent,
        "endpoint": endpoint,
        "params": params or {},
        "safety_policy": safety_policy,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
        "enabled": True,
    }

    async with httpx.AsyncClient() as client:
        create = await client.post(
            f"{_core_url()}/kronos/jobs", json=payload, timeout=15.0
        )
        if create.status_code == 409:
            raise ValueError(f"job id {job_id!r} already exists; pass job_id to override")
        create.raise_for_status()
        created = create.json() or {}

        upcoming = await client.get(
            f"{_core_url()}/kronos/schedule/upcoming", params={"limit": 100}, timeout=10.0
        )
        next_fire = ""
        if upcoming.status_code == 200:
            for entry in upcoming.json():
                if entry.get("job_id") == job_id:
                    next_fire = str(entry.get("next_fire") or "")
                    break

    return {
        "job_id": str(created.get("id") or job_id),
        "name": str(created.get("name") or name),
        "category": str(created.get("category") or category),
        "next_fire": next_fire,
        "enabled": bool(created.get("enabled", True)),
    }


async def zeus_memory_search(*, query: str, limit: int = 5) -> dict[str, Any]:
    lim = max(1, min(20, limit))
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/memory/search",
            json={"query": query, "limit": lim},
            timeout=30.0,
        )
        r.raise_for_status()
        data = r.json() or {}
        results = data.get("results") or []
        lines: list[str] = []
        for i, row in enumerate(results, 1):
            score = float(row.get("score") or 0.0)
            text = str(row.get("text") or "")[:200]
            src = str(row.get("source") or "unknown")
            lines.append(f"{i}. [{score:.3f}] ({src})\n   {text}")
        summary = "\n".join(lines) if lines else "No relevant memories found."
        return {"summary": summary, "count": len(results), "results": results}


# ------------------------------------------------------------------
# Olympian tool pack (LAB-328) — read-side
# ------------------------------------------------------------------


async def olympian_status_read() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/admin/status_file", timeout=5.0)
        r.raise_for_status()
        data = r.json() or {}
        return {
            "path": str(data.get("path") or ""),
            "content": str(data.get("content") or ""),
            "mtime": float(data.get("mtime") or 0.0),
            "exists": bool(data.get("exists", True)),
        }


async def olympian_server_health() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/admin/system", timeout=10.0)
        r.raise_for_status()
        return r.json() or {}


async def olympian_file_read(*, path: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_core_url()}/vault/file",
            params={"path": path},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def olympian_file_search(
    *,
    pattern: str,
    root: str | None = None,
    max_results: int = 50,
    case_sensitive: bool = False,
    fixed_strings: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pattern": pattern,
        "max_results": max(1, min(500, int(max_results))),
        "case_sensitive": bool(case_sensitive),
        "fixed_strings": bool(fixed_strings),
    }
    if root:
        payload["root"] = root
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/vault/search",
            json=payload,
            timeout=15.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def olympian_inbox_append(*, text: str, tags: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; olympian_inbox_append disabled")
    payload: dict[str, Any] = {"text": text}
    if tags:
        payload["tags"] = list(tags)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/inbox/append",
            json=payload,
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def olympian_action_list() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/actions/list", timeout=5.0)
        r.raise_for_status()
        return r.json() or {}


async def olympian_action_run(*, name: str, args: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; olympian_action_run disabled")
    payload: dict[str, Any] = {"name": name, "args": list(args or [])}
    # Action runner timeout is enforced server-side; client allows generous
    # slack for the round-trip.
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/actions/run",
            json=payload,
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def zeus_calendar_today() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/calendar/today", timeout=15.0)
        r.raise_for_status()
        return r.json() or {}


async def zeus_image_generate(
    *,
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    seed: int | None = None,
) -> dict[str, Any]:
    """Generate an image from a text prompt via the local ComfyUI GPUs (Apollo
    RTX 5080 FLUX primary, daedalus RTX 3080 SDXL fallback). Returns a URL to the
    finished PNG. Gated by ZEUS_IMAGE_ENABLED on the server; writes only an image
    file, so no ZEUS_MCP_ALLOW_WRITE gate. Generation can take up to a minute."""
    payload: dict[str, Any] = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
    }
    if seed is not None:
        payload["seed"] = seed
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{_core_url()}/images/generate", json=payload, timeout=210.0)
        r.raise_for_status()
        return r.json() or {}


async def zeus_newsletter_latest() -> dict[str, Any]:
    """Return the most recent newsletter digest entry (compact form)."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_core_url()}/api/newsletter/digests",
            params={"limit": 1},
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json() or {}
        digests = data.get("digests") or []
        if not digests:
            return {"digest": None, "exists": False}
        return {"digest": digests[0], "exists": True}



# ---------------------------------------------------------------------------
# CapitolScope — congressional-trading signals (external Signals API)
# ---------------------------------------------------------------------------
def _capitolscope_url() -> str:
    return os.getenv("CAPITOLSCOPE_SIGNALS_URL", "https://capitolscope.chrislawrence.ca").rstrip("/")


def _capitolscope_key() -> str:
    return os.getenv("CAPITOLSCOPE_SIGNALS_KEY", "")


async def _cs_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET a CapitolScope Signals endpoint. Returns the unwrapped `data` object,
    or {"error": ...} on failure (never raises, so agents degrade gracefully)."""
    key = _capitolscope_key()
    if not key:
        return {"error": "CAPITOLSCOPE_SIGNALS_KEY not set"}
    url = f"{_capitolscope_url()}/api/v1/signals/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params or {}, headers={"X-API-Key": key}, timeout=90)
            r.raise_for_status()
            body = r.json() or {}
            return body.get("data", body)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


async def capitolscope_digest(*, days: int = 7) -> dict[str, Any]:
    """Congressional-trading research brief: what Congress has been buying and
    selling lately, herding clusters, sector rotation, and the members most
    worth scrutiny. Use for market context and event-linked research."""
    return await _cs_get("digest", {"days": days})


async def capitolscope_active_tickers(*, days: int = 90, limit: int = 25) -> dict[str, Any]:
    """Tickers ranked by recent congressional activity — what Congress is
    accumulating or distributing (members, buy/sell split, dollar notional)."""
    return await _cs_get("active-tickers", {"days": days, "limit": limit})


async def capitolscope_ticker(*, ticker: str, days: int = 180, limit: int = 60) -> dict[str, Any]:
    """Recent congressional trades for one ticker (who, when, buy/sell, amount,
    30-day return) — congressional flow behind a specific stock."""
    return await _cs_get("recent-trades", {"ticker": ticker, "days": days, "limit": limit})


async def capitolscope_sector_flow(*, days: int = 90) -> dict[str, Any]:
    """Net congressional dollar flow by GICS sector over a window — a rotation
    signal useful for connecting trading to macro/global events."""
    return await _cs_get("sector-flow", {"days": days})


async def capitolscope_leaderboard(*, limit: int = 20) -> dict[str, Any]:
    """Members ranked by composite Scrutiny Score (trading edge, pre-earnings
    positioning, committee conflicts, herding, disclosure lag, bet-size anomaly)."""
    return await _cs_get("leaderboard", {"limit": limit})


async def capitolscope_context_pack(*, days: int = 7) -> dict[str, Any]:
    """One-call, LLM-ready CapitolScope feed for synthesis: the week's
    congressional-trading activity plus week-over-week deltas and trend labels
    (sector rotation, newly-active tickers, member-count changes), notable
    clusters/trades, and top scrutiny movers. Feed this to a model to connect
    congressional trading shifts to global events."""
    return await _cs_get("context-pack", {"days": days})


# ---------------------------------------------------------------------------
# Pheme - news deep-dive search + gated Twitter posting
# ---------------------------------------------------------------------------
async def zeus_news_search(
    *,
    query: str,
    source: str | None = None,
    topic: str | None = None,
    entity: str | None = None,
    since: str | None = None,
    top_k: int = 8,
) -> dict[str, Any]:
    """Deep-dive search over the Pheme news layer (zeus_news): consolidated
    Canary OSINT articles + CapitolScope congressional-trading signals with
    entity/topic/date filters. Use for "what has the news said about X"
    questions across time."""
    from zeus.memory.search import search_news

    results = await asyncio.to_thread(
        search_news,
        query,
        top_k=top_k,
        source=source,
        topic=topic,
        entity=entity,
        since=since,
    )
    return {
        "results": [
            {
                "title": r["metadata"].get("title", ""),
                "text": r["memory"],
                "score": r["score"],
                "source": r["metadata"].get("source", ""),
                "url": r["metadata"].get("url", ""),
                "published_at": r["metadata"].get("published_at", ""),
                "entities": r["metadata"].get("entities", []),
                "topics": r["metadata"].get("topics", []),
                "significance": r["metadata"].get("significance", 0.0),
            }
            for r in results
        ],
        "count": len(results),
    }


def _pheme_twitter_enabled() -> bool:
    return os.getenv("PHEME_TWITTER_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


async def olympian_twitter_post(
    *, text: str, thread: list[str] | None = None
) -> dict[str, Any]:
    """Post a tweet (plus optional reply thread) to the configured X/Twitter
    account. PUBLIC and IRREVERSIBLE: double-gated by ZEUS_MCP_ALLOW_WRITE and
    PHEME_TWITTER_ENABLED, and every tweet text passes the Aegis 'pheme'
    policy pre-hook inside the poster before anything is sent."""
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; olympian_twitter_post disabled")
    if not _pheme_twitter_enabled():
        raise PermissionError("PHEME_TWITTER_ENABLED is false; olympian_twitter_post disabled")

    from zeus.integrations.twitter.poster import TwitterPostError, post_news_thread

    try:
        ids = await post_news_thread(text, thread or [])
    except TwitterPostError as exc:
        return {"posted": False, "error": str(exc)}
    return {"posted": True, "tweet_ids": ids, "url": f"https://x.com/i/web/status/{ids[0]}"}


# ---------------------------------------------------------------------------
# Epstein researcher — live proxy to the external document-research service.
#
# READ-ONLY. The ~1.3M-doc DOJ/court corpus, retrieval, graph, and synthesis
# LLM live in the separate `epstein` service; Zeus stores nothing. SAFETY:
# mention is not involvement; keep allegations labeled; never surface or infer
# victim identities or redacted content; cite document_id + source_label for
# every claim; obey the manifest's safety_rules. There is NO write path here.
# ---------------------------------------------------------------------------
_EPSTEIN_SAFETY = (
    "Sensitive legal corpus (victims + unproven allegations). Mention is not "
    "involvement; keep allegations labeled; never infer victim identities or "
    "redacted content; cite document_id + source_label for every claim."
)


def _epstein_client():
    from zeus.memory.epstein import get_epstein_client

    client = get_epstein_client()
    if client is None:
        raise PermissionError(
            "ZEUS_EPSTEIN_ENABLED is false; the Epstein research capability is disabled"
        )
    return client


async def epstein_capabilities() -> dict[str, Any]:
    """Live capability manifest of the Epstein research service: doc_types,
    filter fields, endpoints, graph availability, auth mode, and the corpus
    safety_rules. Call FIRST; do not hardcode doc types or filters."""
    client = _epstein_client()
    cap = await client.capabilities()
    cap["_resolved_base"] = client.resolved_base
    cap["_safety"] = _EPSTEIN_SAFETY
    return cap


async def epstein_search(
    *,
    query: str,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    document_ids: list[str] | None = None,
    n_results: int = 10,
    expand_graph: bool = False,
) -> dict[str, Any]:
    """Fast semantic search over the Epstein DOJ/court corpus. Each result
    carries a document_id + source_label you MUST cite. Mention is not
    involvement; keep allegations labeled; never infer victim identities."""
    client = _epstein_client()
    data = await client.search(
        query,
        doc_type=doc_type,
        date_mentioned=date_mentioned,
        document_ids=document_ids,
        n_results=n_results,
        expand_graph=expand_graph,
    )
    data["_safety"] = _EPSTEIN_SAFETY
    return data


async def epstein_document(*, document_id: str) -> dict[str, Any]:
    """Reconstructed full text + metadata of one corpus document by id. Do not
    surface or infer victim identities or redacted content; cite the id."""
    client = _epstein_client()
    d = await client.document(document_id)
    d["_safety"] = _EPSTEIN_SAFETY
    return d


async def epstein_entity(
    *, name: str, depth: int = 1, related_to: str | None = None
) -> dict[str, Any]:
    """Entity dossier from the corpus knowledge graph. Graph co-occurrence is a
    signal for where to read, NEVER an accusation. Degrades gracefully when the
    graph is down (503)."""
    from zeus.memory.epstein import EpsteinError

    client = _epstein_client()
    try:
        d = await client.entity(name, depth=depth, related_to=related_to)
    except EpsteinError as exc:
        if exc.status == 503:
            return {"entity": name, "graph_available": False, "error": "graph down (503)", "_safety": _EPSTEIN_SAFETY}
        raise
    d["_safety"] = _EPSTEIN_SAFETY
    return d


async def epstein_research_start(
    *,
    question: str,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    depth: int = 3,
) -> dict[str, Any]:
    """Start an async deep-research job (decompose -> retrieve -> cited
    synthesis). Returns a job_id immediately; poll epstein_research_result.
    Synthesis may time out but citations still return."""
    client = _epstein_client()
    d = await client.start_job(
        question, doc_type=doc_type, date_mentioned=date_mentioned, depth=depth
    )
    d["_safety"] = _EPSTEIN_SAFETY
    return d


async def epstein_research_result(*, job_id: str) -> dict[str, Any]:
    """Poll a deep-research job. Returns status, steps, report (may be empty on
    synthesis timeout — a known caveat), and citations. ALWAYS surface the
    citations even when the prose is missing."""
    client = _epstein_client()
    d = await client.get_job(job_id)
    d["_safety"] = _EPSTEIN_SAFETY
    return d


async def epstein_research(
    *,
    question: str,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    depth: int = 3,
    wait_seconds: int = 0,
) -> dict[str, Any]:
    """End-to-end research workflow: plan sub-queries -> fast cited retrieval ->
    entity signals -> async deep-synthesis job. Returns a citation-backed
    answer (markdown), the citations, an explicit confidence level, and the
    gaps. Mention is not involvement; allegations stay labeled; victim
    identities are never inferred."""
    _epstein_client()  # gate on ZEUS_EPSTEIN_ENABLED
    from zeus.orchestration.epstein_research import run_research

    result = await run_research(
        question,
        doc_type=doc_type,
        date_mentioned=date_mentioned,
        depth=depth,
        poll_budget_seconds=float(wait_seconds or 0),
    )
    return {
        "question": result.question,
        "answer_markdown": result.to_markdown(),
        "citations": result.citations(),
        "confidence": result.confidence,
        "gaps": result.gaps,
        "job_id": result.job_id,
        "job_status": result.job_status,
        "graph_available": result.graph_available,
        "error": result.error,
        "_safety": _EPSTEIN_SAFETY,
    }


async def epstein_entity_dossier(
    *,
    name: str,
    doc_type: str | None = None,
    depth: int = 1,
    write_report: bool = False,
) -> dict[str, Any]:
    """Cited DOSSIER for one entity: graph connections + dated timeline +
    fanned-out cited excerpts + confidence + gaps. Degrades to search-only when
    the graph is down. Co-occurrence is a signal, NEVER an accusation; allegations
    stay labeled; victim identities are never inferred."""
    _epstein_client()  # gate on ZEUS_EPSTEIN_ENABLED
    from zeus.orchestration.epstein_research import run_entity_dossier, write_research_report

    result = await run_entity_dossier(name, doc_type=doc_type, depth=depth)
    report_path = None
    if write_report and not result.error:
        report_path = str(
            write_research_report("entity_dossier", result.entity, result.to_markdown())
        )
    return {
        "entity": result.entity,
        "dossier_markdown": result.to_markdown(),
        "connections": result.connections,
        "timeline": result.timeline,
        "citations": result.citations(),
        "confidence": result.confidence,
        "gaps": result.gaps,
        "graph_available": result.graph_available,
        "report_path": report_path,
        "error": result.error,
        "_safety": _EPSTEIN_SAFETY,
    }


async def epstein_connection_map(
    *,
    names: list[str],
    depth: int = 2,
    write_report: bool = False,
) -> dict[str, Any]:
    """Map how 2+ entities connect: pairwise graph paths (co-occurrence), named
    intermediaries, and scoped cited evidence per pair, plus a {nodes, edges}
    graph export. Edges are co-occurrence or explicitly-cited relations, NEVER
    accusations; there is no contradiction edge in this corpus."""
    _epstein_client()  # gate on ZEUS_EPSTEIN_ENABLED
    from zeus.orchestration.epstein_research import run_connection_map, write_research_report

    result = await run_connection_map(names, depth=depth)
    report_path = None
    if write_report and not result.error:
        report_path = str(
            write_research_report(
                "connection_map", "-".join(result.entities),
                result.to_markdown(), sidecar=result.to_graph(),
            )
        )
    return {
        "entities": result.entities,
        "map_markdown": result.to_markdown(),
        "graph": result.to_graph(),
        "citations": result.citations(),
        "confidence": result.confidence,
        "gaps": result.gaps,
        "graph_available": result.graph_available,
        "report_path": report_path,
        "error": result.error,
        "_safety": _EPSTEIN_SAFETY,
    }
