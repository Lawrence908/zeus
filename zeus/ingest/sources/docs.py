# zeus/ingest/sources/docs.py - Iris project-docs source.
# Walks Zeus's own documentation (CLAUDE.md, README.md, docs/, zeus/docs/, subsystem
# CLAUDE.md files) and emits heading-aware chunks into the knowledge layer so the
# model can answer questions about its own architecture. Legacy docs under
# zeus/docs/legacy/ are deliberately excluded.
from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.sources.markdown import (
    _HEADING_SPLIT_RE,
    _extract_frontmatter_title,
    _strip_frontmatter,
)
from zeus.ingest.types import Chunk
from zeus.ingest.pipeline import chunk_text


# Relative to repo root. Non-recursive globs inside docs/ and zeus/docs/ so that
# zeus/docs/legacy/ (superseded decision history) stays out of retrieval.
DEFAULT_DOC_GLOBS: list[str] = [
    "CLAUDE.md",
    "README.md",
    "docs/*.md",
    "zeus/docs/*.md",
    "zeus/*/CLAUDE.md",   # subsystem CLAUDE.md files
]


class DocsSource:
    """Ingest Zeus's own project docs into the knowledge layer."""

    target: str = "knowledge"

    def __init__(
        self,
        repo_root: str | Path = ".",
        globs: list[str] | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "user",
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.globs = globs if globs is not None else DEFAULT_DOC_GLOBS
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    def _resolve_paths(self) -> list[tuple[Path, str]]:
        """Return (absolute_path, repo-relative-path) pairs, deduped and sorted."""
        seen: set[str] = set()
        pairs: list[tuple[Path, str]] = []
        for pattern in self.globs:
            for path in sorted(self.repo_root.glob(pattern)):
                if not path.is_file():
                    continue
                rel = str(path.relative_to(self.repo_root))
                if rel in seen:
                    continue
                # Skip legacy trees explicitly in case a pattern ever catches them.
                if "/legacy/" in rel or rel.startswith("legacy/"):
                    continue
                seen.add(rel)
                pairs.append((path, rel))
        return pairs

    async def chunks(self) -> AsyncIterator[Chunk]:
        import logging
        logger = logging.getLogger("iris")

        for path, rel_path in self._resolve_paths():
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError as e:
                logger.warning("docs: cannot read %s, %s", path, e)
                continue

            title = _extract_frontmatter_title(raw)
            body = _strip_frontmatter(raw)

            sections = _HEADING_SPLIT_RE.split(body)
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                for text in chunk_text(section, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=text,
                        source=f"docs:{rel_path}",
                        metadata={
                            "file": rel_path,
                            "title": title or path.stem,
                            "type": "zeus_docs",
                        },
                        user_id=self.user_id,
                    )
