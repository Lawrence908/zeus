"""Zeus Context API (Oracle) — knowledge base query interface."""

from fastapi import APIRouter, FastAPI

app = FastAPI(
    title="Zeus Oracle",
    version="0.1.0",
    description="Zeus Context API — knowledge base query interface",
)

router = APIRouter(prefix="/api/v1")


@router.get("/status")
async def status() -> dict:
    return {
        "service": "oracle",
        "status": "online",
        "knowledge_base": {"documents": 0, "chunks": 0},
    }


@router.get("/query")
async def query(q: str = "") -> dict:
    if not q:
        return {"error": "Query parameter 'q' is required"}
    return {
        "query": q,
        "results": [],
        "message": "Knowledge base is empty — run ingest pipeline to populate",
    }


app.include_router(router)
