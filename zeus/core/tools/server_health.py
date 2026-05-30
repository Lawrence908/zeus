# zeus/core/tools/server_health.py — Olympian aggregate health check
#
# Wraps /admin/system. cacheable=True so a chatty "is the server ok?" doesn't
# fan out to nvidia-smi/docker every turn; the default cache TTL is short
# enough that the data stays fresh between distinct conversational queries.
from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.server_health")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_SPEC = ToolSpec(
    name="olympian_server_health",
    description=(
        "Snapshot of host health: load average, RAM (used / available / "
        "percent), disk usage per allowlisted mount, GPU utilization and "
        "VRAM (via nvidia-smi when available), running container count "
        "(via docker ps when available), and Zeus uptime. Use when the "
        "user asks how the server is doing, whether anything's red, before "
        "suggesting a heavy operation, or to investigate a slowness "
        "complaint. Pure read; no side effects. Returns a single JSON blob."
    ),
    parameters={
        "type": "object",
        "properties": {},
    },
    aegis_policy="tool_arguments",
    timeout_seconds=10.0,
    cacheable=True,
)


def _format_summary(data: dict[str, Any]) -> str:
    lines: list[str] = []
    uptime = data.get("uptime_seconds")
    if isinstance(uptime, (int, float)):
        hours = uptime / 3600.0
        lines.append(f"uptime: {hours:.1f}h")
    load = data.get("load_avg")
    if isinstance(load, list) and len(load) >= 3:
        lines.append(f"load_avg: {load[0]:.2f} {load[1]:.2f} {load[2]:.2f}")
    mem = data.get("memory") or {}
    if mem.get("percent_used") is not None:
        lines.append(
            f"memory: {mem.get('used_mb', 0):.0f}/{mem.get('total_mb', 0):.0f} MB "
            f"({mem.get('percent_used')}%)"
        )
    for d in data.get("disks") or []:
        lines.append(
            f"disk {d.get('path')}: {d.get('used_gb')}/{d.get('total_gb')} GB "
            f"({d.get('percent_used')}%)"
        )
    gpus = data.get("gpus")
    if gpus is None:
        lines.append("gpu: nvidia-smi unavailable")
    else:
        for g in gpus:
            lines.append(
                f"gpu {g.get('index')} ({g.get('name')}): "
                f"{g.get('utilization_pct')}% util, "
                f"{g.get('memory_used_mb')}/{g.get('memory_total_mb')} MB VRAM, "
                f"{g.get('temperature_c')}C"
            )
    docker = data.get("docker")
    if docker is None:
        lines.append("docker: not on PATH")
    else:
        lines.append(f"containers running: {docker.get('running_count')}")
    return "\n".join(lines) if lines else "no data available"


async def _handler(args: dict[str, Any]) -> ToolResult:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{_core_url()}/admin/system")
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_server_health failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code >= 400:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=f"olympian_server_health got HTTP {r.status_code}: {r.text[:200]!r}",
            is_error=True,
        )
    data = r.json() or {}
    summary = _format_summary(data)
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    body = f"{summary}\n\nraw: {raw}"
    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register() -> None:
    """Register olympian_server_health. Always available; component fields degrade gracefully."""
    registry.register(_SPEC, _handler)
    logger.info("olympian_server_health registered")
