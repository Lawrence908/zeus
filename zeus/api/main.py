# zeus/api/main.py — Oracle router for Zeus Core
import os

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from zeus.memory.search import format_context_block, get_profile_facts, search_memories

ORACLE_VERSION = "0.1.0"
ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")

# Max tokens oracle will return in a single context block.
# Keeps prompt injection predictable — callers can request less.
DEFAULT_MAX_TOKENS = int(os.getenv("ORACLE_MAX_TOKENS", "2048"))


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
    top_k: int = Field(5, ge=1, le=20, description="Number of memories to retrieve")


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
        results = search_memories(
            memory=memory,
            query=body.query,
            user_id="chris",
            top_k=body.top_k,
            namespaces=body.namespaces,
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

    facts = get_profile_facts(memory=memory, user_id="chris", top_k=8)
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
