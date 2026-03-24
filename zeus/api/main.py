# zeus/api/main.py — Oracle: Zeus Context API
# Serves structured personal context to agents and LLMs.
# Sits on top of mnemosyne (mem0) and formats results for injection into prompts.
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

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


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    from zeus.memory.config import get_memory_client
    app.state.memory = get_memory_client()
    yield


app = FastAPI(
    title="Oracle — Zeus Context API",
    version=ORACLE_VERSION,
    lifespan=lifespan,
)


def get_memory(request):
    return request.app.state.memory


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/context/query", response_model=ContextResponse)
async def query_context(body: ContextQuery, request=None):
    """
    Retrieve relevant memories and return them as a formatted context block.

    The context string is ready to inject into an LLM system prompt:
        system_prompt += f"\\n\\n## Personal Context\\n{context_response.context}"
    """
    memory = request.app.state.memory if request else None
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not initialized")

    try:
        results = memory.search(
            query=body.query,
            user_id="chris",
            limit=body.top_k,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {e}")

    if not results:
        return ContextResponse(context="", sources=[], token_estimate=0)

    # Format memories as a numbered list for LLM injection
    lines: list[str] = []
    sources: list[ContextSource] = []

    for i, mem in enumerate(results, 1):
        text = mem.get("memory", "")
        lines.append(f"{i}. {text}")
        sources.append(ContextSource(
            memory_id=mem.get("id", ""),
            source=mem.get("metadata", {}).get("source", "unknown"),
            relevance=mem.get("score", 0.0),
        ))

    context = "\n".join(lines)
    # Rough token estimate: 1 token ≈ 4 chars
    token_estimate = len(context) // 4

    # Truncate if over budget
    if token_estimate > body.max_tokens:
        max_chars = body.max_tokens * 4
        context = context[:max_chars] + "\n[truncated]"
        token_estimate = body.max_tokens

    return ContextResponse(
        context=context,
        sources=sources,
        token_estimate=token_estimate,
    )


@app.get("/context/profile", response_model=ProfileResponse)
async def get_profile(request=None):
    """
    Return stable facts about the user — used as baseline system prompt context.

    In Sprint 0 this is a stub. Sprint 1 will populate it from mnemosyne
    after the first ingest run.
    """
    # TODO: query mnemosyne with a "user profile" namespace after first ingest
    return ProfileResponse(
        user_id="chris",
        summary="Profile not yet populated. Run iris ingest first.",
        facts=[],
    )


@app.get("/status")
async def status():
    return {"service": "oracle", "version": ORACLE_VERSION, "env": ZEUS_ENV}
