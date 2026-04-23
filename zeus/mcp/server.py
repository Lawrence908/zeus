"""zeus/mcp/server.py — Zeus MCP server (stdio by default).

Run:
  python3 -m zeus.mcp
  python3 -m zeus.mcp.server
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from zeus.mcp.tools import (
    zeus_ingest_trigger,
    zeus_memory_search,
    zeus_profile,
    zeus_query,
    zeus_remember,
)

mcp = FastMCP("zeus")


@mcp.tool(name="zeus_query")
async def zeus_query_tool(query: str, top_k: int = 8, max_tokens: int = 1024):
    return await zeus_query(query=query, top_k=top_k, max_tokens=max_tokens)


@mcp.tool(name="zeus_profile")
async def zeus_profile_tool():
    return await zeus_profile()


@mcp.tool(name="zeus_remember")
async def zeus_remember_tool(text: str, namespace: str = "general", tags: list[str] | None = None):
    return await zeus_remember(text=text, namespace=namespace, tags=tags or [])


@mcp.tool(name="zeus_ingest_trigger")
async def zeus_ingest_trigger_tool(source: str = "all"):
    return await zeus_ingest_trigger(source=source)


@mcp.tool(name="zeus_memory_search")
async def zeus_memory_search_tool(query: str, limit: int = 5):
    return await zeus_memory_search(query=query, limit=limit)


def main() -> None:
    # FastMCP uses stdio by default.
    mcp.run()


if __name__ == "__main__":
    main()

