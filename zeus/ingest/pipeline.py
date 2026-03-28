# zeus/ingest/pipeline.py — Iris ingest pipeline
# Takes raw documents from a source, chunks them, and stores them via mem0.
# Sources are pluggable — each implements the IngestSource protocol.
from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncIterator, Literal, Protocol

if TYPE_CHECKING:
    from rich.console import Console

from zeus.ingest.privacy import classify_chunk
from zeus.ingest.types import Chunk
from zeus.memory.config import get_memory_client

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


def _is_transient_ingest_error(exc: BaseException) -> bool:
    """
    True when the failure is likely a dead/restarting Ollama or network blip,
    so we should retry the same chunk instead of skipping it.
    """
    msg = str(exc).lower()
    needles = (
        "failed to connect to ollama",
        "server disconnected",
        "connection reset",
        "connection refused",
        "connection aborted",
        "broken pipe",
        "errno 104",
        "errno 111",
        "errno 110",
        "read timeout",
        "connecterror",
        "remoteprotocolerror",
        "connect timeout",
        "pool timeout",
    )
    if any(n in msg for n in needles):
        return True
    if isinstance(exc, OSError) and exc.errno is not None:
        if exc.errno in (104, 111, 110, 32):  # reset, refused, timeout, broken pipe
            return True
    if isinstance(exc, ConnectionError):
        return True
    try:
        import httpx

        if isinstance(
            exc,
            (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.RemoteProtocolError,
                httpx.PoolTimeout,
            ),
        ):
            return True
    except ImportError:
        pass
    return False


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
    mem0_ops: dict[str, int] = field(default_factory=lambda: {
        "ADD": 0, "UPDATE": 0, "DELETE": 0, "NONE": 0,
    })


def _tally_mem0_result(result: dict, ops: dict[str, int]) -> None:
    """Count ADD/UPDATE/DELETE/NONE events from mem0.add() return value."""
    for item in result.get("results", []):
        event = item.get("event", "NONE").upper()
        if event in ops:
            ops[event] += 1


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
    ingest_ui: Literal["auto", "rich", "plain"] = "auto",
    console: Console | None = None,
) -> list[IngestResult]:
    """
    Run the full ingest pipeline for all provided sources.

    dry_run=True chunks and logs without writing to mem0.
    This is useful for previewing what will be ingested.

    ingest_ui: "rich" forces a spinner + live line per chunk; "plain" logs each
    chunk at INFO; "auto" uses rich only when stderr is a TTY (scheduler/CI
    stays on plain logging). Pass console when using Rich logging + progress
    together so output does not garble.
    """
    memory = None if dry_run else get_memory_client()
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
            stored = 0
            errors: list[str] = []
            total = 0
            ops: dict[str, int] = {"ADD": 0, "UPDATE": 0, "DELETE": 0, "NONE": 0}
            t_start = time.monotonic()

            logger.info("iris: starting ingest from %s", source_name)
            if progress is not None and task_id is not None:
                progress.update(
                    task_id,
                    description=f"{source_name} · chunk 0 · starting…",
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
                        mem0_result = await asyncio.to_thread(
                            memory.add,
                            messages=[{"role": "user", "content": chunk.text}],
                            user_id=chunk.user_id,
                            metadata={
                                **chunk.metadata,
                                "source": chunk.source,
                                "privacy_level": privacy_level.value,
                            },
                        )
                        _tally_mem0_result(mem0_result, ops)
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

    def __init__(self, sources: list[IngestSource], chunk_size: int = 512, dry_run: bool = False) -> None:
        self._sources = list(sources)
        self._chunk_size = chunk_size
        self._dry_run = dry_run

    async def run_all_sources(self, incremental: bool = True) -> list["IngestResult"]:
        if not self._sources:
            logger.info("IngestPipeline: no sources configured — skipping")
            return []
        if incremental:
            # incremental mode is not yet implemented — full ingest runs regardless
            logger.debug("IngestPipeline: incremental mode requested (currently a no-op)")
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
