# zeus/memory/news.py - Pheme news layer (consolidated news items over zeus_news).
#
# Mirrors KnowledgeStore (zeus/memory/library.py): dense nomic-embed-text
# vectors, no LLM on the write path. Differences that justify a fourth store
# instead of another zeus_knowledge source:
#   - deterministic point ids from (source, source_id) so re-ingest upserts
#     in place instead of needing delete_by_source sweeps
#   - payload indexes on source / topics / entities / published_at for cheap
#     "personal Ground News" deep-dive filters
#   - retention: sweep_expired() ages items out (pinned items survive)
#   - pipeline write-back: set_analysis() lets Pheme stages attach entities,
#     topics, and significance after ingest without re-embedding
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import httpx
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

logger = logging.getLogger("zeus.memory.news")

DEFAULT_COLLECTION = os.getenv("ZEUS_NEWS_COLLECTION", "zeus_news")
DEFAULT_EMBED_DIMS = 768  # nomic-embed-text

# Stable UUID5 namespace for deterministic point ids. Never change this value:
# it is what makes re-ingest of the same (source, source_id) an in-place upsert.
_POINT_NAMESPACE = uuid.UUID("6d1f3a52-9b3e-4c1f-8a7d-2e5b9c4f0a11")


def retention_days() -> int:
    try:
        return max(1, int(os.getenv("NEWS_RETENTION_DAYS", "45")))
    except ValueError:
        return 45


class NewsItem(BaseModel):
    text: str
    title: str
    source: str                    # "canary" | "capitolscope"
    source_id: str                 # stable id for idempotent re-ingest
    url: str | None = None
    published_at: str = ""         # ISO-8601 string (never floats)
    ingested_at: str = ""          # ISO-8601 string
    entities: list[str] = Field(default_factory=list)  # people, orgs, tickers, bill ids
    topics: list[str] = Field(default_factory=list)
    bias: str | None = None        # source lean/quality tag when provided (e.g. Canary full_grade)
    significance: float = 0.0      # set by Pheme ranking stage
    pinned: bool = False           # survives retention sweep
    metadata: dict[str, Any] = Field(default_factory=dict)

    def point_id(self) -> str:
        return str(uuid.uuid5(_POINT_NAMESPACE, f"{self.source}:{self.source_id}"))

    def payload(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "title": self.title,
            "source": self.source,
            "source_id": self.source_id,
            "url": self.url or "",
            "published_at": self.published_at,
            "ingested_at": self.ingested_at or datetime.now(timezone.utc).isoformat(),
            "entities": list(self.entities),
            "topics": list(self.topics),
            "bias": self.bias or "",
            "significance": float(self.significance),
            "pinned": bool(self.pinned),
            **self.metadata,
        }


class NewsHit(BaseModel):
    id: str
    text: str
    score: float
    title: str
    source: str
    url: str
    published_at: str
    payload: dict[str, Any]


class AddResult(BaseModel):
    added: int = 0
    skipped: int = 0
    unchanged: int = 0
    errors: list[str] = Field(default_factory=list)


class NewsStore:
    """Dense-vector news store over the zeus_news collection. No LLM on writes."""

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

    # -- collection ---------------------------------------------------------

    def ensure_collection(self) -> None:
        if self._ensured:
            return
        existing = {c.name for c in self._client.get_collections().collections}
        if self.collection not in existing:
            logger.info("creating qdrant collection %s", self.collection)
            self._client.create_collection(
                collection_name=self.collection,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
                optimizers_config=qmodels.OptimizersConfigDiff(indexing_threshold=10000),
            )
            for field_name, schema in (
                ("source", qmodels.PayloadSchemaType.KEYWORD),
                ("source_id", qmodels.PayloadSchemaType.KEYWORD),
                ("topics", qmodels.PayloadSchemaType.KEYWORD),
                ("entities", qmodels.PayloadSchemaType.KEYWORD),
                # ISO-8601 strings sort lexicographically; keyword index still
                # lets range filters run via MatchText fallbacks, but datetime
                # index gives real range queries for published_at.
                ("published_at", qmodels.PayloadSchemaType.DATETIME),
                ("ingested_at", qmodels.PayloadSchemaType.DATETIME),
                ("pinned", qmodels.PayloadSchemaType.BOOL),
                ("significance", qmodels.PayloadSchemaType.FLOAT),
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

    def _embed(self, texts: list[str]) -> list[list[float]]:
        keep_alive = os.getenv("ZEUS_EMBED_KEEP_ALIVE", "24h")
        vectors: list[list[float]] = []
        with httpx.Client(
            timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)
        ) as client:
            for text in texts:
                resp = client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.embed_model,
                        "prompt": text,
                        "keep_alive": keep_alive,
                        "options": {"num_ctx": 2048},
                    },
                )
                resp.raise_for_status()
                emb = (resp.json() or {}).get("embedding")
                if not isinstance(emb, list) or not emb:
                    raise RuntimeError(f"ollama returned no embedding ({len(text)} chars)")
                vectors.append(emb)
        return vectors

    # -- write --------------------------------------------------------------

    @staticmethod
    def _text_hash(item: NewsItem) -> str:
        import hashlib

        return hashlib.sha1(f"{item.title}\n{item.text}".encode()).hexdigest()[:16]

    def _existing_payloads(self, ids: list[str]) -> dict[str, dict[str, Any]]:
        try:
            points = self._client.retrieve(
                collection_name=self.collection, ids=ids, with_payload=True
            )
            return {str(p.id): dict(p.payload or {}) for p in points}
        except Exception as exc:
            logger.debug("retrieve existing points failed: %s", exc)
            return {}

    # Pipeline write-back fields that a re-ingest must never clobber.
    _ANALYSIS_FIELDS = ("claim", "significance", "pinned")

    def add_items(self, items: Iterable[NewsItem], *, batch_size: int = 32) -> AddResult:
        """Embed and upsert items. Deterministic ids make re-ingest idempotent.

        Items whose title+text are unchanged since the stored copy are skipped
        entirely (no embed, no upsert) so the pipeline's analysis write-backs
        survive the daily re-ingest. Changed items carry forward analysis
        fields the incoming item does not supply itself.
        """
        self.ensure_collection()
        result = AddResult()
        batch: list[NewsItem] = []

        def flush(buf: list[NewsItem]) -> None:
            if not buf:
                return
            existing = self._existing_payloads([it.point_id() for it in buf])
            to_write: list[NewsItem] = []
            for it in buf:
                prev = existing.get(it.point_id())
                if prev is None:
                    to_write.append(it)
                    continue
                if prev.get("text_hash") == self._text_hash(it):
                    result.unchanged += 1
                    continue
                # Text changed: re-embed, but keep prior analysis write-backs.
                if not it.entities and prev.get("entities"):
                    it.entities = [str(e) for e in prev["entities"]]
                if not it.topics and prev.get("topics"):
                    it.topics = [str(t) for t in prev["topics"]]
                for field_name in self._ANALYSIS_FIELDS:
                    if field_name in prev and field_name not in it.metadata:
                        it.metadata[field_name] = prev[field_name]
                to_write.append(it)
            if not to_write:
                return
            try:
                vecs = self._embed([f"{it.title}\n{it.text}" for it in to_write])
            except Exception as exc:
                msg = f"embed batch failed ({len(to_write)} items): {exc}"
                logger.warning(msg)
                result.errors.append(msg)
                result.skipped += len(to_write)
                return
            points = []
            for i, it in enumerate(to_write):
                payload = it.payload()
                payload["text_hash"] = self._text_hash(it)
                points.append(
                    qmodels.PointStruct(id=it.point_id(), vector=vecs[i], payload=payload)
                )
            try:
                self._client.upsert(collection_name=self.collection, points=points, wait=False)
                result.added += len(points)
            except Exception as exc:
                msg = f"qdrant upsert failed ({len(points)} points): {exc}"
                logger.warning(msg)
                result.errors.append(msg)
                result.skipped += len(points)

        for item in items:
            if not item.text.strip() and not item.title.strip():
                result.skipped += 1
                continue
            batch.append(item)
            if len(batch) >= batch_size:
                flush(batch)
                batch = []
        flush(batch)
        return result

    def set_analysis(
        self,
        source: str,
        source_id: str,
        *,
        entities: list[str] | None = None,
        topics: list[str] | None = None,
        significance: float | None = None,
        pinned: bool | None = None,
        extra: dict[str, Any] | None = None,
    ) -> bool:
        """Write pipeline-stage results back onto an item without re-embedding."""
        self.ensure_collection()
        payload: dict[str, Any] = dict(extra or {})
        if entities is not None:
            payload["entities"] = entities
        if topics is not None:
            payload["topics"] = topics
        if significance is not None:
            payload["significance"] = float(significance)
        if pinned is not None:
            payload["pinned"] = bool(pinned)
        if not payload:
            return False
        pid = str(uuid.uuid5(_POINT_NAMESPACE, f"{source}:{source_id}"))
        try:
            self._client.set_payload(
                collection_name=self.collection, payload=payload, points=[pid], wait=True
            )
            return True
        except Exception as exc:
            logger.warning("set_analysis failed for %s:%s - %s", source, source_id, exc)
            return False

    # -- search -------------------------------------------------------------

    def _build_filter(self, filters: dict[str, Any] | None) -> qmodels.Filter | None:
        """Supported filter keys: source, sources, topic, entity, since, until."""
        if not filters:
            return None
        must: list[Any] = []
        if filters.get("source"):
            must.append(
                qmodels.FieldCondition(
                    key="source", match=qmodels.MatchValue(value=str(filters["source"]))
                )
            )
        if filters.get("sources"):
            must.append(
                qmodels.FieldCondition(
                    key="source",
                    match=qmodels.MatchAny(any=[str(s) for s in filters["sources"]]),
                )
            )
        if filters.get("topic"):
            must.append(
                qmodels.FieldCondition(
                    key="topics", match=qmodels.MatchValue(value=str(filters["topic"]))
                )
            )
        if filters.get("entity"):
            must.append(
                qmodels.FieldCondition(
                    key="entities", match=qmodels.MatchValue(value=str(filters["entity"]))
                )
            )
        since, until = filters.get("since"), filters.get("until")
        if since or until:
            must.append(
                qmodels.FieldCondition(
                    key="published_at",
                    range=qmodels.DatetimeRange(
                        gte=str(since) if since else None,
                        lte=str(until) if until else None,
                    ),
                )
            )
        return qmodels.Filter(must=must) if must else None

    def search(
        self,
        query: str,
        top_k: int = 8,
        filters: dict[str, Any] | None = None,
    ) -> list[NewsHit]:
        self.ensure_collection()
        if not query.strip():
            return []
        [vec] = self._embed([query])
        resp = self._client.query_points(
            collection_name=self.collection,
            query=vec,
            limit=max(1, min(top_k, 50)),
            query_filter=self._build_filter(filters),
            with_payload=True,
        )
        hits: list[NewsHit] = []
        for p in resp.points:
            payload = dict(p.payload or {})
            hits.append(
                NewsHit(
                    id=str(getattr(p, "id", "") or ""),
                    text=str(payload.get("text", "")),
                    score=float(p.score),
                    title=str(payload.get("title", "")),
                    source=str(payload.get("source", "")),
                    url=str(payload.get("url", "")),
                    published_at=str(payload.get("published_at", "")),
                    payload=payload,
                )
            )
        return hits

    def similar(self, point_id: str, top_k: int = 8) -> list[tuple[str, float]]:
        """Nearest neighbours of a stored item by point id (recommend-by-id).

        Returns (point_id, score) pairs excluding the query point. Used by the
        Pheme cluster stage so clustering never re-embeds text.
        """
        self.ensure_collection()
        try:
            resp = self._client.query_points(
                collection_name=self.collection,
                query=point_id,
                limit=max(1, min(top_k, 50)),
                with_payload=False,
            )
        except Exception as exc:
            logger.warning("similar(%s) failed: %s", point_id, exc)
            return []
        return [
            (str(p.id), float(p.score))
            for p in resp.points
            if str(p.id) != str(point_id)
        ]

    def scroll_recent(
        self,
        *,
        since: str,
        sources: list[str] | None = None,
        limit: int = 500,
    ) -> list[NewsHit]:
        """Non-vector scan of items ingested since an ISO-8601 timestamp.

        Used by the pipeline (stage input) and the breaking observer, where
        "everything new" matters more than similarity ranking.
        """
        self.ensure_collection()
        must: list[Any] = [
            qmodels.FieldCondition(
                key="ingested_at", range=qmodels.DatetimeRange(gte=since)
            )
        ]
        if sources:
            must.append(
                qmodels.FieldCondition(key="source", match=qmodels.MatchAny(any=sources))
            )
        points, _ = self._client.scroll(
            collection_name=self.collection,
            scroll_filter=qmodels.Filter(must=must),
            limit=max(1, min(limit, 2000)),
            with_payload=True,
            with_vectors=False,
        )
        hits: list[NewsHit] = []
        for p in points:
            payload = dict(p.payload or {})
            hits.append(
                NewsHit(
                    id=str(getattr(p, "id", "") or ""),
                    text=str(payload.get("text", "")),
                    score=0.0,
                    title=str(payload.get("title", "")),
                    source=str(payload.get("source", "")),
                    url=str(payload.get("url", "")),
                    published_at=str(payload.get("published_at", "")),
                    payload=payload,
                )
            )
        return hits

    # -- delete / retention / count -----------------------------------------

    def delete_by_source(self, source: str, source_id: str) -> int:
        self.ensure_collection()
        flt = qmodels.Filter(
            must=[
                qmodels.FieldCondition(key="source", match=qmodels.MatchValue(value=source)),
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

    def sweep_expired(self, older_than_days: int | None = None) -> int:
        """Delete unpinned items older than the retention window. Returns count removed."""
        self.ensure_collection()
        days = older_than_days if older_than_days is not None else retention_days()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        flt = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="ingested_at", range=qmodels.DatetimeRange(lt=cutoff)
                )
            ],
            must_not=[
                qmodels.FieldCondition(key="pinned", match=qmodels.MatchValue(value=True))
            ],
        )
        before = self._client.count(
            collection_name=self.collection, count_filter=flt, exact=True
        ).count
        if before:
            self._client.delete(
                collection_name=self.collection,
                points_selector=qmodels.FilterSelector(filter=flt),
                wait=True,
            )
            logger.info("news retention sweep removed %d items older than %dd", before, days)
        return int(before)

    def count(self, *, source: str | None = None) -> int:
        self.ensure_collection()
        flt = None
        if source:
            flt = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="source", match=qmodels.MatchValue(value=source)
                    )
                ]
            )
        res = self._client.count(collection_name=self.collection, count_filter=flt, exact=True)
        return int(res.count)


_shared: NewsStore | None = None


def get_news_store() -> NewsStore:
    global _shared
    if _shared is None:
        _shared = NewsStore()
    return _shared
