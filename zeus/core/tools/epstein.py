# zeus/core/tools/epstein.py — Chat-path mirrors of the epstein_* MCP tools.
#
# Six read-only tools over the external epstein research API (the ~1.3M-doc
# DOJ/court corpus lives entirely in that separate service; Zeus proxies it
# live and stores nothing). Registered into the process-local chat tool
# registry so the SAME tools fire from the chat path (QueryEngine.query when
# ZEUS_TOOLS_ENABLED=1), from Kairos (via the allowlist), and — mirrored in
# zeus/mcp/tools.py — from MCP clients.
#
# SAFETY (echoed into every tool description below and non-negotiable):
#   - Mention is not involvement: name co-occurrence is a signal, never an
#     accusation.
#   - Allegations stay labeled as allegations; never state an unverified claim
#     as fact.
#   - Never surface, infer, or reconstruct victim identities or redacted text.
#   - Ground every claim in returned excerpts and cite them (document_id +
#     source_label); say so when the evidence is missing.
# The live manifest's `safety_rules` string is the source of truth — fetch it
# with epstein_capabilities and honor it.
#
# Read-only by construction: there is NO write path to the epstein service.
from __future__ import annotations

import logging
from typing import Any

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.epstein")

# Prepended to every rendered result so the framing rides along with the
# evidence into the model's context, not just the tool description.
_SAFETY_BANNER = (
    "[corpus: sensitive legal records; victims + unproven allegations. "
    "Mention != involvement; keep allegations labeled; never infer victim "
    "identities or redacted content; cite document_id + source_label for "
    "every claim.]"
)


def _err(name: str, msg: str) -> ToolResult:
    return ToolResult(call_id="", name=name, content=msg, is_error=True)


def _client_or_error(name: str):
    from zeus.memory.epstein import get_epstein_client

    client = get_epstein_client()
    if client is None:
        return None, _err(
            name,
            "The Epstein research capability is disabled. Set "
            "ZEUS_EPSTEIN_ENABLED=1 (and optionally ZEUS_EPSTEIN_BASE_URL) "
            "and restart zeus-core.",
        )
    return client, None


# --------------------------------------------------------------------------
# epstein_capabilities
# --------------------------------------------------------------------------
_CAP_SPEC = ToolSpec(
    name="epstein_capabilities",
    description=(
        "Fetch the live capability manifest of the Epstein document-research "
        "service: available doc_types (with counts), filter fields, endpoints, "
        "whether the entity graph is up, auth mode, and the corpus SAFETY "
        "RULES. Call this FIRST before other epstein_* tools and obey the "
        "returned safety_rules. Do not hardcode doc types or filters — they "
        "evolve; read them here at runtime."
    ),
    parameters={"type": "object", "properties": {}},
    timeout_seconds=20.0,
    cacheable=True,
)


async def _cap_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_CAP_SPEC.name)
    if err:
        return err
    from zeus.memory.epstein import EpsteinError

    try:
        cap = await client.capabilities()
    except EpsteinError as exc:
        return _err(_CAP_SPEC.name, f"epstein_capabilities failed: {exc}")

    doc_types = cap.get("doc_types", {}) or {}
    dt_lines = "\n".join(
        f"  - {k or '(untyped)'}: {v}"
        for k, v in sorted(doc_types.items(), key=lambda kv: -int(kv[1] or 0))
    )
    parts = [
        _SAFETY_BANNER,
        f"resolved_base: {client.resolved_base}",
        f"graph_available: {cap.get('graph_available')}",
        f"auth: {cap.get('auth')}",
        f"filter_fields: {', '.join(cap.get('filter_fields', []) or [])}",
        f"doc_types ({len(doc_types)}):\n{dt_lines}",
        "safety_rules:\n" + str(cap.get("safety_rules", "")),
    ]
    return ToolResult(call_id="", name=_CAP_SPEC.name, content="\n".join(parts))


# --------------------------------------------------------------------------
# epstein_search
# --------------------------------------------------------------------------
_SEARCH_SPEC = ToolSpec(
    name="epstein_search",
    description=(
        "Fast semantic search over the Epstein DOJ/court corpus (~1.3M "
        "documents). Returns excerpts each with a document_id + source_label "
        "you MUST cite. Optional filters: doc_type (see epstein_capabilities), "
        "date_mentioned, document_ids (scope to specific docs), n_results, and "
        "expand_graph (also returns co-occurring entities). This is the "
        "workhorse — lead with it. SAFETY: excerpts may name people who are "
        "not implicated; mention is not involvement, keep allegations labeled, "
        "and never infer victim identities or redacted content."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for"},
            "doc_type": {
                "type": "string",
                "description": "Restrict to one doc_type from epstein_capabilities",
            },
            "date_mentioned": {
                "type": "string",
                "description": "Filter to a date mentioned in the text (YYYY or YYYY-MM-DD)",
            },
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Scope the search to these document ids",
            },
            "n_results": {"type": "integer", "minimum": 1, "maximum": 50},
            "expand_graph": {
                "type": "boolean",
                "description": "Also return co-occurring graph entities",
            },
        },
        "required": ["query"],
    },
    timeout_seconds=20.0,
    cacheable=True,
)


def _format_hits(results: list[dict[str, Any]]) -> str:
    from zeus.memory.epstein import EpsteinHit

    if not results:
        return "No excerpts matched."
    lines: list[str] = []
    for i, r in enumerate(results, 1):
        h = EpsteinHit.from_api(r)
        lines.append(
            f"[{i}] cite: {h.citation()} | doc_type={h.doc_type} "
            f"chunk={h.chunk_index} score={h.score:.3f}"
        )
        lines.append(f"    {h.text[:600]}")
    return "\n".join(lines)


async def _search_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_SEARCH_SPEC.name)
    if err:
        return err
    from zeus.memory.epstein import EpsteinError

    query = str(args.get("query", "")).strip()
    if not query:
        return _err(_SEARCH_SPEC.name, "epstein_search requires a non-empty 'query'.")
    try:
        data = await client.search(
            query,
            doc_type=args.get("doc_type"),
            date_mentioned=args.get("date_mentioned"),
            document_ids=args.get("document_ids"),
            n_results=int(args.get("n_results") or 10),
            expand_graph=bool(args.get("expand_graph") or False),
        )
    except EpsteinError as exc:
        return _err(_SEARCH_SPEC.name, f"epstein_search failed: {exc}")

    results = data.get("results", []) or []
    body = [_SAFETY_BANNER, _format_hits(results)]
    entities = data.get("entities") or {}
    if entities:
        names = ", ".join(str(k) for k in list(entities)[:12])
        body.append(
            f"co-occurring entities (signal only, NOT accusations): {names}"
        )
    return ToolResult(call_id="", name=_SEARCH_SPEC.name, content="\n".join(body))


# --------------------------------------------------------------------------
# epstein_document
# --------------------------------------------------------------------------
_DOC_SPEC = ToolSpec(
    name="epstein_document",
    description=(
        "Fetch the reconstructed full text + metadata of one corpus document "
        "by its document_id (from an epstein_search result). Use to read the "
        "full context around an excerpt before drawing a conclusion. SAFETY: "
        "do not surface or infer victim identities or redacted content; cite "
        "the document_id + source_label for anything you quote."
    ),
    parameters={
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "Corpus document id"}
        },
        "required": ["document_id"],
    },
    timeout_seconds=20.0,
    cacheable=True,
)


async def _doc_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_DOC_SPEC.name)
    if err:
        return err
    from zeus.memory.epstein import EpsteinError

    doc_id = str(args.get("document_id", "")).strip()
    if not doc_id:
        return _err(_DOC_SPEC.name, "epstein_document requires 'document_id'.")
    try:
        d = await client.document(doc_id)
    except EpsteinError as exc:
        return _err(_DOC_SPEC.name, f"epstein_document failed: {exc}")

    text = str(d.get("text", ""))
    # Cap the returned text so a huge doc can't blow the tool-result budget;
    # the model can re-fetch or narrow with epstein_search + document_ids.
    capped = text[:4000]
    trailer = "" if len(text) <= 4000 else f"\n... [truncated {len(text) - 4000} chars]"
    parts = [
        _SAFETY_BANNER,
        f"document_id: {d.get('document_id')} | source_label: {d.get('source_label')} "
        f"| doc_type: {d.get('doc_type')} | chunks: {d.get('num_chunks')}",
        "text:",
        capped + trailer,
    ]
    return ToolResult(call_id="", name=_DOC_SPEC.name, content="\n".join(parts))


# --------------------------------------------------------------------------
# epstein_entity
# --------------------------------------------------------------------------
_ENTITY_SPEC = ToolSpec(
    name="epstein_entity",
    description=(
        "Look up an entity (person/org) in the corpus knowledge graph: its "
        "connections and, optionally, the path to another entity (related_to). "
        "The graph shows CO-OCCURRENCE in documents — a strong signal for "
        "where to read next, NEVER evidence of wrongdoing or a relationship. "
        "The graph may be down (returns an error); degrade gracefully and fall "
        "back to epstein_search. SAFETY: co-occurrence is not involvement; "
        "never present a graph edge as an accusation, and never expose victim "
        "identities."
    ),
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Entity name to look up"},
            "depth": {"type": "integer", "minimum": 1, "maximum": 3},
            "related_to": {
                "type": "string",
                "description": "Second entity; return the connection between the two",
            },
        },
        "required": ["name"],
    },
    timeout_seconds=20.0,
    cacheable=True,
)


def _summarize_subgraph(sg: dict[str, Any]) -> str:
    nodes = sg.get("nodes", []) or []
    edges = sg.get("edges", []) or []
    # Named nodes are the meaningful connections (people/orgs). Event nodes
    # carry only a hash `event_id` and are graph plumbing, not entities —
    # count them but don't list opaque ids as if they were connections.
    named = [str(n["name"]) for n in nodes if n.get("name")]
    events = sum(1 for n in nodes if not n.get("name"))
    shown = ", ".join(named[:25])
    more = "" if len(named) <= 25 else f" (+{len(named) - 25} more)"
    tail = f" ({events} event nodes)" if events else ""
    if not named:
        return f"{len(nodes)} nodes, {len(edges)} edges{tail}. No named entities."
    return (
        f"{len(nodes)} nodes, {len(edges)} edges{tail}. "
        f"Co-occurring entities: {shown}{more}"
    )


async def _entity_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_ENTITY_SPEC.name)
    if err:
        return err
    from zeus.memory.epstein import EpsteinError

    name = str(args.get("name", "")).strip()
    if not name:
        return _err(_ENTITY_SPEC.name, "epstein_entity requires 'name'.")
    try:
        d = await client.entity(
            name,
            depth=int(args.get("depth") or 1),
            related_to=args.get("related_to"),
        )
    except EpsteinError as exc:
        if exc.status == 503:
            return _err(
                _ENTITY_SPEC.name,
                "The entity graph is currently unavailable (503). Fall back to "
                "epstein_search for evidence.",
            )
        return _err(_ENTITY_SPEC.name, f"epstein_entity failed: {exc}")

    parts = [
        _SAFETY_BANNER,
        f"entity: {d.get('entity', name)}",
        "graph (co-occurrence only, NOT accusations): "
        + _summarize_subgraph(d.get("subgraph", {}) or {}),
    ]
    conn = d.get("connection")
    if conn:
        parts.append(f"connection: {str(conn)[:800]}")
    return ToolResult(call_id="", name=_ENTITY_SPEC.name, content="\n".join(parts))


# --------------------------------------------------------------------------
# epstein_research_start
# --------------------------------------------------------------------------
_START_SPEC = ToolSpec(
    name="epstein_research_start",
    description=(
        "Start an ASYNC deep-research job over the corpus: it decomposes the "
        "question, retrieves evidence, and synthesizes a citation-backed "
        "report. Returns a job_id immediately — DO NOT wait on it. Poll with "
        "epstein_research_result. Prefer this over the slow synchronous path. "
        "Note: the synthesis (prose) step is currently slow and may time out; "
        "when it does, the job STILL returns real retrieval + citations, so "
        "the result is useful either way. SAFETY: the eventual report must "
        "keep allegations labeled and cite every claim."
    ),
    parameters={
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Research question"},
            "doc_type": {"type": "string", "description": "Optional doc_type filter"},
            "date_mentioned": {"type": "string", "description": "Optional date filter"},
            "depth": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Sub-query decomposition depth (default 3)",
            },
        },
        "required": ["question"],
    },
    timeout_seconds=25.0,
    cacheable=False,
)


async def _start_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_START_SPEC.name)
    if err:
        return err
    from zeus.memory.epstein import EpsteinError

    question = str(args.get("question", "")).strip()
    if not question:
        return _err(_START_SPEC.name, "epstein_research_start requires 'question'.")
    try:
        d = await client.start_job(
            question,
            doc_type=args.get("doc_type"),
            date_mentioned=args.get("date_mentioned"),
            depth=int(args.get("depth") or 3),
        )
    except EpsteinError as exc:
        return _err(_START_SPEC.name, f"epstein_research_start failed: {exc}")

    return ToolResult(
        call_id="",
        name=_START_SPEC.name,
        content=(
            f"{_SAFETY_BANNER}\n"
            f"Deep-research job started.\n"
            f"job_id: {d.get('job_id')}\n"
            f"status: {d.get('status')}\n"
            f"Poll epstein_research_result with this job_id. The job runs in "
            f"the background — do not block this reply on it. Synthesis may be "
            f"slow; citations arrive even if the prose times out."
        ),
    )


# --------------------------------------------------------------------------
# epstein_research_result
# --------------------------------------------------------------------------
_RESULT_SPEC = ToolSpec(
    name="epstein_research_result",
    description=(
        "Poll a deep-research job started with epstein_research_start. Returns "
        "status (queued|running|done|error), the step log, the synthesized "
        "report (may be empty or note 'Synthesis failed: timed out' — a known "
        "infra caveat), and the citations gathered (document_id + "
        "source_label). ALWAYS surface the citations to the user even when the "
        "prose is missing. SAFETY: render allegations as allegations and cite "
        "every claim; do not fill gaps with speculation."
    ),
    parameters={
        "type": "object",
        "properties": {
            "job_id": {"type": "string", "description": "Job id from epstein_research_start"}
        },
        "required": ["job_id"],
    },
    timeout_seconds=20.0,
    cacheable=False,
)


def _format_citations(citations: list[dict[str, Any]]) -> str:
    if not citations:
        return "citations: (none returned)"
    lines = ["citations:"]
    for i, c in enumerate(citations, 1):
        label = c.get("source_label") or c.get("doc_type") or "corpus"
        lines.append(
            f"  [{i}] {c.get('document_id')} ({label}) chunk={c.get('chunk_index', '')}"
        )
    return "\n".join(lines)


async def _result_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_RESULT_SPEC.name)
    if err:
        return err
    from zeus.memory.epstein import EpsteinError

    job_id = str(args.get("job_id", "")).strip()
    if not job_id:
        return _err(_RESULT_SPEC.name, "epstein_research_result requires 'job_id'.")
    try:
        d = await client.get_job(job_id)
    except EpsteinError as exc:
        return _err(_RESULT_SPEC.name, f"epstein_research_result failed: {exc}")

    status = str(d.get("status", "unknown"))
    steps = d.get("steps") or []
    report = str(d.get("report") or "").strip()
    citations = d.get("citations") or []

    parts = [
        _SAFETY_BANNER,
        f"job_id: {job_id} | status: {status}",
        f"steps: {' -> '.join(str(s) for s in steps)}" if steps else "steps: (none)",
    ]
    if d.get("error"):
        parts.append(f"error: {d['error']}")
    parts.append(_format_citations(citations))
    if report:
        parts.append("report:\n" + report[:4000])
    elif status in ("queued", "running"):
        parts.append("report: not ready yet — poll again shortly.")
    else:
        parts.append(
            "report: (no prose — synthesis unavailable; use the citations "
            "above, which are the real retrieved evidence)."
        )
    return ToolResult(call_id="", name=_RESULT_SPEC.name, content="\n".join(parts))


# --------------------------------------------------------------------------
# epstein_research — one-shot orchestrated workflow (plan -> retrieve ->
# entity -> job) returning a citation-backed answer with confidence + gaps.
# --------------------------------------------------------------------------
_RESEARCH_SPEC = ToolSpec(
    name="epstein_research",
    description=(
        "Investigate a question against the Epstein corpus END TO END and "
        "return a citation-backed answer in one call: it plans sub-queries, "
        "fans out fast searches, pulls entity signals, and starts a deep "
        "async synthesis job. Leads with real cited evidence immediately; the "
        "synthesized prose follows via the returned job_id (poll it with "
        "epstein_research_result). Use this for 'research question X' asks. The "
        "answer states an explicit CONFIDENCE level and the GAPS in the "
        "evidence. SAFETY: mention is not involvement; allegations stay "
        "labeled; victim identities and redacted content are never inferred; "
        "every claim is cited or flagged as unsupported."
    ),
    parameters={
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The research question"},
            "doc_type": {"type": "string", "description": "Optional doc_type filter"},
            "date_mentioned": {"type": "string", "description": "Optional date filter"},
            "depth": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Deep-research decomposition depth (default 3)",
            },
            "wait_seconds": {
                "type": "integer",
                "minimum": 0,
                "maximum": 120,
                "description": (
                    "Seconds to wait for the deep synthesis before returning "
                    "(default 0 = return fast evidence + job handle now). Keep "
                    "small in chat; the report can be polled separately."
                ),
            },
        },
        "required": ["question"],
    },
    timeout_seconds=150.0,
    cacheable=False,
)


async def _research_handler(args: dict[str, Any]) -> ToolResult:
    client, err = _client_or_error(_RESEARCH_SPEC.name)
    if err:
        return err

    question = str(args.get("question", "")).strip()
    if not question:
        return _err(_RESEARCH_SPEC.name, "epstein_research requires a 'question'.")

    from zeus.orchestration.epstein_research import run_research

    try:
        result = await run_research(
            question,
            doc_type=args.get("doc_type"),
            date_mentioned=args.get("date_mentioned"),
            depth=int(args.get("depth") or 3),
            poll_budget_seconds=float(args.get("wait_seconds") or 0),
            client=client,
        )
    except Exception as exc:  # noqa: BLE001 - never let the workflow crash the turn
        logger.warning("epstein_research failed: %s", exc)
        return _err(_RESEARCH_SPEC.name, f"epstein_research failed: {exc}")

    content = _SAFETY_BANNER + "\n" + result.to_markdown()
    return ToolResult(
        call_id="", name=_RESEARCH_SPEC.name, content=content, is_error=bool(result.error)
    )


# --------------------------------------------------------------------------
# registration
# --------------------------------------------------------------------------
_TOOLS = [
    (_CAP_SPEC, _cap_handler),
    (_SEARCH_SPEC, _search_handler),
    (_DOC_SPEC, _doc_handler),
    (_ENTITY_SPEC, _entity_handler),
    (_START_SPEC, _start_handler),
    (_RESULT_SPEC, _result_handler),
    (_RESEARCH_SPEC, _research_handler),
]


def register() -> None:
    """Register the six read-only Epstein tools (only when the capability is on).

    Gated by ZEUS_EPSTEIN_ENABLED so the tools don't appear in the chat/Kairos
    tool surface when the capability is disabled.
    """
    import os

    if os.getenv("ZEUS_EPSTEIN_ENABLED", "0").strip().lower() not in (
        "1",
        "true",
        "yes",
        "on",
    ):
        logger.info("epstein tools not registered (ZEUS_EPSTEIN_ENABLED off)")
        return
    for spec, handler in _TOOLS:
        registry.register(spec, handler)
    logger.info("epstein tools registered: %s", ", ".join(s.name for s, _ in _TOOLS))
