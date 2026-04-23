# zeus/core/tools/registry.py — Process-local chat tool registry
from __future__ import annotations

import logging

from zeus.core.tools.base import ToolHandler, ToolSpec

logger = logging.getLogger("zeus.tools")

_REGISTRY: dict[str, tuple[ToolSpec, ToolHandler]] = {}


def register(spec: ToolSpec, handler: ToolHandler) -> None:
    """Register a tool. Replaces any prior registration with the same name."""
    if spec.name in _REGISTRY:
        logger.info("tool %r re-registered", spec.name)
    _REGISTRY[spec.name] = (spec, handler)


def unregister(name: str) -> None:
    """Remove a tool. Used by tests to reset state between cases."""
    _REGISTRY.pop(name, None)


def get(name: str) -> tuple[ToolSpec, ToolHandler] | None:
    return _REGISTRY.get(name)


def list_specs() -> list[ToolSpec]:
    return [spec for spec, _ in _REGISTRY.values()]


def available() -> bool:
    return bool(_REGISTRY)


def clear() -> None:
    """Test helper — wipe all registered tools."""
    _REGISTRY.clear()
