# zeus/core/tools/adapters.py — Anthropic + Ollama tool-call wire-format adapters
#
# Pure functions; no I/O. See zeus/docs/tool-use-spec.md for the cross-provider
# differences these paper over (Anthropic: input_schema + tool_use_id +
# tool_result blocks in user messages; Ollama: parameters + no call id +
# role="tool" follow-ups, associated by name + emission order).
from __future__ import annotations

from typing import Any

from zeus.core.tools.base import ToolCall, ToolResult, ToolSpec


# ---------------------------------------------------------------------------
# Spec -> provider wire format
# ---------------------------------------------------------------------------


def tools_to_anthropic(specs: list[ToolSpec]) -> list[dict[str, Any]]:
    """Convert tool specs into the Anthropic Messages `tools` shape."""
    return [
        {
            "name": spec.name,
            "description": spec.description,
            "input_schema": spec.parameters,
        }
        for spec in specs
    ]


def tools_to_ollama(specs: list[ToolSpec]) -> list[dict[str, Any]]:
    """Convert tool specs into the Ollama /api/chat `tools` shape."""
    return [
        {
            "type": "function",
            "function": {
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.parameters,
            },
        }
        for spec in specs
    ]


# ---------------------------------------------------------------------------
# Provider response -> normalized ToolCall list
# ---------------------------------------------------------------------------


def parse_anthropic_message(msg: Any) -> tuple[str, list[ToolCall], str]:
    """Extract (text, tool_calls, stop_reason) from an Anthropic Messages response.

    `msg` is an anthropic.types.Message (or a dict-shaped equivalent, for tests).
    Text comes from concatenating all `text` blocks; tool calls come from
    `tool_use` blocks. The Anthropic call id (`toolu_...`) is preserved.
    """
    content = _attr(msg, "content", []) or []
    stop_reason = str(_attr(msg, "stop_reason", "") or "")

    text_parts: list[str] = []
    calls: list[ToolCall] = []
    for block in content:
        btype = _attr(block, "type", "")
        if btype == "text":
            text_parts.append(str(_attr(block, "text", "") or ""))
        elif btype == "tool_use":
            calls.append(
                ToolCall(
                    call_id=str(_attr(block, "id", "") or ""),
                    name=str(_attr(block, "name", "") or ""),
                    arguments=dict(_attr(block, "input", {}) or {}),
                )
            )
    return "".join(text_parts), calls, stop_reason


def parse_ollama_message(msg: dict[str, Any], turn_idx: int) -> tuple[str, list[ToolCall], str]:
    """Extract (text, tool_calls, stop_reason) from an Ollama /api/chat response.

    Ollama response shape: {"message": {"role":"assistant", "content":"...",
    "tool_calls":[{"function":{"name":"..","arguments":{...}}}]}, "done":true}.
    Ollama has no native call id, so we synthesize one as f"{name}-{turn_idx}-{i}".
    A stop_reason of "tool_use" is inferred when tool_calls are present; otherwise
    "end_turn" when done=true.
    """
    inner = msg.get("message") if isinstance(msg.get("message"), dict) else msg
    inner = inner or {}
    text = str(inner.get("content") or "")

    calls: list[ToolCall] = []
    raw_calls = inner.get("tool_calls") or []
    for i, rc in enumerate(raw_calls):
        fn = rc.get("function") or {}
        name = str(fn.get("name") or "")
        args_field = fn.get("arguments")
        # Ollama's native endpoint returns a parsed object; the OpenAI-compat
        # endpoint returns a JSON string. Accept either.
        if isinstance(args_field, str):
            import json

            try:
                args = json.loads(args_field)
            except json.JSONDecodeError:
                args = {}
        elif isinstance(args_field, dict):
            args = args_field
        else:
            args = {}
        calls.append(
            ToolCall(
                call_id=f"{name or 'call'}-{turn_idx}-{i}",
                name=name,
                arguments=args,
            )
        )

    if calls:
        stop_reason = "tool_use"
    elif msg.get("done"):
        stop_reason = "end_turn"
    else:
        stop_reason = ""
    return text, calls, stop_reason


# ---------------------------------------------------------------------------
# Tool results -> provider follow-up messages
# ---------------------------------------------------------------------------


def tool_results_for_anthropic(results: list[ToolResult]) -> dict[str, Any]:
    """Build the SINGLE user message that carries tool_result blocks.

    Per Anthropic's contract, tool_result blocks must be the first blocks in
    the user message and that user message must immediately follow the
    assistant turn that emitted the tool_use blocks. The caller places this
    message directly after echoing the assistant turn.
    """
    blocks: list[dict[str, Any]] = []
    for r in results:
        block: dict[str, Any] = {
            "type": "tool_result",
            "tool_use_id": r.call_id,
            "content": r.content,
        }
        if r.is_error:
            block["is_error"] = True
        blocks.append(block)
    return {"role": "user", "content": blocks}


def tool_results_for_ollama(results: list[ToolResult]) -> list[dict[str, Any]]:
    """Build Ollama follow-up messages, one per result, in emission order.

    Ollama has no tool_use_id; association is positional, so the caller MUST
    preserve the order in which ToolCalls were emitted.
    """
    return [
        {
            "role": "tool",
            "content": r.content,
            "tool_name": r.name,
        }
        for r in results
    ]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _attr(obj: Any, key: str, default: Any) -> Any:
    """Get `key` from either an SDK object (getattr) or a dict (.get)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
