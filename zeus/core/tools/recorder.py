# zeus/core/tools/recorder.py — Ring buffer of recent chat-path tool invocations
#
# Populated by run_tool_loop._execute_one() for every path: success, error,
# Aegis reject, cache hit. Exposed via GET /admin/tools/invocations so the
# React Tools page can show a live feed.
#
# MCP-server invocations happen out-of-process by external clients (Claude
# Desktop, Cursor), so they do not show up here; only the chat-path loop
# records into this buffer.
from __future__ import annotations

import time
from collections import deque
from typing import Any, Literal

from pydantic import BaseModel, Field


_MAX_INVOCATIONS = 200
_MAX_ARGS_CHARS = 500
_MAX_CONTENT_CHARS = 500


class ToolInvocation(BaseModel):
    """One recorded tool call. Arg and content text are truncated for UI use."""

    ts: float = Field(..., description="Unix timestamp when the call completed.")
    tool: str
    source: Literal["chat", "chat_async", "direct"]
    args: dict[str, Any] = Field(default_factory=dict)
    content: str = ""
    is_error: bool = False
    cache_hit: bool = False
    duration_ms: int = 0
    aegis_flags: list[str] = Field(default_factory=list)
    aegis_rejected: bool = False


_BUFFER: deque[ToolInvocation] = deque(maxlen=_MAX_INVOCATIONS)


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def record_invocation(
    *,
    tool: str,
    args: dict[str, Any],
    content: str,
    is_error: bool,
    cache_hit: bool,
    duration_ms: int,
    aegis_flags: list[str] | None = None,
    aegis_rejected: bool = False,
    source: Literal["chat", "chat_async", "direct"] = "chat",
) -> None:
    """Append an invocation record. Oldest entries are dropped at the maxlen cap."""
    # Shallow-copy args so later callers mutating the dict can't retroactively
    # change what the UI shows. Serialize complex values to strings.
    safe_args: dict[str, Any] = {}
    for k, v in (args or {}).items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe_args[k] = v
        else:
            safe_args[k] = _truncate(str(v), 200)

    entry = ToolInvocation(
        ts=time.time(),
        tool=tool,
        source=source,
        args=safe_args,
        content=_truncate(content, _MAX_CONTENT_CHARS),
        is_error=is_error,
        cache_hit=cache_hit,
        duration_ms=max(0, int(duration_ms)),
        aegis_flags=list(aegis_flags or []),
        aegis_rejected=aegis_rejected,
    )
    _BUFFER.append(entry)


def list_invocations(
    *,
    limit: int = 50,
    tool: str | None = None,
) -> list[ToolInvocation]:
    """Return most-recent-first invocations, optionally filtered by tool name."""
    limit = max(1, min(_MAX_INVOCATIONS, int(limit)))
    # Iterate in reverse to get newest first.
    out: list[ToolInvocation] = []
    for entry in reversed(_BUFFER):
        if tool is not None and entry.tool != tool:
            continue
        out.append(entry)
        if len(out) >= limit:
            break
    return out


def clear_invocations() -> None:
    """Test helper — wipe the ring buffer."""
    _BUFFER.clear()


def buffer_size() -> int:
    return len(_BUFFER)


def _percentile(sorted_vals: list[int], q: float) -> int:
    if not sorted_vals:
        return 0
    idx = min(len(sorted_vals) - 1, int(round(q * (len(sorted_vals) - 1))))
    return sorted_vals[idx]


def metrics_summary(*, window_seconds: float | None = None) -> dict[str, Any]:
    """Aggregate the invocation ring buffer for /admin/metrics.

    Rolls the recorded chat-path tool calls into overall + per-tool counts,
    error / cache-hit / Aegis-reject rates, and duration p50/p95. Pass
    window_seconds to restrict to recent calls (e.g. last 15 min); None uses
    the whole buffer (bounded by _MAX_INVOCATIONS).
    """
    entries = list(_BUFFER)
    if window_seconds is not None:
        cutoff = time.time() - window_seconds
        entries = [e for e in entries if e.ts >= cutoff]

    total = len(entries)
    base: dict[str, Any] = {
        "total": total,
        "buffer_max": _MAX_INVOCATIONS,
        "window_seconds": window_seconds,
        "oldest_ts": entries[0].ts if entries else None,
        "newest_ts": entries[-1].ts if entries else None,
    }
    if total == 0:
        base.update(
            {
                "error_rate": 0.0,
                "cache_hit_rate": 0.0,
                "aegis_reject_count": 0,
                "latency_ms_p50": 0,
                "latency_ms_p95": 0,
                "per_tool": {},
            }
        )
        return base

    errors = sum(1 for e in entries if e.is_error)
    cache_hits = sum(1 for e in entries if e.cache_hit)
    aegis_rejects = sum(1 for e in entries if e.aegis_rejected)
    durations = sorted(e.duration_ms for e in entries)

    per_tool: dict[str, dict[str, Any]] = {}
    for name in {e.tool for e in entries}:
        group = [e for e in entries if e.tool == name]
        g_durations = sorted(e.duration_ms for e in group)
        per_tool[name] = {
            "calls": len(group),
            "errors": sum(1 for e in group if e.is_error),
            "cache_hits": sum(1 for e in group if e.cache_hit),
            "aegis_rejects": sum(1 for e in group if e.aegis_rejected),
            "latency_ms_p50": _percentile(g_durations, 0.50),
            "latency_ms_p95": _percentile(g_durations, 0.95),
        }

    base.update(
        {
            "error_rate": round(errors / total, 4),
            "cache_hit_rate": round(cache_hits / total, 4),
            "aegis_reject_count": aegis_rejects,
            "latency_ms_p50": _percentile(durations, 0.50),
            "latency_ms_p95": _percentile(durations, 0.95),
            # Busiest tools first so a dashboard table reads top-down.
            "per_tool": dict(
                sorted(per_tool.items(), key=lambda kv: kv[1]["calls"], reverse=True)
            ),
        }
    )
    return base
