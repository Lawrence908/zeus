# zeus/ingest/sources/obsidian.py — Obsidian vault ingest source (Sprint 10a)
# Parses .md files in an Obsidian vault with:
#   - YAML frontmatter extraction → metadata
#   - [[WikiLink]] reference collection → metadata
#   - #tag extraction → chunk tags
#   - Daily note detection (YYYY-MM-DD.md filename pattern)
import logging
import os
import re
from pathlib import Path
from typing import Any, AsyncIterator

import yaml

from zeus.ingest.pipeline import chunk_text
from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.obsidian")

_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
_TAG_RE = re.compile(r"(?<!\S)#([A-Za-z][A-Za-z0-9_/-]*)")
_DAILY_NOTE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_HEADING_SPLIT_RE = re.compile(r"(?=^#{1,3} )", re.MULTILINE)

_DEFAULT_EXCLUDE = {".obsidian", "templates", "archive", ".trash"}


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (metadata_dict, body_without_frontmatter). YAML lists and nested keys supported."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw = match.group(1).strip()
    body = text[match.end():].strip()

    try:
        loaded = yaml.safe_load(raw)
        meta: dict[str, Any] = loaded if isinstance(loaded, dict) else {}
    except yaml.YAMLError:
        meta = {}

    return meta, body


class ObsidianSource:
    """
    Ingest all Markdown notes from an Obsidian vault directory.

    Env var: OBSIDIAN_VAULT_PATH
    Config keys: vault_path, exclude_dirs, chunk_size, chunk_overlap
    """

    target: str = "knowledge"

    def __init__(
        self,
        vault_path: str | Path | None = None,
        exclude_dirs: list[str] | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
    ) -> None:
        self.vault_path = Path(vault_path or os.getenv("OBSIDIAN_VAULT_PATH", ""))
        self.exclude_dirs = set(exclude_dirs or _DEFAULT_EXCLUDE)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    def _iter_notes(self) -> list[Path]:
        if not self.vault_path.is_dir():
            logger.warning("obsidian: vault not found at %s", self.vault_path)
            return []

        notes: list[Path] = []
        for path in self.vault_path.rglob("*.md"):
            # Skip excluded directories
            if any(part in self.exclude_dirs for part in path.parts):
                continue
            notes.append(path)
        return sorted(notes)

    async def chunks(self) -> AsyncIterator[Chunk]:
        for path in self._iter_notes():
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError as exc:
                logger.warning("obsidian: cannot read %s — %s", path, exc)
                continue

            frontmatter, body = _parse_frontmatter(raw)
            wikilinks = _WIKILINK_RE.findall(body)
            tags = _TAG_RE.findall(body)
            is_daily = bool(_DAILY_NOTE_RE.match(path.stem))
            rel_path = str(path.relative_to(self.vault_path))

            title_raw = frontmatter.get("title")
            title = str(title_raw).strip() if title_raw is not None else path.stem
            meta_base = {
                "file": rel_path,
                "title": title,
                "type": "obsidian_daily" if is_daily else "obsidian",
                "tags": tags,
                "wikilinks": wikilinks[:50],  # cap to avoid giant metadata
                **{k: v for k, v in frontmatter.items() if k not in ("title",)},
            }

            sections = _HEADING_SPLIT_RE.split(body)
            section_num = 0
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                section_num += 1

                for text in chunk_text(section, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=text,
                        source=f"obsidian:{rel_path}",
                        metadata={**meta_base, "section": section_num},
                        user_id=self.user_id,
                    )
