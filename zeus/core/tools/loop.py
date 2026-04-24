# zeus/core/tools/loop.py — Provider-agnostic chat tool-call driver
#
# Called from QueryEngine.query() when ZEUS_TOOLS_ENABLED is set. One call into
# run_tool_loop() replaces the single _run_llm() call: the driver fans out
# model -> tool_calls -> tool_results -> model -> ... until the model stops
# emitting tool calls or the per-query call cap is reached. Aegis evaluates
# every tool argument dict before execution and every tool result text before
# it is fed back to the model.
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from pydantic import BaseModel, Field

from zeus.core.tools import registry
from zeus.core.tools.adapters import (
    tool_results_for_anthropic,
    tool_results_for_ollama,
)
from zeus.core.tools.base import ToolCall, ToolResult, ToolSpec
from zeus.core.tools.cache import get_cache
from zeus.core.tools.recorder import record_invocation
from zeus.safety.policy_engine import AegisPolicyEngine, aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.tools.loop")


class ToolLoopResult(BaseModel):
    reply: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    iterations: int = 0
    stop_reason: str = ""
    truncated: bool = False


async def run_tool_loop(
    *,
    system: str,
    user_prompt: str,
    tools: list[ToolSpec],
    max_tokens: int,
    max_calls: int,
    use_claude: bool,
) -> ToolLoopResult:
    """Drive the tool-call loop until the model emits no more tool calls.

    `use_claude` tells us which provider is on the other end so we can build
    follow-up messages in the right shape. It's threaded through rather than
    recomputed so tests can exercise both paths deterministically.
    """
    # Import here to avoid a circular import at module load time
    # (query.py imports from tools; tools.loop calls into query._run_llm_with_tools).
    from zeus.core.query import _run_llm_with_tools

    messages: list[dict[str, Any]] = [{"role": "user", "content": user_prompt}]
    all_calls: list[ToolCall] = []
    all_results: list[ToolResult] = []

    final_text = ""
    stop_reason = ""
    iterations = 0
    truncated = False

    # Hard upper bound on loop iterations so a buggy model that keeps emitting
    # tool calls without progress cannot spin forever. max_calls is the
    # per-query tool-call BUDGET (each iteration may emit multiple calls);
    # iteration_cap gives one extra model turn so the model can compose a
    # final reply after the last allowed tool call. Without the +1, callers
    # using max_calls=1 would only ever get the pre-tool preamble back.
    iteration_cap = max(2, max_calls + 1)

    while iterations < iteration_cap:
        iterations += 1
        # Once the per-query tool-call budget is exhausted, withhold tools so
        # the model is forced to compose a final reply from the results it
        # already has, rather than emitting more calls that just become
        # "cap reached" errors.
        available_tools = [] if len(all_calls) >= max_calls else tools
        text, calls, stop_reason = await _run_llm_with_tools(
            system=system,
            messages=messages,
            tools=available_tools,
            max_tokens=max_tokens,
            turn_idx=iterations,
        )
        final_text = text

        if not calls:
            break

        # Echo the assistant turn into history before we append the tool results.
        messages.append(_assistant_turn(text, calls, use_claude=use_claude))

        results: list[ToolResult] = []
        for call in calls:
            if len(all_calls) >= max_calls:
                truncated = True
                results.append(
                    ToolResult(
                        call_id=call.call_id,
                        name=call.name,
                        content=f"Tool-call cap ({max_calls}) reached for this query.",
                        is_error=True,
                    )
                )
                all_calls.append(call)
                continue
            all_calls.append(call)
            result = await _execute_one(call)
            results.append(result)

        all_results.extend(results)

        # Append the tool results in the shape the next model call expects.
        if use_claude:
            messages.append(tool_results_for_anthropic(results))
        else:
            messages.extend(tool_results_for_ollama(results))

        if truncated:
            # One more pass with the truncation error messages gives the model a
            # chance to compose a final reply from what it has. But we don't let
            # it call more tools -- the iteration_cap guard catches it.
            pass

    return ToolLoopResult(
        reply=final_text,
        tool_calls=all_calls,
        tool_results=all_results,
        iterations=iterations,
        stop_reason=stop_reason,
        truncated=truncated,
    )


async def _execute_one(call: ToolCall) -> ToolResult:
    """Run a single tool call with Aegis gates on args and results.

    Every path records a ToolInvocation entry (success, error, cache hit,
    Aegis reject) into the in-process ring buffer so /admin/tools/invocations
    and the React Tools page have a single authoritative feed.
    """
    result, cache_hit, aegis_flags, aegis_rejected = await _execute_one_impl(call)
    record_invocation(
        tool=call.name,
        args=call.arguments,
        content=result.content,
        is_error=result.is_error,
        cache_hit=cache_hit,
        duration_ms=result.duration_ms,
        aegis_flags=aegis_flags,
        aegis_rejected=aegis_rejected,
        source="chat",
    )
    return result


async def _execute_one_impl(
    call: ToolCall,
) -> tuple[ToolResult, bool, list[str], bool]:
    """Do the real work for _execute_one. Returns
    (result, cache_hit, aegis_flags, aegis_rejected)."""
    entry = registry.get(call.name)
    if entry is None:
        return (
            ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Unknown tool {call.name!r}.",
                is_error=True,
            ),
            False,
            [],
            False,
        )
    spec, handler = entry

    # Aegis pre: validate tool arguments before execution.
    if aegis_enabled():
        engine = AegisPolicyEngine(policy=spec.aegis_policy)
        outcome = engine.evaluate_payload(call.arguments)
        if outcome.status == "rejected":
            logger.warning(
                "aegis rejected args for tool=%s policy=%s: %s",
                call.name,
                spec.aegis_policy,
                outcome.message,
            )
            return (
                ToolResult(
                    call_id=call.call_id,
                    name=call.name,
                    content=(
                        outcome.message
                        or f"Tool arguments blocked by Aegis policy {spec.aegis_policy!r}."
                    ),
                    is_error=True,
                ),
                False,
                list(outcome.flags),
                True,
            )

    # Cache hit? Only cacheable tools participate. The cache module is a no-op
    # when ZEUS_TOOL_CACHE_TTL_SECONDS=0, so this guard is cheap either way.
    cache = get_cache()
    if spec.cacheable:
        cached = cache.get(call.name, call.arguments)
        if cached is not None:
            logger.info("tool cache hit: %s", call.name)
            return (
                cached.model_copy(update={"call_id": call.call_id, "name": call.name}),
                True,
                [],
                False,
            )

    t0 = time.monotonic()
    try:
        result = await asyncio.wait_for(
            handler(call.arguments), timeout=spec.timeout_seconds
        )
    except asyncio.TimeoutError:
        dur = int((time.monotonic() - t0) * 1000)
        return (
            ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Tool {call.name} timed out after {spec.timeout_seconds:.0f}s.",
                is_error=True,
                duration_ms=dur,
            ),
            False,
            [],
            False,
        )
    except Exception as exc:
        dur = int((time.monotonic() - t0) * 1000)
        logger.exception("tool %s raised", call.name)
        return (
            ToolResult(
                call_id=call.call_id,
                name=call.name,
                content=f"Tool {call.name} failed: {exc!s}",
                is_error=True,
                duration_ms=dur,
            ),
            False,
            [],
            False,
        )

    # Ensure handler-provided fields (call_id/name) match the call.
    if not result.call_id:
        result = result.model_copy(update={"call_id": call.call_id})
    if not result.name:
        result = result.model_copy(update={"name": call.name})
    if not result.duration_ms:
        result = result.model_copy(
            update={"duration_ms": int((time.monotonic() - t0) * 1000)}
        )

    # Aegis post: scan the result text before it is fed back to the model.
    post_flags: list[str] = []
    post_rejected = False
    if aegis_enabled():
        outcome = evaluate_text(result.content, policy_name=spec.aegis_policy)
        post_flags = list(outcome.flags)
        if outcome.status == "rejected":
            logger.warning(
                "aegis rejected result for tool=%s policy=%s: %s",
                call.name,
                spec.aegis_policy,
                outcome.message,
            )
            post_rejected = True
            result = result.model_copy(
                update={
                    "content": (
                        outcome.message
                        or f"Tool result blocked by Aegis policy {spec.aegis_policy!r}."
                    ),
                    "is_error": True,
                }
            )

    if spec.cacheable:
        cache.set(call.name, call.arguments, result)

    return result, False, post_flags, post_rejected


def _assistant_turn(
    text: str, calls: list[ToolCall], *, use_claude: bool
) -> dict[str, Any]:
    """Rebuild the assistant turn in the shape the next call expects.

    Anthropic wants a content array with interleaved text + tool_use blocks.
    Ollama wants {"role":"assistant","content":"..","tool_calls":[...]}.
    """
    if use_claude:
        content: list[dict[str, Any]] = []
        if text:
            content.append({"type": "text", "text": text})
        for c in calls:
            content.append(
                {
                    "type": "tool_use",
                    "id": c.call_id,
                    "name": c.name,
                    "input": c.arguments,
                }
            )
        return {"role": "assistant", "content": content}

    return {
        "role": "assistant",
        "content": text,
        "tool_calls": [
            {
                "function": {
                    "name": c.name,
                    "arguments": c.arguments,
                }
            }
            for c in calls
        ],
    }
