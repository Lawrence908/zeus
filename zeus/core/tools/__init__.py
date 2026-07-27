# zeus/core/tools/__init__.py — Chat-path tool-use package
from __future__ import annotations

import os

from zeus.core.tools import registry
from zeus.core.tools.base import ToolCall, ToolHandler, ToolResult, ToolSpec


def tools_enabled() -> bool:
    return os.getenv("ZEUS_TOOLS_ENABLED", "0").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def tools_max_calls() -> int:
    try:
        return max(1, int(os.getenv("ZEUS_TOOLS_MAX_CALLS_PER_QUERY", "5")))
    except (TypeError, ValueError):
        return 5


def tools_allowlist() -> set[str] | None:
    """Parse ZEUS_TOOLS_ALLOWLIST (comma-separated tool names).

    Returns None when unset/empty, meaning "all registered tools are allowed".
    This is the per-env rollout control: prod can enable ZEUS_TOOLS_ENABLED=1
    with a read-only allowlist while dev runs the full pack.
    """
    raw = os.getenv("ZEUS_TOOLS_ALLOWLIST", "").strip()
    if not raw:
        return None
    return {name.strip() for name in raw.split(",") if name.strip()}


def allowed_tool_specs() -> list[ToolSpec]:
    """Registered tool specs filtered by the allowlist, registry order preserved.

    Single source of truth for "which tools does the chat model see this turn":
    used both to build the system-prompt tool list and to hand tools to the loop,
    so the model is never told about a tool it isn't allowed to call.
    """
    allow = tools_allowlist()
    specs = registry.list_specs()
    if allow is None:
        return specs
    return [spec for spec in specs if spec.name in allow]


__all__ = [
    "ToolCall",
    "ToolHandler",
    "ToolResult",
    "ToolSpec",
    "allowed_tool_specs",
    "registry",
    "tools_allowlist",
    "tools_enabled",
    "tools_max_calls",
]
