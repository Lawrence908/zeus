"""zeus/mcp/tools.py — MCP tool implementations calling Zeus Core HTTP APIs."""

from __future__ import annotations

import os
from typing import Any

import httpx


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


def _allow_write() -> bool:
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in {"1", "true", "yes", "y"}


async def zeus_query(*, query: str, top_k: int = 8, max_tokens: int = 1024) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/context/query",
            json={"query": query, "top_k": top_k, "max_tokens": max_tokens},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json() or {}
        sources = data.get("sources") or []
        source_strings = []
        for s in sources:
            src = (s or {}).get("source")
            if src:
                source_strings.append(str(src))
        return {
            "context": str(data.get("context") or ""),
            "sources": source_strings,
            "token_estimate": int(data.get("token_estimate") or 0),
        }


async def zeus_profile() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/context/profile", timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        summary = str(data.get("summary") or "")
        facts = data.get("facts") or []
        profile = summary
        if facts:
            profile = summary + "\n" + "\n".join(f"- {str(f)}" for f in facts[:12])
        return {"profile": profile.strip(), "updated_at": ""}


async def zeus_remember(*, text: str, namespace: str = "general", tags: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; zeus_remember disabled")

    payload = {"text": text, "namespace": namespace, "tags": tags or []}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{_core_url()}/memory/add", json=payload, timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        return {"memory_id": str(data.get("memory_id") or ""), "status": str(data.get("status") or "ok")}


async def zeus_ingest_trigger(*, source: str = "all") -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; zeus_ingest_trigger disabled")

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/ingest/trigger",
            json={"source": source},
            timeout=120.0,
        )
        r.raise_for_status()
        data = r.json() or {}
        return {
            "status": str(data.get("status") or "ok"),
            "chunks_indexed": int(data.get("chunks_indexed") or 0),
            "sources_run": list(data.get("sources_run") or []),
        }


async def kronos_create_job(
    *,
    name: str,
    description: str = "",
    category: str = "custom",
    cron: str | None = None,
    run_at: str | None = None,
    executor: str | None = None,
    agent: str | None = None,
    endpoint: str = "/run",
    params: dict[str, Any] | None = None,
    timezone: str = "UTC",
    safety_policy: str = "standard",
    timeout_seconds: int = 300,
    max_retries: int = 1,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Create a Kronos scheduled job. Proxies to POST /kronos/jobs.

    Provide exactly one of cron/run_at, and exactly one of executor/agent.
    Returns the created job_id and the next scheduled fire time.
    """
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; kronos_create_job disabled")

    if (cron is None) == (run_at is None):
        raise ValueError("kronos_create_job: pass exactly one of cron or run_at")
    if (executor is None) == (agent is None):
        raise ValueError("kronos_create_job: pass exactly one of executor or agent")

    # Derive a stable id from the name when caller doesn't pick one.
    if not job_id:
        slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
        job_id = slug[:60] or "job"

    payload: dict[str, Any] = {
        "id": job_id,
        "name": name,
        "description": description,
        "category": category,
        "schedule": {"cron": cron, "run_at": run_at, "timezone": timezone},
        "executor": executor,
        "agent": agent,
        "endpoint": endpoint,
        "params": params or {},
        "safety_policy": safety_policy,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
        "enabled": True,
    }

    async with httpx.AsyncClient() as client:
        create = await client.post(
            f"{_core_url()}/kronos/jobs", json=payload, timeout=15.0
        )
        if create.status_code == 409:
            raise ValueError(f"job id {job_id!r} already exists; pass job_id to override")
        create.raise_for_status()
        created = create.json() or {}

        upcoming = await client.get(
            f"{_core_url()}/kronos/schedule/upcoming", params={"limit": 100}, timeout=10.0
        )
        next_fire = ""
        if upcoming.status_code == 200:
            for entry in upcoming.json():
                if entry.get("job_id") == job_id:
                    next_fire = str(entry.get("next_fire") or "")
                    break

    return {
        "job_id": str(created.get("id") or job_id),
        "name": str(created.get("name") or name),
        "category": str(created.get("category") or category),
        "next_fire": next_fire,
        "enabled": bool(created.get("enabled", True)),
    }


async def zeus_memory_search(*, query: str, limit: int = 5) -> dict[str, Any]:
    lim = max(1, min(20, limit))
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/memory/search",
            json={"query": query, "limit": lim},
            timeout=30.0,
        )
        r.raise_for_status()
        data = r.json() or {}
        results = data.get("results") or []
        lines: list[str] = []
        for i, row in enumerate(results, 1):
            score = float(row.get("score") or 0.0)
            text = str(row.get("text") or "")[:200]
            src = str(row.get("source") or "unknown")
            lines.append(f"{i}. [{score:.3f}] ({src})\n   {text}")
        summary = "\n".join(lines) if lines else "No relevant memories found."
        return {"summary": summary, "count": len(results), "results": results}


# ------------------------------------------------------------------
# Olympian tool pack (LAB-328) — read-side
# ------------------------------------------------------------------


async def olympian_status_read() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/admin/status_file", timeout=5.0)
        r.raise_for_status()
        data = r.json() or {}
        return {
            "path": str(data.get("path") or ""),
            "content": str(data.get("content") or ""),
            "mtime": float(data.get("mtime") or 0.0),
            "exists": bool(data.get("exists", True)),
        }


async def olympian_server_health() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/admin/system", timeout=10.0)
        r.raise_for_status()
        return r.json() or {}


async def olympian_file_read(*, path: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_core_url()}/vault/file",
            params={"path": path},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def olympian_file_search(
    *,
    pattern: str,
    root: str | None = None,
    max_results: int = 50,
    case_sensitive: bool = False,
    fixed_strings: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pattern": pattern,
        "max_results": max(1, min(500, int(max_results))),
        "case_sensitive": bool(case_sensitive),
        "fixed_strings": bool(fixed_strings),
    }
    if root:
        payload["root"] = root
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/vault/search",
            json=payload,
            timeout=15.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def olympian_inbox_append(*, text: str, tags: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; olympian_inbox_append disabled")
    payload: dict[str, Any] = {"text": text}
    if tags:
        payload["tags"] = list(tags)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/inbox/append",
            json=payload,
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def olympian_action_list() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/actions/list", timeout=5.0)
        r.raise_for_status()
        return r.json() or {}


async def olympian_action_run(*, name: str, args: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; olympian_action_run disabled")
    payload: dict[str, Any] = {"name": name, "args": list(args or [])}
    # Action runner timeout is enforced server-side; client allows generous
    # slack for the round-trip.
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/actions/run",
            json=payload,
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json() or {}


async def zeus_calendar_today() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/calendar/today", timeout=15.0)
        r.raise_for_status()
        return r.json() or {}


async def zeus_newsletter_latest() -> dict[str, Any]:
    """Return the most recent newsletter digest entry (compact form)."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_core_url()}/api/newsletter/digests",
            params={"limit": 1},
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json() or {}
        digests = data.get("digests") or []
        if not digests:
            return {"digest": None, "exists": False}
        return {"digest": digests[0], "exists": True}

