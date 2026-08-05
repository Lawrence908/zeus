# zeus/mcp/catalog.py — Static metadata for MCP-server tools
#
# The MCP server (zeus/mcp/server.py) runs as a separate process launched
# via stdio by MCP clients (Claude Desktop, Cursor, etc.), so zeus-core cannot
# introspect its live tool registry at request time. This catalog mirrors
# the tools registered in server.py one-for-one and is the single source of
# truth for the /admin/tools admin endpoint's MCP section.
#
# Keep this in sync with server.py when adding / removing MCP tools.
# LAB-107 (MCP Tool Definitions) + LAB-328 (Olympian Tool Pack) are where
# new MCP tools are scoped.
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class McpToolSpec:
    """Catalog entry for an MCP server tool.

    `parameters` uses JSON Schema object form (same shape as chat-path
    ToolSpec.parameters) so the frontend can render it with one code path.
    """

    name: str
    description: str
    parameters: dict[str, Any]
    write_gated: bool = False


def _mcp_allow_write() -> bool:
    """Mirror of zeus/mcp/tools.py::_allow_write() for consistent reporting."""
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }


MCP_TOOLS: list[McpToolSpec] = [
    McpToolSpec(
        name="zeus_query",
        description=(
            "Retrieve grounded context for a query: profile facts, memories, "
            "knowledge, and reference snippets, formatted for downstream "
            "reasoning. Returns the assembled context block plus a list of "
            "source identifiers. Use when an MCP client (Claude Desktop, "
            "Cursor) needs Zeus's personal context to answer."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question or topic."},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 8},
                "max_tokens": {"type": "integer", "minimum": 128, "maximum": 8192, "default": 1024},
            },
            "required": ["query"],
        },
    ),
    McpToolSpec(
        name="zeus_profile",
        description=(
            "Return the user's durable profile: summary paragraph plus up "
            "to 12 high-signal facts. No query needed. Zero write side."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    McpToolSpec(
        name="zeus_memory_search",
        description=(
            "Targeted search of the bi-temporal memory store (zeus_memories). "
            "Returns matching fact entries with score, source, and excerpt. "
            "Prefer this over zeus_query when you need raw hits, not a "
            "composed context paragraph."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
            },
            "required": ["query"],
        },
    ),
    McpToolSpec(
        name="zeus_remember",
        description=(
            "Write a new fact to Zeus's memory. Gated by the "
            "ZEUS_MCP_ALLOW_WRITE env flag — when false, the tool raises "
            "PermissionError and nothing is written."
        ),
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The fact or observation to remember."},
                "namespace": {"type": "string", "default": "general"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["text"],
        },
        write_gated=True,
    ),
    McpToolSpec(
        name="zeus_ingest_trigger",
        description=(
            "Trigger a re-ingest of one source or all sources through Iris. "
            "Long-running (up to 120s timeout). Gated by ZEUS_MCP_ALLOW_WRITE."
        ),
        parameters={
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "default": "all",
                    "description": "Source name (e.g. 'obsidian', 'chatgpt') or 'all' for the full pipeline.",
                },
            },
        },
        write_gated=True,
    ),
    McpToolSpec(
        name="olympian_status_read",
        description=(
            "Read the user-maintained status file (default ~/.zeus/status.md). "
            "Returns its current contents and mtime. Use when the caller asks "
            "'what's on my plate?', 'what am I working on?', or wants a "
            "compact view of the user's current focus. Zero retrieval latency; "
            "prefer this over zeus_query when the question is about today's plan."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    McpToolSpec(
        name="olympian_server_health",
        description=(
            "Aggregate host health snapshot: load average, RAM, disk usage "
            "per allowlisted mount, GPU utilization and VRAM (via nvidia-smi), "
            "running container count (via docker ps), and Zeus uptime. Pure "
            "read. Use when the caller asks how the server is doing, whether "
            "anything's red, or before suggesting a heavy operation."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    McpToolSpec(
        name="olympian_file_read",
        description=(
            "Read a single file from one of Zeus's allowlisted vault roots "
            "(ZEUS_FILE_READ_ROOTS). Returns the content, size, and mtime. "
            "Path traversal and symlink escapes are rejected server-side. "
            "1 MB read cap. Use when you need the exact contents of a known "
            "file rather than a vector-search excerpt."
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or ~-expanded path inside an allowlisted root.",
                },
            },
            "required": ["path"],
        },
    ),
    McpToolSpec(
        name="olympian_file_search",
        description=(
            "ripgrep-backed full-text search across the allowlisted vault "
            "roots (ZEUS_FILE_READ_ROOTS). Returns path/line/column/text "
            "matches. Much faster and more exact than vector search for "
            "'did I write about X?' questions. Defaults: case-insensitive "
            "regex, 50 results, 5 MB per-file cap, 10 s overall timeout."
        ),
        parameters={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex (or literal if fixed_strings=true).",
                },
                "root": {
                    "type": "string",
                    "description": "Optional single root from the allowlist; omit to search all.",
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "default": 50,
                },
                "case_sensitive": {"type": "boolean", "default": False},
                "fixed_strings": {
                    "type": "boolean",
                    "default": False,
                    "description": "Treat pattern as a literal string, not a regex.",
                },
            },
            "required": ["pattern"],
        },
    ),
    McpToolSpec(
        name="olympian_inbox_append",
        description=(
            "Append a single timestamped bullet line to the user's inbox "
            "file (default ~/.zeus/inbox.md). Use for capture: 'remember "
            "this for later', 'add to my inbox', 'note that X'. Tags are "
            "appended as #tag tokens. Atomic write under fcntl lock. Gated "
            "by ZEUS_MCP_ALLOW_WRITE."
        ),
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The captured note (one line; newlines collapsed).",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags (no leading #, no whitespace).",
                },
            },
            "required": ["text"],
        },
        write_gated=True,
    ),
    McpToolSpec(
        name="olympian_action_list",
        description=(
            "List the executable scripts the operator has dropped into "
            "ZEUS_ACTIONS_DIR (default ~/.zeus/actions/). Returns name, "
            "path, mtime, and the first `# desc:` comment line. Gated by "
            "ZEUS_ACTIONS_ENABLED. Use to discover which actions are "
            "available before calling olympian_action_run."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    McpToolSpec(
        name="olympian_action_run",
        description=(
            "Execute one named script from ZEUS_ACTIONS_DIR. The allowlist "
            "is the directory itself; arguments are passed positionally with "
            "no shell interpretation. Output is capped at 64 KB per stream. "
            "Gated by BOTH ZEUS_ACTIONS_ENABLED and ZEUS_MCP_ALLOW_WRITE."
        ),
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Action name (the script's basename without .sh).",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Positional args (each <=256 chars, max 16).",
                },
            },
            "required": ["name"],
        },
        write_gated=True,
    ),
    McpToolSpec(
        name="zeus_calendar_today",
        description=(
            "Return today's calendar events from already-ingested gcal data. "
            "Reads from MemoryStore via vector search (does not call the "
            "live Google Calendar API), so freshness depends on the latest "
            "Iris ingest. Use when the caller asks 'what's on my calendar?', "
            "'what meetings do I have today?', or wants today's schedule."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    McpToolSpec(
        name="zeus_newsletter_latest",
        description=(
            "Return the most recent newsletter digest entry (TLDR / others) "
            "without rendering the full web UI. Compact form suitable for "
            "Telegram or Meshtastic responses. Use when the caller asks "
            "'what's in today's newsletter?' or 'summarize the latest digest'."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    McpToolSpec(
        name="zeus_news_search",
        description=(
            "Deep-dive search over the Pheme news layer (zeus_news): "
            "consolidated Canary OSINT articles and CapitolScope "
            "congressional-trading signals over time, with source / topic / "
            "entity / date filters. Use for 'what has the news said about X'."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "source": {"type": "string", "enum": ["canary", "capitolscope"]},
                "topic": {"type": "string"},
                "entity": {"type": "string"},
                "since": {"type": "string"},
                "top_k": {"type": "integer", "default": 8},
            },
            "required": ["query"],
        },
    ),
    McpToolSpec(
        name="olympian_twitter_post",
        description=(
            "Post a tweet (plus optional reply thread) to the configured "
            "X/Twitter account. Public and irreversible: double-gated by "
            "ZEUS_MCP_ALLOW_WRITE and PHEME_TWITTER_ENABLED; every tweet "
            "passes the Aegis 'pheme' policy before send."
        ),
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "thread": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["text"],
        },
        write_gated=True,
    ),
]


def current_mcp_write_enabled() -> bool:
    """Runtime query — whether writes are currently permitted."""
    return _mcp_allow_write()
