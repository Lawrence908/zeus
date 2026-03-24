# zeus/ingest/pipeline.py — Iris ingest pipeline
# Takes raw documents from a source, chunks them, and stores them via mem0.
# Sources are pluggable — each implements the IngestSource protocol.
import asyncio
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator, Protocol

from zeus.memory.config import get_memory_client

logger = logging.getLogger("iris")


@dataclass
class Chunk:
    """A single ingested chunk ready for embedding and storage."""
    text: str
    source: str                      # e.g. "markdown:notes/2024-01.md"
    metadata: dict = field(default_factory=dict)
    user_id: str = "chris"           # mem0 partitions by user_id


class IngestSource(Protocol):
    """All source parsers implement this interface."""

    async def chunks(self) -> AsyncIterator[Chunk]:
        """Yield chunks from the source."""
        ...


@dataclass
class IngestResult:
    source: str
    chunks_processed: int
    chunks_stored: int
    errors: list[str] = field(default_factory=list)


async def run_ingest(
    sources: list[IngestSource],
    chunk_size: int = 512,
    dry_run: bool = False,
) -> list[IngestResult]:
    """
    Run the full ingest pipeline for all provided sources.

    dry_run=True chunks and logs without writing to mem0.
    This is useful for previewing what will be ingested.
    """
    memory = None if dry_run else get_memory_client()
    results: list[IngestResult] = []

    for source in sources:
        source_name = type(source).__name__
        stored = 0
        errors: list[str] = []
        total = 0

        logger.info(f"iris: starting ingest from {source_name}")

        async for chunk in source.chunks():
            total += 1
            if dry_run:
                logger.debug(f"[dry_run] {chunk.source}: {chunk.text[:80]!r}…")
                stored += 1
                continue

            try:
                # mem0.add() handles embedding + storage in one call.
                # It wraps the text as a message so mem0 can extract facts.
                memory.add(
                    messages=[{"role": "user", "content": chunk.text}],
                    user_id=chunk.user_id,
                    metadata={**chunk.metadata, "source": chunk.source},
                )
                stored += 1
            except Exception as e:
                errors.append(f"{chunk.source}: {e}")
                logger.warning(f"iris: failed to store chunk — {e}")

        result = IngestResult(
            source=source_name,
            chunks_processed=total,
            chunks_stored=stored,
            errors=errors,
        )
        results.append(result)
        logger.info(
            f"iris: {source_name} complete — {stored}/{total} stored, "
            f"{len(errors)} errors"
        )

    return results


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """
    Split text into overlapping chunks by word count.

    Token-accurate splitting (via tiktoken) is not worth the dependency here —
    word-count is close enough for nomic-embed-text's 2048-token window.
    """
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks
