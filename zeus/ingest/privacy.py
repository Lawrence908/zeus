"""zeus/ingest/privacy.py — Lightweight privacy tagging for ingested chunks."""

from __future__ import annotations

import re
from enum import Enum

from zeus.ingest.pipeline import Chunk


class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    PRIVATE = "private"


_SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(sk-[A-Za-z0-9_\-]{10,})\b"),  # common API key prefix
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
    re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY-----"),
    re.compile(r"\b(password|passphrase)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"\b(api[_ -]?key|token|secret)\s*[:=]\s*\S+", re.IGNORECASE),
]


def classify_chunk(chunk: Chunk) -> PrivacyLevel:
    """
    Tag chunks with a privacy level.

    v1 is intentionally conservative: most personal notes are PERSONAL.
    This is metadata-only tagging; it does not block ingest.
    """
    source = (chunk.source or "").lower()

    if source.startswith("email:"):
        baseline = PrivacyLevel.PERSONAL
    elif source.startswith("context_pack:"):
        baseline = PrivacyLevel.PERSONAL
    elif source.startswith("chatgpt:"):
        baseline = PrivacyLevel.PERSONAL
    else:
        baseline = PrivacyLevel.PERSONAL

    text = chunk.text or ""
    for pat in _SECRET_PATTERNS:
        if pat.search(text):
            return PrivacyLevel.SENSITIVE

    return baseline

