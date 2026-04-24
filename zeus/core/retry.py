# zeus/core/retry.py — Shared transient-error classifier and async retry helper.
# Extracted from zeus/ingest/pipeline.py so non-ingest subsystems (Kronos, bus)
# can reuse the same "is this an Ollama / HTTP blip worth retrying" logic.
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

logger = logging.getLogger("zeus.retry")

T = TypeVar("T")


def is_transient_http_error(exc: BaseException) -> bool:
    """
    True when the failure is likely a dead/restarting service or network blip,
    so the caller should retry rather than fail hard.
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


async def with_retry(
    coro_factory: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    backoff: tuple[float, ...] = (0.5, 1.0, 2.0),
    transient: Callable[[BaseException], bool] = is_transient_http_error,
    label: str = "call",
) -> T:
    """
    Run ``coro_factory()`` up to ``max_retries + 1`` times.

    Retries only when ``transient(exc)`` is True. The ``backoff`` tuple supplies
    sleep durations between attempts; if there are more retries than values,
    the last value is reused.
    """
    attempt = 0
    last_exc: BaseException | None = None
    while True:
        try:
            return await coro_factory()
        except BaseException as exc:
            last_exc = exc
            if not transient(exc) or attempt >= max_retries:
                raise
            sleep_for = backoff[attempt] if attempt < len(backoff) else backoff[-1]
            logger.warning(
                "%s: transient failure (attempt %d/%d): %s; retrying in %.1fs",
                label, attempt + 1, max_retries + 1, exc, sleep_for,
            )
            await asyncio.sleep(sleep_for)
            attempt += 1
    # unreachable, but keeps type checkers happy
    raise last_exc  # type: ignore[misc]
