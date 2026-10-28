# zeus/core/analytics.py: Read-only Umami analytics over HTTP
#
# GET /analytics/umami/stats?site=all&period=7d&limit=5
# GET /analytics/umami/events?period=7d&event=backup_completed&limit=20
#
# Backs the `umami_stats` / `umami_events` chat tools and MCP tools. The SQL and
# result shaping live in zeus/integrations/umami.py (shared with the monthly
# digest script); this module only owns the connection.
#
# Connection: UMAMI_DB_URL, e.g.
#   postgresql://umami_ro:<password>@umami-db:5432/umami
# umami-db is reachable only on the `umami-analytics` Docker network, which
# zeus-core joins in compose.yaml. The host-side stdio MCP server has no route
# to it, which is why the MCP tools go through this endpoint instead of
# connecting directly.
#
# Read-only twice over: the umami_ro role only has SELECT, and every session
# also sets default_transaction_read_only so a mis-provisioned role (or someone
# pointing UMAMI_DB_URL at the owner account) still cannot write.
from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from zeus.integrations import umami
from zeus.integrations.umami import UmamiError, UmamiNotFound

logger = logging.getLogger("zeus.analytics")

router = APIRouter(prefix="/analytics/umami", tags=["analytics"])

_SESSION_OPTIONS = "-c default_transaction_read_only=on -c statement_timeout=15000"


def umami_db_url() -> str:
    return os.getenv("UMAMI_DB_URL", "").strip()


@contextmanager
def _session(dsn: str) -> Iterator[umami.Runner]:
    """One psycopg connection per request, exposed as a umami.Runner."""
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(
        dsn,
        connect_timeout=5,
        options=_SESSION_OPTIONS,
        autocommit=True,
        row_factory=dict_row,
    ) as conn:

        def run(sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return list(cur.fetchall())

        yield run


def _query(fn: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    dsn = umami_db_url()
    if not dsn:
        raise HTTPException(status_code=503, detail="UMAMI_DB_URL is not set")
    try:
        with _session(dsn) as run:
            return fn(run, *args, **kwargs)
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"psycopg not installed: {exc}") from exc
    except UmamiNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UmamiError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - driver errors surface as 502
        # libpq error text names host and role, never the password.
        msg = f"{type(exc).__name__}: {str(exc).strip()[:300]}"
        logger.warning("umami query failed: %s", msg)
        raise HTTPException(status_code=502, detail=f"umami database error: {msg}") from exc


@router.get("/stats")
async def umami_stats_endpoint(
    site: str = "all",
    period: str = "7d",
    limit: int = Query(5, ge=1, le=25),
) -> dict[str, Any]:
    result = await asyncio.to_thread(_query, umami.stats, site, period, limit=limit)
    result["summary"] = umami.format_stats_text(result)
    return result


@router.get("/events")
async def umami_events_endpoint(
    period: str = "7d",
    event: str = "",
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    result = await asyncio.to_thread(
        _query, umami.homelab_events, period, event=event, limit=limit
    )
    result["summary"] = umami.format_events_text(result)
    return result
