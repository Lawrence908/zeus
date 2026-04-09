# zeus/memory/config.py — Mnemosyne configuration
# Builds mem0 config that switches LLM/embedder based on ZEUS_ENV
import os
import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenUsage:
    """Thread-safe accumulator for LLM token usage during ingest."""

    input_tokens: int = 0
    output_tokens: int = 0
    llm_calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record(self, input_tok: int, output_tok: int) -> None:
        with self._lock:
            self.input_tokens += input_tok
            self.output_tokens += output_tok
            self.llm_calls += 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


# Module-level tracker — reset per ingest run via reset_token_usage().
_token_usage = TokenUsage()


def get_token_usage() -> TokenUsage:
    return _token_usage


def reset_token_usage() -> None:
    global _token_usage
    _token_usage = TokenUsage()


def get_memory_config() -> dict[str, Any]:
    """Return mem0 configuration dict based on environment and provider override.

    Default provider selection:
      - dev  -> Claude API
      - prod -> Ollama

    Optional override:
      - ZEUS_LLM=claude forces Claude in any environment
      - ZEUS_LLM=ollama forces Ollama in any environment

    Embeddings always use Ollama so vectors remain compatible across environments.
    """
    env = os.getenv("ZEUS_ENV", "dev")
    llm_override = os.getenv("ZEUS_LLM", "").strip().lower()

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection = os.getenv("QDRANT_COLLECTION", "zeus_memories")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11435")
    embed_model = os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text")

    base_config: dict[str, Any] = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "url": qdrant_url,
                "collection_name": qdrant_collection,
                "embedding_model_dims": 768,
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": embed_model,
                "ollama_base_url": ollama_url,
            },
        },
        "version": "v1.1",
    }

    if llm_override and llm_override not in {"claude", "ollama"}:
        raise ValueError(
            "ZEUS_LLM must be one of: 'claude', 'ollama', or unset."
        )

    if llm_override:
        provider = llm_override
    else:
        provider = "ollama" if env == "prod" else "claude"

    claude_model = os.getenv(
        "ZEUS_CLAUDE_MODEL",
        os.getenv("ZEUS_DEV_MODEL", "claude-sonnet-4-6"),
    )
    ollama_model = os.getenv(
        "ZEUS_OLLAMA_MODEL",
        os.getenv("ZEUS_PROD_MODEL", "qwen2.5:7b-instruct"),
    )

    if provider == "ollama":
        base_config["llm"] = {
            "provider": "ollama",
            "config": {
                "model": ollama_model,
                "ollama_base_url": ollama_url,
                "temperature": 0.1,
                "max_tokens": 2048,
            },
        }
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY required when using Claude "
                "(ZEUS_ENV=dev default or ZEUS_LLM=claude override)."
            )
        base_config["llm"] = {
            "provider": "anthropic",
            "config": {
                "model": claude_model,
                "api_key": api_key,
                "temperature": 0.1,
                "max_tokens": 2048,
            },
        }

    return base_config


_patched = False
_embed_patched = False


def _patch_ollama_embedding() -> None:
    """Patch mem0's OllamaEmbedding to set a connect/read timeout on the
    underlying httpx client, preventing indefinite hangs when Ollama is
    overloaded or unresponsive.

    Controlled by OLLAMA_EMBED_TIMEOUT_SEC (default: 120).
    Set to 0 to disable the patch (no timeout).
    """
    global _embed_patched
    if _embed_patched:
        return
    _embed_patched = True

    raw = os.getenv("OLLAMA_EMBED_TIMEOUT_SEC", "120").strip()
    try:
        timeout_sec = float(raw)
    except ValueError:
        timeout_sec = 120.0
    if timeout_sec <= 0:
        return

    try:
        from mem0.embeddings.ollama import OllamaEmbedding
        from ollama import Client
    except ImportError:
        return

    _orig_init = OllamaEmbedding.__init__

    def _init_with_timeout(self, config=None):  # type: ignore[override]
        _orig_init(self, config)
        self.client = Client(
            host=self.config.ollama_base_url,
            timeout=timeout_sec,
        )

    OllamaEmbedding.__init__ = _init_with_timeout  # type: ignore[method-assign]


def _patch_anthropic_llm():
    """Patch mem0's Anthropic LLM for two things:

    1. Strip top_p so only temperature is sent (claude-sonnet-4-6 rejects both).
    2. Intercept API responses to accumulate token usage stats.
    """
    global _patched
    if _patched:
        return
    _patched = True

    try:
        from mem0.llms.anthropic import AnthropicLLM
    except ImportError:
        return

    _orig_params = AnthropicLLM._get_common_params

    def _patched_params(self, **kwargs):
        params = _orig_params(self, **kwargs)
        params.pop("top_p", None)
        return params

    AnthropicLLM._get_common_params = _patched_params

    _orig_generate = AnthropicLLM.generate_response

    def _tracked_generate(self, messages, response_format=None, tools=None,
                          tool_choice="auto", **kwargs):
        system_message = ""
        filtered_messages = []
        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:
                filtered_messages.append(message)

        params = self._get_supported_params(messages=messages, **kwargs)
        params.update({
            "model": self.config.model,
            "messages": filtered_messages,
            "system": system_message,
        })
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.messages.create(**params)

        if hasattr(response, "usage") and response.usage:
            _token_usage.record(
                input_tok=getattr(response.usage, "input_tokens", 0),
                output_tok=getattr(response.usage, "output_tokens", 0),
            )

        return response.content[0].text

    AnthropicLLM.generate_response = _tracked_generate


def get_memory_client():
    """Initialize and return a configured mem0 Memory instance."""
    from mem0 import Memory

    _patch_anthropic_llm()
    _patch_ollama_embedding()
    config = get_memory_config()
    return Memory.from_config(config)
