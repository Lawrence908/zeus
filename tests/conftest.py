# tests/conftest.py — Shared fixtures for Zeus tests
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_tool_state():
    """Ensure each test starts with an empty chat-tool registry and cache.

    Both `_REGISTRY` (registry.py) and `_CACHE` (cache.py) are module-level
    process state. Without a reset, a test that registers a tool or caches
    a result could poison later tests.
    """
    from zeus.core.tools import registry
    from zeus.core.tools.cache import get_cache

    registry.clear()
    get_cache().clear()
    yield
    registry.clear()
    get_cache().clear()
