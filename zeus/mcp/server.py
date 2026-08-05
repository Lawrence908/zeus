"""zeus/mcp/server.py — Zeus MCP server (stdio by default).

Run:
  python3 -m zeus.mcp
  python3 -m zeus.mcp.server
"""

from __future__ import annotations

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env so tools that read os.getenv (e.g. CAPITOLSCOPE_SIGNALS_KEY) work
# regardless of how the stdio MCP server is launched.
load_dotenv()

from zeus.mcp.tools import (
    capitolscope_active_tickers,
    capitolscope_context_pack,
    capitolscope_digest,
    capitolscope_leaderboard,
    capitolscope_sector_flow,
    capitolscope_ticker,
    epstein_capabilities,
    epstein_connection_map,
    epstein_document,
    epstein_entity,
    epstein_entity_dossier,
    epstein_research,
    epstein_research_result,
    epstein_research_start,
    epstein_search,
    kronos_create_job,
    olympian_action_list,
    olympian_action_run,
    olympian_file_read,
    olympian_file_search,
    olympian_inbox_append,
    olympian_server_health,
    olympian_status_read,
    olympian_twitter_post,
    zeus_calendar_today,
    zeus_image_generate,
    zeus_ingest_trigger,
    zeus_memory_search,
    zeus_news_search,
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


@mcp.tool(name="zeus_image_generate")
async def zeus_image_generate_tool(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    seed: int | None = None,
):
    return await zeus_image_generate(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        seed=seed,
    )


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


@mcp.tool(name="zeus_news_search")
async def zeus_news_search_tool(
    query: str,
    source: str | None = None,
    topic: str | None = None,
    entity: str | None = None,
    since: str | None = None,
    top_k: int = 8,
):
    return await zeus_news_search(
        query=query, source=source, topic=topic, entity=entity, since=since, top_k=top_k
    )


@mcp.tool(name="olympian_twitter_post")
async def olympian_twitter_post_tool(text: str, thread: list[str] | None = None):
    return await olympian_twitter_post(text=text, thread=thread)


@mcp.tool(name="capitolscope_digest")
async def capitolscope_digest_tool(days: int = 7):
    return await capitolscope_digest(days=days)


@mcp.tool(name="capitolscope_active_tickers")
async def capitolscope_active_tickers_tool(days: int = 90, limit: int = 25):
    return await capitolscope_active_tickers(days=days, limit=limit)


@mcp.tool(name="capitolscope_context_pack")
async def capitolscope_context_pack_tool(days: int = 7):
    return await capitolscope_context_pack(days=days)


@mcp.tool(name="capitolscope_ticker")
async def capitolscope_ticker_tool(ticker: str, days: int = 180, limit: int = 60):
    return await capitolscope_ticker(ticker=ticker, days=days, limit=limit)


@mcp.tool(name="capitolscope_sector_flow")
async def capitolscope_sector_flow_tool(days: int = 90):
    return await capitolscope_sector_flow(days=days)


@mcp.tool(name="capitolscope_leaderboard")
async def capitolscope_leaderboard_tool(limit: int = 20):
    return await capitolscope_leaderboard(limit=limit)


@mcp.tool(name="epstein_capabilities")
async def epstein_capabilities_tool():
    return await epstein_capabilities()


@mcp.tool(name="epstein_search")
async def epstein_search_tool(
    query: str,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    document_ids: list[str] | None = None,
    n_results: int = 10,
    expand_graph: bool = False,
):
    return await epstein_search(
        query=query,
        doc_type=doc_type,
        date_mentioned=date_mentioned,
        document_ids=document_ids,
        n_results=n_results,
        expand_graph=expand_graph,
    )


@mcp.tool(name="epstein_document")
async def epstein_document_tool(document_id: str):
    return await epstein_document(document_id=document_id)


@mcp.tool(name="epstein_entity")
async def epstein_entity_tool(name: str, depth: int = 1, related_to: str | None = None):
    return await epstein_entity(name=name, depth=depth, related_to=related_to)


@mcp.tool(name="epstein_research_start")
async def epstein_research_start_tool(
    question: str,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    depth: int = 3,
):
    return await epstein_research_start(
        question=question, doc_type=doc_type, date_mentioned=date_mentioned, depth=depth
    )


@mcp.tool(name="epstein_research_result")
async def epstein_research_result_tool(job_id: str):
    return await epstein_research_result(job_id=job_id)


@mcp.tool(name="epstein_research")
async def epstein_research_tool(
    question: str,
    doc_type: str | None = None,
    date_mentioned: str | None = None,
    depth: int = 3,
    wait_seconds: int = 0,
):
    return await epstein_research(
        question=question,
        doc_type=doc_type,
        date_mentioned=date_mentioned,
        depth=depth,
        wait_seconds=wait_seconds,
    )


@mcp.tool(name="epstein_entity_dossier")
async def epstein_entity_dossier_tool(
    name: str,
    doc_type: str | None = None,
    depth: int = 1,
    write_report: bool = False,
):
    return await epstein_entity_dossier(
        name=name, doc_type=doc_type, depth=depth, write_report=write_report
    )


@mcp.tool(name="epstein_connection_map")
async def epstein_connection_map_tool(
    names: list[str],
    depth: int = 2,
    write_report: bool = False,
):
    return await epstein_connection_map(names=names, depth=depth, write_report=write_report)


def main() -> None:
    # FastMCP uses stdio by default.
    mcp.run()


if __name__ == "__main__":
    main()

