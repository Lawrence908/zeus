# zeus/ingest/sources/context_pack.py — Iris context pack source parser
from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.pipeline import Chunk, chunk_text
from zeus.ingest.sources.markdown import _HEADING_SPLIT_RE, _strip_frontmatter


class ContextPackSource:
    """Ingest a single hand-curated context_pack.md with high-priority metadata."""

    def __init__(
        self,
        path: str | Path = "zeus/data/raw/context_pack.md",
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        user_id: str = "chris",
    ) -> None:
        self.path = Path(path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    async def chunks(self) -> AsyncIterator[Chunk]:
        if not self.path.exists():
            return

        raw = self.path.read_text(encoding="utf-8")
        body = _strip_frontmatter(raw)

        sections = _HEADING_SPLIT_RE.split(body)
        for section in sections:
            section = section.strip()
            if not section:
                continue

            for text in chunk_text(section, self.chunk_size, self.chunk_overlap):
                yield Chunk(
                    text=text,
                    source="context_pack:context_pack.md",
                    metadata={
                        "file": "context_pack.md",
                        "type": "context_pack",
                        "priority": "high",
                        "namespace": "context_pack",
                    },
                    user_id=self.user_id,
                )
