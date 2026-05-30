# zeus/core/admin.py — Admin API routes and dashboard (Sprint 9b-9c / LAB-148-149)
# Exposes /admin/metrics, /admin/ingest/stats, and /admin HTML dashboard.
import asyncio
import os
import shutil
import time
from collections import deque
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
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
        "kronos": await _kronos_metrics(request),
    }


async def _kronos_metrics(request: Request) -> dict[str, Any]:
    """Summarise Kronos state for the admin dashboard. Empty dict when disabled."""
    from datetime import datetime, timedelta, timezone

    registry = getattr(request.app.state, "kronos_registry", None)
    scheduler = getattr(request.app.state, "kronos_scheduler", None)
    if registry is None:
        return {"enabled": False}

    jobs = await registry.list()
    enabled_jobs = [j for j in jobs if j.enabled]
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_runs = await registry.list_runs(since=since, limit=500)

    by_status: dict[str, int] = {}
    by_category_dur: dict[str, list[float]] = {}
    for run in recent_runs:
        by_status[run.status.value] = by_status.get(run.status.value, 0) + 1
        job = next((j for j in jobs if j.id == run.job_id), None)
        if job is None or run.duration_ms is None:
            continue
        by_category_dur.setdefault(job.category.value, []).append(run.duration_ms)
    avg_duration_by_category = {
        cat: round(sum(vals) / len(vals), 1) for cat, vals in by_category_dur.items()
    }

    # "Overdue" = enabled cron job whose next expected fire is in the past
    # relative to its last_fired_at.
    from zeus.kronos.api import _compute_next_fire  # local import to avoid cycle at module load

    now = datetime.now(timezone.utc)
    overdue = 0
    for job in enabled_jobs:
        last = await registry.last_fired_at(job.id)
        next_fire = _compute_next_fire(job, now, last)
        if next_fire is not None and next_fire < now:
            overdue += 1

    return {
        "enabled": True,
        "total_jobs": len(jobs),
        "enabled_jobs": len(enabled_jobs),
        "runs_24h": {
            "total": len(recent_runs),
            "by_status": by_status,
        },
        "avg_duration_ms_by_category": avg_duration_by_category,
        "overdue": overdue,
        "scheduler_health": scheduler.health if scheduler is not None else {},
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


# ------------------------------------------------------------------
# Tool directory + invocations feed (LAB-403 / LAB-404)
# ------------------------------------------------------------------


@router.get("/tools")
async def tools_directory(request: Request) -> dict[str, Any]:
    """Unified catalog of every tool Zeus has.

    Chat-path tools come from the in-process registry and fire during
    QueryEngine.query() when ZEUS_TOOLS_ENABLED=1. MCP tools come from the
    static catalog in zeus/mcp/catalog.py and are exposed to external MCP
    clients (Claude Desktop, Cursor) via the separate stdio MCP server.

    Response shape is a single flat `tools` list with a `source` field so
    the frontend can render chat/MCP side-by-side or filtered.
    """
    from zeus.core.tools import registry as tool_registry
    from zeus.core.tools import tools_enabled, tools_max_calls
    from zeus.mcp.catalog import MCP_TOOLS, current_mcp_write_enabled

    tools: list[dict[str, Any]] = []

    for spec in tool_registry.list_specs():
        tools.append(
            {
                "source": "chat",
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.parameters,
                "cacheable": spec.cacheable,
                "aegis_policy": spec.aegis_policy,
                "timeout_seconds": spec.timeout_seconds,
                "write_gated": False,
            }
        )

    mcp_write_live = current_mcp_write_enabled()
    for mspec in MCP_TOOLS:
        tools.append(
            {
                "source": "mcp",
                "name": mspec.name,
                "description": mspec.description,
                "parameters": mspec.parameters,
                "cacheable": False,
                "aegis_policy": None,
                "timeout_seconds": None,
                "write_gated": mspec.write_gated,
                # Only meaningful for write-gated MCP tools; UI renders accordingly.
                "write_enabled_now": mspec.write_gated and mcp_write_live,
            }
        )

    return {
        "tools": tools,
        "chat": {
            "enabled": tools_enabled(),
            "max_calls_per_query": tools_max_calls(),
            "count": sum(1 for t in tools if t["source"] == "chat"),
        },
        "mcp": {
            "write_enabled": mcp_write_live,
            "count": sum(1 for t in tools if t["source"] == "mcp"),
        },
    }


@router.get("/tools/invocations")
async def tools_invocations(
    request: Request,
    limit: int = 50,
    tool: str | None = None,
) -> dict[str, Any]:
    """Return the most recent chat-path tool invocations.

    Populated by `run_tool_loop._execute_one` for every execution path
    (success, error, cache hit, Aegis reject). MCP tool invocations from
    external clients are NOT captured here because they happen in the
    separate stdio MCP process.
    """
    from zeus.core.tools.recorder import list_invocations

    items = list_invocations(limit=limit, tool=tool)
    return {
        "invocations": [inv.model_dump() for inv in items],
        "count": len(items),
        "filter": {"tool": tool, "limit": limit},
    }


@router.post("/query-log/clear")
async def admin_query_log_clear(request: Request) -> dict[str, str]:
    """Clear the in-process admin query log ring buffer (observability only)."""
    qlog: deque | None = getattr(request.app.state, "query_log", None)
    if qlog is not None:
        qlog.clear()
    return {"status": "ok"}


# ------------------------------------------------------------------
# Status file + system health (Olympian tool pack, LAB-328)
# ------------------------------------------------------------------


def _status_path() -> Path:
    raw = os.getenv("ZEUS_STATUS_PATH", "~/.zeus/status.md")
    return Path(os.path.expanduser(raw))


@router.get("/status_file")
async def admin_status_file() -> dict[str, Any]:
    """Read the user-maintained status file (default ~/.zeus/status.md).

    Backs olympian_status_read. ZEUS_STATUS_AUTOCREATE=1 returns an empty
    payload instead of 404 when the file does not yet exist; otherwise we
    surface 404 so the caller knows to create it.
    """
    p = _status_path()
    autocreate = os.getenv("ZEUS_STATUS_AUTOCREATE", "0").strip().lower() in (
        "1", "true", "yes", "on",
    )
    if not p.exists():
        if autocreate:
            return {"path": str(p), "content": "", "mtime": 0.0, "exists": False}
        raise HTTPException(status_code=404, detail=f"Status file not found at {p}")
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        mtime = p.stat().st_mtime
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read {p}: {exc}") from exc
    return {"path": str(p), "content": content, "mtime": mtime, "exists": True}


def _read_proc_meminfo() -> dict[str, float]:
    """Parse /proc/meminfo into MB. Returns {} on non-Linux hosts."""
    out: dict[str, float] = {}
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                key, _, rest = line.partition(":")
                rest = rest.strip()
                if not rest.endswith("kB"):
                    continue
                try:
                    kb = float(rest.split()[0])
                except (ValueError, IndexError):
                    continue
                out[key.strip()] = kb / 1024.0  # MB
    except OSError:
        return {}
    return out


def _read_proc_loadavg() -> tuple[float, float, float] | None:
    try:
        with open("/proc/loadavg", encoding="utf-8") as fh:
            parts = fh.read().split()
        return (float(parts[0]), float(parts[1]), float(parts[2]))
    except (OSError, ValueError, IndexError):
        return None


def _disk_usage(paths: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in paths:
        p = os.path.expanduser(raw)
        if not p or p in seen:
            continue
        seen.add(p)
        try:
            usage = shutil.disk_usage(p)
        except OSError:
            continue
        out.append({
            "path": p,
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "percent_used": round(usage.used / usage.total * 100.0, 1) if usage.total else 0.0,
        })
    return out


async def _nvidia_smi_summary() -> list[dict[str, Any]] | None:
    """Run nvidia-smi --query-gpu and parse one row per GPU. Returns None if unavailable."""
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi",
            "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu",
            "--format=csv,noheader,nounits",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=3.0)
    except (FileNotFoundError, asyncio.TimeoutError, OSError):
        return None
    rows: list[dict[str, Any]] = []
    for line in stdout.decode("utf-8", errors="replace").splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        try:
            rows.append({
                "index": int(parts[0]),
                "name": parts[1],
                "utilization_pct": float(parts[2]),
                "memory_used_mb": float(parts[3]),
                "memory_total_mb": float(parts[4]),
                "temperature_c": float(parts[5]),
            })
        except ValueError:
            continue
    return rows


async def _docker_ps_summary() -> dict[str, Any] | None:
    """Count running containers via `docker ps`. Returns None if docker not on PATH."""
    if shutil.which("docker") is None:
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            "docker", "ps", "--format", "{{.Names}}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=3.0)
    except (FileNotFoundError, asyncio.TimeoutError, OSError):
        return None
    names = [n for n in stdout.decode("utf-8", errors="replace").splitlines() if n.strip()]
    # Cap names to keep the response within Meshtastic-friendly budgets when
    # the host runs many containers; running_count remains authoritative.
    cap = 20
    truncated = len(names) > cap
    return {
        "running_count": len(names),
        "names": names[:cap],
        "names_truncated": truncated,
    }


@router.get("/system")
async def admin_system(request: Request) -> dict[str, Any]:
    """Aggregate host health snapshot. Backs olympian_server_health.

    Pure read-only: load avg, RAM, disk per allowlisted mount, GPU via
    nvidia-smi, container count via docker ps, plus Qdrant/Ollama latency
    pulled from /status. Each component degrades gracefully if its data
    source is missing (non-Linux host, no GPU, no docker on PATH).
    """
    mem = _read_proc_meminfo()
    load = _read_proc_loadavg()

    disk_paths_raw = os.getenv("ZEUS_SYSTEM_HEALTH_DISKS", "/,/home")
    disk_paths = [p.strip() for p in disk_paths_raw.split(",") if p.strip()]

    gpu_enabled = os.getenv("ZEUS_SYSTEM_HEALTH_GPU", "1").strip().lower() in (
        "1", "true", "yes", "on",
    )

    gpu_task = _nvidia_smi_summary() if gpu_enabled else asyncio.sleep(0, result=None)
    docker_task = _docker_ps_summary()
    gpu, docker_info = await asyncio.gather(gpu_task, docker_task)

    boot = getattr(request.app.state, "boot_time", time.time())
    return {
        "uptime_seconds": round(time.time() - boot, 1),
        "load_avg": list(load) if load is not None else None,
        "memory": {
            "total_mb": round(mem.get("MemTotal", 0.0), 1),
            "available_mb": round(mem.get("MemAvailable", 0.0), 1),
            "used_mb": round(max(0.0, mem.get("MemTotal", 0.0) - mem.get("MemAvailable", 0.0)), 1),
            "percent_used": (
                round((1.0 - mem["MemAvailable"] / mem["MemTotal"]) * 100.0, 1)
                if mem.get("MemTotal") and mem.get("MemAvailable") is not None
                else None
            ),
        } if mem else None,
        "disks": _disk_usage(disk_paths),
        "gpus": gpu,
        "docker": docker_info,
    }


