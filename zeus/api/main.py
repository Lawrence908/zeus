# zeus/api/main.py — Oracle router for Zeus Core
import asyncio
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from zeus.memory.search import MEMORY_SEARCH_TOP_K, format_context_block, get_profile_facts, search_memories

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "zeus_memories")
ZEUS_KNOWLEDGE_COLLECTION = os.getenv("ZEUS_KNOWLEDGE_COLLECTION", "zeus_knowledge")
ZEUS_USER_ID = os.getenv("ZEUS_USER_ID", "chris")

ORACLE_VERSION = "0.1.0"
ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")

# Max tokens oracle will return in a single context block.
# Keeps prompt injection predictable — callers can request less.
DEFAULT_MAX_TOKENS = int(os.getenv("ORACLE_MAX_TOKENS", "2048"))

_DEFAULT_ORACLE_TOP_K = int(os.getenv("ZEUS_ORACLE_TOP_K", str(MEMORY_SEARCH_TOP_K)))
_ORACLE_TOP_K = max(1, min(20, _DEFAULT_ORACLE_TOP_K))

INGEST_CHUNK_SIZE = max(64, int(os.getenv("ZEUS_INGEST_CHUNK_SIZE", "512")))
INGEST_CHUNK_OVERLAP = max(0, int(os.getenv("ZEUS_INGEST_CHUNK_OVERLAP", "72")))

_TRIGGER_SOURCE_CHOICES = frozenset(
    {
        "all",
        "context_pack",
        "markdown",
        "chatgpt",
        "email",
        "obsidian",
        "git",
        "gcal",
        "bookmarks",
    }
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ContextQuery(BaseModel):
    query: str = Field(..., description="Natural language query for context retrieval")
    max_tokens: int = Field(DEFAULT_MAX_TOKENS, ge=64, le=8192)
    namespaces: list[str] = Field(
        default_factory=list,
        description="Optional filter to specific memory namespaces",
    )
    top_k: int = Field(default=_ORACLE_TOP_K, ge=1, le=20, description="Number of memories to retrieve")


class ContextSource(BaseModel):
    memory_id: str
    source: str
    relevance: float


class ContextResponse(BaseModel):
    context: str          # formatted context block ready for LLM injection
    sources: list[ContextSource]
    token_estimate: int


class ProfileResponse(BaseModel):
    user_id: str
    summary: str
    facts: list[str]


class MemorySearchBody(BaseModel):
    query: str = Field(..., description="Natural language memory search")
    limit: int | None = Field(None, ge=1, le=20, description="Alias for top_k")
    top_k: int | None = Field(None, ge=1, le=20)
    namespaces: list[str] = Field(default_factory=list)


class MemoryHit(BaseModel):
    id: str
    score: float
    text: str
    source: str
    metadata: dict


class MemorySearchResponse(BaseModel):
    results: list[MemoryHit]


class MemoryEntry(BaseModel):
    id: str
    text: str
    source: str
    metadata: dict
    created_at: str | None = None
    updated_at: str | None = None


class MemoryListResponse(BaseModel):
    entries: list[MemoryEntry]
    next_offset: str | None = None
    total_estimate: int | None = None


class MemorySourcesResponse(BaseModel):
    sources: list[str]


class MemoryUpdateBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


class IngestTriggerBody(BaseModel):
    source: str = Field(
        "all",
        description="One of: all, markdown, chatgpt, obsidian, context_pack, email, git, gcal, bookmarks",
    )
    user_id: str = Field("chris", description="mem0 user id")


class IngestTriggerResponse(BaseModel):
    status: str
    chunks_indexed: int
    sources_run: list[str]


router = APIRouter(tags=["oracle"])


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/context/query", response_model=ContextResponse)
async def query_context(body: ContextQuery, request: Request):
    """
    Retrieve relevant memories and return them as a formatted context block.

    The context string is ready to inject into an LLM system prompt:
        system_prompt += f"\\n\\n## Personal Context\\n{context_response.context}"
    """
    try:
        results = await asyncio.to_thread(
            search_memories,
            body.query,
            "chris",
            body.top_k,
            body.namespaces,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {e}")

    if not results:
        return ContextResponse(context="", sources=[], token_estimate=0)

    context, token_estimate = format_context_block(results, max_tokens=body.max_tokens)
    sources: list[ContextSource] = []
    for mem in results:
        md = mem.get("metadata", {}) or {}
        sources.append(ContextSource(
            memory_id=mem.get("id", ""),
            source=md.get("source_id") or md.get("source") or "unknown",
            relevance=float(mem.get("score") or 0.0),
        ))

    return ContextResponse(
        context=context,
        sources=sources,
        token_estimate=token_estimate,
    )


def _raw_memory_hits(rows: list[dict]) -> list[MemoryHit]:
    out: list[MemoryHit] = []
    for m in rows:
        md = m.get("metadata", {}) or {}
        text = str(m.get("memory", "") or "").strip()
        src = str(md.get("source_id") or md.get("source") or "unknown")
        out.append(
            MemoryHit(
                id=str(m.get("id", "") or ""),
                score=float(m.get("score") or 0.0),
                text=text,
                source=src,
                metadata=dict(md),
            )
        )
    return out


@router.post("/memory/search", response_model=MemorySearchResponse)
async def memory_search_raw(body: MemorySearchBody, request: Request):
    """Raw memory hits for MCP / debugging (no formatted context block)."""
    k = body.top_k if body.top_k is not None else body.limit
    if k is None:
        k = MEMORY_SEARCH_TOP_K

    try:
        rows = await asyncio.to_thread(
            search_memories,
            body.query,
            "chris",
            k,
            body.namespaces,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {e}")

    return MemorySearchResponse(results=_raw_memory_hits(rows))


@router.post("/ingest/trigger", response_model=IngestTriggerResponse)
async def ingest_trigger(body: IngestTriggerBody, request: Request):
    """Run Iris ingest for one source (or all). Writes to MemoryStore / KnowledgeStore."""
    src = (body.source or "all").strip().lower()
    if src not in _TRIGGER_SOURCE_CHOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source {body.source!r}; expected one of {sorted(_TRIGGER_SOURCE_CHOICES)}",
        )

    from zeus.ingest.pipeline import run_ingest
    from zeus.ingest.run import build_sources_for_trigger

    try:
        sources = build_sources_for_trigger(
            src,
            user_id=body.user_id,
            chunk_size=INGEST_CHUNK_SIZE,
            chunk_overlap=INGEST_CHUNK_OVERLAP,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = await run_ingest(
        sources,
        chunk_size=INGEST_CHUNK_SIZE,
        dry_run=False,
        ingest_ui="plain",
    )
    total = sum(r.chunks_stored for r in results)
    labels = [r.source for r in results]
    return IngestTriggerResponse(status="ok", chunks_indexed=total, sources_run=labels)


def _point_to_entry(point: dict) -> MemoryEntry:
    payload = point.get("payload", {}) or {}
    # MemoryStore payload key is "text" (KnowledgeStore-aligned); fall back to
    # mem0's legacy "data" for any pre-migration points that still linger.
    text = str(payload.get("text") or payload.get("data") or "").strip()
    source = str(payload.get("source", "") or "unknown")
    metadata = {
        k: v for k, v in payload.items()
        if k not in {"text", "data", "hash", "user_id"}
    }
    return MemoryEntry(
        id=str(point.get("id", "")),
        text=text,
        source=source,
        metadata=metadata,
        created_at=payload.get("created_at"),
        updated_at=payload.get("updated_at"),
    )


async def _qdrant_post(client: httpx.AsyncClient, path: str, body: dict) -> dict:
    url = f"{QDRANT_URL.rstrip('/')}{path}"
    try:
        resp = await client.post(url, json=body, timeout=10.0)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Qdrant request failed: {exc}") from exc
    return resp.json()


@router.get("/memory/list", response_model=MemoryListResponse)
async def memory_list(
    request: Request,
    limit: int = 50,
    offset: str | None = None,
    source: str | None = None,
):
    """Browse stored memories via Qdrant scroll. Optional ``source`` payload filter."""
    limit = max(1, min(200, limit))
    client: httpx.AsyncClient = request.app.state.http_client

    must: list[dict] = [{"key": "user_id", "match": {"value": ZEUS_USER_ID}}]
    if source:
        must.append({"key": "source", "match": {"value": source}})

    body: dict = {
        "limit": limit,
        "with_payload": True,
        "with_vector": False,
        "filter": {"must": must},
    }
    if offset:
        body["offset"] = offset

    data = await _qdrant_post(
        client, f"/collections/{QDRANT_COLLECTION}/points/scroll", body
    )
    result = data.get("result", {}) or {}
    points = result.get("points", []) or []
    entries = [_point_to_entry(p) for p in points]

    total_estimate: int | None = None
    if not offset and not source:
        try:
            info_resp = await client.get(
                f"{QDRANT_URL.rstrip('/')}/collections/{QDRANT_COLLECTION}",
                timeout=5.0,
            )
            if info_resp.status_code == 200:
                total_estimate = int(
                    info_resp.json().get("result", {}).get("points_count") or 0
                )
        except httpx.HTTPError:
            pass

    return MemoryListResponse(
        entries=entries,
        next_offset=str(result.get("next_page_offset")) if result.get("next_page_offset") else None,
        total_estimate=total_estimate,
    )


@router.get("/memory/sources", response_model=MemorySourcesResponse)
async def memory_sources(request: Request):
    """Distinct ``source`` values for the current user. Used by the browser filter."""
    client: httpx.AsyncClient = request.app.state.http_client
    seen: set[str] = set()
    offset: str | None = None
    pages = 0
    while pages < 20:
        body: dict = {
            "limit": 200,
            "with_payload": {"include": ["source"]},
            "with_vector": False,
            "filter": {"must": [{"key": "user_id", "match": {"value": ZEUS_USER_ID}}]},
        }
        if offset:
            body["offset"] = offset
        data = await _qdrant_post(
            client, f"/collections/{QDRANT_COLLECTION}/points/scroll", body
        )
        result = data.get("result", {}) or {}
        for point in result.get("points", []) or []:
            src = (point.get("payload", {}) or {}).get("source")
            if src:
                seen.add(str(src))
        offset = result.get("next_page_offset")
        if not offset:
            break
        pages += 1
    return MemorySourcesResponse(sources=sorted(seen))


@router.get("/memory/{memory_id}", response_model=MemoryEntry)
async def memory_get(memory_id: str, request: Request) -> MemoryEntry:
    client: httpx.AsyncClient = request.app.state.http_client
    url = f"{QDRANT_URL.rstrip('/')}/collections/{QDRANT_COLLECTION}/points/{memory_id}"
    try:
        resp = await client.get(url, params={"with_payload": "true"}, timeout=5.0)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Qdrant request failed: {exc}") from exc
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Memory not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Qdrant error: {resp.text}")
    point = resp.json().get("result") or {}
    return _point_to_entry(point)


@router.patch("/memory/{memory_id}", response_model=MemoryEntry)
async def memory_update(memory_id: str, body: MemoryUpdateBody, request: Request) -> MemoryEntry:
    from zeus.memory.store import get_memory_store

    store = get_memory_store()
    try:
        await asyncio.to_thread(store.update, memory_id, body.text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"memory update failed: {exc}") from exc
    return await memory_get(memory_id, request)


@router.delete("/memory/{memory_id}")
async def memory_delete(memory_id: str, request: Request) -> dict:
    from zeus.memory.store import get_memory_store

    store = get_memory_store()
    try:
        await asyncio.to_thread(store.delete, memory_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"memory delete failed: {exc}") from exc
    return {"ok": True, "id": memory_id}


class MemoryAddBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    source: str = Field("manual", description="Source label: manual, chat, kairos, ...")
    source_id: str | None = Field(None, description="Stable dedupe key; defaults to uuid")
    extract_facts: bool = Field(
        False,
        description="If True, route through small_llm_call for LLM fact extraction",
    )


class MemoryAddResponse(BaseModel):
    status: str
    added: int
    skipped: int
    raw_fallbacks: int
    errors: list[str]


@router.post("/memory/add", response_model=MemoryAddResponse)
async def memory_add(body: MemoryAddBody) -> MemoryAddResponse:
    """Add a memory item. Used by the MCP `zeus_remember` tool and manual UI."""
    import uuid

    from zeus.memory.store import get_memory_store

    store = get_memory_store()
    source_id = body.source_id or f"{body.source}:{uuid.uuid4()}"
    try:
        result = await store.add_text(
            body.text,
            source=body.source,
            source_id=source_id,
            user_id=ZEUS_USER_ID,
            extract_facts=body.extract_facts,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"memory add failed: {exc}") from exc
    return MemoryAddResponse(
        status="ok" if result.added > 0 else "empty",
        added=result.added,
        skipped=result.skipped,
        raw_fallbacks=result.raw_fallbacks,
        errors=result.errors,
    )


@router.get("/context/profile", response_model=ProfileResponse)
async def get_profile(request: Request):
    """Return stable facts about the user — baseline system prompt context."""
    facts = await asyncio.to_thread(get_profile_facts, "chris", 8)
    if not facts:
        return ProfileResponse(
            user_id="chris",
            summary="Profile not yet populated. Run iris ingest first.",
            facts=[],
        )

    summary = " ".join(facts[:3])
    return ProfileResponse(
        user_id="chris",
        summary=summary,
        facts=facts,
    )


@router.get("/context/status")
async def status():
    return {"service": "oracle", "version": ORACLE_VERSION, "env": ZEUS_ENV}


# ---------------------------------------------------------------------------
# Knowledge browse / search — parallel to /memory/* but against zeus_knowledge.
# Read-only + delete-by-source (bulk chunks don't support per-point edits).
# ---------------------------------------------------------------------------

class KnowledgeEntry(BaseModel):
    id: str
    text: str
    source: str
    source_id: str | None = None
    source_path: str | None = None
    chunk_index: int | None = None
    metadata: dict
    created_at: str | None = None


class KnowledgeListResponse(BaseModel):
    entries: list[KnowledgeEntry]
    next_offset: str | None = None
    total_estimate: int | None = None


class KnowledgeSearchBody(BaseModel):
    query: str = Field(..., description="Hybrid (dense+BM25) knowledge search")
    top_k: int | None = Field(None, ge=1, le=20)
    sources: list[str] = Field(default_factory=list)


class KnowledgeHitModel(BaseModel):
    id: str
    score: float
    text: str
    source: str
    metadata: dict


class KnowledgeSearchResponse(BaseModel):
    results: list[KnowledgeHitModel]


class FacetBucket(BaseModel):
    value: str
    count: int


class KnowledgeFacetsResponse(BaseModel):
    total: int
    source: list[FacetBucket]
    type: list[FacetBucket]
    book: list[FacetBucket]


class KnowledgeDeleteResponse(BaseModel):
    ok: bool
    deleted: int
    source: str
    source_id: str


class KnowledgeFacetDeleteResponse(BaseModel):
    ok: bool
    key: str
    value: str
    deleted: int  # best-effort: pre-delete count when exact=false is unavailable


class IdBatch(BaseModel):
    ids: list[str] = Field(..., min_length=1, max_length=500)


class BulkDeleteResponse(BaseModel):
    ok: bool
    deleted: int


# Qdrant payload keys safe to expose for facet-style bulk delete.
# Keeping this narrow prevents a naive DELETE with key=user_id from nuking
# the whole collection.
_ALLOWED_FACET_DELETE_KEYS: frozenset[str] = frozenset({"source", "type", "book"})


def _iso_or_none(value) -> str | None:
    """Accept float (time.time()) or ISO-8601 string; return ISO-8601 or None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    return str(value)


def _knowledge_point_to_entry(point: dict) -> KnowledgeEntry:
    payload = point.get("payload", {}) or {}
    metadata = {
        k: v for k, v in payload.items()
        if k not in {"text", "user_id", "created_at", "source", "source_id", "source_path", "chunk_index"}
    }
    return KnowledgeEntry(
        id=str(point.get("id", "")),
        text=str(payload.get("text", "") or "").strip(),
        source=str(payload.get("source", "") or "unknown"),
        source_id=payload.get("source_id"),
        source_path=payload.get("source_path"),
        chunk_index=payload.get("chunk_index"),
        metadata=metadata,
        created_at=_iso_or_none(payload.get("created_at")),
    )


async def _qdrant_facet(
    client: httpx.AsyncClient, key: str, extra_must: list[dict] | None = None
) -> list[FacetBucket]:
    body: dict = {"key": key, "limit": 50}
    must: list[dict] = [{"key": "user_id", "match": {"value": ZEUS_USER_ID}}]
    if extra_must:
        must.extend(extra_must)
    body["filter"] = {"must": must}
    try:
        resp = await client.post(
            f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}/facet",
            json=body,
            timeout=10.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError:
        return []
    hits = (resp.json().get("result", {}) or {}).get("hits", []) or []
    return [FacetBucket(value=str(h["value"]), count=int(h["count"])) for h in hits if h.get("value") is not None]


@router.get("/knowledge/list", response_model=KnowledgeListResponse)
async def knowledge_list(
    request: Request,
    limit: int = 50,
    offset: str | None = None,
    source: str | None = None,
    type: str | None = None,
    book: str | None = None,
):
    """Browse knowledge chunks via Qdrant scroll. Filters: source, type, book."""
    limit = max(1, min(200, limit))
    client: httpx.AsyncClient = request.app.state.http_client

    must: list[dict] = [{"key": "user_id", "match": {"value": ZEUS_USER_ID}}]
    if source:
        must.append({"key": "source", "match": {"value": source}})
    if type:
        must.append({"key": "type", "match": {"value": type}})
    if book:
        must.append({"key": "book", "match": {"value": book}})

    body: dict = {
        "limit": limit,
        "with_payload": True,
        "with_vector": False,
        "filter": {"must": must},
    }
    if offset:
        body["offset"] = offset

    data = await _qdrant_post(
        client, f"/collections/{ZEUS_KNOWLEDGE_COLLECTION}/points/scroll", body
    )
    result = data.get("result", {}) or {}
    points = result.get("points", []) or []
    entries = [_knowledge_point_to_entry(p) for p in points]

    total_estimate: int | None = None
    if not offset and not source and not type and not book:
        try:
            info_resp = await client.get(
                f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}",
                timeout=5.0,
            )
            if info_resp.status_code == 200:
                total_estimate = int(
                    info_resp.json().get("result", {}).get("points_count") or 0
                )
        except httpx.HTTPError:
            pass

    return KnowledgeListResponse(
        entries=entries,
        next_offset=str(result.get("next_page_offset")) if result.get("next_page_offset") else None,
        total_estimate=total_estimate,
    )


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def knowledge_search(body: KnowledgeSearchBody):
    """Hybrid dense+BM25 search over zeus_knowledge (with optional source filter)."""
    from zeus.memory.search import search_knowledge

    k = body.top_k or 20
    try:
        rows = await asyncio.to_thread(
            search_knowledge,
            body.query,
            ZEUS_USER_ID,
            k,
            body.sources or None,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {exc}") from exc

    results: list[KnowledgeHitModel] = []
    for r in rows:
        md = r.get("metadata", {}) or {}
        text = str(r.get("memory", "") or "").strip()
        src = str(md.get("source") or "unknown")
        results.append(
            KnowledgeHitModel(
                id=str(r.get("id") or ""),
                score=float(r.get("score") or 0.0),
                text=text,
                source=src,
                metadata=dict(md),
            )
        )
    return KnowledgeSearchResponse(results=results)


@router.get("/knowledge/facets", response_model=KnowledgeFacetsResponse)
async def knowledge_facets(
    request: Request,
    source: str | None = None,
    type: str | None = None,
):
    """Facet counts for source / type / book — drives the sidebar sidebar in KnowledgePage.

    Passing ``source`` or ``type`` narrows the book facet to that subset, so the
    sidebar updates as filters apply.
    """
    client: httpx.AsyncClient = request.app.state.http_client
    narrow: list[dict] = []
    if source:
        narrow.append({"key": "source", "match": {"value": source}})
    if type:
        narrow.append({"key": "type", "match": {"value": type}})

    # total points for the current filter scope
    total = 0
    try:
        resp = await client.post(
            f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}/points/count",
            json={
                "filter": {"must": [{"key": "user_id", "match": {"value": ZEUS_USER_ID}}] + narrow},
                "exact": False,
            },
            timeout=5.0,
        )
        if resp.status_code == 200:
            total = int((resp.json().get("result", {}) or {}).get("count", 0))
    except httpx.HTTPError:
        pass

    # unfiltered axes come from narrow scope; book/type narrow to both, source unfiltered.
    source_facet, type_facet, book_facet = await asyncio.gather(
        _qdrant_facet(client, "source"),
        _qdrant_facet(client, "type", narrow if source else None),
        _qdrant_facet(client, "book", narrow or None),
    )
    return KnowledgeFacetsResponse(
        total=total,
        source=source_facet,
        type=type_facet,
        book=book_facet,
    )


@router.get("/knowledge/{point_id}", response_model=KnowledgeEntry)
async def knowledge_get(point_id: str, request: Request) -> KnowledgeEntry:
    client: httpx.AsyncClient = request.app.state.http_client
    url = f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}/points/{point_id}"
    try:
        resp = await client.get(url, params={"with_payload": "true"}, timeout=5.0)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Qdrant request failed: {exc}") from exc
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Qdrant error: {resp.text}")
    point = resp.json().get("result") or {}
    return _knowledge_point_to_entry(point)


@router.delete("/knowledge/by-source", response_model=KnowledgeDeleteResponse)
async def knowledge_delete_by_source(source: str, source_id: str) -> KnowledgeDeleteResponse:
    """Bulk-delete every knowledge point tagged with (source, source_id).

    Use this when re-ingesting a file or dropping a whole book — per-point
    delete isn't offered because knowledge chunks are derived, not authored.
    """
    from zeus.memory.library import get_knowledge_store

    store = get_knowledge_store()
    try:
        deleted = await asyncio.to_thread(store.delete_by_source, source, source_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"knowledge delete failed: {exc}") from exc
    return KnowledgeDeleteResponse(
        ok=bool(deleted),
        deleted=int(deleted or 0),
        source=source,
        source_id=source_id,
    )


@router.delete("/knowledge/by-facet", response_model=KnowledgeFacetDeleteResponse)
async def knowledge_delete_by_facet(
    request: Request,
    key: str,
    value: str,
) -> KnowledgeFacetDeleteResponse:
    """Delete every zeus_knowledge point where ``payload.{key} == value``.

    Scoped to ``source`` / ``type`` / ``book`` — the only keys where a
    delete-everything gesture makes sense. Accept-list keeps a stray
    ``key=user_id`` from wiping the whole collection.
    """
    if key not in _ALLOWED_FACET_DELETE_KEYS:
        raise HTTPException(
            status_code=400,
            detail=f"key must be one of {sorted(_ALLOWED_FACET_DELETE_KEYS)}, got {key!r}",
        )
    if not value:
        raise HTTPException(status_code=400, detail="value is required")

    client: httpx.AsyncClient = request.app.state.http_client
    flt = {
        "must": [
            {"key": "user_id", "match": {"value": ZEUS_USER_ID}},
            {"key": key, "match": {"value": value}},
        ]
    }

    # Best-effort count first, so the response can report how many got removed.
    deleted = 0
    try:
        count_resp = await client.post(
            f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}/points/count",
            json={"filter": flt, "exact": True},
            timeout=10.0,
        )
        if count_resp.status_code == 200:
            deleted = int((count_resp.json().get("result", {}) or {}).get("count", 0))
    except httpx.HTTPError:
        pass

    try:
        del_resp = await client.post(
            f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}/points/delete",
            json={"filter": flt},
            params={"wait": "true"},
            timeout=30.0,
        )
        del_resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"qdrant delete failed: {exc}") from exc

    return KnowledgeFacetDeleteResponse(ok=True, key=key, value=value, deleted=deleted)


@router.post("/knowledge/delete_batch", response_model=BulkDeleteResponse)
async def knowledge_delete_batch(body: IdBatch, request: Request) -> BulkDeleteResponse:
    """Delete a set of knowledge point IDs in one Qdrant round-trip."""
    client: httpx.AsyncClient = request.app.state.http_client
    try:
        resp = await client.post(
            f"{QDRANT_URL.rstrip('/')}/collections/{ZEUS_KNOWLEDGE_COLLECTION}/points/delete",
            json={"points": body.ids},
            params={"wait": "true"},
            timeout=30.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"qdrant delete failed: {exc}") from exc
    return BulkDeleteResponse(ok=True, deleted=len(body.ids))


@router.post("/memory/delete_batch", response_model=BulkDeleteResponse)
async def memory_delete_batch(body: IdBatch) -> BulkDeleteResponse:
    """Delete a set of memory IDs through MemoryStore (keeps any cleanup side-effects)."""
    from zeus.memory.store import get_memory_store

    store = get_memory_store()
    deleted = 0
    errors: list[str] = []
    for mid in body.ids:
        try:
            await asyncio.to_thread(store.delete, mid)
            deleted += 1
        except Exception as exc:
            errors.append(f"{mid}: {exc}")
    if errors and deleted == 0:
        raise HTTPException(status_code=500, detail=f"all deletes failed: {errors[:3]}")
    return BulkDeleteResponse(ok=deleted > 0, deleted=deleted)
