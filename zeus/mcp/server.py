"""zeus/mcp/server.py — Zeus MCP server (stdio by default).

Run:
  python3 -m zeus.mcp
  python3 -m zeus.mcp.server
"""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from zeus.mcp.tools import zeus_profile, zeus_query, zeus_remember

mcp = FastMCP("zeus")


@mcp.tool()
async def zeus_query_tool(query: str, top_k: int = 5, max_tokens: int = 1024):
    return await zeus_query(query=query, top_k=top_k, max_tokens=max_tokens)


@mcp.tool()
async def zeus_profile_tool():
    return await zeus_profile()


@mcp.tool()
async def zeus_remember_tool(text: str, namespace: str = "general", tags: list[str] | None = None):
    return await zeus_remember(text=text, namespace=namespace, tags=tags or [])


def main() -> None:
    # FastMCP uses stdio by default.
    mcp.run()


if __name__ == "__main__":
    main()

