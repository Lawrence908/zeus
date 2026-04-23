# zeus/core/admin.py — Admin API routes and dashboard (Sprint 9b-9c / LAB-148-149)
# Exposes /admin/metrics, /admin/ingest/stats, and /admin HTML dashboard.
import os
import time
from collections import deque
from pathlib import Path
from typing import Any

import httpx
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
    """Return Qdrant collection statistics for all collections."""
    try:
        from zeus.memory.store import get_memory_store

        qdrant = get_memory_store()._client  # noqa: SLF001 — admin-only reach-through

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


@router.get("/diagnostics")
async def admin_diagnostics(request: Request) -> dict[str, Any]:
    """
    Container-scoped diagnostics plus Ollama /api/ps (models loaded in Ollama).
    Does not enumerate arbitrary host processes — those require host tools or shared PID ns.
    """
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11435").rstrip("/")
    client: httpx.AsyncClient = request.app.state.http_client
    out: dict[str, Any] = {
        "zeus_pid": os.getpid(),
        "scope_note": (
            "Host clients (e.g. many python3 PIDs in lsof on the published Ollama port) "
            "are not visible here unless Zeus shares the host PID/network namespace."
        ),
        "ollama_ps": None,
        "ollama_ps_error": None,
        "ollama_running_model_count": None,
    }
    try:
        resp = await client.get(f"{ollama_url}/api/ps", timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            out["ollama_ps"] = data
            models = data.get("models") if isinstance(data, dict) else None
            if isinstance(models, list):
                out["ollama_running_model_count"] = len(models)
        else:
            out["ollama_ps_error"] = f"HTTP {resp.status_code}"
    except Exception as exc:
        out["ollama_ps_error"] = str(exc)
    return out


@router.get("/tool_cache/stats")
async def tool_cache_stats(request: Request) -> dict[str, Any]:
    """Expose chat-path tool-result cache counters for ops / smoke tests."""
    from zeus.core.tools import registry as tool_registry
    from zeus.core.tools.cache import _max_entries, _ttl_seconds, get_cache

    stats = get_cache().stats()
    return {
        **stats,
        "ttl_seconds": _ttl_seconds(),
        "max_entries": _max_entries(),
        "registered_tools": [
            {"name": s.name, "cacheable": s.cacheable}
            for s in tool_registry.list_specs()
        ],
    }


@router.post("/tool_cache/clear")
async def tool_cache_clear(request: Request) -> dict[str, Any]:
    """Drop every cached tool result. Handy during smoke tests."""
    from zeus.core.tools.cache import get_cache

    get_cache().clear()
    return {"ok": True, "stats": get_cache().stats()}


@router.post("/query-log/clear")
async def admin_query_log_clear(request: Request) -> dict[str, str]:
    """Clear the in-process admin query log ring buffer (observability only)."""
    qlog: deque | None = getattr(request.app.state, "query_log", None)
    if qlog is not None:
        qlog.clear()
    return {"status": "ok"}


