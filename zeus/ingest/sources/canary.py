# zeus/ingest/sources/canary.py - Canary OSINT platform → Pheme news layer.
#
# Pulls processed articles from the Canary API (JWT login as a dedicated
# analyst service account) and yields one Chunk per article with NewsItem
# fields in metadata. target="news" routes them to NewsStore (zeus_news);
# deterministic point ids there make re-ingest idempotent.
#
# Config (env, interpolated via zeus/ingest/config.yaml):
#   CANARY_API_URL   e.g. http://127.0.0.1:8126
#   CANARY_EMAIL     service account email (analyst role)
#   CANARY_PASSWORD  service account password
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

import httpx

from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.canary")

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# GDELT items often carry filename-shaped titles ("article 29079025 64b2 ... .html").
# The URL path usually holds the real slug; recover the headline from there.
_FILENAME_TITLE_RE = re.compile(r"^article[ _-][0-9a-f]{4,}.*(\.html?)?$", re.IGNORECASE)
_SLUG_JUNK_RE = re.compile(r"^(article|news|story|index|ap[_-]news)[_-]?", re.IGNORECASE)


def _strip_html(text: str) -> str:
    return _WS_RE.sub(" ", _TAG_RE.sub(" ", text)).strip()


def _title_from_url(url: str) -> str:
    """Best-effort headline from the URL slug when the source title is a filename."""
    try:
        path = url.split("?", 1)[0].rstrip("/").split("/")
    except Exception:
        return ""
    for segment in reversed(path):
        seg = segment.strip().lower()
        if not seg:
            continue
        seg = re.sub(r"\.html?$", "", seg)
        seg = re.sub(r"^\d+\.", "", seg)  # numeric story-id prefix ("26410899.")
        if _SLUG_JUNK_RE.match(seg) or "." in seg or len(seg) < 12:
            continue
        words = [w for w in seg.replace("_", "-").split("-") if w]
        alpha_words = [
            w for w in words
            if w.isalpha() and not all(c in "0123456789abcdef" for c in w)
        ]
        if len(alpha_words) >= 3 and len(alpha_words) >= 0.6 * len(words):
            return " ".join(words).capitalize()
    return ""


def _clean_title(title: str, url: str) -> str:
    t = title.strip()
    if t.lower().startswith(("http://", "https://")):
        # Some feeds put the article URL in the title field; recover from
        # whichever URL has a usable slug.
        return _title_from_url(t) or _title_from_url(url) or ""
    if _FILENAME_TITLE_RE.match(t):
        return _title_from_url(url) or ""
    return title


class CanaryNewsSource:
    """Fetch processed Canary articles as news items."""

    target = "news"

    def __init__(
        self,
        *,
        api_url: str | None = None,
        email: str | None = None,
        password: str | None = None,
        days_back: int = 3,
        limit: int = 200,
        user_id: str = "user",
    ) -> None:
        self.api_url = (api_url or os.getenv("CANARY_API_URL", "")).rstrip("/")
        self.email = email or os.getenv("CANARY_EMAIL", "")
        self.password = password or os.getenv("CANARY_PASSWORD", "")
        self.days_back = max(1, days_back)
        self.limit = max(1, min(limit, 200))  # Canary caps limit at 200
        self.user_id = user_id
        if not self.api_url:
            raise ValueError("canary: CANARY_API_URL not set")
        if not self.email or not self.password:
            raise ValueError("canary: CANARY_EMAIL / CANARY_PASSWORD not set")

    async def _login(self, client: httpx.AsyncClient) -> str:
        r = await client.post(
            f"{self.api_url}/auth/login",
            json={"email": self.email, "password": self.password},
        )
        r.raise_for_status()
        token = (r.json() or {}).get("access_token", "")
        if not token:
            raise RuntimeError("canary login returned no access_token")
        return token

    async def _fetch_articles(self, client: httpx.AsyncClient, token: str) -> list[dict]:
        date_from = (
            datetime.now(timezone.utc) - timedelta(days=self.days_back)
        ).isoformat()
        articles: list[dict] = []
        offset = 0
        while len(articles) < self.limit:
            page = min(self.limit - len(articles), 100)
            r = await client.get(
                f"{self.api_url}/articles",
                params={
                    "status": "processed",
                    "date_from": date_from,
                    "limit": page,
                    "offset": offset,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            r.raise_for_status()
            batch = r.json() or []
            if not isinstance(batch, list) or not batch:
                break
            articles.extend(batch)
            if len(batch) < page:
                break
            offset += len(batch)
        return articles

    async def chunks(self) -> AsyncIterator[Chunk]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            token = await self._login(client)
            articles = await self._fetch_articles(client, token)

        logger.info("canary: %d processed article(s) in last %dd", len(articles), self.days_back)
        for art in articles:
            art_id = str(art.get("id", "")).strip()
            url = str(art.get("url", "") or "")
            title = _clean_title(_strip_html(str(art.get("title", "") or "")), url)
            summary = _strip_html(str(art.get("summary", "") or ""))
            text = summary or title
            if not art_id or not text:
                continue
            yield Chunk(
                text=text,
                source=f"canary:{art_id}",
                metadata={
                    "title": title,
                    "url": url,
                    "published_at": str(
                        art.get("published_at") or art.get("fetched_at") or ""
                    ),
                    "bias": str(art.get("full_grade", "") or ""),
                    "canary_source": str(art.get("source_name", "") or ""),
                },
                user_id=self.user_id,
            )
