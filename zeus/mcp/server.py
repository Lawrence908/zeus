"""zeus/mcp/server.py — Zeus MCP server (stdio by default).

Run:
  python3 -m zeus.mcp
  python3 -m zeus.mcp.server
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from zeus.mcp.tools import (
    kronos_create_job,
    olympian_action_list,
    olympian_action_run,
    olympian_file_read,
    olympian_file_search,
    olympian_inbox_append,
    olympian_server_health,
    olympian_status_read,
    zeus_calendar_today,
    zeus_ingest_trigger,
    zeus_memory_search,
    zeus_newsletter_latest,
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


@mcp.tool(name="olympian_status_read")
async def olympian_status_read_tool():
    return await olympian_status_read()


@mcp.tool(name="olympian_server_health")
async def olympian_server_health_tool():
    return await olympian_server_health()


@mcp.tool(name="olympian_file_read")
async def olympian_file_read_tool(path: str):
    return await olympian_file_read(path=path)


@mcp.tool(name="olympian_file_search")
async def olympian_file_search_tool(
    pattern: str,
    root: str | None = None,
    max_results: int = 50,
    case_sensitive: bool = False,
    fixed_strings: bool = False,
):
    return await olympian_file_search(
        pattern=pattern,
        root=root,
        max_results=max_results,
        case_sensitive=case_sensitive,
        fixed_strings=fixed_strings,
    )


@mcp.tool(name="olympian_inbox_append")
async def olympian_inbox_append_tool(text: str, tags: list[str] | None = None):
    return await olympian_inbox_append(text=text, tags=tags)


@mcp.tool(name="olympian_action_list")
async def olympian_action_list_tool():
    return await olympian_action_list()


@mcp.tool(name="olympian_action_run")
async def olympian_action_run_tool(name: str, args: list[str] | None = None):
    return await olympian_action_run(name=name, args=args)


@mcp.tool(name="zeus_calendar_today")
async def zeus_calendar_today_tool():
    return await zeus_calendar_today()


@mcp.tool(name="zeus_newsletter_latest")
async def zeus_newsletter_latest_tool():
    return await zeus_newsletter_latest()


@mcp.tool(name="kronos_create_job")
async def kronos_create_job_tool(
    name: str,
    description: str = "",
    category: str = "custom",
    cron: str | None = None,
    run_at: str | None = None,
    executor: str | None = None,
    agent: str | None = None,
    endpoint: str = "/run",
    params: dict | None = None,
    timezone: str = "UTC",
    safety_policy: str = "standard",
    timeout_seconds: int = 300,
    max_retries: int = 1,
    job_id: str | None = None,
):
    return await kronos_create_job(
        name=name,
        description=description,
        category=category,
        cron=cron,
        run_at=run_at,
        executor=executor,
        agent=agent,
        endpoint=endpoint,
        params=params,
        timezone=timezone,
        safety_policy=safety_policy,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        job_id=job_id,
    )


def main() -> None:
    # FastMCP uses stdio by default.
    mcp.run()


if __name__ == "__main__":
    main()

