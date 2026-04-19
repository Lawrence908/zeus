# zeus/memory/store.py — Mnemosyne memory layer, Qdrant-backed, no mem0.
#
# Replaces the mem0 library with a hand-rolled ~200 LOC class that mirrors
# KnowledgeStore (zeus/memory/library.py) and adds an LLM fact-extraction pass
# on writes via zeus.core.small_llm.
#
# Why: mem0 v2.0.0 (April 2026) deleted mem0g and rewrote half its config
# surface; v1.x had three breaking changes in 24 hours on our deployment. We
# own this layer now. See docs/ZEUS_LINEAR_TICKET_PLAN.md and
# docs/memory-architecture-plan.md for context.
#
# Payload shape (all ISO-8601 strings where dates appear — fixes the
# MemoryItem Pydantic 500):
#     text, subject, predicate, object, category, confidence,
#     temporal, valid_from, valid_until, contains_pii,
#     source, source_id, source_span, user_id,
#     created_at, updated_at, ...metadata
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from zeus.memory._embed import DEFAULT_EMBED_DIMS, embed_texts

logger = logging.getLogger("zeus.memory.store")

DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION", "zeus_memories")
MIN_CONFIDENCE = float(os.getenv("ZEUS_MEMORY_MIN_CONFIDENCE", "0.6"))

_PROMPT_PATH = Path(__file__).resolve().parents[1] / "core" / "prompts" / "memory_extract.md"


# ---------------------------------------------------------------------------
# Pydantic schemas — consumed by small_llm_call(response_format=FactExtraction)
# ---------------------------------------------------------------------------

Category = Literal[
    "preference",
    "identity",
    "relationship",
    "skill",
    "event",
    "task",
    "decision",
    "belief",
    "other",
]

Temporal = Literal["permanent", "long_term", "transient"]


class Fact(BaseModel):
    """One atomic fact emitted by the extraction LLM."""

    text: str = Field(..., max_length=240)
    subject: str = Field(..., min_length=1)
    predicate: str = Field(..., min_length=1)
    object: str | None = None
    category: Category
    confidence: float = Field(..., ge=0.0, le=1.0)
    temporal: Temporal = "long_term"
    valid_from: date | None = None
    valid_until: date | None = None
    contains_pii: bool = False
    source_id: str = Field(..., min_length=1)
    source_span: str | None = Field(default=None, max_length=240)

    @field_validator("valid_from", "valid_until", mode="before")
    @classmethod
    def _coerce_partial_date(cls, v):
        """Haiku sometimes emits '2026' or '2026-04' instead of a full ISO date.
        Coerce those to the earliest day in that range; drop anything we can't parse."""
        if v is None or isinstance(v, date):
            return v
        if not isinstance(v, str):
            return v
        s = v.strip()
        if not s:
            return None
        # Full ISO date, pass through.
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s[:10]
        # Year only ("2026") → Jan 1.
        if len(s) == 4 and s.isdigit():
            return f"{s}-01-01"
        # Year-month ("2026-04") → first of the month.
        if len(s) == 7 and s[4] == "-" and s[:4].isdigit() and s[5:].isdigit():
            return f"{s}-01"
        return None


class FactExtraction(BaseModel):
    """Hard-capped list of facts. Cap size is the 2026 mem0-incident mitigation."""

    facts: list[Fact] = Field(..., max_length=10)


# ---------------------------------------------------------------------------
# Runtime dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MemoryHit:
    id: str
    text: str
    score: float
    source: str
    category: str
    payload: dict[str, Any]


@dataclass
class AddResult:
    added: int = 0
    skipped: int = 0
    extraction_attempts: int = 0
    raw_fallbacks: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _date_to_iso(d: date | None) -> str | None:
    return d.isoformat() if d is not None else None


def _load_extraction_prompt() -> str:
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("extraction prompt load failed: %s", exc)
        return (
            "Extract atomic facts as JSON {\"facts\":[...]}. Max 10 facts. "
            "No prose. English only. Drop below 0.6 confidence."
        )


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------

class MemoryStore:
    """Qdrant-backed curated fact store with optional LLM extraction on write."""

    def __init__(
        self,
        *,
        qdrant_url: str | None = None,
        collection: str = DEFAULT_COLLECTION,
        vector_size: int = DEFAULT_EMBED_DIMS,
    ) -> None:
        self.collection = collection
        self.vector_size = vector_size
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
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
                optimizers_config=qmodels.OptimizersConfigDiff(indexing_threshold=2000),
            )
            for name, schema in (
                ("user_id", qmodels.PayloadSchemaType.KEYWORD),
                ("source", qmodels.PayloadSchemaType.KEYWORD),
                ("source_id", qmodels.PayloadSchemaType.KEYWORD),
                ("subject", qmodels.PayloadSchemaType.KEYWORD),
                ("predicate", qmodels.PayloadSchemaType.KEYWORD),
                ("category", qmodels.PayloadSchemaType.KEYWORD),
                ("contains_pii", qmodels.PayloadSchemaType.BOOL),
                ("valid_from", qmodels.PayloadSchemaType.DATETIME),
                ("valid_until", qmodels.PayloadSchemaType.DATETIME),
            ):
                try:
                    self._client.create_payload_index(
                        collection_name=self.collection,
                        field_name=name,
                        field_schema=schema,
                    )
                except Exception as exc:
                    logger.debug("payload index %s: %s", name, exc)
        self._ensured = True

    # -- write --------------------------------------------------------------

    def _payload_from_fact(
        self,
        fact: Fact,
        *,
        source: str,
        user_id: str,
        extra_metadata: dict[str, Any] | None,
        created_at: str,
    ) -> dict[str, Any]:
        base = {
            "text": fact.text,
            "subject": fact.subject,
            "predicate": fact.predicate,
            "object": fact.object,
            "category": fact.category,
            "confidence": fact.confidence,
            "temporal": fact.temporal,
            "valid_from": _date_to_iso(fact.valid_from),
            "valid_until": _date_to_iso(fact.valid_until),
            "contains_pii": fact.contains_pii,
            "source": source,
            "source_id": fact.source_id,
            "source_span": fact.source_span,
            "user_id": user_id,
            "created_at": created_at,
            "updated_at": created_at,
        }
        if extra_metadata:
            for k, v in extra_metadata.items():
                base.setdefault(k, v)
        return base

    def _raw_payload(
        self,
        *,
        text: str,
        source: str,
        source_id: str,
        user_id: str,
        extra_metadata: dict[str, Any] | None,
        created_at: str,
    ) -> dict[str, Any]:
        base = {
            "text": text,
            "subject": "user",
            "predicate": "noted",
            "object": None,
            "category": "other",
            "confidence": 1.0,
            "temporal": "long_term",
            "valid_from": None,
            "valid_until": None,
            "contains_pii": False,
            "source": source,
            "source_id": source_id,
            "source_span": None,
            "user_id": user_id,
            "created_at": created_at,
            "updated_at": created_at,
        }
        if extra_metadata:
            for k, v in extra_metadata.items():
                base.setdefault(k, v)
        return base

    def _upsert(self, payloads: list[dict[str, Any]]) -> list[str]:
        self.ensure_collection()
        texts = [p["text"] for p in payloads]
        vectors = embed_texts(texts)
        ids: list[str] = [str(uuid.uuid4()) for _ in payloads]
        points = [
            qmodels.PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
            for i in range(len(payloads))
        ]
        self._client.upsert(collection_name=self.collection, points=points, wait=False)
        return ids

    async def add_text(
        self,
        text: str,
        *,
        source: str,
        source_id: str,
        user_id: str = "chris",
        extract_facts: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> AddResult:
        """Main write path. extract_facts=True routes through small_llm_call."""
        result = AddResult()
        if not text or not text.strip():
            result.skipped += 1
            return result

        created_at = _now_iso()

        if not extract_facts:
            payload = self._raw_payload(
                text=text.strip(),
                source=source,
                source_id=source_id,
                user_id=user_id,
                extra_metadata=metadata,
                created_at=created_at,
            )
            try:
                await asyncio.to_thread(self._upsert, [payload])
                result.added += 1
            except Exception as exc:
                msg = f"upsert failed: {exc}"
                logger.warning(msg)
                result.errors.append(msg)
                result.skipped += 1
            return result

        # extract_facts=True: call the small-task LLM to extract atomic claims.
        from zeus.core.small_llm import (
            AllProvidersFailed,
            small_llm_call,
        )

        result.extraction_attempts += 1
        system = _load_extraction_prompt()
        user_payload = json.dumps(
            {"source_id": source_id, "text": text}, ensure_ascii=False
        )

        try:
            llm_result = await small_llm_call(
                system=system,
                user=user_payload,
                max_tokens=2048,
                response_format=FactExtraction,
                min_privacy_tier=1,
                caller="memory_store.add_text",
            )
        except AllProvidersFailed as exc:
            msg = f"extraction failed (all providers): {exc}"
            logger.warning(msg)
            result.errors.append(msg)
            # Defensive fallback: store raw so we don't silently drop the write.
            return await self._raw_fallback(
                text=text,
                source=source,
                source_id=source_id,
                user_id=user_id,
                metadata=metadata,
                result=result,
            )

        parsed = llm_result.parsed
        if not isinstance(parsed, FactExtraction):
            # Structured parse failed twice on every provider — store raw.
            logger.warning(
                "extraction returned unstructured output after retries; storing raw (%s)",
                source_id,
            )
            return await self._raw_fallback(
                text=text,
                source=source,
                source_id=source_id,
                user_id=user_id,
                metadata=metadata,
                result=result,
            )

        facts = [f for f in parsed.facts if f.confidence >= MIN_CONFIDENCE]
        if not facts:
            # LLM returned no durable facts — nothing to store. Not an error.
            return result

        payloads = [
            self._payload_from_fact(
                f,
                source=source,
                user_id=user_id,
                extra_metadata=metadata,
                created_at=created_at,
            )
            for f in facts
        ]
        try:
            await asyncio.to_thread(self._upsert, payloads)
            result.added += len(payloads)
        except Exception as exc:
            msg = f"upsert failed ({len(payloads)} facts): {exc}"
            logger.warning(msg)
            result.errors.append(msg)
            result.skipped += len(payloads)
        return result

    async def _raw_fallback(
        self,
        *,
        text: str,
        source: str,
        source_id: str,
        user_id: str,
        metadata: dict[str, Any] | None,
        result: AddResult,
    ) -> AddResult:
        created_at = _now_iso()
        payload = self._raw_payload(
            text=text.strip(),
            source=source,
            source_id=source_id,
            user_id=user_id,
            extra_metadata=metadata,
            created_at=created_at,
        )
        try:
            await asyncio.to_thread(self._upsert, [payload])
            result.added += 1
            result.raw_fallbacks += 1
        except Exception as exc:
            msg = f"raw fallback upsert failed: {exc}"
            logger.warning(msg)
            result.errors.append(msg)
            result.skipped += 1
        return result

    # -- search -------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        user_id: str = "chris",
        top_k: int = 8,
        category: str | list[str] | None = None,
        valid_as_of: date | None = None,
        contains_pii: bool | None = None,
        sources: list[str] | None = None,
    ) -> list[MemoryHit]:
        self.ensure_collection()
        if not query.strip():
            return []
        [vector] = embed_texts([query])

        must: list[qmodels.FieldCondition] = [
            qmodels.FieldCondition(
                key="user_id", match=qmodels.MatchValue(value=user_id)
            )
        ]
        if sources:
            must.append(
                qmodels.FieldCondition(
                    key="source", match=qmodels.MatchAny(any=sources)
                )
            )
        if category:
            categories = [category] if isinstance(category, str) else category
            must.append(
                qmodels.FieldCondition(
                    key="category", match=qmodels.MatchAny(any=categories)
                )
            )
        if contains_pii is not None:
            must.append(
                qmodels.FieldCondition(
                    key="contains_pii", match=qmodels.MatchValue(value=contains_pii)
                )
            )
        if valid_as_of is not None:
            as_iso = valid_as_of.isoformat()
            # valid_from <= as_iso (or null)
            should_from = [
                qmodels.IsEmptyCondition(is_empty=qmodels.PayloadField(key="valid_from")),
                qmodels.FieldCondition(
                    key="valid_from",
                    range=qmodels.DatetimeRange(lte=as_iso),
                ),
            ]
            # valid_until > as_iso (or null)
            should_until = [
                qmodels.IsEmptyCondition(is_empty=qmodels.PayloadField(key="valid_until")),
                qmodels.FieldCondition(
                    key="valid_until",
                    range=qmodels.DatetimeRange(gt=as_iso),
                ),
            ]
            must.append(qmodels.Filter(should=should_from))
            must.append(qmodels.Filter(should=should_until))

        qfilter = qmodels.Filter(must=must)
        response = self._client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=top_k,
            query_filter=qfilter,
            with_payload=True,
        )

        out: list[MemoryHit] = []
        for h in response.points:
            payload = dict(h.payload or {})
            out.append(
                MemoryHit(
                    id=str(h.id),
                    text=str(payload.get("text", "")),
                    score=float(h.score),
                    source=str(payload.get("source", "")),
                    category=str(payload.get("category", "")),
                    payload=payload,
                )
            )
        return out

    # -- update / delete ----------------------------------------------------

    def update(self, memory_id: str, text: str) -> None:
        """Re-embed and overwrite the text + updated_at; leaves structured fields intact."""
        self.ensure_collection()
        existing = self._client.retrieve(
            collection_name=self.collection,
            ids=[memory_id],
            with_payload=True,
        )
        if not existing:
            raise KeyError(f"memory {memory_id} not found")
        payload = dict(existing[0].payload or {})
        payload["text"] = text
        payload["updated_at"] = _now_iso()
        [vector] = embed_texts([text])
        self._client.upsert(
            collection_name=self.collection,
            points=[qmodels.PointStruct(id=memory_id, vector=vector, payload=payload)],
            wait=True,
        )

    def delete(self, memory_id: str) -> None:
        self.ensure_collection()
        self._client.delete(
            collection_name=self.collection,
            points_selector=qmodels.PointIdsList(points=[memory_id]),
            wait=True,
        )

    def delete_by_source(self, source: str, source_id: str) -> int:
        self.ensure_collection()
        flt = qmodels.Filter(
            must=[
                qmodels.FieldCondition(key="source", match=qmodels.MatchValue(value=source)),
                qmodels.FieldCondition(key="source_id", match=qmodels.MatchValue(value=source_id)),
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


_shared: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    global _shared
    if _shared is None:
        _shared = MemoryStore()
    return _shared
