# zeus/core/epstein_router.py — HTTP surface for the Zeus OS Epstein app.
#
# Thin JSON wrapper over the read-only corpus tooling so the /os launcher app
# can drive it from the browser. Every endpoint is read-only against the corpus
# (there is no write path here; findings write-back stays in the Kronos job).
#
# PRIVATE BRANCH ONLY. This router — and its include in zeus/core/main.py — live
# only on the `epstein` branch and must never merge to main. It is gated at
# runtime by ZEUS_EPSTEIN_ENABLED (get_epstein_client returns None when off), so
# even if it ever shipped it is inert without the private corpus creds.
#
# Endpoints (all under /epstein):
#   GET  /epstein/status       — capability probe (enabled? reachable? manifest)
#   POST /epstein/search       — fast dense retrieval, cited hits
#   POST /epstein/dossier      — one-entity cited dossier (+ markdown)
#   POST /epstein/connections  — how 2+ entities connect (+ {nodes,edges} graph)
#
# Co-occurrence is a signal about where to read, NEVER an accusation. The
# safety framing from the corpus manifest is passed straight through.
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from zeus.memory.epstein import EpsteinError, EpsteinHit, get_epstein_client
from zeus.orchestration.epstein_research import (
    run_connection_map,
    run_entity_dossier,
)

logger = logging.getLogger("zeus.epstein")

router = APIRouter(prefix="/epstein", tags=["epstein"])

_DISABLED = {
    "enabled": False,
    "reachable": False,
    "error": "Epstein research capability disabled (ZEUS_EPSTEIN_ENABLED=0).",
}


def _hit_dict(h: EpsteinHit) -> dict[str, Any]:
    return {
        "text": h.text,
        "document_id": h.document_id,
        "source_label": h.source_label,
        "doc_type": h.doc_type,
        "chunk_index": h.chunk_index,
        "score": h.score,
        "citation": h.citation(),
    }


# -- request models --------------------------------------------------------


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    doc_type: str | None = None
    n_results: int = Field(default=10, ge=1, le=50)
    expand_graph: bool = False


class DossierRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    depth: int = Field(default=1, ge=1, le=3)
    doc_type: str | None = None


class ConnectionsRequest(BaseModel):
    names: list[str] = Field(min_length=2, max_length=6)
    depth: int = Field(default=2, ge=1, le=3)


# -- endpoints -------------------------------------------------------------


@router.get("/status")
async def status() -> dict[str, Any]:
    """Probe the corpus API. Never raises: the app uses this to decide whether
    to show the workbench or a clear 'corpus offline' state."""
    client = get_epstein_client()
    if client is None:
        return dict(_DISABLED)
    try:
        cap = await client.capabilities()
    except EpsteinError as exc:
        return {"enabled": True, "reachable": False, "error": str(exc)}
    return {
        "enabled": True,
        "reachable": True,
        "capabilities": cap,
        "safety_rules": cap.get("safety_rules"),
        "graph_available": bool(cap.get("graph_available")),
        "doc_types": cap.get("doc_types") or {},
    }


@router.post("/search")
async def search(req: SearchRequest) -> dict[str, Any]:
    client = get_epstein_client()
    if client is None:
        return dict(_DISABLED)
    try:
        r = await client.search(
            req.query,
            doc_type=req.doc_type,
            n_results=req.n_results,
            expand_graph=req.expand_graph,
        )
    except EpsteinError as exc:
        return {"enabled": True, "reachable": False, "error": str(exc)}
    hits = [EpsteinHit.from_api(x) for x in r.get("results", []) or []]
    return {
        "enabled": True,
        "reachable": True,
        "query": req.query,
        "results": [_hit_dict(h) for h in hits],
        "entities": r.get("entities") or {},
    }


@router.post("/dossier")
async def dossier(req: DossierRequest) -> dict[str, Any]:
    client = get_epstein_client()
    if client is None:
        return dict(_DISABLED)
    d = await run_entity_dossier(req.name, depth=req.depth, doc_type=req.doc_type)
    if d.error:
        return {"enabled": True, "reachable": False, "error": d.error,
                "entity": d.entity, "markdown": d.to_markdown()}
    return {
        "enabled": True,
        "reachable": True,
        "entity": d.entity,
        "graph_available": d.graph_available,
        "confidence": d.confidence,
        "connections": d.connections,
        "timeline": d.timeline,
        "doc_types": d.doc_types,
        "evidence": [_hit_dict(h) for h in d.evidence],
        "citations": d.citations(),
        "gaps": d.gaps,
        "safety_rules": d.safety_rules,
        "markdown": d.to_markdown(),
    }


@router.post("/connections")
async def connections(req: ConnectionsRequest) -> dict[str, Any]:
    client = get_epstein_client()
    if client is None:
        return dict(_DISABLED)
    m = await run_connection_map(req.names, depth=req.depth)
    if m.error:
        return {"enabled": True, "reachable": False, "error": m.error,
                "entities": m.entities, "markdown": m.to_markdown()}
    pairs = [
        {
            "a": p["a"],
            "b": p["b"],
            "connected": bool(p.get("connected")),
            "intermediaries": p.get("intermediaries", []),
            "events": p.get("events", []),
            "evidence": [_hit_dict(h) for h in (p.get("evidence", []) or [])],
        }
        for p in m.pairs
    ]
    return {
        "enabled": True,
        "reachable": True,
        "entities": m.entities,
        "graph_available": m.graph_available,
        "confidence": m.confidence,
        "pairs": pairs,
        "graph": m.to_graph(),
        "citations": m.citations(),
        "gaps": m.gaps,
        "safety_rules": m.safety_rules,
        "markdown": m.to_markdown(),
    }
