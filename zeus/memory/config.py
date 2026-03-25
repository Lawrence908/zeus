# zeus/memory/config.py — Mnemosyne configuration
# Builds mem0 config that switches LLM/embedder based on ZEUS_ENV
import os
from typing import Any


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

    # Shared: vector store and embedder are identical in both envs
    # so that memories written in dev are readable in prod
    base_config: dict[str, Any] = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "url": qdrant_url,
                "collection_name": qdrant_collection,
                "embedding_model_dims": 768,  # nomic-embed-text output dim
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

    # Provider-specific model values with compatibility fallbacks.
    claude_model = os.getenv(
        "ZEUS_CLAUDE_MODEL",
        os.getenv("ZEUS_DEV_MODEL", "claude-sonnet-4-6"),
    )
    ollama_model = os.getenv(
        "ZEUS_OLLAMA_MODEL",
        os.getenv("ZEUS_PROD_MODEL", "qwen2.5:7b-instruct"),
    )

    if provider == "ollama":
        # Local extraction path (default in prod, optional in dev).
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
        # Cloud extraction path (default in dev, optional in prod).
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


def _patch_anthropic_params():
    """Patch mem0's Anthropic LLM to avoid sending both temperature and top_p.

    claude-sonnet-4-6 rejects requests that include both parameters.
    mem0's base class always sends both, so we strip top_p before the
    Anthropic client sees the kwargs.
    """
    try:
        from mem0.llms.anthropic import AnthropicLLM
    except ImportError:
        return

    _orig = AnthropicLLM._get_common_params

    def _patched(self, **kwargs):
        params = _orig(self, **kwargs)
        params.pop("top_p", None)
        return params

    AnthropicLLM._get_common_params = _patched


def get_memory_client():
    """Initialize and return a configured mem0 Memory instance."""
    from mem0 import Memory

    _patch_anthropic_params()
    config = get_memory_config()
    return Memory.from_config(config)
