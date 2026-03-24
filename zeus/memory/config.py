# zeus/memory/config.py
"""Mnemosyne — mem0 configuration with environment-based backend switching.

This module configures mem0 to use different LLM backends based on ZEUS_ENV:
  - dev:  Claude API (Sonnet 4.6) for extraction and inference
  - prod: Ollama with local models (Qwen2.5-7B) on the 3080 server

mem0 uses hybrid storage:
  - Vector DB (Qdrant) for semantic search
  - Graph DB for relationships
  - KV store for fast facts
"""

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QdrantConfig:
    """Qdrant vector database configuration."""
    host: str = field(default_factory=lambda: os.getenv("QDRANT_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("QDRANT_PORT", "6333")))
    collection_name: str = "zeus_memories"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": "qdrant",
            "config": {
                "host": self.host,
                "port": self.port,
                "collection_name": self.collection_name,
            },
        }


@dataclass 
class EmbedderConfig:
    """Embedding model configuration — uses Ollama for both dev and prod."""
    model: str = "nomic-embed-text"
    ollama_host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": "ollama",
            "config": {
                "model": self.model,
                "ollama_base_url": self.ollama_host,
            },
        }


@dataclass
class LLMConfig:
    """LLM configuration for mem0 extraction — switches based on ZEUS_ENV."""
    provider: str = ""
    model: str = ""
    api_key: str | None = None
    ollama_host: str = ""
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create LLM config based on ZEUS_ENV."""
        env = os.getenv("ZEUS_ENV", "dev")
        
        if env == "prod":
            return cls(
                provider="ollama",
                model=os.getenv("ZEUS_LLM_MODEL", "qwen2.5:7b-instruct-q4_K_M"),
                ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            )
        else:
            # Default to dev mode with Claude API
            return cls(
                provider="anthropic",
                model=os.getenv("ZEUS_LLM_MODEL", "claude-sonnet-4-20250514"),
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
    
    def to_dict(self) -> dict[str, Any]:
        if self.provider == "ollama":
            return {
                "provider": "ollama",
                "config": {
                    "model": self.model,
                    "ollama_base_url": self.ollama_host,
                    "temperature": 0.1,
                    "max_tokens": 2000,
                },
            }
        else:
            return {
                "provider": "anthropic",
                "config": {
                    "model": self.model,
                    "api_key": self.api_key,
                    "temperature": 0.1,
                    "max_tokens": 2000,
                },
            }


@dataclass
class Mem0Config:
    """Complete mem0 configuration."""
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    embedder: EmbedderConfig = field(default_factory=EmbedderConfig)
    llm: LLMConfig = field(default_factory=LLMConfig.from_env)
    
    # mem0 specific settings
    version: str = "v1.1"
    user_id: str = "zeus-default"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to mem0-compatible config dict."""
        return {
            "version": self.version,
            "vector_store": self.qdrant.to_dict(),
            "embedder": self.embedder.to_dict(),
            "llm": self.llm.to_dict(),
        }


def get_mem0_config() -> dict[str, Any]:
    """Get mem0 configuration dict based on current environment.
    
    Usage:
        from zeus.memory.config import get_mem0_config
        from mem0 import Memory
        
        config = get_mem0_config()
        memory = Memory.from_config(config)
    """
    return Mem0Config().to_dict()


def get_env_info() -> dict[str, str]:
    """Get current environment info for debugging."""
    env = os.getenv("ZEUS_ENV", "dev")
    config = Mem0Config()
    
    return {
        "environment": env,
        "llm_provider": config.llm.provider,
        "llm_model": config.llm.model,
        "embedder_model": config.embedder.model,
        "qdrant_host": f"{config.qdrant.host}:{config.qdrant.port}",
    }


# Convenience exports
__all__ = [
    "Mem0Config",
    "QdrantConfig", 
    "EmbedderConfig",
    "LLMConfig",
    "get_mem0_config",
    "get_env_info",
]
