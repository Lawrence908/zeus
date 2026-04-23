# zeus/core/small_llm.py — Small-task LLM provider router.
#
# General-purpose LLM entry point for structured-output / batch tasks that
# shouldn't live on the chat LLM path (`_run_llm()` in zeus/core/query.py).
# First caller is MemoryStore fact extraction; future callers include chat
# session titles, newsletter bullet condensation, privacy classifier,
# tool-argument validation hints, KAIROS observation summaries.
#
# Design principles:
#   * Privacy tier gating: every call declares min_privacy_tier (1 or 2).
#     Tier-1 means "SAFE for PII" — Gemini free tier is excluded (trains on
#     inputs), Cerebras is excluded (retention unclear). See CLAUDE.md.
#   * Provider chain with fallback on transient errors (429/5xx/timeout).
#   * Native structured output (response_format Pydantic model) + one
#     repair-retry on ValidationError, then fall back to raw text.
#   * Hard daily-$ cap across paid providers, tracked in SQLite.
#   * No LiteLLM dep (supply-chain attack Mar 2026).
from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("zeus.small_llm")

# ---------------------------------------------------------------------------
# Config + types
# ---------------------------------------------------------------------------

DEFAULT_CHAIN = os.getenv(
    "ZEUS_SMALL_LLM_CHAIN",
    "gemini_paid,groq,openrouter,anthropic_haiku,ollama",
).split(",")

DAILY_USD_CAP = float(os.getenv("ZEUS_SMALL_LLM_DAILY_USD_CAP", "2.00"))

USAGE_DB_PATH = Path(
    os.getenv("ZEUS_SMALL_LLM_USAGE_DB", "zeus/data/small_llm_usage.db")
)


@dataclass
class ProviderSpec:
    name: str
    privacy_tier: int              # 1 = SAFE for PII, 2 = OK for depersonalised
    default_model: str
    allowed_models: tuple[str, ...]
    is_paid: bool                  # counts toward DAILY_USD_CAP
    # Cost per 1M tokens (in_cost, out_cost) — used for usage log, 0 for free/local.
    cost_per_mtok_in: float = 0.0
    cost_per_mtok_out: float = 0.0


@dataclass
class SmallLLMResult:
    text: str
    parsed: BaseModel | None
    provider_used: str
    model_used: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    attempts: int
    errors: list[str] = field(default_factory=list)


class AllProvidersFailed(RuntimeError):
    """Raised when every provider in the tier-filtered chain errored."""


# ---------------------------------------------------------------------------
# Provider registry — providers advertise themselves as "enabled" by having
# their required env vars set. Adding a new provider = one function + one
# registry entry.
# ---------------------------------------------------------------------------

def _split_env(name: str, default: str) -> tuple[str, ...]:
    raw = os.getenv(name) or default
    return tuple(m.strip() for m in raw.split(",") if m.strip())


_PROVIDERS: dict[str, ProviderSpec] = {
    "gemini_paid": ProviderSpec(
        name="gemini_paid",
        privacy_tier=1,  # Only when billing is enabled on the key; free tier TRAINS.
        default_model=os.getenv("ZEUS_GEMINI_PAID_MODEL", "gemini-2.5-flash-lite"),
        allowed_models=_split_env(
            "ZEUS_GEMINI_PAID_ALLOWED_MODELS",
            "gemini-2.5-flash-lite,gemini-2.5-flash,gemini-2.0-flash",
        ),
        is_paid=True,
        # Flash-Lite pricing (paid tier): $0.10 / $0.40 per M tokens.
        cost_per_mtok_in=0.10,
        cost_per_mtok_out=0.40,
    ),
    "groq": ProviderSpec(
        name="groq",
        privacy_tier=1,  # Enable ZDR in Groq console to keep tier 1.
        default_model=os.getenv("ZEUS_GROQ_MODEL", "llama-3.3-70b-versatile"),
        allowed_models=_split_env(
            "ZEUS_GROQ_ALLOWED_MODELS",
            "llama-3.3-70b-versatile,llama-4-scout-17b,kimi-k2",
        ),
        is_paid=False,  # Free tier up to 14.4K calls/day; we don't track against USD cap.
    ),
    "openrouter": ProviderSpec(
        name="openrouter",
        # Tier depends on upstream model / data-policy filter. Default to tier 2
        # to be safe; callers that trust the configured models can override by
        # setting ZEUS_OPENROUTER_TIER=1 after confirming data-policy filter.
        privacy_tier=int(os.getenv("ZEUS_OPENROUTER_TIER", "2")),
        default_model=os.getenv("ZEUS_OPENROUTER_MODEL", "deepseek/deepseek-chat-v3"),
        allowed_models=_split_env(
            "ZEUS_OPENROUTER_ALLOWED_MODELS",
            "deepseek/deepseek-chat-v3,meta-llama/llama-3.3-70b-instruct:free,"
            "google/gemini-2.5-flash-lite,openai/gpt-5-nano,openai/gpt-4o-mini,"
            "anthropic/claude-sonnet-4.5",
        ),
        is_paid=True,  # Treated as paid — OpenRouter can route to paid upstreams.
        cost_per_mtok_in=0.30,   # rough average; actual cost depends on model
        cost_per_mtok_out=1.20,
    ),
    "anthropic_haiku": ProviderSpec(
        name="anthropic_haiku",
        privacy_tier=1,
        default_model=os.getenv(
            "ZEUS_ANTHROPIC_HAIKU_MODEL", "claude-haiku-4-5-20251001"
        ),
        allowed_models=_split_env(
            "ZEUS_ANTHROPIC_HAIKU_ALLOWED_MODELS",
            "claude-haiku-4-5-20251001,claude-haiku-4-5",
        ),
        is_paid=True,
        cost_per_mtok_in=1.00,
        cost_per_mtok_out=5.00,
    ),
    "ollama": ProviderSpec(
        name="ollama",
        privacy_tier=1,
        default_model=os.getenv("ZEUS_OLLAMA_SMALL_MODEL", "qwen2.5:7b-instruct"),
        allowed_models=_split_env(
            "ZEUS_OLLAMA_SMALL_ALLOWED_MODELS",
            "qwen2.5:7b-instruct,llama3.1:8b-instruct-q4_K_M,qwen3:8b",
        ),
        is_paid=False,
    ),
}


def _is_enabled(spec: ProviderSpec) -> bool:
    if spec.name == "gemini_paid":
        return bool(os.getenv("GOOGLE_API_KEY"))
    if spec.name == "groq":
        return bool(os.getenv("GROQ_API_KEY"))
    if spec.name == "openrouter":
        return bool(os.getenv("OPENROUTER_API_KEY"))
    if spec.name == "anthropic_haiku":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    if spec.name == "ollama":
        return bool(os.getenv("OLLAMA_URL", "http://localhost:11435"))
    return False


# ---------------------------------------------------------------------------
# Usage log — stdlib sqlite3 for dep-footprint discipline.
# ---------------------------------------------------------------------------

_USAGE_INIT_SQL = """
CREATE TABLE IF NOT EXISTS usage (
    ts TEXT NOT NULL,
    caller TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    tier INTEGER NOT NULL,
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    ok INTEGER NOT NULL DEFAULT 1,
    error TEXT
);
CREATE INDEX IF NOT EXISTS ix_usage_ts ON usage (ts);
CREATE INDEX IF NOT EXISTS ix_usage_provider_ts ON usage (provider, ts);
"""


def _ensure_usage_db() -> sqlite3.Connection:
    USAGE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(USAGE_DB_PATH))
    conn.executescript(_USAGE_INIT_SQL)
    return conn


def _log_usage(
    *,
    caller: str | None,
    provider: str,
    model: str,
    tier: int,
    tokens_in: int,
    tokens_out: int,
    cost_usd: float,
    latency_ms: int,
    ok: bool,
    error: str | None,
) -> None:
    try:
        with closing(_ensure_usage_db()) as conn:
            conn.execute(
                "INSERT INTO usage VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    caller,
                    provider,
                    model,
                    tier,
                    tokens_in,
                    tokens_out,
                    cost_usd,
                    latency_ms,
                    1 if ok else 0,
                    error,
                ),
            )
            conn.commit()
    except sqlite3.Error as exc:
        logger.warning("usage log write failed: %s", exc)


def _daily_paid_spend_usd() -> float:
    """Sum paid-provider cost_usd for the current UTC day."""
    today = datetime.now(timezone.utc).date().isoformat()
    try:
        with closing(_ensure_usage_db()) as conn:
            cur = conn.execute(
                "SELECT COALESCE(SUM(cost_usd), 0) FROM usage "
                "WHERE ok=1 AND cost_usd > 0 AND ts >= ?",
                (f"{today}T00:00:00+00:00",),
            )
            row = cur.fetchone()
            return float(row[0] or 0.0)
    except sqlite3.Error as exc:
        logger.warning("usage log read failed: %s", exc)
        return 0.0


# ---------------------------------------------------------------------------
# Structured output helpers
# ---------------------------------------------------------------------------

def _schema_hint(response_format: type[BaseModel] | Literal["text"]) -> str:
    """A human-readable JSON-schema hint embedded in the user message.

    Belt-and-braces: we pass the provider's native response_format too, but
    some providers ignore it or return prose. Including the schema in the
    prompt makes the repair-retry path almost always succeed.
    """
    if response_format == "text":
        return ""
    schema = response_format.model_json_schema()
    return (
        "\n\nReturn ONLY valid JSON matching this schema (no prose, no markdown fences):\n"
        + json.dumps(schema, indent=2)
    )


def _strip_fences(text: str) -> str:
    """Extract the first complete JSON object/array from a provider response.

    Handles three common provider misbehaviours:
      1. ```json ... ``` fences (some Ollama models, occasional Gemini)
      2. Trailing prose after a JSON object ("...} \n\nThe text had no facts.")
      3. Leading prose before a JSON object ("Sure, here's the JSON: {...}")
    """
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        if s.endswith("```"):
            s = s[: -3]
        s = s.strip()

    # Find the first balanced JSON object/array. Skips strings correctly so that
    # braces inside "..." don't throw off the depth counter.
    start = -1
    for i, ch in enumerate(s):
        if ch in "{[":
            start = i
            break
    if start < 0:
        return s

    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                return s[start : i + 1]
    return s[start:]


def _try_parse(
    text: str, response_format: type[BaseModel] | Literal["text"]
) -> tuple[BaseModel | None, str | None]:
    if response_format == "text":
        return None, None
    try:
        return response_format.model_validate_json(_strip_fences(text)), None
    except ValidationError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, f"invalid json: {exc}"


# ---------------------------------------------------------------------------
# Provider implementations (HTTP-only; no SDKs unless we already have them).
# ---------------------------------------------------------------------------

async def _call_anthropic_haiku(
    *, system: str, user: str, max_tokens: int, model: str
) -> tuple[str, int, int]:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = ""
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            text += block.text
    usage = getattr(resp, "usage", None)
    tin = int(getattr(usage, "input_tokens", 0) or 0) if usage else 0
    tout = int(getattr(usage, "output_tokens", 0) or 0) if usage else 0
    return text, tin, tout


async def _call_ollama(
    *, system: str, user: str, max_tokens: int, model: str
) -> tuple[str, int, int]:
    url = (os.getenv("OLLAMA_URL", "http://localhost:11435")).rstrip("/")
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.1},
    }
    # Structured-output prompts (schema + examples) can push qwen2.5:7b past
    # 120s cold. Keep the default loose; bound on a bigger host via env.
    read_s = float(os.getenv("ZEUS_OLLAMA_SMALL_READ_TIMEOUT_SEC", "300"))
    timeout = httpx.Timeout(connect=10.0, read=read_s, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{url}/api/chat", json=body)
        resp.raise_for_status()
        data = resp.json()
    text = str((data.get("message") or {}).get("content", ""))
    tin = int(data.get("prompt_eval_count", 0) or 0)
    tout = int(data.get("eval_count", 0) or 0)
    return text, tin, tout


async def _call_openai_compat(
    *,
    system: str,
    user: str,
    max_tokens: int,
    model: str,
    base_url: str,
    api_key: str,
    extra_headers: dict[str, str] | None = None,
) -> tuple[str, int, int]:
    """Unified caller for OpenAI-compatible chat endpoints.

    Works with: Gemini (https://generativelanguage.googleapis.com/v1beta/openai),
    Groq (https://api.groq.com/openai/v1), OpenRouter (https://openrouter.ai/api/v1),
    DeepInfra, Together, Cerebras. Provider-specific JSON-mode quirks are mild
    enough that the schema-in-prompt fallback handles them uniformly.
    """
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    timeout = httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)

    # 429 backoff with jitter — keeps cheap tier-1 providers (Gemini paid in
    # particular) in play under burst load instead of immediately falling
    # through to more expensive providers. Comma-separated ms delays; empty
    # disables retries entirely.
    default_delays_ms = [2000, 5000, 15000]
    delays_ms_raw = os.getenv("ZEUS_SMALL_LLM_RETRY_DELAYS_MS", "2000,5000,15000")
    if delays_ms_raw.strip() == "":
        delays_ms = []
    else:
        delays_ms = []
        invalid_delay_tokens: list[str] = []
        for x in delays_ms_raw.split(","):
            token = x.strip()
            if not token:
                continue
            try:
                delays_ms.append(int(token))
            except ValueError:
                invalid_delay_tokens.append(token)
        if invalid_delay_tokens:
            logger.warning(
                "Ignoring invalid ZEUS_SMALL_LLM_RETRY_DELAYS_MS token(s): %s",
                ", ".join(invalid_delay_tokens),
            )
        if not delays_ms:
            logger.warning(
                "ZEUS_SMALL_LLM_RETRY_DELAYS_MS had no valid integer delays; "
                "falling back to default retry delays: %s",
                default_delays_ms,
            )
            delays_ms = default_delays_ms

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(len(delays_ms) + 1):
            resp = await client.post(
                f"{base_url.rstrip('/')}/chat/completions", json=body, headers=headers
            )
            if resp.status_code != 429 or attempt == len(delays_ms):
                break
            await resp.aclose()
            delay = delays_ms[attempt] / 1000.0
            delay *= 0.8 + 0.4 * random.random()  # ±20% jitter
            await asyncio.sleep(delay)
        resp.raise_for_status()
        data = resp.json()
    choices = data.get("choices") or []
    text = ""
    if choices:
        msg = choices[0].get("message") or {}
        text = str(msg.get("content") or "")
    usage = data.get("usage") or {}
    tin = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    tout = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    return text, tin, tout


async def _call_gemini_paid(
    *, system: str, user: str, max_tokens: int, model: str
) -> tuple[str, int, int]:
    return await _call_openai_compat(
        system=system,
        user=user,
        max_tokens=max_tokens,
        model=model,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        api_key=os.environ["GOOGLE_API_KEY"],
    )


async def _call_groq(
    *, system: str, user: str, max_tokens: int, model: str
) -> tuple[str, int, int]:
    return await _call_openai_compat(
        system=system,
        user=user,
        max_tokens=max_tokens,
        model=model,
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.environ["GROQ_API_KEY"],
    )


async def _call_openrouter(
    *, system: str, user: str, max_tokens: int, model: str
) -> tuple[str, int, int]:
    # Optional headers surface your app in OpenRouter's dashboard & leaderboards.
    extra: dict[str, str] = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost:8203")
    title = os.getenv("OPENROUTER_X_TITLE", "Zeus (self-hosted)")
    if referer:
        extra["HTTP-Referer"] = referer
    if title:
        extra["X-Title"] = title
    return await _call_openai_compat(
        system=system,
        user=user,
        max_tokens=max_tokens,
        model=model,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.environ["OPENROUTER_API_KEY"],
        extra_headers=extra,
    )


_PROVIDER_CALLS = {
    "gemini_paid": _call_gemini_paid,
    "groq": _call_groq,
    "openrouter": _call_openrouter,
    "anthropic_haiku": _call_anthropic_haiku,
    "ollama": _call_ollama,
}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def small_llm_call(
    *,
    system: str,
    user: str,
    max_tokens: int = 512,
    response_format: type[BaseModel] | Literal["text"] = "text",
    min_privacy_tier: Literal[1, 2] = 2,
    model_hint: str | None = None,
    caller: str | None = None,
) -> SmallLLMResult:
    """Route a small-task LLM call through the tier-filtered provider chain.

    Fallback on transient error (429/5xx/timeout/JSON-validation). At most one
    attempt per provider; on structured-output ValidationError we do one
    in-provider repair-retry before moving on.
    """
    chain = [name.strip() for name in DEFAULT_CHAIN if name.strip()]
    errors: list[str] = []
    attempts = 0
    last_text = ""
    last_tin = 0
    last_tout = 0

    user_with_schema = user + _schema_hint(response_format)
    paid_spend = _daily_paid_spend_usd()

    for provider_name in chain:
        spec = _PROVIDERS.get(provider_name)
        if spec is None:
            errors.append(f"{provider_name}: unknown provider")
            continue
        if not _is_enabled(spec):
            errors.append(f"{provider_name}: not enabled (missing env)")
            continue
        if spec.privacy_tier > min_privacy_tier:
            errors.append(
                f"{provider_name}: tier {spec.privacy_tier} > required {min_privacy_tier}"
            )
            continue
        if spec.is_paid and paid_spend >= DAILY_USD_CAP:
            errors.append(
                f"{provider_name}: daily USD cap ${DAILY_USD_CAP} reached (${paid_spend:.2f})"
            )
            continue

        model = model_hint if model_hint in spec.allowed_models else spec.default_model
        call = _PROVIDER_CALLS[provider_name]

        # Up to 2 attempts: original + one repair retry on ValidationError.
        parsed: BaseModel | None = None
        parse_err: str | None = None
        for attempt in range(2):
            attempts += 1
            t0 = time.perf_counter()
            try:
                prompt = user_with_schema
                if attempt == 1 and parse_err:
                    prompt = (
                        user_with_schema
                        + f"\n\nYour previous response failed validation: {parse_err}\n"
                        "Return ONLY valid JSON matching the schema."
                    )
                text, tin, tout = await call(
                    system=system, user=prompt, max_tokens=max_tokens, model=model
                )
            except Exception as exc:  # transient / network / SDK error
                latency_ms = int((time.perf_counter() - t0) * 1000)
                err = f"{provider_name}({model}): {type(exc).__name__}: {exc}"
                errors.append(err)
                logger.warning("small_llm call failed — %s", err)
                _log_usage(
                    caller=caller,
                    provider=provider_name,
                    model=model,
                    tier=spec.privacy_tier,
                    tokens_in=0,
                    tokens_out=0,
                    cost_usd=0.0,
                    latency_ms=latency_ms,
                    ok=False,
                    error=str(exc)[:500],
                )
                break  # fall through to next provider

            latency_ms = int((time.perf_counter() - t0) * 1000)
            last_text, last_tin, last_tout = text, tin, tout
            cost_usd = (
                (tin / 1_000_000) * spec.cost_per_mtok_in
                + (tout / 1_000_000) * spec.cost_per_mtok_out
            )
            paid_spend += cost_usd if spec.is_paid else 0.0

            parsed, parse_err = _try_parse(text, response_format)
            ok = parse_err is None
            _log_usage(
                caller=caller,
                provider=provider_name,
                model=model,
                tier=spec.privacy_tier,
                tokens_in=tin,
                tokens_out=tout,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                ok=ok,
                error=parse_err,
            )
            if ok or response_format == "text":
                return SmallLLMResult(
                    text=text,
                    parsed=parsed,
                    provider_used=provider_name,
                    model_used=model,
                    latency_ms=latency_ms,
                    tokens_in=tin,
                    tokens_out=tout,
                    cost_usd=cost_usd,
                    attempts=attempts,
                    errors=errors,
                )
            # ValidationError — repair retry next iteration on same provider.

        # Second attempt failed validation too — fall through to next provider.
        if parse_err:
            errors.append(f"{provider_name}: validation failed twice — {parse_err[:200]}")

    # Every provider exhausted. If any provider returned *some* text,
    # return it with parsed=None so the caller can fall back (e.g. store raw).
    if last_text:
        logger.warning(
            "small_llm: all providers failed structured output; returning raw text"
        )
        return SmallLLMResult(
            text=last_text,
            parsed=None,
            provider_used="fallback_raw",
            model_used="",
            latency_ms=0,
            tokens_in=last_tin,
            tokens_out=last_tout,
            cost_usd=0.0,
            attempts=attempts,
            errors=errors,
        )
    raise AllProvidersFailed("; ".join(errors) or "no providers configured")
