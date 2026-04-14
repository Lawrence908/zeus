# zeus/api/main.py — Oracle router for Zeus Core
import asyncio
import os

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from zeus.memory.search import MEMORY_SEARCH_TOP_K, format_context_block, get_profile_facts, search_memories

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "zeus_memories")
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
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    try:
        results = await asyncio.to_thread(
            search_memories,
            memory,
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
        sources.append(ContextSource(
            memory_id=mem.get("id", ""),
            source=mem.get("metadata", {}).get("source", "unknown"),
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
        src = str(md.get("source", "") or "unknown")
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
    """Raw mem0 hits for MCP / debugging (no formatted context block)."""
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    k = body.top_k if body.top_k is not None else body.limit
    if k is None:
        k = MEMORY_SEARCH_TOP_K

    try:
        rows = await asyncio.to_thread(
            search_memories,
            memory,
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
    """Run Iris ingest for one source (or all). Uses app.state.memory."""
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

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
        memory=memory,
        ingest_ui="plain",
    )
    total = sum(r.chunks_stored for r in results)
    labels = [r.source for r in results]
    return IngestTriggerResponse(status="ok", chunks_indexed=total, sources_run=labels)


def _point_to_entry(point: dict) -> MemoryEntry:
    payload = point.get("payload", {}) or {}
    text = str(payload.get("data", "") or "").strip()
    source = str(payload.get("source", "") or "unknown")
    metadata = {
        k: v for k, v in payload.items()
        if k not in {"data", "hash", "user_id"}
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
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")
    try:
        await asyncio.to_thread(memory.update, memory_id=memory_id, data=body.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"mem0 update failed: {exc}") from exc
    return await memory_get(memory_id, request)


@router.delete("/memory/{memory_id}")
async def memory_delete(memory_id: str, request: Request) -> dict:
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")
    try:
        await asyncio.to_thread(memory.delete, memory_id=memory_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"mem0 delete failed: {exc}") from exc
    return {"ok": True, "id": memory_id}


@router.get("/context/profile", response_model=ProfileResponse)
async def get_profile(request: Request):
    """
    Return stable facts about the user — used as baseline system prompt context.

    In Sprint 0 this is a stub. Sprint 1 will populate it from mnemosyne
    after the first ingest run.
    """
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    facts = await asyncio.to_thread(get_profile_facts, memory, "chris", 8)
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
