# tests/test_umami.py: Umami analytics: query module, Core router, chat + MCP tools
#
# No database: a fake Runner answers each SQL constant with canned rows, the way
# psycopg (dict rows, ints) or the digest's psql runner (CSV strings) would.
# The chat tool is exercised end to end through httpx.ASGITransport into the
# real router, so tool -> HTTP -> router -> query module is one code path.
from __future__ import annotations

import asyncio
import re
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from zeus.core import analytics
from zeus.core.tools import registry
from zeus.core.tools import umami as umami_tool
from zeus.integrations import umami

NOW = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
PORTFOLIO = "da89adad-395b-40f9-a7fb-7034d1bb2833"
ECON = "11111111-1111-1111-1111-111111111111"
HOMELAB = "22222222-2222-2222-2222-222222222222"

WEBSITES = [
    {"website_id": ECON, "name": "Econ", "domain": "econ.chrislawrence.ca"},
    {"website_id": HOMELAB, "name": "Homelab events", "domain": "daedalus.homelab"},
    {"website_id": PORTFOLIO, "name": "Portfolio", "domain": "portfolio.chrislawrence.ca"},
]


class FakeRunner:
    def __init__(self, *, as_strings: bool = False) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.as_strings = as_strings

    def _cast(self, rows: list[dict]) -> list[dict]:
        if not self.as_strings:
            return rows
        return [{k: "" if v is None else str(v) for k, v in r.items()} for r in rows]

    def __call__(self, sql: str, params: dict) -> list[dict]:
        self.calls.append((sql, params))
        if sql is umami.SQL_WEBSITES:
            return self._cast(WEBSITES)
        if sql is umami.SQL_TOTALS:
            if params["website_id"] == PORTFOLIO:
                row = {"pageviews": 120, "visitors": 40, "visits": 50, "events": 30,
                       "prev_pageviews": 100, "prev_visitors": 0, "prev_visits": 45, "prev_events": 30}
            else:
                row = {k: 0 for k in ("pageviews", "visitors", "visits", "events", "prev_pageviews",
                                      "prev_visitors", "prev_visits", "prev_events")}
            return self._cast([row])
        if sql is umami.SQL_TOPS:
            return self._cast([
                {"kind": "page", "label": "/", "n": 80},
                {"kind": "page", "label": "/projects", "n": 40},
                {"kind": "referrer", "label": "chrislawrence.ca", "n": 9},
                {"kind": "event", "label": "engaged", "n": 12},
            ])
        if sql is umami.SQL_EVENT_COUNTS:
            return self._cast([{"event_name": "backup_completed", "n": 7, "last_at": NOW}])
        if sql is umami.SQL_RECENT_EVENTS:
            return self._cast([{"created_at": NOW, "event_name": "backup_completed",
                                "url_path": "/backup/umami", "data": "service=umami, size=4.2M"}])
        raise AssertionError(f"unexpected SQL: {sql[:60]}")


# --- period parsing -------------------------------------------------------


@pytest.mark.parametrize(
    ("period", "delta"),
    [("24h", timedelta(hours=24)), ("7d", timedelta(days=7)), ("30D", timedelta(days=30)),
     (" 4w ", timedelta(weeks=4))],
)
def test_parse_period(period, delta):
    assert umami.parse_period(period) == delta


@pytest.mark.parametrize("period", ["", "7", "1y", "0h", "400d", "7d; drop table website"])
def test_parse_period_rejects(period):
    with pytest.raises(umami.UmamiError):
        umami.parse_period(period)


# --- SQL hygiene ----------------------------------------------------------


def test_sql_is_parameterized_and_excludes_deleted():
    assert "deleted_at IS NULL" in umami.SQL_WEBSITES
    for sql in (umami.SQL_TOTALS, umami.SQL_TOPS, umami.SQL_EVENT_COUNTS, umami.SQL_RECENT_EVENTS):
        # Every placeholder is cast, so it binds identically under psycopg and psql.
        for m in re.finditer(r"%\((\w+)\)s(::\w+)?", sql):
            assert m.group(2), f"uncast placeholder {m.group(0)}"
        assert "{" not in sql  # no str.format templating
        assert not re.search(r"(?i)\b(insert|update|delete|drop|alter|create)\b", sql)


def test_values_never_reach_sql_text():
    run = FakeRunner()
    umami.stats(run, "Portfolio", "7d", now=NOW)
    for sql, params in run.calls:
        assert PORTFOLIO not in sql
        for v in params.values():
            assert str(v) not in sql or str(v) in {"", "5"}


# --- stats ----------------------------------------------------------------


def test_stats_all_excludes_homelab_site_and_shapes_result():
    run = FakeRunner()
    r = umami.stats(run, "all", "7d", now=NOW)
    assert [s["name"] for s in r["sites"]] == ["Econ", "Portfolio"]
    assert r["start"] == (NOW - timedelta(days=7)).isoformat()
    assert r["previous_start"] == (NOW - timedelta(days=14)).isoformat()

    p = r["sites"][1]
    assert (p["pageviews"], p["visitors"], p["visits"], p["events"]) == (120, 40, 50, 30)
    assert p["change_pct"] == {"pageviews": 20.0, "visitors": None, "visits": 11.1, "events": 0.0}
    assert p["top_pages"][0] == {"path": "/", "pageviews": 80}
    assert p["top_referrers"] == [{"domain": "chrislawrence.ca", "visitors": 9}]
    assert p["top_events"] == [{"name": "engaged", "count": 12}]
    assert r["totals"]["pageviews"] == 120

    # Idle site skips the tops query entirely.
    tops_calls = [params["website_id"] for sql, params in run.calls if sql is umami.SQL_TOPS]
    assert tops_calls == [PORTFOLIO]


def test_stats_accepts_psql_string_rows():
    r = umami.stats(FakeRunner(as_strings=True), "portfolio.chrislawrence.ca", "24h", now=NOW)
    assert r["sites"][0]["pageviews"] == 120
    assert r["sites"][0]["top_pages"][1] == {"path": "/projects", "pageviews": 40}


def test_stats_unknown_site_lists_available():
    with pytest.raises(umami.UmamiNotFound, match="Portfolio"):
        umami.stats(FakeRunner(), "Gravity", "7d", now=NOW)


def test_homelab_site_reachable_by_name():
    r = umami.stats(FakeRunner(), "homelab events", "7d", now=NOW)
    assert r["sites"][0]["website_id"] == HOMELAB


def test_format_stats_text():
    text = umami.format_stats_text(umami.stats(FakeRunner(), "all", "7d", now=NOW))
    assert "Portfolio (portfolio.chrislawrence.ca): 120 pageviews (+20.0%), 40 visitors (new)" in text
    assert "Top pages: / 80, /projects 40" in text
    assert "No traffic: Econ" in text
    assert "All sites:" in text
    assert "\u2014" not in text


# --- homelab events -------------------------------------------------------


def test_homelab_events():
    run = FakeRunner()
    r = umami.homelab_events(run, "24h", event="backup_completed", now=NOW)
    assert r["site"] == "Homelab events"
    assert r["counts"] == [{"name": "backup_completed", "count": 7, "last_at": NOW.isoformat()}]
    assert all(p["event"] == "backup_completed" for sql, p in run.calls if "event" in p)
    text = umami.format_events_text(r)
    assert "backup_completed: 7" in text and "[service=umami, size=4.2M]" in text


def test_homelab_events_missing_site(monkeypatch):
    monkeypatch.setenv("UMAMI_HOMELAB_DOMAIN", "nowhere.example")
    no_homelab = [w for w in WEBSITES if w["website_id"] != HOMELAB]
    with pytest.raises(umami.UmamiNotFound):
        umami.homelab_events(lambda sql, p: no_homelab, "7d", now=NOW)


# --- Core router ----------------------------------------------------------


def _app(monkeypatch, runner: FakeRunner | None = None) -> FastAPI:
    run = runner or FakeRunner()

    @contextmanager
    def fake_session(dsn):
        assert dsn == "postgresql://umami_ro:x@umami-db:5432/umami"
        yield run

    monkeypatch.setenv("UMAMI_DB_URL", "postgresql://umami_ro:x@umami-db:5432/umami")
    monkeypatch.setattr(analytics, "_session", fake_session)
    app = FastAPI()
    app.include_router(analytics.router)
    return app


def test_router_stats_and_errors(monkeypatch):
    client = TestClient(_app(monkeypatch))
    r = client.get("/analytics/umami/stats", params={"site": "Portfolio", "period": "30d"})
    assert r.status_code == 200
    body = r.json()
    assert body["period"] == "30d" and body["sites"][0]["pageviews"] == 120
    assert body["summary"].startswith("Umami, last 30d")

    assert client.get("/analytics/umami/stats", params={"site": "Nope"}).status_code == 404
    assert client.get("/analytics/umami/stats", params={"period": "forever"}).status_code == 400
    assert client.get("/analytics/umami/stats", params={"limit": 99}).status_code == 422

    ev = client.get("/analytics/umami/events", params={"period": "7d"})
    assert ev.status_code == 200 and "backup_completed" in ev.json()["summary"]


def test_router_unconfigured(monkeypatch):
    monkeypatch.delenv("UMAMI_DB_URL", raising=False)
    app = FastAPI()
    app.include_router(analytics.router)
    r = TestClient(app).get("/analytics/umami/stats")
    assert r.status_code == 503 and "UMAMI_DB_URL" in r.json()["detail"]


def test_router_db_error_is_502(monkeypatch):
    def boom(sql, params):
        raise RuntimeError("connection refused")

    r = TestClient(_app(monkeypatch, boom)).get("/analytics/umami/stats")
    assert r.status_code == 502 and "connection refused" in r.json()["detail"]


# --- chat tools -----------------------------------------------------------


def test_chat_tools_register_only_when_configured(monkeypatch):
    monkeypatch.delenv("UMAMI_DB_URL", raising=False)
    assert umami_tool.register_if_configured() is False
    assert registry.get("umami_stats") is None

    monkeypatch.setenv("UMAMI_DB_URL", "postgresql://x")
    assert umami_tool.register_if_configured() is True
    assert registry.get("umami_stats") is not None
    assert registry.get("umami_events") is not None


def test_chat_tool_end_to_end(monkeypatch):
    app = _app(monkeypatch)
    real_client = httpx.AsyncClient

    def asgi_client(*args, **kwargs):
        kwargs["transport"] = httpx.ASGITransport(app=app)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(umami_tool.httpx, "AsyncClient", asgi_client)
    monkeypatch.setattr(umami_tool, "_core_url", lambda: "http://core")
    umami_tool.register_if_configured()

    _, stats_handler = registry.get("umami_stats")
    ok = asyncio.run(stats_handler({"site": "Portfolio", "period": "7d"}))
    assert not ok.is_error and "120 pageviews" in ok.content

    bad = asyncio.run(stats_handler({"site": "Nope"}))
    assert bad.is_error and "HTTP 404" in bad.content and "no Umami website" in bad.content

    _, events_handler = registry.get("umami_events")
    ev = asyncio.run(events_handler({"period": "24h", "event": "backup_completed"}))
    assert not ev.is_error and "backup_completed: 7" in ev.content


# --- MCP ------------------------------------------------------------------


def test_mcp_tools_registered_and_cataloged():
    from zeus.mcp.catalog import MCP_TOOLS
    from zeus.mcp.server import mcp

    names = {t.name for t in asyncio.run(mcp.list_tools())}
    assert {"umami_stats", "umami_events"} <= names
    assert {"umami_stats", "umami_events"} <= {t.name for t in MCP_TOOLS}
