# zeus/ingest/types.py — Shared ingest datatypes (avoids pipeline ↔ privacy cycles)
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A single ingested chunk ready for embedding and storage."""
    text: str
    source: str  # e.g. "markdown:notes/2024-01.md"
    metadata: dict = field(default_factory=dict)
    user_id: str = "chris"  # mem0 partitions by user_id
