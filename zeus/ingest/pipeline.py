# zeus/ingest/pipeline.py — Iris ingest pipeline
# Takes raw documents from a source, chunks them, and stores them via MemoryStore
# (curated facts with LLM extraction) or KnowledgeStore (raw chunks).
# Sources are pluggable — each implements the IngestSource protocol.
from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, Literal, Protocol

if TYPE_CHECKING:
    from rich.console import Console

from zeus.ingest.privacy import classify_chunk
from zeus.ingest.types import Chunk
from zeus.memory.library import KnowledgeChunk, KnowledgeStore, get_knowledge_store
from zeus.memory.store import AddResult, MemoryStore, get_memory_store

logger = logging.getLogger("iris")


def _ingest_prompt_mode() -> Literal["auto", "always", "never"]:
    raw = os.getenv("IRIS_INGEST_PROMPT_ON_TRANSIENT", "auto").strip().lower()
    if raw in ("always", "1", "true", "yes"):
        return "always"
    if raw in ("never", "0", "false", "no"):
        return "never"
    return "auto"


def _ingest_transient_max_retries() -> int:
    """0 = unlimited retries for transient Ollama/HTTP failures."""
    raw = os.getenv("IRIS_INGEST_TRANSIENT_MAX_RETRIES", "0").strip()
    try:
        n = int(raw)
    except ValueError:
        return 0
    return max(0, n)


from zeus.core.retry import is_transient_http_error as _is_transient_ingest_error  # noqa: E402


async def _prompt_retry_or_skip(chunk_index: int, source_label: str) -> bool:
    """
    Ask whether to keep retrying this chunk. Returns True to retry, False to skip.
    """
    line = (
        f"\niris: chunk [{chunk_index}] ({source_label}) still failing "
        "(Ollama/embed or network). Ollama ready? [Y/n] "
        "(Y/Enter = retry, n = skip this chunk): "
    )

    def _read_choice() -> bool:
        try:
            reply = input(line).strip().lower()
        except EOFError:
            return True
        if reply in ("n", "no"):
            return False
        return True

    return await asyncio.to_thread(_read_choice)


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
    target: str = "memory"
    memory_ops: dict[str, int] = field(default_factory=lambda: {
        "ADDED": 0, "SKIPPED": 0, "RAW_FALLBACKS": 0, "EXTRACTIONS": 0,
    })
    knowledge_ops: dict[str, int] = field(default_factory=lambda: {
        "ADD": 0, "SKIP": 0, "ERROR": 0,
    })


def _tally_memory_result(result: AddResult, ops: dict[str, int]) -> None:
    """Accumulate MemoryStore AddResult into per-source counters."""
    ops["ADDED"] += result.added
    ops["SKIPPED"] += result.skipped
    ops["RAW_FALLBACKS"] += result.raw_fallbacks
    ops["EXTRACTIONS"] += result.extraction_attempts


def _resolve_memory(dry_run: bool, injected: MemoryStore | None) -> MemoryStore | None:
    """Return MemoryStore for live ingest, or None for dry_run."""
    if dry_run:
        return None
    if injected is not None:
        return injected
    return get_memory_store()


def _resolve_knowledge(
    dry_run: bool, injected: KnowledgeStore | None
) -> KnowledgeStore | None:
    """Return KnowledgeStore for live ingest, or None for dry_run."""
    if dry_run:
        return None
    if injected is not None:
        return injected
    return get_knowledge_store()


def _chunk_to_knowledge(chunk: Chunk, privacy_level: str) -> KnowledgeChunk:
    """Map a pipeline Chunk (mem0-shaped) onto a KnowledgeChunk for raw RAG store."""
    src_label = chunk.source or "unknown"
    if ":" in src_label:
        source_kind, source_path = src_label.split(":", 1)
    else:
        source_kind, source_path = src_label, ""
    md = dict(chunk.metadata or {})
    chunk_index = int(md.pop("section", 0) or 0)
    md["privacy_level"] = privacy_level
    return KnowledgeChunk(
        text=chunk.text,
        source=source_kind,
        source_id=src_label,
        source_path=source_path,
        chunk_index=chunk_index,
        user_id=chunk.user_id,
        metadata=md,
    )


async def _store_chunk_memory(
    store: MemoryStore, chunk: Chunk, privacy_level: str
) -> AddResult:
    """Route a chunk through MemoryStore's LLM fact-extraction path."""
    src_label = chunk.source or "unknown"
    if ":" in src_label:
        source_kind, _source_path = src_label.split(":", 1)
    else:
        source_kind = src_label
    metadata = {
        **chunk.metadata,
        "privacy_level": privacy_level,
    }
    return await store.add_text(
        chunk.text,
        source=source_kind,
        source_id=src_label,
        user_id=chunk.user_id,
        extract_facts=True,
        metadata=metadata,
    )


def _store_chunk_knowledge(
    store: KnowledgeStore, chunk: Chunk, privacy_level: str
) -> None:
    """Blocking knowledge upsert. Raises on failure so the retry loop can catch it."""
    kc = _chunk_to_knowledge(chunk, privacy_level)
    result = store.add_chunks([kc])
    if result.errors:
        raise RuntimeError(result.errors[0])
    if result.added == 0:
        raise RuntimeError(f"knowledge store accepted 0 chunks (skipped={result.skipped})")


def _use_rich_progress(ingest_ui: Literal["auto", "rich", "plain"]) -> bool:
    if ingest_ui == "plain":
        return False
    if ingest_ui == "rich":
        return True
    return sys.stderr.isatty()


async def run_ingest(
    sources: list[IngestSource],
    chunk_size: int = 512,
    dry_run: bool = False,
    *,
    memory: MemoryStore | None = None,
    knowledge: KnowledgeStore | None = None,
    ingest_ui: Literal["auto", "rich", "plain"] = "auto",
    console: Console | None = None,
) -> list[IngestResult]:
    """
    Run the full ingest pipeline for all provided sources.

    dry_run=True chunks and logs without writing to MemoryStore / KnowledgeStore.
    """
    memory_store: MemoryStore | None = None
    knowledge_store: KnowledgeStore | None = None
    targets = {getattr(s, "target", "memory") for s in sources}
    if "memory" in targets:
        memory_store = _resolve_memory(dry_run, memory)
    if "knowledge" in targets:
        knowledge_store = _resolve_knowledge(dry_run, knowledge)
    results: list[IngestResult] = []
    use_progress = _use_rich_progress(ingest_ui)
    progress_cm = nullcontext(None)
    if use_progress:
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

            prog_console = console
            if prog_console is None:
                from rich.console import Console

                prog_console = Console(stderr=True)
            progress_cm = Progress(
                SpinnerColumn(style="cyan"),
                TextColumn("[bold]{task.description}[/bold]", justify="left"),
                TimeElapsedColumn(),
                console=prog_console,
                transient=True,
            )
        except ImportError:
            use_progress = False
            progress_cm = nullcontext(None)

    with progress_cm as progress:
        task_id = None
        if progress is not None:
            mode = "dry-run" if dry_run else "live"
            task_id = progress.add_task(f"iris · {mode} · …", total=None)

        for source in sources:
            source_name = type(source).__name__
            source_target = getattr(source, "target", "memory")
            stored = 0
            errors: list[str] = []
            total = 0
            mem_ops: dict[str, int] = {
                "ADDED": 0, "SKIPPED": 0, "RAW_FALLBACKS": 0, "EXTRACTIONS": 0,
            }
            k_ops: dict[str, int] = {"ADD": 0, "SKIP": 0, "ERROR": 0}
            t_start = time.monotonic()

            logger.info(
                "iris: starting ingest from %s → %s", source_name, source_target
            )
            if progress is not None and task_id is not None:
                progress.update(
                    task_id,
                    description=f"{source_name} [{source_target}] · chunk 0 · starting…",
                )

            async for chunk in source.chunks():
                total += 1
                if dry_run:
                    logger.debug(
                        "[dry_run] %s: %r…",
                        chunk.source,
                        chunk.text[:80],
                    )
                    stored += 1
                    if progress is not None and task_id is not None:
                        snippet = (chunk.text[:56] + "…") if len(chunk.text) > 56 else chunk.text
                        progress.update(
                            task_id,
                            description=f"{source_name} · chunk {total} · {snippet}",
                        )
                    continue

                chunk_t0 = time.monotonic()
                privacy_level = classify_chunk(chunk)
                transient_attempt = 0
                max_transient = _ingest_transient_max_retries()
                prompt_mode = _ingest_prompt_mode()
                backoff = 2.0
                backoff_cap = 60.0
                logged_transient_header = False

                while True:
                    try:
                        if source_target == "knowledge":
                            await asyncio.to_thread(
                                _store_chunk_knowledge,
                                knowledge_store,
                                chunk,
                                privacy_level.value,
                            )
                            k_ops["ADD"] += 1
                        else:
                            if memory_store is None:
                                raise RuntimeError("memory target selected but no MemoryStore configured")
                            mem_result = await _store_chunk_memory(
                                memory_store, chunk, privacy_level.value
                            )
                            _tally_memory_result(mem_result, mem_ops)
                            if mem_result.errors:
                                errors.extend(mem_result.errors)
                        stored += 1
                        chunk_dt = time.monotonic() - chunk_t0
                        snippet = (
                            (chunk.text[:56] + "…") if len(chunk.text) > 56 else chunk.text
                        )
                        if use_progress and progress is not None and task_id is not None:
                            progress.update(
                                task_id,
                                description=(
                                    f"{source_name} · chunk {total} · {chunk_dt:.1f}s · {snippet}"
                                ),
                            )
                        else:
                            logger.info(
                                "iris: [%s] stored chunk in %.1fs — %s: %r…",
                                total,
                                chunk_dt,
                                chunk.source,
                                chunk.text[:60],
                            )
                        break
                    except Exception as e:
                        if not _is_transient_ingest_error(e):
                            errors.append(f"{chunk.source}: {e}")
                            logger.warning(
                                "iris: [%s] failed to store chunk — %s", total, e
                            )
                            break

                        transient_attempt += 1
                        if max_transient and transient_attempt > max_transient:
                            errors.append(
                                f"{chunk.source}: {e} "
                                f"(gave up after {max_transient} transient retries; "
                                "raise IRIS_INGEST_TRANSIENT_MAX_RETRIES or unset for unlimited)"
                            )
                            logger.warning(
                                "iris: [%s] transient retries exhausted (%s) — %s",
                                total,
                                max_transient,
                                e,
                            )
                            break

                        if not logged_transient_header:
                            logger.warning(
                                "iris: [%s] transient failure (same chunk will retry) — %s",
                                total,
                                e,
                            )
                            logged_transient_header = True
                        elif transient_attempt % 5 == 0:
                            logger.info(
                                "iris: [%s] still retrying transient error "
                                "(attempt %s) — %s",
                                total,
                                transient_attempt,
                                e,
                            )

                        tty = sys.stdin.isatty()
                        want_prompt = False
                        if prompt_mode == "never":
                            pass
                        elif prompt_mode == "always":
                            want_prompt = transient_attempt >= 1 and transient_attempt % 5 == 0
                        elif prompt_mode == "auto" and tty:
                            # First prompt after a few automatic backoffs, then occasionally.
                            want_prompt = transient_attempt >= 3 and (
                                transient_attempt == 3
                                or (transient_attempt - 3) % 12 == 0
                            )
                        if want_prompt:
                            retry = await _prompt_retry_or_skip(total, chunk.source)
                            if not retry:
                                errors.append(
                                    f"{chunk.source}: {e} (skipped after user chose n)"
                                )
                                logger.warning(
                                    "iris: [%s] chunk skipped after transient failures",
                                    total,
                                )
                                break

                        sleep_s = min(backoff, backoff_cap)
                        backoff = min(backoff * 2.0, backoff_cap)
                        if use_progress and progress is not None and task_id is not None:
                            snip = (
                                (chunk.text[:40] + "…")
                                if len(chunk.text) > 40
                                else chunk.text
                            )
                            progress.update(
                                task_id,
                                description=(
                                    f"{source_name} · chunk {total} · "
                                    f"waiting {sleep_s:.0f}s · retry {transient_attempt} · {snip}"
                                ),
                            )
                        await asyncio.sleep(sleep_s)

            elapsed = time.monotonic() - t_start
            if source_target == "knowledge" and errors:
                k_ops["ERROR"] += len(errors)
            result = IngestResult(
                source=source_name,
                chunks_processed=total,
                chunks_stored=stored,
                errors=errors,
                elapsed_sec=elapsed,
                target=source_target,
                memory_ops=mem_ops,
                knowledge_ops=k_ops,
            )
            results.append(result)
            logger.info(
                "iris: %s complete — %s/%s stored, %s errors, %.1fs",
                source_name,
                stored,
                total,
                len(errors),
                elapsed,
            )

    return results


class IngestPipeline:
    """
    Thin wrapper around run_ingest for use by the scheduler.

    Pass a pre-configured list of IngestSource instances at construction time.
    The scheduler calls run_all_sources() on the configured interval.
    """

    def __init__(
        self,
        sources: list[IngestSource],
        chunk_size: int = 512,
        dry_run: bool = False,
        *,
        memory: MemoryStore | None = None,
    ) -> None:
        self._sources = list(sources)
        self._chunk_size = chunk_size
        self._dry_run = dry_run
        self._memory = memory

    async def run_all_sources(self, incremental: bool = True) -> list["IngestResult"]:
        if not self._sources:
            logger.info("IngestPipeline: no sources configured — skipping")
            return []
        if incremental:
            # incremental mode is not yet implemented — full ingest runs regardless
            logger.debug("IngestPipeline: incremental mode requested (currently a no-op)")
        return await run_ingest(
            self._sources,
            chunk_size=self._chunk_size,
            dry_run=self._dry_run,
            memory=self._memory,
        )


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
