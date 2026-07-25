# zeus/core/tools/current_time.py — Report the current wall-clock time
#
# Fixes the "it's currently 14:37" hallucination: without this tool the chat
# LLM has no clock access and will happily invent a time. cacheable=False
# is not negotiable — the result changes every second by definition.
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.current_time")


def _default_timezone() -> str:
    # ZEUS_DEFAULT_TIMEZONE lets ops pin the "local" interpretation without
    # relying on the container TZ env. Falls back to UTC which is always safe.
    return (os.getenv("ZEUS_DEFAULT_TIMEZONE", "") or "UTC").strip() or "UTC"


# Small hand-written map for the long tail of "user types a place name and
# the model should be able to copy it in verbatim". The model is reliably
# better at copying than at recalling the right IANA string. Keys are
# lowercased; resolution is exact match first, then a few normalisation
# rules (strip "the ", spaces ↔ underscores, common misspellings).
#
# This is not exhaustive — it covers what comes up in everyday chat. For
# anything missing the tool falls back to scanning all available IANA names
# with a forgiving substring match.
_LOCATION_MAP: dict[str, str] = {
    # Canada / US
    "vancouver": "America/Vancouver",
    "victoria": "America/Vancouver",
    "seattle": "America/Los_Angeles",
    "portland": "America/Los_Angeles",
    "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "san francisco": "America/Los_Angeles",
    "sf": "America/Los_Angeles",
    "pacific time": "America/Los_Angeles",
    "pst": "America/Los_Angeles",
    "pdt": "America/Los_Angeles",
    "denver": "America/Denver",
    "salt lake city": "America/Denver",
    "mountain time": "America/Denver",
    "mst": "America/Denver",
    "mdt": "America/Denver",
    "chicago": "America/Chicago",
    "houston": "America/Chicago",
    "central time": "America/Chicago",
    "cst": "America/Chicago",
    "cdt": "America/Chicago",
    "new york": "America/New_York",
    "nyc": "America/New_York",
    "boston": "America/New_York",
    "washington": "America/New_York",
    "dc": "America/New_York",
    "eastern time": "America/New_York",
    "est": "America/New_York",
    "edt": "America/New_York",
    "toronto": "America/Toronto",
    "montreal": "America/Toronto",
    "halifax": "America/Halifax",
    "calgary": "America/Edmonton",
    "edmonton": "America/Edmonton",
    "winnipeg": "America/Winnipeg",
    "mexico city": "America/Mexico_City",
    # Europe
    "london": "Europe/London",
    "uk": "Europe/London",
    "england": "Europe/London",
    "ireland": "Europe/Dublin",
    "dublin": "Europe/Dublin",
    "paris": "Europe/Paris",
    "france": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "germany": "Europe/Berlin",
    "amsterdam": "Europe/Amsterdam",
    "netherlands": "Europe/Amsterdam",
    "madrid": "Europe/Madrid",
    "spain": "Europe/Madrid",
    "rome": "Europe/Rome",
    "italy": "Europe/Rome",
    "lisbon": "Europe/Lisbon",
    "portugal": "Europe/Lisbon",
    "athens": "Europe/Athens",
    "greece": "Europe/Athens",
    "warsaw": "Europe/Warsaw",
    "poland": "Europe/Warsaw",
    "stockholm": "Europe/Stockholm",
    "sweden": "Europe/Stockholm",
    "oslo": "Europe/Oslo",
    "norway": "Europe/Oslo",
    "copenhagen": "Europe/Copenhagen",
    "denmark": "Europe/Copenhagen",
    "helsinki": "Europe/Helsinki",
    "finland": "Europe/Helsinki",
    "moscow": "Europe/Moscow",
    "russia": "Europe/Moscow",
    "istanbul": "Europe/Istanbul",
    "turkey": "Europe/Istanbul",
    # Middle East / Africa
    "tel aviv": "Asia/Jerusalem",
    "jerusalem": "Asia/Jerusalem",
    "israel": "Asia/Jerusalem",
    "dubai": "Asia/Dubai",
    "uae": "Asia/Dubai",
    "abu dhabi": "Asia/Dubai",
    "riyadh": "Asia/Riyadh",
    "saudi arabia": "Asia/Riyadh",
    "cairo": "Africa/Cairo",
    "egypt": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "south africa": "Africa/Johannesburg",
    "lagos": "Africa/Lagos",
    "nigeria": "Africa/Lagos",
    "nairobi": "Africa/Nairobi",
    "kenya": "Africa/Nairobi",
    # Asia
    "delhi": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "india": "Asia/Kolkata",
    "ist": "Asia/Kolkata",
    "kathmandu": "Asia/Kathmandu",
    "nepal": "Asia/Kathmandu",
    "dhaka": "Asia/Dhaka",
    "bangladesh": "Asia/Dhaka",
    "colombo": "Asia/Colombo",
    "sri lanka": "Asia/Colombo",
    "bangkok": "Asia/Bangkok",
    "thailand": "Asia/Bangkok",
    "hanoi": "Asia/Bangkok",
    "vietnam": "Asia/Bangkok",
    "saigon": "Asia/Ho_Chi_Minh",
    "ho chi minh": "Asia/Ho_Chi_Minh",
    "ho chi minh city": "Asia/Ho_Chi_Minh",
    "kuala lumpur": "Asia/Kuala_Lumpur",
    "malaysia": "Asia/Kuala_Lumpur",
    "singapore": "Asia/Singapore",
    "manila": "Asia/Manila",
    "philippines": "Asia/Manila",
    "jakarta": "Asia/Jakarta",
    "indonesia": "Asia/Jakarta",
    "bali": "Asia/Makassar",
    "hong kong": "Asia/Hong_Kong",
    "hk": "Asia/Hong_Kong",
    "macau": "Asia/Macau",
    "taipei": "Asia/Taipei",
    "taiwan": "Asia/Taipei",
    "shanghai": "Asia/Shanghai",
    "beijing": "Asia/Shanghai",
    "china": "Asia/Shanghai",
    "shenzhen": "Asia/Shanghai",
    "guangzhou": "Asia/Shanghai",
    "tokyo": "Asia/Tokyo",
    "osaka": "Asia/Tokyo",
    "japan": "Asia/Tokyo",
    "jst": "Asia/Tokyo",
    "seoul": "Asia/Seoul",
    "south korea": "Asia/Seoul",
    "korea": "Asia/Seoul",
    "pyongyang": "Asia/Pyongyang",
    "north korea": "Asia/Pyongyang",
    "ulan bator": "Asia/Ulaanbaatar",
    "ulaanbaatar": "Asia/Ulaanbaatar",
    "mongolia": "Asia/Ulaanbaatar",
    # Oceania
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "brisbane": "Australia/Brisbane",
    "perth": "Australia/Perth",
    "adelaide": "Australia/Adelaide",
    "darwin": "Australia/Darwin",
    "hobart": "Australia/Hobart",
    "australia": "Australia/Sydney",
    "canberra": "Australia/Sydney",
    "auckland": "Pacific/Auckland",
    "wellington": "Pacific/Auckland",
    "new zealand": "Pacific/Auckland",
    "nz": "Pacific/Auckland",
    "fiji": "Pacific/Fiji",
    "suva": "Pacific/Fiji",
    "vanuatu": "Pacific/Efate",
    "port vila": "Pacific/Efate",
    "samoa": "Pacific/Apia",
    "apia": "Pacific/Apia",
    "tonga": "Pacific/Tongatapu",
    "tahiti": "Pacific/Tahiti",
    "papeete": "Pacific/Tahiti",
    "honolulu": "Pacific/Honolulu",
    "hawaii": "Pacific/Honolulu",
    "hst": "Pacific/Honolulu",
    "noumea": "Pacific/Noumea",
    "new caledonia": "Pacific/Noumea",
    "guam": "Pacific/Guam",
    # South America
    "sao paulo": "America/Sao_Paulo",
    "rio": "America/Sao_Paulo",
    "rio de janeiro": "America/Sao_Paulo",
    "brazil": "America/Sao_Paulo",
    "brasilia": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "argentina": "America/Argentina/Buenos_Aires",
    "santiago": "America/Santiago",
    "chile": "America/Santiago",
    "lima": "America/Lima",
    "peru": "America/Lima",
    "bogota": "America/Bogota",
    "colombia": "America/Bogota",
    "caracas": "America/Caracas",
    "venezuela": "America/Caracas",
    # Generic
    "utc": "UTC",
    "gmt": "Etc/GMT",
    "z": "UTC",
    "zulu": "UTC",
}


_PUNCT_RE = re.compile(r"[^\w\s/]")


def _normalize_location(s: str) -> str:
    s = s.strip().lower()
    s = _PUNCT_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s)
    if s.startswith("the "):
        s = s[4:]
    return s


def _resolve_location(loc: str) -> tuple[str | None, str | None]:
    """Map a free-text location to an IANA timezone name.

    Returns (iana_name, used_form). used_form is a short string we can show
    the user so they know how we interpreted their query. Returns
    (None, None) when nothing reasonable matches.
    """
    # The model often passes an already-IANA string into `location`
    # ("America/Vancouver", "Asia/Tokyo"). Try the raw input as a tz first —
    # if it's valid, we're done. Trim whitespace; preserve case (IANA is
    # case-sensitive).
    bare = loc.strip()
    if bare:
        try:
            ZoneInfo(bare)
            return bare, bare
        except ZoneInfoNotFoundError:
            pass

    norm = _normalize_location(loc)
    if not norm:
        return None, None

    if norm in _LOCATION_MAP:
        return _LOCATION_MAP[norm], norm

    # Try with underscores (matches IANA names like "New_York").
    alt = norm.replace(" ", "_")
    if alt in _LOCATION_MAP:
        return _LOCATION_MAP[alt], alt

    # Word-boundary match into the curated map keys (catches "vanuatu islands"
    # → "vanuatu" without matching the "la" inside "gibberishplace"). Prefer
    # longest matched key.
    tokens = set(norm.split())
    best_key: str | None = None
    for key in _LOCATION_MAP:
        key_tokens = key.split()
        if all(tok in tokens for tok in key_tokens):
            if best_key is None or len(key) > len(best_key):
                best_key = key
    if best_key is not None:
        return _LOCATION_MAP[best_key], best_key

    # Last resort: scan the full IANA list for a city-name suffix match.
    target = alt.title().replace(" ", "_")
    for tz in available_timezones():
        if tz.split("/")[-1].lower() == norm.replace(" ", "_"):
            return tz, tz
    for tz in available_timezones():
        if tz.endswith("/" + target):
            return tz, tz

    return None, None


_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "timezone": {
            "type": "string",
            "description": (
                "IANA timezone name (e.g. 'America/Vancouver', 'UTC'). "
                "Use this when you already know the exact IANA name."
            ),
        },
        "location": {
            "type": "string",
            "description": (
                "Free-text place name when the user asks about a specific "
                "city, country, or region (e.g. 'Vanuatu', 'Shanghai', "
                "'NYC', 'central time'). The server resolves this to an "
                "IANA timezone. Use this whenever the user names a place; "
                "prefer it over `timezone` because it's harder to misspell."
            ),
        },
        "format": {
            "type": "string",
            "enum": ["human", "iso", "unix"],
            "description": (
                "Output format. 'human' (default) = 24-hour clock with "
                "timezone abbreviation and weekday, e.g. "
                "'17:58:34 PDT on Thursday, April 23, 2026'. "
                "'iso' = ISO 8601 with UTC offset. "
                "'unix' = seconds since the epoch."
            ),
        },
    },
}


_SPEC = ToolSpec(
    name="current_time",
    description=(
        "Returns the current wall-clock date and time. You MUST call this "
        "tool whenever the user asks about the current time, date, day of "
        "the week, 'now', 'today', 'tonight', 'this morning', 'what time is "
        "it', or anything similar. Do NOT answer from memory, retrieval, or "
        "training data — the clock changes every second and only this tool "
        "has the real value. "
        "When the user names a specific place (city, country, region) you "
        "MUST pass `location` with that place name verbatim — the server "
        "resolves it to the right IANA timezone for you. Do NOT try to "
        "compute the offset yourself, do NOT call without `location` and "
        "then apologise about the wrong timezone; pass the place name on "
        "the FIRST call. Default output is human-friendly 24-hour format "
        "with timezone abbreviation; quote it verbatim in your reply."
    ),
    parameters=_SCHEMA,
    aegis_policy="tool_arguments",
    timeout_seconds=1.0,
    cacheable=False,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    fmt = str(args.get("format") or "human").strip().lower()

    # Resolution precedence: explicit `timezone` arg → resolved `location` →
    # server default. The model is encouraged to use `location`; `timezone`
    # remains for callers that already know the IANA name.
    tz_name: str | None = None
    resolved_via: str | None = None
    if args.get("timezone"):
        tz_name = str(args["timezone"]).strip() or None
    if not tz_name and args.get("location"):
        loc = str(args["location"]).strip()
        resolved, used = _resolve_location(loc)
        if resolved is None:
            return ToolResult(
                call_id="",
                name=_SPEC.name,
                content=(
                    f"Could not resolve location {loc!r} to a timezone. "
                    "Pass `timezone` as an IANA name (e.g. 'Pacific/Efate' "
                    "for Vanuatu)."
                ),
                is_error=True,
            )
        tz_name = resolved
        resolved_via = used

    if not tz_name:
        tz_name = _default_timezone()

    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return ToolResult(
            call_id="",
            name=_SPEC.name,
            content=(
                f"Unknown timezone {tz_name!r}. Use an IANA name like "
                "'America/Vancouver', 'Europe/London', or 'UTC'."
            ),
            is_error=True,
        )

    now = datetime.now(tz=timezone.utc).astimezone(tz)

    if fmt == "unix":
        body = f"{int(now.timestamp())}"
    elif fmt == "iso":
        body = now.isoformat(timespec="seconds")
    else:
        tz_abbr = now.strftime("%Z") or tz_name
        body = now.strftime(f"%H:%M:%S {tz_abbr} on %A, %B %-d, %Y")

    if resolved_via and resolved_via.lower() not in tz_name.lower():
        # Append a short trace so the model can quote both forms when useful.
        body = f"{body} ({tz_name})"

    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register() -> None:
    """Register current_time. Always available; no external dependency."""
    registry.register(_SPEC, _handler)
    logger.info("current_time registered (default tz=%s)", _default_timezone())
