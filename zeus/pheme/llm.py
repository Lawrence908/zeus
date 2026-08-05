# zeus/pheme/llm.py - Local-only LLM entry point for Pheme analytical stages.
#
# Wraps small_llm_call pinned to the ollama provider so no Pheme stage can
# reach a cloud provider, and adds a validate-and-retry loop (the reflection
# pattern from zeus/core/query.py) because qwen2.5:7b is unreliable at
# structured output. Every structured stage goes through pheme_llm_call.
from __future__ import annotations

import logging
import os
from typing import TypeVar

from pydantic import BaseModel

from zeus.core.small_llm import AllProvidersFailed, small_llm_call

logger = logging.getLogger("zeus.pheme.llm")

T = TypeVar("T", bound=BaseModel)

_MAX_ATTEMPTS = 3


def pheme_model() -> str:
    return os.getenv("PHEME_LLM_MODEL", "qwen2.5:7b-instruct").strip()


class PhemeLLMFailed(RuntimeError):
    """Raised when local Ollama cannot produce a valid structured result."""


async def pheme_llm_call(
    *,
    system: str,
    user: str,
    response_format: type[T],
    max_tokens: int = 512,
    caller: str = "pheme",
) -> T:
    """Structured local-only call with up to 3 validate-and-retry attempts.

    small_llm_call already does one in-provider repair retry on validation
    failure; this loop re-issues the whole call (fresh sampling) when that
    still comes back unparsed.
    """
    errors: list[str] = []
    prompt = user
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            result = await small_llm_call(
                system=system,
                user=prompt,
                max_tokens=max_tokens,
                response_format=response_format,
                min_privacy_tier=1,
                providers=["ollama"],
                model_hint=pheme_model(),
                caller=caller,
            )
        except AllProvidersFailed as exc:
            raise PhemeLLMFailed(f"local ollama unavailable: {exc}") from exc
        if result.parsed is not None:
            return result.parsed  # type: ignore[return-value]
        errors.append(f"attempt {attempt}: unparsed output {result.text[:120]!r}")
        logger.warning("pheme llm attempt %d/%d failed validation (%s)", attempt, _MAX_ATTEMPTS, caller)
        prompt = (
            user
            + "\n\nYour previous answer was not valid JSON for the requested schema. "
            "Respond with ONLY the JSON object, no prose, no code fences."
        )
    raise PhemeLLMFailed("; ".join(errors))


async def pheme_llm_text(
    *,
    system: str,
    user: str,
    max_tokens: int = 1024,
    caller: str = "pheme",
) -> str:
    """Free-text local-only call (digest synthesis)."""
    try:
        result = await small_llm_call(
            system=system,
            user=user,
            max_tokens=max_tokens,
            response_format="text",
            min_privacy_tier=1,
            providers=["ollama"],
            model_hint=pheme_model(),
            caller=caller,
        )
    except AllProvidersFailed as exc:
        raise PhemeLLMFailed(f"local ollama unavailable: {exc}") from exc
    return result.text.strip()
