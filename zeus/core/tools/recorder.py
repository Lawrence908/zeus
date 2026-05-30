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
