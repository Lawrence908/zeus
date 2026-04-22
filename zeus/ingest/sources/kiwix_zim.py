# zeus/ingest/sources/kiwix_zim.py — Kiwix ZIM ingest source (Phase 2.5)
#
# Walks ZIM archives on disk via libzim, extracts article text, emits Chunks
# into zeus_knowledge. For small, curated reference material where semantic
# search quality matters more than freshness.
#
# Split vs the live Reference layer:
#   - This source (ingest)       → zeus_knowledge, semantic search, one-time embed cost.
#                                  Use for small curated ZIMs (StackExchange, cooking, etc.).
#   - zeus.memory.reference      → kiwix-serve HTTP proxy, keyword FTS, zero storage.
#                                  Use for large/unbounded corpora (Wikipedia, Wiktionary).
#
# Hard rule: refuse any ZIM larger than ``ZEUS_KIWIX_MAX_ZIM_MB`` (default 2048).
# The guardrail prevents an accidental Wikipedia ingest from bloating Qdrant.
# The user must explicitly raise the threshold to override.
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import AsyncIterator, Iterator

from bs4 import BeautifulSoup

from zeus.ingest.pipeline import chunk_text
from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.kiwix_zim")


def _html_to_text(html: str) -> str:
    """Strip tags to plain text. Returns empty string on parse failure."""
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(" ", strip=True)
    except Exception as exc:
        logger.debug("kiwix_zim: html parse failed — %s", exc)
        return ""


class KiwixZimSource:
    """Ingest article bodies from one or more ZIM archives on disk.

    New-namespace ZIMs (``has_new_namespace_scheme=True``) don't use the old
    ``A/`` article-namespace prefix — entries are filtered by mimetype instead.
    Redirect entries are skipped.
    """

    target: str = "knowledge"

    def __init__(
        self,
        zim_dir: str | Path | None = None,
        books: list[str] | None = None,
        max_zim_mb: int | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
    ) -> None:
        self.zim_dir = Path(zim_dir or os.getenv("ZEUS_KIWIX_ZIM_DIR", ""))
        self.books: set[str] | None = set(books) if books else None
        env_cap = os.getenv("ZEUS_KIWIX_MAX_ZIM_MB")
        if max_zim_mb is not None:
            self.max_zim_mb = int(max_zim_mb)
        elif env_cap:
            self.max_zim_mb = int(env_cap)
        else:
            self.max_zim_mb = 2048
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    def _eligible_zims(self) -> list[Path]:
        if not self.zim_dir or not self.zim_dir.is_dir():
            logger.warning("kiwix_zim: zim_dir not found at %s", self.zim_dir)
            return []

        cap_bytes = self.max_zim_mb * 1024 * 1024
        eligible: list[Path] = []
        for path in sorted(self.zim_dir.glob("*.zim")):
            resolved = path.resolve()
            if not resolved.is_file():
                logger.warning("kiwix_zim: skipping dangling symlink %s", path.name)
                continue
            if self.books is not None and path.stem not in self.books:
                continue
            size = path.stat().st_size
            if size > cap_bytes:
                logger.warning(
                    "kiwix_zim: skipping %s (%.1f MB > %d MB cap); "
                    "query large ZIMs via the live Reference layer instead",
                    path.name,
                    size / (1024 * 1024),
                    self.max_zim_mb,
                )
                continue
            eligible.append(path)
        return eligible

    def _iter_articles(self, zim_path: Path) -> Iterator[tuple[str, str, str]]:
        from libzim.reader import Archive

        archive = Archive(zim_path)
        total = archive.entry_count
        logger.info(
            "kiwix_zim: %s — %d entries, %d articles",
            zim_path.name,
            total,
            archive.article_count,
        )
        for i in range(total):
            try:
                entry = archive._get_entry_by_id(i)
            except Exception as exc:
                logger.debug("kiwix_zim: entry %d unreadable — %s", i, exc)
                continue
            if entry.is_redirect:
                continue
            try:
                item = entry.get_item()
                mimetype = item.mimetype or ""
                if not mimetype.startswith("text/html"):
                    continue
                raw = bytes(item.content)
            except Exception as exc:
                logger.debug("kiwix_zim: item %s unreadable — %s", entry.path, exc)
                continue
            html = raw.decode("utf-8", errors="replace")
            yield entry.path, entry.title, html

    async def chunks(self) -> AsyncIterator[Chunk]:
        for zim_path in self._eligible_zims():
            book_stem = zim_path.stem
            emitted = 0
            for path, title, html in self._iter_articles(zim_path):
                text = _html_to_text(html)
                if len(text) < 50:
                    continue
                for piece in chunk_text(text, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=piece,
                        source=f"kiwix:{book_stem}:{path}",
                        metadata={
                            "file": f"{book_stem}/{path}",
                            "title": title,
                            "type": "kiwix_zim",
                            "book": book_stem,
                            "url": f"https://kiwix-nomad.chrislawrence.ca/viewer#{book_stem}/{path}",
                        },
                        user_id=self.user_id,
                    )
                    emitted += 1
            logger.info("kiwix_zim: %s → %d chunks", book_stem, emitted)
