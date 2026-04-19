# zeus/ingest/sources/bookmarks.py — Browser bookmarks ingest source (Sprint 10d)
# Parses Netscape Bookmark HTML format (Chrome / Firefox / Safari export).
# Generates one chunk per bookmark with title, URL, folder path, and add date.
# Deduplicates by URL. Optional page content fetch is disabled by default.
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator
from urllib.parse import urlparse

from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.bookmarks")

_DEFAULT_EXPORT = "zeus/data/raw/bookmarks.html"


def _parse_bookmarks_html(html: str) -> list[dict]:
    """
    Parse a Netscape Bookmark File Format HTML export.

    Returns a list of dicts with keys: title, url, folder, add_date.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ImportError(
            "Bookmarks support requires: pip install beautifulsoup4"
        ) from exc

    soup = BeautifulSoup(html, "html.parser")
    bookmarks: list[dict] = []
    seen_urls: set[str] = set()

    def _walk(tag, folder_path: list[str]) -> None:
        for child in tag.children:
            if not hasattr(child, "name"):
                continue

            if child.name == "dt":
                inner = list(child.children)
                for item in inner:
                    if not hasattr(item, "name"):
                        continue

                    if item.name == "a":
                        url = item.get("href", "").strip()
                        if not url or url in seen_urls:
                            continue
                        # Skip javascript: and data: URLs
                        scheme = urlparse(url).scheme
                        if scheme not in ("http", "https"):
                            continue
                        seen_urls.add(url)

                        add_date_raw = item.get("add_date", "")
                        try:
                            add_date = datetime.utcfromtimestamp(int(add_date_raw)).strftime("%Y-%m-%d")
                        except (ValueError, TypeError):
                            add_date = ""

                        bookmarks.append({
                            "title": item.get_text(strip=True) or urlparse(url).netloc,
                            "url": url,
                            "folder": " / ".join(folder_path) if folder_path else "Bookmarks",
                            "add_date": add_date,
                        })

                    elif item.name == "h3":
                        # Folder heading — recurse into following <dl>
                        folder_name = item.get_text(strip=True)
                        dl = item.find_next_sibling("dl")
                        if dl:
                            _walk(dl, folder_path + [folder_name])

    root_dl = soup.find("dl")
    if root_dl:
        _walk(root_dl, [])

    return bookmarks


class BookmarksSource:
    """
    Ingest browser bookmarks from a Netscape Bookmark HTML export.

    Config keys: export_path, fetch_content (bool, default False)
    Env var: BOOKMARKS_EXPORT_PATH
    """

    target: str = "knowledge"

    def __init__(
        self,
        export_path: str | Path | None = None,
        fetch_content: bool = False,
        user_id: str = "chris",
    ) -> None:
        self.export_path = Path(export_path or os.getenv("BOOKMARKS_EXPORT_PATH", _DEFAULT_EXPORT))
        self.fetch_content = fetch_content  # reserved for future use
        self.user_id = user_id

    async def chunks(self) -> AsyncIterator[Chunk]:
        if not self.export_path.exists():
            logger.warning("bookmarks: export file not found at %s", self.export_path)
            return

        try:
            html = self.export_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("bookmarks: cannot read %s — %s", self.export_path, exc)
            return

        try:
            bookmarks = _parse_bookmarks_html(html)
        except ImportError as exc:
            logger.error("bookmarks: %s", exc)
            return
        except Exception as exc:
            logger.error("bookmarks: parse failed — %s", exc)
            return

        logger.info("bookmarks: parsed %d bookmarks from %s", len(bookmarks), self.export_path)

        for bm in bookmarks:
            date_part = f", added: {bm['add_date']}" if bm["add_date"] else ""
            text = (
                f"Bookmark: {bm['title']} — {bm['url']} "
                f"(folder: {bm['folder']}{date_part})"
            )

            yield Chunk(
                text=text,
                source=f"bookmarks:{urlparse(bm['url']).netloc}",
                metadata={
                    "title": bm["title"],
                    "url": bm["url"],
                    "folder": bm["folder"],
                    "add_date": bm["add_date"],
                    "type": "bookmark",
                },
                user_id=self.user_id,
            )
