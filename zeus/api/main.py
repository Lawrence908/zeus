# zeus/api/main.py — Oracle router for Zeus Core
import asyncio
import os

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from zeus.memory.search import MEMORY_SEARCH_TOP_K, format_context_block, get_profile_facts, search_memories

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
