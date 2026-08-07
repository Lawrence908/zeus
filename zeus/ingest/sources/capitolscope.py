# zeus/ingest/sources/capitolscope.py - CapitolScope Signals API → Pheme news layer.
#
# Pulls the structured congressional-trading context pack (headline, sector
# rotation, notable trades, herding clusters, scrutiny movers) and yields one
# Chunk per signal with NewsItem fields in metadata. target="news" routes to
# NewsStore (zeus_news). Trades and clusters get stable source_ids so daily
# re-ingest upserts in place; window-shaped items (headline, sector rotation,
# scrutiny movers) are keyed by window end date and age out via retention.
#
# Config (env, interpolated via zeus/ingest/config.yaml):
#   CAPITOLSCOPE_SIGNALS_URL   e.g. https://capitolscope.chrislawrence.ca
#   CAPITOLSCOPE_SIGNALS_KEY   Signals API key (X-API-Key header)
from __future__ import annotations

import logging
import os
import re
from typing import Any, AsyncIterator

import httpx

from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.capitolscope")

_ID_SAFE_RE = re.compile(r"[^a-z0-9]+")


def _slug(value: str) -> str:
    return _ID_SAFE_RE.sub("-", value.strip().lower()).strip("-") or "unknown"


def _usd(amount: Any) -> str:
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "?"
    if n >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n / 1_000:.0f}K"
    return f"${n:.0f}"


class CapitolScopeNewsSource:
    """Fetch the CapitolScope signals context pack as structured news items."""

    target = "news"

    def __init__(
        self,
        *,
        api_url: str | None = None,
        api_key: str | None = None,
        days_back: int = 2,
        user_id: str = "user",
    ) -> None:
        self.api_url = (
            api_url or os.getenv("CAPITOLSCOPE_SIGNALS_URL", "")
        ).rstrip("/")
        self.api_key = api_key or os.getenv("CAPITOLSCOPE_SIGNALS_KEY", "")
        self.days_back = max(1, days_back)
        self.user_id = user_id
        if not self.api_url:
            raise ValueError("capitolscope: CAPITOLSCOPE_SIGNALS_URL not set")
        if not self.api_key:
            raise ValueError("capitolscope: CAPITOLSCOPE_SIGNALS_KEY not set")

    async def _fetch_pack(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.get(
                f"{self.api_url}/api/v1/signals/context-pack",
                params={"days": self.days_back},
                headers={"X-API-Key": self.api_key},
            )
            r.raise_for_status()
            body = r.json() or {}
            data = body.get("data", body)
            return data if isinstance(data, dict) else {}

    async def chunks(self) -> AsyncIterator[Chunk]:
        pack = await self._fetch_pack()
        window = pack.get("this_week") or {}
        w_start = str(window.get("start", ""))
        w_end = str(window.get("end", ""))
        published = f"{w_end}T00:00:00+00:00" if w_end else ""

        def chunk(source_id: str, title: str, text: str, *,
                  entities: list[str], topics: list[str]) -> Chunk:
            return Chunk(
                text=text,
                source=f"capitolscope:{source_id}",
                metadata={
                    "title": title,
                    "published_at": published,
                    "entities": [e for e in entities if e],
                    "topics": ["congressional-trading", *topics],
                },
                user_id=self.user_id,
            )

        emitted = 0

        headline = pack.get("headline") or {}
        if headline.get("tickers_active"):
            rotation = pack.get("sector_rotation") or []
            rot_lines = "; ".join(
                f"{s.get('sector')}: {s.get('trend', '')} ({_usd(s.get('net_notional'))} net)"
                for s in rotation[:5]
                if isinstance(s, dict)
            )
            text = (
                f"Congressional trading window {w_start} to {w_end}: "
                f"{headline.get('tickers_active')} active tickers, "
                f"{headline.get('buys')} buys vs {headline.get('sells')} sells "
                f"({_usd(headline.get('notional'))} notional, bias {headline.get('net_bias')}), "
                f"{headline.get('new_tickers_vs_prior')} newly active tickers vs prior window."
            )
            if rot_lines:
                text += f" Sector rotation: {rot_lines}."
            yield chunk(
                f"window:{w_end}:headline",
                f"Congressional trading headline {w_end}",
                text,
                entities=[str(s.get("sector", "")) for s in rotation[:5] if isinstance(s, dict)],
                topics=["sector-rotation"],
            )
            emitted += 1

        for trade in pack.get("notable_trades") or []:
            if not isinstance(trade, dict):
                continue
            member = str(trade.get("member", "") or "")
            ticker = str(trade.get("ticker", "") or "")
            direction = str(trade.get("direction", "") or "")
            tdate = str(trade.get("transaction_date", "") or "")
            if not member or not ticker:
                continue
            lag = trade.get("disclosure_lag_days")
            text = (
                f"{member} ({trade.get('party')}-{trade.get('chamber')}) "
                f"{direction} {_usd(trade.get('amount'))} of {ticker} "
                f"({trade.get('sector')}) on {tdate}, disclosed {trade.get('disclosed_date')}"
                + (f", {lag}d disclosure lag" if lag is not None else "")
                + "."
            )
            yield chunk(
                f"trade:{_slug(member)}:{ticker}:{tdate}:{_slug(direction)}",
                f"{member} {direction} {ticker}",
                text,
                entities=[member, ticker, str(trade.get("sector", ""))],
                topics=["notable-trade"],
            )
            emitted += 1

        for cluster in pack.get("notable_clusters") or []:
            if not isinstance(cluster, dict):
                continue
            ticker = str(cluster.get("ticker", "") or "")
            direction = str(cluster.get("direction", "") or "")
            c_start = str(cluster.get("window_start", "") or "")
            members = [str(m) for m in cluster.get("members") or []]
            if not ticker:
                continue
            text = (
                f"Herding cluster: {cluster.get('member_count')} members "
                f"({', '.join(members)}) {direction} {ticker} within "
                f"{cluster.get('span_days')} days starting {c_start}, "
                f"{_usd(cluster.get('total_notional'))} total notional, "
                f"lead {cluster.get('lead_member')} on {cluster.get('lead_date')}."
            )
            yield chunk(
                f"cluster:{ticker}:{c_start}:{_slug(direction)}",
                f"Cluster {direction} {ticker}",
                text,
                entities=[ticker, *members],
                topics=["herding-cluster"],
            )
            emitted += 1

        movers = [m for m in pack.get("scrutiny_movers") or [] if isinstance(m, dict)]
        if movers:
            lines = "; ".join(
                f"{m.get('member')} ({m.get('party')}-{m.get('chamber')}) "
                f"score {m.get('scrutiny_score')} ({m.get('leading_factor')})"
                for m in movers[:10]
            )
            yield chunk(
                f"window:{w_end}:scrutiny",
                f"Scrutiny movers {w_end}",
                f"Members most worth scrutiny in window {w_start} to {w_end}: {lines}.",
                entities=[str(m.get("member", "")) for m in movers[:10]],
                topics=["scrutiny"],
            )
            emitted += 1

        logger.info("capitolscope: emitted %d signal item(s) for window %s..%s", emitted, w_start, w_end)
