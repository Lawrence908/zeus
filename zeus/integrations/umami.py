# zeus/integrations/umami.py: Read-only Umami analytics queries (SQL + result shaping)
#
# Stdlib only, and deliberately driver-agnostic: every query goes through a
# `Runner`, a callable `(sql, params) -> list[dict]`. zeus-core supplies a
# psycopg runner (zeus/core/analytics.py) over UMAMI_DB_URL; the monthly digest
# in services/umami/scripts/monthly-digest.py loads this file by path and
# supplies a `docker exec umami-db psql` runner. Keeping the SQL here means the
# chat tool, the MCP tool and the digest can never disagree about what a
# "visitor" is.
#
# SQL uses psycopg pyformat placeholders (%(name)s) with explicit casts, so the
# same text binds server-side under psycopg and maps 1:1 onto psql's quoted
# :'name' variables. Never interpolate values into the SQL string.
#
# Definitions (match the Umami dashboard closely enough to sanity-check):
#   pageviews = website_event rows with event_type 1
#   visitors  = distinct session_id over all events in the window
#   visits    = distinct visit_id over all events in the window
#   events    = website_event rows with event_type 2 (custom events)
# Soft-deleted websites (deleted_at set) are always excluded.
from __future__ import annotations

import os
import re
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

Runner = Callable[[str, dict[str, Any]], list[dict[str, Any]]]

PAGEVIEW = 1
CUSTOM_EVENT = 2

_METRICS = ("pageviews", "visitors", "visits", "events")
_PERIOD_RE = re.compile(r"^\s*(\d{1,4})\s*([hdw])\s*$", re.IGNORECASE)
_PERIOD_UNITS = {"h": "hours", "d": "days", "w": "weeks"}
_MAX_PERIOD = timedelta(days=366)


class UmamiError(ValueError):
    """Bad input (unknown site, unparseable period). Safe to show the caller."""


class UmamiNotFound(UmamiError):
    """The requested website does not exist or is soft-deleted."""


def homelab_domain() -> str:
    """Domain of the server-side "Homelab events" website (umami-event.sh)."""
    return (os.getenv("UMAMI_HOMELAB_DOMAIN", "") or "daedalus.homelab").strip().lower()


def parse_period(period: str) -> timedelta:
    """'24h' / '7d' / '4w' -> timedelta. Bounded to 1h..366d."""
    m = _PERIOD_RE.match(period or "")
    if not m:
        raise UmamiError(f"period must look like 24h, 7d or 4w, got {period!r}")
    delta = timedelta(**{_PERIOD_UNITS[m.group(2).lower()]: int(m.group(1))})
    if delta < timedelta(hours=1) or delta > _MAX_PERIOD:
        raise UmamiError(f"period must be between 1h and 366d, got {period!r}")
    return delta


# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------

SQL_WEBSITES = """
SELECT website_id::text AS website_id, name, coalesce(domain, '') AS domain
FROM website
WHERE deleted_at IS NULL
ORDER BY name
"""

# Current and previous window in one scan; the WHERE covers both.
SQL_TOTALS = """
SELECT
  count(*) FILTER (WHERE created_at >= %(start)s::timestamptz AND event_type = 1) AS pageviews,
  count(DISTINCT session_id) FILTER (WHERE created_at >= %(start)s::timestamptz) AS visitors,
  count(DISTINCT visit_id) FILTER (WHERE created_at >= %(start)s::timestamptz) AS visits,
  count(*) FILTER (WHERE created_at >= %(start)s::timestamptz AND event_type = 2) AS events,
  count(*) FILTER (WHERE created_at < %(start)s::timestamptz AND event_type = 1) AS prev_pageviews,
  count(DISTINCT session_id) FILTER (WHERE created_at < %(start)s::timestamptz) AS prev_visitors,
  count(DISTINCT visit_id) FILTER (WHERE created_at < %(start)s::timestamptz) AS prev_visits,
  count(*) FILTER (WHERE created_at < %(start)s::timestamptz AND event_type = 2) AS prev_events
FROM website_event
WHERE website_id = %(website_id)s::uuid
  AND created_at >= %(prev_start)s::timestamptz
  AND created_at < %(end)s::timestamptz
"""

# Top pages (pageviews), top referrers (distinct sessions, own domain excluded)
# and top custom events, one round trip.
SQL_TOPS = """
(SELECT 'page' AS kind, url_path AS label, count(*) AS n
   FROM website_event
  WHERE website_id = %(website_id)s::uuid
    AND created_at >= %(start)s::timestamptz AND created_at < %(end)s::timestamptz
    AND event_type = 1
  GROUP BY url_path
  ORDER BY n DESC, label
  LIMIT %(limit)s::int)
UNION ALL
(SELECT 'referrer' AS kind, referrer_domain AS label, count(DISTINCT session_id) AS n
   FROM website_event
  WHERE website_id = %(website_id)s::uuid
    AND created_at >= %(start)s::timestamptz AND created_at < %(end)s::timestamptz
    AND event_type = 1
    AND coalesce(referrer_domain, '') <> ''
    AND lower(referrer_domain) <> lower(%(domain)s::text)
    AND lower(referrer_domain) <> 'www.' || lower(%(domain)s::text)
  GROUP BY referrer_domain
  ORDER BY n DESC, label
  LIMIT %(limit)s::int)
UNION ALL
(SELECT 'event' AS kind, event_name AS label, count(*) AS n
   FROM website_event
  WHERE website_id = %(website_id)s::uuid
    AND created_at >= %(start)s::timestamptz AND created_at < %(end)s::timestamptz
    AND event_type = 2
    AND coalesce(event_name, '') <> ''
  GROUP BY event_name
  ORDER BY n DESC, label
  LIMIT %(limit)s::int)
"""

# Empty %(event)s means "all event names".
SQL_EVENT_COUNTS = """
SELECT event_name, count(*) AS n, max(created_at) AS last_at
FROM website_event
WHERE website_id = %(website_id)s::uuid
  AND created_at >= %(start)s::timestamptz AND created_at < %(end)s::timestamptz
  AND event_type = 2
  AND (%(event)s::text = '' OR event_name = %(event)s::text)
GROUP BY event_name
ORDER BY n DESC, event_name
"""

SQL_RECENT_EVENTS = """
SELECT e.created_at, e.event_name, e.url_path,
       coalesce(string_agg(
         d.data_key || '=' || coalesce(d.string_value, trim_scale(d.number_value)::text,
                                       d.date_value::text, ''),
         ', ' ORDER BY d.data_key), '') AS data
FROM website_event e
LEFT JOIN event_data d
  ON d.website_event_id = e.event_id AND d.website_id = e.website_id
WHERE e.website_id = %(website_id)s::uuid
  AND e.created_at >= %(start)s::timestamptz AND e.created_at < %(end)s::timestamptz
  AND e.event_type = 2
  AND (%(event)s::text = '' OR e.event_name = %(event)s::text)
GROUP BY e.event_id, e.created_at, e.event_name, e.url_path
ORDER BY e.created_at DESC
LIMIT %(limit)s::int
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _int(v: Any) -> int:
    # psycopg returns ints; the psql CSV runner returns strings ("" for NULL).
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


def _iso(v: Any) -> str:
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).isoformat(timespec="seconds")
    return str(v or "")


def _pct(cur: int, prev: int) -> float | None:
    if prev == 0:
        return None
    return round((cur - prev) / prev * 100.0, 1)


def _utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def list_websites(run: Runner) -> list[dict[str, str]]:
    return [
        {"website_id": str(r["website_id"]), "name": str(r["name"]), "domain": str(r["domain"] or "")}
        for r in run(SQL_WEBSITES, {})
    ]


def resolve_sites(run: Runner, site: str = "all") -> list[dict[str, str]]:
    """'all' -> every live website except the Homelab events one; otherwise
    match one website by name, domain or website_id (case-insensitive)."""
    sites = list_websites(run)
    key = (site or "all").strip().lower()
    if key == "all":
        return [s for s in sites if s["domain"].lower() != homelab_domain()]
    for s in sites:
        if key in (s["name"].lower(), s["domain"].lower(), s["website_id"].lower()):
            return [s]
    names = ", ".join(s["name"] for s in sites) or "none"
    raise UmamiNotFound(f"no Umami website matches {site!r}; available: {names}")


def homelab_site(run: Runner) -> dict[str, str]:
    for s in list_websites(run):
        if s["domain"].lower() == homelab_domain() or s["name"].lower() == "homelab events":
            return s
    raise UmamiNotFound(
        f"no Umami website with domain {homelab_domain()!r} (the 'Homelab events' site)"
    )


def _metrics_block(cur: dict[str, int], prev: dict[str, int]) -> dict[str, Any]:
    return {
        **cur,
        "previous": prev,
        "change_pct": {k: _pct(cur[k], prev[k]) for k in _METRICS},
    }


# ---------------------------------------------------------------------------
# Public query API
# ---------------------------------------------------------------------------


def site_stats(
    run: Runner,
    site: dict[str, str],
    start: datetime,
    end: datetime,
    prev_start: datetime,
    *,
    limit: int = 5,
) -> dict[str, Any]:
    params = {
        "website_id": site["website_id"],
        "domain": site["domain"],
        "start": _utc(start),
        "end": _utc(end),
        "prev_start": _utc(prev_start),
        "limit": max(1, min(25, int(limit))),
    }
    rows = run(SQL_TOTALS, params)
    row = rows[0] if rows else {}
    cur = {k: _int(row.get(k)) for k in _METRICS}
    prev = {k: _int(row.get(f"prev_{k}")) for k in _METRICS}

    tops: dict[str, list[dict[str, Any]]] = {"page": [], "referrer": [], "event": []}
    if cur["pageviews"] or cur["events"]:
        for r in run(SQL_TOPS, params):
            tops.setdefault(str(r["kind"]), []).append({"label": str(r["label"]), "count": _int(r["n"])})

    return {
        "name": site["name"],
        "domain": site["domain"],
        "website_id": site["website_id"],
        **_metrics_block(cur, prev),
        "top_pages": [{"path": t["label"], "pageviews": t["count"]} for t in tops["page"]],
        "top_referrers": [{"domain": t["label"], "visitors": t["count"]} for t in tops["referrer"]],
        "top_events": [{"name": t["label"], "count": t["count"]} for t in tops["event"]],
    }


def stats_between(
    run: Runner,
    site: str,
    start: datetime,
    end: datetime,
    prev_start: datetime,
    *,
    limit: int = 5,
) -> dict[str, Any]:
    """Stats for [start, end) compared with [prev_start, start)."""
    start, end, prev_start = _utc(start), _utc(end), _utc(prev_start)
    if not (prev_start <= start < end):
        raise UmamiError("windows must satisfy prev_start <= start < end")
    sites = resolve_sites(run, site)
    per_site = [site_stats(run, s, start, end, prev_start, limit=limit) for s in sites]
    cur = {k: sum(s[k] for s in per_site) for k in _METRICS}
    prev = {k: sum(s["previous"][k] for s in per_site) for k in _METRICS}
    return {
        "site": site,
        "start": _iso(_utc(start)),
        "end": _iso(_utc(end)),
        "previous_start": _iso(_utc(prev_start)),
        "sites": per_site,
        "totals": _metrics_block(cur, prev),
    }


def stats(
    run: Runner,
    site: str = "all",
    period: str = "7d",
    *,
    limit: int = 5,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Rolling-window stats: the last `period` vs the `period` before it."""
    delta = parse_period(period)
    end = _utc(now or datetime.now(timezone.utc))
    result = stats_between(run, site, end - delta, end, end - 2 * delta, limit=limit)
    result["period"] = period.strip().lower()
    return result


def homelab_events_between(
    run: Runner,
    start: datetime,
    end: datetime,
    *,
    event: str = "",
    limit: int = 20,
) -> dict[str, Any]:
    site = homelab_site(run)
    params = {
        "website_id": site["website_id"],
        "start": _utc(start),
        "end": _utc(end),
        "event": (event or "").strip(),
        "limit": max(1, min(100, int(limit))),
    }
    counts = [
        {"name": str(r["event_name"]), "count": _int(r["n"]), "last_at": _iso(r["last_at"])}
        for r in run(SQL_EVENT_COUNTS, params)
    ]
    recent = [
        {
            "at": _iso(r["created_at"]),
            "name": str(r["event_name"] or ""),
            "path": str(r["url_path"] or ""),
            "data": str(r["data"] or ""),
        }
        for r in run(SQL_RECENT_EVENTS, params)
    ]
    return {
        "site": site["name"],
        "event": params["event"],
        "start": _iso(params["start"]),
        "end": _iso(params["end"]),
        "counts": counts,
        "recent": recent,
    }


def homelab_events(
    run: Runner,
    period: str = "7d",
    *,
    event: str = "",
    limit: int = 20,
    now: datetime | None = None,
) -> dict[str, Any]:
    delta = parse_period(period)
    end = _utc(now or datetime.now(timezone.utc))
    result = homelab_events_between(run, end - delta, end, event=event, limit=limit)
    result["period"] = period.strip().lower()
    return result


# ---------------------------------------------------------------------------
# Plain-text rendering (chat tool, MCP summary, monthly digest)
# ---------------------------------------------------------------------------


def _change(cur: int, pct: float | None) -> str:
    if pct is None:
        return " (new)" if cur else ""
    return f" ({pct:+.1f}%)"


def _metric_line(block: dict[str, Any]) -> str:
    ch = block["change_pct"]
    return (
        f"{block['pageviews']} pageviews{_change(block['pageviews'], ch['pageviews'])}, "
        f"{block['visitors']} visitors{_change(block['visitors'], ch['visitors'])}, "
        f"{block['visits']} visits, "
        f"{block['events']} events{_change(block['events'], ch['events'])}"
    )


def format_stats_text(result: dict[str, Any], *, title: str | None = None) -> str:
    if title is None:
        title = (
            f"Umami, last {result.get('period', '')} ({result['start']} to {result['end']}), "
            "change vs the previous period"
        )
    lines = [title]
    idle: list[str] = []
    for s in result["sites"]:
        if not any(s[k] or s["previous"][k] for k in _METRICS):
            idle.append(s["name"])
            continue
        lines.append("")
        lines.append(f"{s['name']} ({s['domain']}): {_metric_line(s)}")
        if s["top_pages"]:
            lines.append("  Top pages: " + ", ".join(f"{p['path']} {p['pageviews']}" for p in s["top_pages"]))
        if s["top_referrers"]:
            lines.append(
                "  Top referrers: " + ", ".join(f"{r['domain']} {r['visitors']}" for r in s["top_referrers"])
            )
        if s["top_events"]:
            lines.append("  Top events: " + ", ".join(f"{e['name']} {e['count']}" for e in s["top_events"]))
    if len(result["sites"]) > 1:
        lines.append("")
        lines.append(f"All sites: {_metric_line(result['totals'])}")
    if idle:
        lines.append(f"No traffic: {', '.join(idle)}")
    return "\n".join(lines)


def format_events_text(result: dict[str, Any], *, title: str | None = None) -> str:
    if title is None:
        scope = f" '{result['event']}'" if result.get("event") else ""
        title = f"{result['site']}{scope}, last {result.get('period', '')} ({result['start']} to {result['end']})"
    lines = [title]
    if not result["counts"]:
        lines.append("No events recorded in this window.")
        return "\n".join(lines)
    lines.extend(f"- {c['name']}: {c['count']} (last {c['last_at']})" for c in result["counts"])
    if result["recent"]:
        lines.append("Recent:")
        for e in result["recent"]:
            data = f" [{e['data']}]" if e["data"] else ""
            lines.append(f"  {e['at']} {e['name']}{data}")
    return "\n".join(lines)
