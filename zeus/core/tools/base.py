# zeus/core/tools/base.py — Pydantic types for chat-path tool-use (LAB Zeus 10 / step 1)
from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, Field, field_validator

# snake_case, 2..41 chars, starts with a letter. Matches OpenAI / Anthropic /
# Ollama tool-name conventions and is safe to drop into URLs and log lines.
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{1,40}$")


class ToolSpec(BaseModel):
    """Declarative description of a tool the chat LLM can call.

    The handler is stored alongside the spec in the registry rather than on
    the model itself so ToolSpec remains trivially serialisable (admin UI,
    logs, provider adapters).

    `cacheable` defaults to False (safe). Opt a tool in only when identical
    args returning identical results is actually true — i.e. the tool is
    idempotent AND has no time-sensitive component. `web_search` is
    cacheable; `current_time` is not.
    """

    name: str
    description: str = Field(..., min_length=8)
    parameters: dict[str, Any]  # JSON Schema, object form
    aegis_policy: str = "tool_arguments"
    timeout_seconds: float = 30.0
    cacheable: bool = False

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError(f"invalid tool name {v!r}; must match {_NAME_RE.pattern}")
        return v

    @field_validator("parameters")
    @classmethod
    def _validate_parameters(cls, v: dict[str, Any]) -> dict[str, Any]:
        if v.get("type") != "object":
            raise ValueError("tool parameters must be JSON Schema of type=object")
        return v


class ToolCall(BaseModel):
    """A single tool invocation emitted by the chat LLM."""

    call_id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Outcome of executing a ToolCall. Content is serialised text fed back to the model."""

    call_id: str
    name: str
    content: str
    is_error: bool = False
    duration_ms: int = 0


# A registered handler: async callable that takes parsed arguments and returns
# a ToolResult. Handlers should catch their own expected errors and return
# is_error=True; unexpected exceptions are caught by run_tool_loop.
ToolHandler = Callable[[dict[str, Any]], Awaitable[ToolResult]]
