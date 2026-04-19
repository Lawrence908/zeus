# zeus/memory/library.py — Knowledge layer (raw chunked RAG over bulk documents).
#
# Named-vector collection with both dense embeddings (nomic-embed-text, 768d,
# cosine) and BM25 sparse embeddings (Qdrant/bm25 via fastembed). Hybrid
# retrieval fuses the two via Qdrant-native Reciprocal Rank Fusion. Optional
# BGE-reranker-v2-m3 rerank pass tightens top-k.
#
# Companion to MemoryStore (zeus/memory/store.py) — Knowledge stores full
# chunks with no LLM fact-extraction, the right shape for bulk ingest of
# Obsidian notes, chatgpt exports, newsletters, etc.
from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

logger = logging.getLogger("zeus.memory.library")

DEFAULT_COLLECTION = os.getenv("ZEUS_KNOWLEDGE_COLLECTION", "zeus_knowledge")
DEFAULT_EMBED_DIMS = 768  # nomic-embed-text

# Named-vector keys — keep stable, they're written into Qdrant points.
DENSE_VECTOR = "dense"
SPARSE_VECTOR = "bm25"

# Feature flags. Hybrid + rerank require extra deps (fastembed, FlagEmbedding)
# and are opt-in so a fresh repo still works with a pure-dense setup.
HYBRID_ENABLED = os.getenv("ZEUS_KNOWLEDGE_HYBRID", "1").strip() not in ("0", "false", "no")
RERANK_ENABLED = os.getenv("ZEUS_KNOWLEDGE_RERANK", "0").strip() not in ("0", "false", "no")


@dataclass
class KnowledgeChunk:
    text: str
    source: str
    source_id: str
    source_path: str = ""
    chunk_index: int = 0
    user_id: str = "chris"
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def payload(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "source_id": self.source_id,
            "source_path": self.source_path,
            "chunk_index": self.chunk_index,
            "user_id": self.user_id,
            "created_at": self.created_at,
            **self.metadata,
        }


@dataclass
class KnowledgeHit:
    text: str
    score: float
    source: str
    source_path: str
    payload: dict[str, Any]


@dataclass
class AddResult:
    added: int
    skipped: int
    errors: list[str] = field(default_factory=list)


class KnowledgeStore:
    """Hybrid dense + BM25 knowledge store with optional reranker."""

    def __init__(
        self,
        *,
        qdrant_url: str | None = None,
        ollama_url: str | None = None,
        embed_model: str | None = None,
        collection: str = DEFAULT_COLLECTION,
        vector_size: int = DEFAULT_EMBED_DIMS,
    ) -> None:
        self.collection = collection
        self.vector_size = vector_size
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.ollama_url = (
            ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11435")
        ).rstrip("/")
        self.embed_model = embed_model or os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text")
        self._client = QdrantClient(url=self.qdrant_url)
        self._ensured = False
        self._bm25 = None  # lazy fastembed.SparseTextEmbedding

    # -- collection ---------------------------------------------------------

    def _make_vectors_config(self) -> dict[str, qmodels.VectorParams]:
        return {
            DENSE_VECTOR: qmodels.VectorParams(
                size=self.vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        }

    def _make_sparse_config(self) -> dict[str, qmodels.SparseVectorParams]:
        # `modifier=IDF` tells Qdrant to apply BM25-style IDF weighting server-side.
        return {
            SPARSE_VECTOR: qmodels.SparseVectorParams(
                modifier=qmodels.Modifier.IDF,
            ),
        }

    def ensure_collection(self) -> None:
        if self._ensured:
            return
        existing = {c.name for c in self._client.get_collections().collections}
        if self.collection not in existing:
            logger.info("creating qdrant collection %s (hybrid=%s)", self.collection, HYBRID_ENABLED)
            kwargs: dict[str, Any] = dict(
                collection_name=self.collection,
                vectors_config=self._make_vectors_config(),
                optimizers_config=qmodels.OptimizersConfigDiff(indexing_threshold=10000),
            )
            if HYBRID_ENABLED:
                kwargs["sparse_vectors_config"] = self._make_sparse_config()
            self._client.create_collection(**kwargs)
            for field_name, schema in (
                ("source", qmodels.PayloadSchemaType.KEYWORD),
                ("source_id", qmodels.PayloadSchemaType.KEYWORD),
                ("user_id", qmodels.PayloadSchemaType.KEYWORD),
            ):
                try:
                    self._client.create_payload_index(
                        collection_name=self.collection,
                        field_name=field_name,
                        field_schema=schema,
                    )
                except Exception as exc:
                    logger.debug("payload index %s: %s", field_name, exc)
        self._ensured = True

    # -- embeddings ---------------------------------------------------------

    def _embed_dense(self, texts: list[str]) -> list[list[float]]:
        """Call Ollama /api/embeddings once per text (no batch endpoint)."""
        vectors: list[list[float]] = []
        with httpx.Client(timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)) as client:
            for text in texts:
                resp = client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.embed_model, "prompt": text},
                )
                resp.raise_for_status()
                data = resp.json()
                emb = data.get("embedding")
                if not isinstance(emb, list) or not emb:
                    raise RuntimeError(f"ollama returned no embedding for chunk ({len(text)} chars)")
                vectors.append(emb)
        return vectors

    # Back-compat alias.
    _embed = _embed_dense

    def _get_bm25(self):
        if self._bm25 is None:
            from fastembed import SparseTextEmbedding

            self._bm25 = SparseTextEmbedding("Qdrant/bm25")
            logger.info("loaded BM25 sparse encoder (Qdrant/bm25)")
        return self._bm25

    def _embed_sparse(self, texts: list[str]) -> list[qmodels.SparseVector]:
        model = self._get_bm25()
        out: list[qmodels.SparseVector] = []
        for emb in model.embed(texts):
            out.append(
                qmodels.SparseVector(
                    indices=emb.indices.tolist(),
                    values=emb.values.tolist(),
                )
            )
        return out

    # -- write --------------------------------------------------------------

    def add_chunks(
        self,
        chunks: Iterable[KnowledgeChunk],
        *,
        batch_size: int = 64,
    ) -> AddResult:
        """Embed and upsert chunks in batches. Dense always; sparse if HYBRID_ENABLED."""
        self.ensure_collection()
        result = AddResult(added=0, skipped=0)
        batch: list[KnowledgeChunk] = []

        def flush(buf: list[KnowledgeChunk]) -> None:
            if not buf:
                return
            try:
                dense_vecs = self._embed_dense([c.text for c in buf])
            except Exception as exc:
                msg = f"embed batch failed ({len(buf)} chunks): {exc}"
                logger.warning(msg)
                result.errors.append(msg)
                result.skipped += len(buf)
                return

            sparse_vecs: list[qmodels.SparseVector] | None = None
            if HYBRID_ENABLED:
                try:
                    sparse_vecs = self._embed_sparse([c.text for c in buf])
                except Exception as exc:
                    # Degrade gracefully: a BM25 failure shouldn't lose the whole batch.
                    logger.warning("bm25 batch failed, storing dense-only: %s", exc)
                    sparse_vecs = None

            points: list[qmodels.PointStruct] = []
            for i, chunk in enumerate(buf):
                vec_map: dict[str, Any] = {DENSE_VECTOR: dense_vecs[i]}
                if sparse_vecs is not None:
                    vec_map[SPARSE_VECTOR] = sparse_vecs[i]
                points.append(
                    qmodels.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vec_map,
                        payload=chunk.payload(),
                    )
                )
            try:
                self._client.upsert(collection_name=self.collection, points=points, wait=False)
                result.added += len(points)
            except Exception as exc:
                msg = f"qdrant upsert failed ({len(points)} points): {exc}"
                logger.warning(msg)
                result.errors.append(msg)
                result.skipped += len(points)

        for chunk in chunks:
            if not chunk.text or not chunk.text.strip():
                result.skipped += 1
                continue
            batch.append(chunk)
            if len(batch) >= batch_size:
                flush(batch)
                batch = []
        flush(batch)

        return result

    # -- search -------------------------------------------------------------

    def _build_filter(
        self, *, user_id: str | None, sources: list[str] | None
    ) -> qmodels.Filter | None:
        must: list[qmodels.FieldCondition] = []
        if user_id:
            must.append(
                qmodels.FieldCondition(
                    key="user_id", match=qmodels.MatchValue(value=user_id)
                )
            )
        if sources:
            must.append(
                qmodels.FieldCondition(
                    key="source", match=qmodels.MatchAny(any=sources)
                )
            )
        return qmodels.Filter(must=must) if must else None

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        user_id: str | None = None,
        sources: list[str] | None = None,
        candidate_k: int | None = None,
    ) -> list[KnowledgeHit]:
        """Hybrid (dense + BM25) retrieval with RRF fusion, optional rerank pass.

        ``candidate_k`` controls the pre-rerank pool (defaults to 4x top_k,
        capped at 40). Rerank is a no-op when ``ZEUS_KNOWLEDGE_RERANK=0``.
        """
        self.ensure_collection()
        if not query.strip():
            return []

        cand_k = candidate_k or max(top_k * 4, 20)
        cand_k = min(cand_k, 40)

        qfilter = self._build_filter(user_id=user_id, sources=sources)

        points = self._query_hybrid(query, cand_k, qfilter) if HYBRID_ENABLED \
            else self._query_dense_only(query, cand_k, qfilter)

        hits: list[KnowledgeHit] = []
        for p in points:
            payload = dict(p.payload or {})
            hits.append(
                KnowledgeHit(
                    text=str(payload.get("text", "")),
                    score=float(p.score),
                    source=str(payload.get("source", "")),
                    source_path=str(payload.get("source_path", "")),
                    payload=payload,
                )
            )

        if RERANK_ENABLED and hits:
            hits = self._rerank(query, hits)

        return hits[:top_k]

    def _query_dense_only(self, query: str, limit: int, qfilter):
        [vec] = self._embed_dense([query])
        resp = self._client.query_points(
            collection_name=self.collection,
            query=vec,
            using=DENSE_VECTOR,
            limit=limit,
            query_filter=qfilter,
            with_payload=True,
        )
        return resp.points

    def _query_hybrid(self, query: str, limit: int, qfilter):
        """Dense + BM25 RRF fusion in a single Qdrant round-trip."""
        [dense] = self._embed_dense([query])
        try:
            [sparse] = self._embed_sparse([query])
        except Exception as exc:
            logger.warning("bm25 query encode failed, falling back to dense-only: %s", exc)
            return self._query_dense_only(query, limit, qfilter)

        # Prefetch limit is larger than final limit so RRF has real overlap to fuse.
        prefetch_limit = max(limit, 50)
        resp = self._client.query_points(
            collection_name=self.collection,
            prefetch=[
                qmodels.Prefetch(
                    query=dense,
                    using=DENSE_VECTOR,
                    limit=prefetch_limit,
                    filter=qfilter,
                ),
                qmodels.Prefetch(
                    query=sparse,
                    using=SPARSE_VECTOR,
                    limit=prefetch_limit,
                    filter=qfilter,
                ),
            ],
            query=qmodels.FusionQuery(fusion=qmodels.Fusion.RRF),
            limit=limit,
            with_payload=True,
        )
        return resp.points

    def _rerank(self, query: str, hits: list[KnowledgeHit]) -> list[KnowledgeHit]:
        try:
            from zeus.memory.reranker import get_reranker

            reranker = get_reranker()
        except Exception as exc:
            logger.warning("reranker unavailable, skipping: %s", exc)
            return hits

        pairs = [(query, h.text) for h in hits]
        try:
            scores = reranker.score_pairs(pairs)
        except Exception as exc:
            logger.warning("reranker scoring failed, returning original order: %s", exc)
            return hits

        scored = list(zip(hits, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        out: list[KnowledgeHit] = []
        for h, s in scored:
            out.append(
                KnowledgeHit(
                    text=h.text,
                    score=float(s),
                    source=h.source,
                    source_path=h.source_path,
                    payload=h.payload,
                )
            )
        return out

    # -- delete / count -----------------------------------------------------

    def delete_by_source(self, source: str, source_id: str) -> int:
        self.ensure_collection()
        flt = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="source", match=qmodels.MatchValue(value=source)
                ),
                qmodels.FieldCondition(
                    key="source_id", match=qmodels.MatchValue(value=source_id)
                ),
            ]
        )
        res = self._client.delete(
            collection_name=self.collection,
            points_selector=qmodels.FilterSelector(filter=flt),
            wait=True,
        )
        return 1 if getattr(res, "status", None) else 0

    def count(self, *, user_id: str | None = None) -> int:
        self.ensure_collection()
        flt = None
        if user_id:
            flt = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="user_id", match=qmodels.MatchValue(value=user_id)
                    )
                ]
            )
        res = self._client.count(collection_name=self.collection, count_filter=flt, exact=True)
        return int(res.count)


_shared: KnowledgeStore | None = None


def get_knowledge_store() -> KnowledgeStore:
    global _shared
    if _shared is None:
        _shared = KnowledgeStore()
    return _shared
