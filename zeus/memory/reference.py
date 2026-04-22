# zeus/memory/reference.py — Phase 2 Reference layer (live external sources)
#
# Live HTTP proxies to external knowledge sources (kiwix ZIM server, NOMAD RAG).
# These are queried on-demand at chat time and are NEVER ingested. Failures are
# swallowed (empty list, WARN log) so reference outages cannot break a chat turn.
from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger("zeus.memory.reference")


@dataclass
class ReferenceHit:
    """One retrieved snippet from an external reference source."""

    text: str
    score: float
    source: str  # "kiwix" | "nomad"
    source_path: str = ""
    url: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


_KIWIX_TIMEOUT_SEC = 3.0
_NOMAD_TIMEOUT_SEC = 5.0

# OPDS / Atom XML namespaces used by kiwix-serve.
_ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}


class KiwixClient:
    """Minimal async client for a kiwix-serve instance.

    Uses the OPDS search endpoint which returns Atom XML regardless of ZIM
    layout. Results are parsed into ReferenceHit objects; exceptions are
    logged and swallowed — callers always get a list (possibly empty).
    """

    def __init__(
        self,
        base_url: str,
        *,
        cf_client_id: str = "",
        cf_client_secret: str = "",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers: dict[str, str] = {}
        if cf_client_id and cf_client_secret:
            # Cloudflare Access service-token auth.
            self._headers["CF-Access-Client-Id"] = cf_client_id
            self._headers["CF-Access-Client-Secret"] = cf_client_secret

    async def search(self, query: str, top_k: int = 5) -> list[ReferenceHit]:
        if not query.strip():
            return []
        # Cross-book search: /search?pattern=<q>&pageLength=<k>&format=xml
        # (format=xml returns OPDS Atom instead of the default HTML UI).
        # Scope to a single book with books.name=<name> if needed later.
        # Scope to a single language (default: English) so kiwix doesn't refuse
        # cross-language searches. Override with ZEUS_KIWIX_LANG, or set it to
        # empty to fall back to books.name scoping via ZEUS_KIWIX_BOOK.
        lang = os.getenv("ZEUS_KIWIX_LANG", "eng").strip()
        book = os.getenv("ZEUS_KIWIX_BOOK", "").strip()
        params: dict[str, str] = {
            "pattern": query,
            "pageLength": str(max(1, min(20, top_k))),
            "format": "xml",
        }
        if book:
            params["books.name"] = book
        elif lang:
            params["books.filter.lang"] = lang
        url = f"{self._base_url}/search"
        try:
            async with httpx.AsyncClient(
                timeout=_KIWIX_TIMEOUT_SEC,
                follow_redirects=True,
                headers=self._headers or None,
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                body = resp.text
        except Exception as exc:
            logger.warning("kiwix search failed (%s): %s", url, exc)
            return []

        return self._parse_opds(body, top_k)

    def _parse_opds(self, body: str, top_k: int) -> list[ReferenceHit]:
        """Parse either OPDS Atom (cross-book) or RSS (single-book) output.

        Kiwix returns RSS 2.0 when the search is scoped to one book via
        ``books.name``, and OPDS Atom when it spans the catalog.
        """
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            logger.warning("kiwix parse error: %s", exc)
            return []

        # RSS 2.0: <rss><channel><item>...</item></channel></rss>
        items: list[ET.Element] = []
        if root.tag.lower().endswith("rss"):
            channel = root.find("channel")
            if channel is not None:
                items = channel.findall("item")
        else:
            # Atom OPDS
            items = root.findall("a:entry", _ATOM_NS) or root.findall("entry")

        hits: list[ReferenceHit] = []
        total = len(items) or 1
        for rank, item in enumerate(items[:top_k]):
            title = _find_text(item, "title")
            summary = (
                _find_text(item, "description")
                or _find_text(item, "summary")
                or _find_text(item, "content")
            )
            # Strip HTML highlight tags kiwix inserts (<b>…</b>).
            summary = _strip_html(summary)
            link_href = ""
            link_el = item.find("link")
            if link_el is not None:
                link_href = (link_el.text or "").strip() or link_el.attrib.get("href", "")
            if not link_href:
                for a_link in item.findall("a:link", _ATOM_NS):
                    href = a_link.attrib.get("href", "")
                    if href and not href.startswith("/catalog"):
                        link_href = href
                        break

            text = summary or title
            if not text.strip():
                continue
            score = max(0.1, 1.0 - (rank / total))
            full_url = (
                link_href if link_href.startswith("http") else f"{self._base_url}{link_href}"
            )
            hits.append(
                ReferenceHit(
                    text=text.strip(),
                    score=score,
                    source="kiwix",
                    source_path=title.strip(),
                    url=full_url,
                )
            )
        return hits


_HTML_TAG_RE = __import__("re").compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    if not text:
        return ""
    return _HTML_TAG_RE.sub("", text).strip()


def _find_text(entry: ET.Element, tag: str) -> str:
    el = entry.find(f"a:{tag}", _ATOM_NS)
    if el is None:
        el = entry.find(tag)
    if el is None:
        return ""
    # Join all text including children's text/tail so inline <b>… tags don't
    # truncate the value. Kiwix RSS highlights matches with <b>…</b>.
    return "".join(el.itertext())


class NomadClient:
    """Thin client for Project NOMAD's RAG endpoint.

    The exact NOMAD HTTP shape is still being finalised in a parallel thread,
    so this client POSTs ``{"query": ..., "top_k": ...}`` to ``{base}/search``
    and expects ``{"hits": [{"text": ..., "score": ..., "source": ...,
    "url": ...}, ...]}``. On any failure it returns an empty list.
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def search(self, query: str, top_k: int = 5) -> list[ReferenceHit]:
        if not query.strip():
            return []
        url = f"{self._base_url}/search"
        try:
            async with httpx.AsyncClient(timeout=_NOMAD_TIMEOUT_SEC) as client:
                resp = await client.post(
                    url, json={"query": query, "top_k": top_k}
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("nomad search failed (%s): %s", url, exc)
            return []

        raw_hits = data.get("hits") if isinstance(data, dict) else None
        if not isinstance(raw_hits, list):
            return []

        hits: list[ReferenceHit] = []
        for item in raw_hits[:top_k]:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            try:
                score = float(item.get("score", 0.5))
            except (TypeError, ValueError):
                score = 0.5
            hits.append(
                ReferenceHit(
                    text=text,
                    score=score,
                    source="nomad",
                    source_path=str(item.get("source", "")),
                    url=str(item.get("url", "")),
                )
            )
        return hits


_kiwix_singleton: KiwixClient | None = None
_nomad_singleton: NomadClient | None = None
_initialised = False


def get_reference_clients() -> tuple[KiwixClient | None, NomadClient | None]:
    """Return process-wide singletons, gated by env vars.

    - ZEUS_KIWIX_ENABLED (default "1")
    - ZEUS_KIWIX_URL (default http://nomad_kiwix_server:8080)
    - ZEUS_NOMAD_ENABLED (default "0" until discovery confirms the endpoint)
    - ZEUS_NOMAD_URL
    """
    global _kiwix_singleton, _nomad_singleton, _initialised
    if _initialised:
        return _kiwix_singleton, _nomad_singleton

    if _env_bool("ZEUS_KIWIX_ENABLED", True):
        url = os.getenv("ZEUS_KIWIX_URL", "").strip()
        cf_id = os.getenv("ZEUS_KIWIX_CF_ACCESS_CLIENT_ID", "").strip()
        cf_secret = os.getenv("ZEUS_KIWIX_CF_ACCESS_CLIENT_SECRET", "").strip()
        if url:
            _kiwix_singleton = KiwixClient(
                url, cf_client_id=cf_id, cf_client_secret=cf_secret
            )
            auth = "service-token" if (cf_id and cf_secret) else "none"
            logger.info("kiwix reference client enabled: %s (auth=%s)", url, auth)

    if _env_bool("ZEUS_NOMAD_ENABLED", False):
        url = os.getenv("ZEUS_NOMAD_URL", "").strip()
        if url:
            _nomad_singleton = NomadClient(url)
            logger.info("nomad reference client enabled: %s", url)

    _initialised = True
    return _kiwix_singleton, _nomad_singleton


def reset_reference_clients() -> None:
    """Test hook — drop the singletons so env changes are re-read."""
    global _kiwix_singleton, _nomad_singleton, _initialised
    _kiwix_singleton = None
    _nomad_singleton = None
    _initialised = False
