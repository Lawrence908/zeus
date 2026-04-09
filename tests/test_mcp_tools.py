# tests/test_mcp_tools.py — MCP tool registration smoke (LAB-108)
import asyncio

from zeus.mcp.server import mcp


def test_tools_registered():
    async def _run() -> None:
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        expected = {
            "zeus_query",
            "zeus_remember",
            "zeus_profile",
            "zeus_ingest_trigger",
            "zeus_memory_search",
        }
        missing = expected - names
        assert not missing, f"Missing tools: {missing}; have: {sorted(names)}"

    asyncio.run(_run())
