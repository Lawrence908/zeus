# zeus/orchestration/hooks.py — Before/after policy hooks for the agent bus
# Hooks wrap every bus call: pre-hooks fire before the request is forwarded,
# post-hooks fire after the response is received.
#
# Includes built-in logging hooks, retry-with-backoff post-hook (LAB-338),
# bus metrics post-hook (LAB-339), and pre-hook context validation (LAB-340).

import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")

# A hook function receives a context dict and returns a (possibly mutated) one.
HookFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]

# Mandatory keys for pre-hook context (LAB-340)
_PRE_HOOK_REQUIRED_KEYS = frozenset({
    "source", "target_agent", "endpoint", "method", "payload", "correlation_id",
})


@dataclass
class Hook:
    name: str
    fn: HookFn
    stage: str  # "pre" | "post"


class HookRegistry:
    """
    Ordered registry of pre / post hooks that run around every bus call.

    Pre-hooks  — run before the request is dispatched; can mutate payload.
    Post-hooks — run after the response is received; can mutate or reject it.

    Any hook that raises will abort the call chain and propagate the exception
    to the caller, so safety hooks should raise on policy violations.
    """

    def __init__(self) -> None:
        self._pre: list[Hook] = []
        self._post: list[Hook] = []

    def register_pre(self, name: str, fn: HookFn) -> None:
        self._pre.append(Hook(name=name, fn=fn, stage="pre"))
        logger.debug("Registered pre-hook: %s", name)

    def register_post(self, name: str, fn: HookFn) -> None:
        self._post.append(Hook(name=name, fn=fn, stage="post"))
        logger.debug("Registered post-hook: %s", name)

    async def run_pre(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run all pre-hooks in registration order."""
        for hook in self._pre:
            try:
                context = await hook.fn(context)
            except Exception:
                logger.error("Pre-hook %r failed", hook.name, exc_info=True)
                raise
        return context

    async def run_post(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run all post-hooks in registration order."""
        for hook in self._post:
            try:
                context = await hook.fn(context)
            except Exception:
                logger.error("Post-hook %r failed", hook.name, exc_info=True)
                raise
        return context


# ------------------------------------------------------------------
# Built-in hooks
# ------------------------------------------------------------------


async def _log_pre(context: dict[str, Any]) -> dict[str, Any]:
    logger.debug(
        "[bus:pre] %s → %s%s",
        context.get("source", "?"),
        context.get("target_agent", context.get("target", "?")),
        context.get("endpoint", ""),
    )
    return context


async def _log_post(context: dict[str, Any]) -> dict[str, Any]:
    logger.debug(
        "[bus:post] %s%s → status=%s",
        context.get("target_agent", context.get("target", "?")),
        context.get("endpoint", ""),
        context.get("response_status", "?"),
    )
    return context


# ------------------------------------------------------------------
# Pre-hook context validator (LAB-340)
# ------------------------------------------------------------------


async def _validate_pre_context(context: dict[str, Any]) -> dict[str, Any]:
    """Enforce mandatory keys on pre-hook context. Raises in dev, warns in prod."""
    missing = _PRE_HOOK_REQUIRED_KEYS - context.keys()
    if missing:
        msg = f"Pre-hook context missing required keys: {sorted(missing)}"
        if ZEUS_ENV == "dev":
            raise ValueError(msg)
        logger.warning(msg)
    return context


# ------------------------------------------------------------------
# Retry-with-backoff post-hook (LAB-338)
# ------------------------------------------------------------------

_TRANSIENT_STATUS_CODES = {502, 503, 504}


async def _retry_backoff_post_hook(context: dict[str, Any]) -> dict[str, Any]:
    """
    Flag transient errors for retry by setting context["should_retry"] = True.
    The bus_call() caller is responsible for acting on this flag.
    """
    status = context.get("response_status")
    if isinstance(status, int) and status in _TRANSIENT_STATUS_CODES:
        context["should_retry"] = True
        logger.info(
            "[bus:retry-hook] transient %d for %s%s — flagging for retry",
            status,
            context.get("target_agent", "?"),
            context.get("endpoint", ""),
        )
    return context


# ------------------------------------------------------------------
# Bus metrics post-hook (LAB-339)
# ------------------------------------------------------------------


class BusMetrics:
    """Simple in-memory metrics counter per agent."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, int | float]] = defaultdict(
            lambda: {"calls": 0, "errors": 0, "latency_total_ms": 0.0}
        )

    def record(self, agent: str, *, error: bool = False, latency_ms: float = 0.0) -> None:
        bucket = self._data[agent]
        bucket["calls"] += 1
        if error:
            bucket["errors"] += 1
        bucket["latency_total_ms"] += latency_ms

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return dict(self._data)


# Module-level instance — wired into app.state in build_default_registry()
bus_metrics = BusMetrics()


async def _bus_metrics_post_hook(context: dict[str, Any]) -> dict[str, Any]:
    agent = context.get("target_agent", "unknown")
    status = context.get("response_status")
    is_error = isinstance(status, int) and status >= 400
    # Approximate latency from context if available
    latency = context.get("latency_ms", 0.0)
    bus_metrics.record(agent, error=is_error, latency_ms=latency)
    return context


# ------------------------------------------------------------------
# Registry builder
# ------------------------------------------------------------------


def build_default_registry() -> HookRegistry:
    """Return a HookRegistry pre-wired with standard hooks."""
    registry = HookRegistry()
    # Pre-hooks (run before dispatch)
    registry.register_pre("validate_context", _validate_pre_context)
    registry.register_pre("log", _log_pre)
    # Post-hooks (run after response)
    registry.register_post("log", _log_post)
    registry.register_post("retry_backoff", _retry_backoff_post_hook)
    registry.register_post("bus_metrics", _bus_metrics_post_hook)
    return registry
