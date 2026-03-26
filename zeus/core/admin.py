# zeus/core/admin.py — Admin API routes and dashboard (Sprint 9b-9c / LAB-148-149)
# Exposes /admin/metrics, /admin/ingest/stats, and /admin HTML dashboard.
import time
from collections import deque
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# In-process ring buffer for recent query log entries (populated by middleware)
# Keyed on the app instance via app.state.query_log
_QUERY_LOG_MAXLEN = 200


def init_query_log(app) -> None:
    """Call from lifespan to initialise the query log on app.state."""
    app.state.query_log = deque(maxlen=_QUERY_LOG_MAXLEN)


def record_query(app, entry: dict) -> None:
    """Thread-safe append to the in-process query log."""
    try:
        app.state.query_log.append(entry)
    except AttributeError:
        pass  # app.state not initialised yet — silent skip


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@router.get("")
@router.get("/")
async def admin_dashboard():
    """Serve the admin HTML dashboard."""
    html_path = Path(__file__).resolve().parent / "static" / "admin.html"
    return FileResponse(str(html_path), media_type="text/html")


@router.get("/metrics")
async def metrics(request: Request) -> dict[str, Any]:
    """Return uptime, agent swarm status, and recent query count."""
    boot_time = getattr(request.app.state, "boot_time", time.time())
    runtime = getattr(request.app.state, "agent_runtime", None)
    query_log: deque = getattr(request.app.state, "query_log", deque())

    scheduler = getattr(request.app.state, "ingest_scheduler", None)
    scheduler_info: dict[str, Any] = {}
    if scheduler is not None:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            })
        scheduler_info = {"running": scheduler.running, "jobs": jobs}

    recent = list(query_log)
    avg_latency = (
        round(sum(e["latency_ms"] for e in recent) / len(recent), 1)
        if recent else None
    )

    return {
        "uptime_seconds": round(time.time() - boot_time, 1),
        "agents": runtime.get_status() if runtime else {},
        "recent_query_count": len(recent),
        "avg_latency_ms": avg_latency,
        "recent_queries": recent[-20:],  # last 20 for dashboard table
        "scheduler": scheduler_info,
    }


@router.get("/ingest/stats")
async def ingest_stats(request: Request) -> dict[str, Any]:
    """Return Qdrant collection info and per-source chunk counts."""
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        return {"error": "memory client not initialised"}

    try:
        # mem0 wraps Qdrant — reach through to the underlying client
        qdrant = _get_qdrant_client(memory)
        if qdrant is None:
            return {"error": "qdrant client not accessible"}

        collections_resp = qdrant.get_collections()
        collection_names = [c.name for c in collections_resp.collections]

        stats: dict[str, Any] = {"collections": {}}
        for name in collection_names:
            info = qdrant.get_collection(name)
            stats["collections"][name] = {
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": str(info.status),
            }

        return stats

    except Exception as exc:
        return {"error": str(exc)}


def _get_qdrant_client(memory):
    """Try to extract the raw qdrant_client from the mem0 client."""
    # mem0 stores it at memory.vector_store.client or similar paths
    for attr in ("vector_store", "_vector_store"):
        vs = getattr(memory, attr, None)
        if vs is not None:
            for inner in ("client", "_client", "qdrant_client"):
                c = getattr(vs, inner, None)
                if c is not None:
                    return c
    return None
