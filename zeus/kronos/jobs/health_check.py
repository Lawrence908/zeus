# zeus/kronos/jobs/health_check.py — Periodic readiness probe across services.
#
# Pings qdrant /readyz and ollama /api/tags via httpx and reports up/down per
# service with latency. Useful as a small example of a parameterised built-in;
# a future Phase 3 job could route failures to inbox_append.
from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx


async def run_service_health(params: dict[str, Any]) -> dict[str, Any]:
    targets: dict[str, str] = dict(params.get("targets") or {})
    if not targets:
        targets = {
            "qdrant": (os.getenv("QDRANT_URL", "http://localhost:6333").rstrip("/")
                       + "/readyz"),
            "ollama": (os.getenv("OLLAMA_URL", "http://localhost:11435").rstrip("/")
                       + "/api/tags"),
        }
    timeout = float(params.get("timeout_seconds") or 5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        results = await asyncio.gather(
            *(_probe(client, name, url) for name, url in targets.items()),
            return_exceptions=False,
        )

    services = dict(results)  # type: ignore[arg-type]
    down = [name for name, info in services.items() if info["status"] != "up"]
    return {
        "status": "ok" if not down else "degraded",
        "services": services,
        "down": down,
    }


async def _probe(client: httpx.AsyncClient, name: str, url: str) -> tuple[str, dict[str, Any]]:
    t0 = time.monotonic()
    try:
        resp = await client.get(url)
        latency_ms = round((time.monotonic() - t0) * 1000, 1)
        return name, {
            "status": "up" if resp.status_code < 400 else "down",
            "http_status": resp.status_code,
            "latency_ms": latency_ms,
            "url": url,
        }
    except Exception as exc:
        return name, {
            "status": "down",
            "error": str(exc),
            "latency_ms": round((time.monotonic() - t0) * 1000, 1),
            "url": url,
        }
