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


__all__ = [
    "ToolCall",
    "ToolHandler",
    "ToolResult",
    "ToolSpec",
    "registry",
    "tools_enabled",
    "tools_max_calls",
]
