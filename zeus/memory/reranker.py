# zeus/memory/reranker.py — HTTP client for the homelab rerank-gateway.
#
# This used to load BAAI/bge-reranker-v2-m3 in-process via sentence-transformers.
# It was the ONLY torch consumer in the entire Zeus tree, which meant a ~1.1GB
# checkpoint and the CUDA wheels rode along in a 22GB image, and its HuggingFace
# cache was baked into the image rather than mounted, so the checkpoint was
# re-downloaded on every rebuild. The model now runs in
# services/rerank-gateway/, which owns an ordered pool of text-embeddings-
# inference backends (apollo's 5080 first, a daedalus CPU node as fallback) with
# health probing and failover. Zeus is one of its two consumers; context-pack is
# the other.
#
# The public surface is unchanged on purpose: KnowledgeStore._rerank and
# MemoryStore._rerank still call get_reranker().score_pairs(pairs), and both
# already wrap that in a try/except that logs and keeps the original ordering.
# That pre-existing fail-open contract is what makes a network hop safe here —
# a gateway outage degrades ranking, it does not break retrieval.
#
# Env:
#   ZEUS_RERANKER_URL     — gateway base url (default http://rerank-gateway:8191)
#   ZEUS_RERANKER_TIMEOUT — seconds for one call. Must stay ABOVE the gateway's
#                           own RERANK_REQUEST_TIMEOUT, or a truncated read
#                           replaces the gateway's error text with a timeout.
#   ZEUS_RERANKER_MODEL   — advisory only now; the checkpoint is chosen by the
#                           gateway's pool and reported in its /healthz.
#   ZEUS_RERANKER_DEVICE  — deprecated, ignored. Device selection belongs to the pool.
#   ZEUS_RERANKER_FP16    — deprecated, ignored. Same reason.
from __future__ import annotations

import logging
import os
import threading
from typing import Sequence

import httpx

logger = logging.getLogger("zeus.memory.reranker")

_URL = os.getenv("ZEUS_RERANKER_URL", "http://rerank-gateway:8191").rstrip("/")
_TIMEOUT = float(os.getenv("ZEUS_RERANKER_TIMEOUT", "25.0"))
# Advisory. Logged once at construction so a pool serving something else is
# visible in the logs, but not enforced here — the gateway does that check
# against each node's TEI /info and refuses to route to a mismatched node.
_MODEL = os.getenv("ZEUS_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
# Must not exceed the gateway's RERANK_MAX_TEXTS, which rejects larger bodies
# with 413. Candidate pools here are 40 by default, so this is only reached by a
# caller that raised ZEUS_KNOWLEDGE_RERANK_CANDIDATES a long way.
_MAX_TEXTS = int(os.getenv("ZEUS_RERANKER_MAX_TEXTS", "256"))

_DEPRECATED = ("ZEUS_RERANKER_DEVICE", "ZEUS_RERANKER_FP16")

# Did reranking actually happen? Callers fail open (library.py logs "returning
# original order" and carries on), which is right for serving and dangerous for
# measurement: a flag saying ZEUS_KNOWLEDGE_RERANK=1 records intent, not effect.
# On 2026-09-18 the GPU node was off and the CPU fallback took 24s against a 5s
# queue timeout, so every request 503'd and an entire eval run scored unreranked
# while reporting rerank=1. Comparing that against a genuinely reranked baseline
# would have read as a large code regression. Counted here, at the one place
# that knows, so the eval can record effect instead of intent.
_STATS = {"attempts": 0, "ok": 0}


def rerank_stats() -> dict[str, int]:
    """Snapshot of rerank attempts vs successes for this process."""
    return dict(_STATS)


def rerank_applied() -> bool | None:
    """True if every attempt succeeded, False if any failed, None if never tried."""
    if _STATS["attempts"] == 0:
        return None
    return _STATS["ok"] == _STATS["attempts"]


def _warn_deprecated() -> None:
    for name in _DEPRECATED:
        if os.getenv(name):
            logger.warning(
                "%s is set but ignored: the reranker now runs in rerank-gateway "
                "and the pool decides which device serves a request. Point "
                "ZEUS_RERANKER_URL elsewhere if you need a different backend.",
                name,
            )


class RerankClient:
    """Thin HTTP client for rerank-gateway's TEI-compatible POST /rerank.

    ``score_pairs(pairs)`` returns one relevance score per input pair, in the
    caller's original order — higher is more relevant, and both callers
    (``KnowledgeStore._rerank``, ``MemoryStore._rerank``) sort descending.
    """

    def __init__(self, *, url: str = _URL, timeout: float = _TIMEOUT, model_id: str = _MODEL) -> None:
        self.url = url.rstrip("/")
        self.model_id = model_id
        # One client for the process so connections pool across queries. The
        # callers are synchronous, so this is httpx.Client and not AsyncClient.
        self._http = httpx.Client(timeout=timeout)
        logger.info("reranker -> %s (advisory model %s)", self.url, self.model_id)

    def _score_one_query(self, query: str, texts: list[str]) -> list[float]:
        """Scores for one query against texts, returned in texts order."""
        r = self._http.post(
            f"{self.url}/rerank",
            json={
                "query": query,
                "texts": texts,
                # TEI's default applies a sigmoid; sentence-transformers'
                # CrossEncoder.predict returned the raw classification logit.
                # Sigmoid is monotonic so the ORDER is identical either way, but
                # KnowledgeHit.score and MemoryHit.score carry these numbers
                # downstream, so keeping the range identical means nothing that
                # compares or thresholds a score changes behaviour.
                "raw_scores": True,
            },
        )
        r.raise_for_status()
        # [{"index": i, "score": s}, ...] sorted by score, NOT by index. The
        # scatter below is mandatory: callers zip these against their own hit
        # list, so returning them in the gateway's order would silently pair
        # every score with the wrong document.
        out = [0.0] * len(texts)
        for item in r.json():
            idx = item["index"]
            if 0 <= idx < len(texts):
                out[idx] = float(item["score"])
        return out

    def score_pairs(
        self,
        pairs: Sequence[tuple[str, str]],
        *,
        batch_size: int = 32,
    ) -> list[float]:
        """Score (query, text) pairs, preserving the caller's order.

        Both real call sites pass a single constant query, but the signature has
        always accepted arbitrary pairs, so pairs are grouped by query and each
        group is sent as one request. ``batch_size`` is advisory now: it is the
        model's concern, and the gateway's backends do their own batching. It is
        kept in the signature so the interface is unchanged.
        """
        if not pairs:
            return []

        # query -> [(original position, text), ...]
        groups: dict[str, list[tuple[int, str]]] = {}
        for i, (query, text) in enumerate(pairs):
            groups.setdefault(query, []).append((i, text))

        scores = [0.0] * len(pairs)
        _STATS["attempts"] += 1
        for query, items in groups.items():
            # Chunked so a caller with a very deep candidate pool does not trip
            # the gateway's RERANK_MAX_TEXTS cap.
            for start in range(0, len(items), _MAX_TEXTS):
                chunk = items[start : start + _MAX_TEXTS]
                chunk_scores = self._score_one_query(query, [t for _, t in chunk])
                for (pos, _), score in zip(chunk, chunk_scores):
                    scores[pos] = score
        # Only on the way out: an exception here propagates to the caller's
        # fail-open handler, leaving attempts > ok, which is exactly the signal.
        _STATS["ok"] += 1
        return scores


# The old class name. Kept as an alias so any other import site or test that
# reaches for BgeReranker keeps working across this change.
BgeReranker = RerankClient


_shared: RerankClient | None = None
_shared_lock = threading.Lock()


def get_reranker() -> RerankClient:
    """Process-wide singleton. Thread-safe double-checked lock on init.

    Constructing this is now cheap — it opens no model and allocates no VRAM —
    but the singleton is kept so the connection pool is shared rather than
    rebuilt per query.
    """
    global _shared
    if _shared is None:
        with _shared_lock:
            if _shared is None:
                _warn_deprecated()
                _shared = RerankClient()
    return _shared
