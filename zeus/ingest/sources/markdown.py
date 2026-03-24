# zeus/ingest/sources/markdown.py — Iris markdown source parser
# Reads .md files from a glob pattern and yields chunks.
# Strips frontmatter and splits on heading boundaries before word-chunking,
# so chunk boundaries respect document structure rather than cutting mid-section.
import re
from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.pipeline import Chunk, chunk_text

# Matches YAML frontmatter block at the start of a file
_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", re.DOTALL)

# Split on H1/H2/H3 headings — keeps the heading as the start of each section
_HEADING_SPLIT_RE = re.compile(r"(?=^#{1,3} )", re.MULTILINE)


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text).strip()


def _extract_frontmatter_title(text: str) -> str | None:
    """Pull 'title:' from YAML frontmatter if present."""
    match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


class MarkdownSource:
    """Ingest .md files from one or more glob patterns."""

    def __init__(
        self,
        globs: list[str],
        base_dir: str | Path = ".",
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
    ) -> None:
        self.globs = globs
        self.base_dir = Path(base_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    def _iter_files(self) -> list[Path]:
        files: list[Path] = []
        for pattern in self.globs:
            files.extend(sorted(self.base_dir.glob(pattern)))
        return files

    async def chunks(self) -> AsyncIterator[Chunk]:
        for path in self._iter_files():
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError as e:
                import logging
                logging.getLogger("iris").warning(f"markdown: cannot read {path} — {e}")
                continue

            title = _extract_frontmatter_title(raw)
            body = _strip_frontmatter(raw)
            rel_path = str(path.relative_to(self.base_dir))

            # Split on headings first to avoid cutting mid-section
            sections = _HEADING_SPLIT_RE.split(body)
            for section in sections:
                section = section.strip()
                if not section:
                    continue

                for text in chunk_text(section, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=text,
                        source=f"markdown:{rel_path}",
                        metadata={
                            "file": rel_path,
                            "title": title or path.stem,
                            "type": "markdown",
                        },
                        user_id=self.user_id,
                    )
