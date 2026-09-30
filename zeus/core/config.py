# zeus/core/config.py
"""Shared runtime configuration helpers.

Kept dependency-free (stdlib only) so every layer -- core, mcp, kronos,
orchestration, voice -- can import it without risking a cycle.
"""

from __future__ import annotations

import os

# Port zeus-core binds inside the container. compose publishes it on the host
# as ZEUS_CORE_PORT and sets ZEUS_CORE_URL to this value for in-container callers.
DEFAULT_PUBLISHED_PORT = "8203"


def core_base_url() -> str:
    """Base URL for the zeus-core HTTP bus, without a trailing slash.

    Resolution order:
      1. ZEUS_CORE_URL, which compose sets to the container-internal address.
      2. ZEUS_CORE_PORT, the host-published port, for processes running outside
         the compose network (the stdio MCP server, host-run Kronos jobs, Kairos).

    Deriving from ZEUS_CORE_PORT rather than hardcoding a port matters because a
    deployment that publishes on anything other than the default would otherwise
    need the fallback patched at every call site. Missing one fails as a silent
    connection-refused, which reads as "the feature is broken" rather than
    "the port is wrong".
    """
    explicit = os.getenv("ZEUS_CORE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    port = os.getenv("ZEUS_CORE_PORT", "").strip() or DEFAULT_PUBLISHED_PORT
    return f"http://127.0.0.1:{port}"
