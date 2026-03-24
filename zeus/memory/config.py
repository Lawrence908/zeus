# zeus/memory/config.py — Mnemosyne configuration
# Builds mem0 config that switches LLM/embedder based on ZEUS_ENV
import os
from typing import Any


def get_memory_config() -> dict[str, Any]:
    """Return mem0 configuration dict based on ZEUS_ENV.

    Dev:  Claude API (Sonnet 4.6) for extraction, Ollama for embeddings
    Prod: Ollama (Qwen2.5-7B) for extraction, Ollama for embeddings

    Both environments use the same Qdrant instance and embedding model
    so vectors are compatible across dev/prod.
    """
    env = os.getenv("ZEUS_ENV", "dev")

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection = os.getenv("QDRANT_COLLECTION", "zeus_memories")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
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

    if env == "prod":
        # Prod: Ollama running Qwen2.5-7B-Instruct for memory extraction
        prod_model = os.getenv("ZEUS_PROD_MODEL", "qwen2.5:7b-instruct-q4_K_M")
        base_config["llm"] = {
            "provider": "ollama",
            "config": {
                "model": prod_model,
                "ollama_base_url": ollama_url,
                "temperature": 0.1,
                "max_tokens": 2048,
            },
        }
    else:
        # Dev: Claude API for higher-quality extraction during development
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        dev_model = os.getenv("ZEUS_DEV_MODEL", "claude-sonnet-4-6-20250514")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY required when ZEUS_ENV=dev. "
                "Set it in .env or switch to ZEUS_ENV=prod for local-only mode."
            )
        base_config["llm"] = {
            "provider": "anthropic",
            "config": {
                "model": dev_model,
                "api_key": api_key,
                "temperature": 0.1,
                "max_tokens": 2048,
            },
        }

    return base_config


def get_memory_client():
    """Initialize and return a configured mem0 Memory instance."""
    from mem0 import Memory

    config = get_memory_config()
    return Memory.from_config(config)
