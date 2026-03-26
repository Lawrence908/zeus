# zeus/orchestration/hooks.py — Before/after policy hooks for the agent bus
# Hooks wrap every bus call: pre-hooks fire before the request is forwarded,
# post-hooks fire after the response is received.
#
# This is the primary enforcement point for Aegis policies once the safety
# layer (Sprint 3 / LAB-119) is wired in.  For now the built-in hooks just
# log; the registry makes it trivial to bolt on policy checks later.

import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

# A hook function receives a context dict and returns a (possibly mutated) one.
HookFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


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
        context.get("target", "?"),
        context.get("endpoint", ""),
    )
    return context


async def _log_post(context: dict[str, Any]) -> dict[str, Any]:
    logger.debug(
        "[bus:post] %s%s → status=%s",
        context.get("target", "?"),
        context.get("endpoint", ""),
        context.get("response_status", "?"),
    )
    return context


def build_default_registry() -> HookRegistry:
    """Return a HookRegistry pre-wired with the standard logging hooks."""
    registry = HookRegistry()
    registry.register_pre("log", _log_pre)
    registry.register_post("log", _log_post)
    return registry
