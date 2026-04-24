# tests/conftest.py — Shared fixtures for Zeus tests
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_tool_state():
    """Ensure each test starts with empty tool registry / cache / invocations.

    All three are module-level process state; without a reset, a test that
    registers a tool, caches a result, or records an invocation could
    poison later tests.
    """
    from zeus.core.tools import registry
    from zeus.core.tools.cache import get_cache
    from zeus.core.tools.recorder import clear_invocations

    registry.clear()
    get_cache().clear()
    clear_invocations()
    yield
    registry.clear()
    get_cache().clear()
    clear_invocations()
