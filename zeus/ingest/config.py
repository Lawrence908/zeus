# zeus/ingest/config.py — Declarative ingest config loader
#
# Loads zeus/ingest/config.yaml and validates per-source routing rules for the
# Memory / Knowledge / (Phase 2) Reference layers. See docs/memory-architecture-plan.md.
#
# Usage:
#   from zeus.ingest.config import load_ingest_config
#   cfg = load_ingest_config()                      # default path
#   cfg = load_ingest_config("custom/path.yaml")    # override
#   source_cfg = cfg.sources.get("obsidian")        # SourceConfig | None
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Literal

_ENV_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DEFAULT_CONFIG_PATH = "zeus/ingest/config.yaml"

Target = Literal["memory", "knowledge", "reference"]
# Phase 2: reference is a query-time proxy (kiwix/NOMAD), not an ingest target,
# but the schema accepts it so configs can declare intent without errors.
_SUPPORTED_TARGETS: set[str] = {"memory", "knowledge", "reference"}


class MarkdownRoot(BaseModel):
    """One base directory + glob set for the markdown source."""
    model_config = ConfigDict(extra="forbid")

    base_dir: str
    globs: list[str] = Field(default_factory=lambda: ["**/*.md"])
    exclude: list[str] = Field(default_factory=list)


class SourceConfig(BaseModel):
    """Per-source ingest routing and parameters.

    Only `target` is universally required. Other fields are source-specific;
    unknown fields are preserved in `extra` so new sources can be added without
    updating this schema immediately.
    """
    model_config = ConfigDict(extra="allow")

    target: Target

    # Common / optional path-shaped fields — declared so they get env-var expansion.
    path: str | None = None
    vault_path: str | None = None
    base_dir: str | None = None
    roots: list[MarkdownRoot] | None = None
    exclude: list[str] = Field(default_factory=list)

    # Numeric knobs (optional overrides of defaults).
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    limit: int | None = None
    max_commits: int | None = None
    days_back: int | None = None
    days_forward: int | None = None

    # kiwix_zim-specific.
    zim_dir: str | None = None
    books: list[str] | None = None
    max_zim_mb: int | None = None

    @field_validator("target")
    @classmethod
    def _validate_target(cls, v: str) -> str:
        if v not in ("memory", "knowledge", "reference"):
            raise ValueError(
                f"target must be memory|knowledge|reference, got {v!r}"
            )
        return v

    def reject_if_phase2_only(self, source_name: str) -> None:
        """Ingest-only guardrail.

        Reference is accepted by the schema (LAB-NEW-C) because it's a valid
        routing target, but it's served by ``zeus.memory.reference`` at query
        time — there is nothing to ingest. A config with ``target: reference``
        is a mistake at the ingest layer.
        """
        if self.target == "reference":
            raise ValueError(
                f"source {source_name!r} has target='reference'; "
                "reference is a query-time proxy (kiwix/NOMAD), not an ingest target"
            )
        if self.target not in _SUPPORTED_TARGETS:
            raise ValueError(
                f"source {source_name!r} has unknown target={self.target!r}"
            )


class Defaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = "chris"
    chunk_size: int = 512
    chunk_overlap: int = 64


class IngestConfig(BaseModel):
    """Top-level ingest config loaded from zeus/ingest/config.yaml."""
    model_config = ConfigDict(extra="forbid")

    defaults: Defaults = Field(default_factory=Defaults)
    sources: dict[str, SourceConfig] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _require_sources(self) -> "IngestConfig":
        if not self.sources:
            raise ValueError("ingest config must define at least one source")
        return self

    def source(self, name: str) -> SourceConfig | None:
        return self.sources.get(name)


def _expand_env(value: Any) -> Any:
    """Recursively expand ${VAR} / $VAR in every string value.

    Unset env vars expand to the empty string (not left verbatim), so callers
    can treat an empty path as "source not configured" without regex-checking.
    """
    if isinstance(value, str):
        return _ENV_VAR_RE.sub(
            lambda m: os.environ.get(m.group(1) or m.group(2), ""),
            value,
        )
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    return value


def load_ingest_config(path: str | Path = DEFAULT_CONFIG_PATH) -> IngestConfig:
    """Load and validate an ingest config YAML file.

    Raises FileNotFoundError if the file is missing, yaml.YAMLError on parse
    failure, and pydantic ValidationError on schema violations.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"ingest config not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"ingest config root must be a mapping, got {type(raw).__name__}")

    expanded = _expand_env(raw)
    return IngestConfig.model_validate(expanded)
