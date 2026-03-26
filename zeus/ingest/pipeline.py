# zeus/ingest/pipeline.py — Iris ingest pipeline
# Takes raw documents from a source, chunks them, and stores them via mem0.
# Sources are pluggable — each implements the IngestSource protocol.
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import AsyncIterator, Protocol

from zeus.ingest.privacy import classify_chunk
from zeus.ingest.types import Chunk
from zeus.memory.config import get_memory_client

logger = logging.getLogger("iris")


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
    elapsed_sec: float = 0.0
    mem0_ops: dict[str, int] = field(default_factory=lambda: {
        "ADD": 0, "UPDATE": 0, "DELETE": 0, "NONE": 0,
    })


def _tally_mem0_result(result: dict, ops: dict[str, int]) -> None:
    """Count ADD/UPDATE/DELETE/NONE events from mem0.add() return value."""
    for item in result.get("results", []):
        event = item.get("event", "NONE").upper()
        if event in ops:
            ops[event] += 1


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
        ops: dict[str, int] = {"ADD": 0, "UPDATE": 0, "DELETE": 0, "NONE": 0}
        t_start = time.monotonic()

        logger.info(f"iris: starting ingest from {source_name}")

        async for chunk in source.chunks():
            total += 1
            if dry_run:
                logger.debug(f"[dry_run] {chunk.source}: {chunk.text[:80]!r}…")
                stored += 1
                continue

            chunk_t0 = time.monotonic()
            try:
                privacy_level = classify_chunk(chunk)
                mem0_result = memory.add(
                    messages=[{"role": "user", "content": chunk.text}],
                    user_id=chunk.user_id,
                    metadata={**chunk.metadata, "source": chunk.source, "privacy_level": privacy_level.value},
                )
                _tally_mem0_result(mem0_result, ops)
                stored += 1
                chunk_dt = time.monotonic() - chunk_t0
                logger.info(
                    f"iris: [{total}] stored chunk in {chunk_dt:.1f}s — "
                    f"{chunk.source}: {chunk.text[:60]!r}…"
                )
            except Exception as e:
                errors.append(f"{chunk.source}: {e}")
                logger.warning(f"iris: [{total}] failed to store chunk — {e}")

        elapsed = time.monotonic() - t_start
        result = IngestResult(
            source=source_name,
            chunks_processed=total,
            chunks_stored=stored,
            errors=errors,
            elapsed_sec=elapsed,
            mem0_ops=ops,
        )
        results.append(result)
        logger.info(
            f"iris: {source_name} complete — {stored}/{total} stored, "
            f"{len(errors)} errors, {elapsed:.1f}s"
        )

    return results


class IngestPipeline:
    """
    Thin wrapper around run_ingest for use by the scheduler.

    Pass a pre-configured list of IngestSource instances at construction time.
    The scheduler calls run_all_sources() on the configured interval.
    """

    def __init__(self, sources: list[IngestSource], chunk_size: int = 512, dry_run: bool = False) -> None:
        self._sources = list(sources)
        self._chunk_size = chunk_size
        self._dry_run = dry_run

    async def run_all_sources(self, incremental: bool = True) -> list["IngestResult"]:
        if not self._sources:
            logger.info("IngestPipeline: no sources configured — skipping")
            return []
        return await run_ingest(self._sources, chunk_size=self._chunk_size, dry_run=self._dry_run)


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
