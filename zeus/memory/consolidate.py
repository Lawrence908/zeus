# zeus/memory/consolidate.py — Memory consolidation job (Sprint 9e)
# Periodically deduplicates near-duplicate chunks in Qdrant to keep
# mnemosyne lean. Similarity threshold is controlled by env var.
import logging
import math
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("mnemosyne.consolidate")

SIMILARITY_THRESHOLD = float(os.getenv("CONSOLIDATE_SIMILARITY_THRESHOLD", "0.95"))
# Batch size for Qdrant scroll — keep memory usage bounded
_SCROLL_BATCH = 200


@dataclass
class ConsolidationResult:
    scanned: int = 0
    candidate_pairs: int = 0
    merged: int = 0
    deleted: int = 0
    errors: list[str] = field(default_factory=list)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _merge_texts(texts: list[str]) -> str:
    """Merge a group of near-duplicate texts, keeping the longest."""
    return max(texts, key=len)


class MemoryConsolidator:
    """
    Scan Qdrant for near-duplicate chunks, merge them, and clean up.

    This runs on a schedule via APScheduler (see zeus/ingest/scheduler.py).
    It accesses Qdrant directly rather than through mem0 to avoid
    re-embedding during the dedup scan.
    """

    def __init__(self, memory_client: Any, similarity_threshold: float = SIMILARITY_THRESHOLD) -> None:
        self._memory = memory_client
        self._threshold = similarity_threshold

    def _get_qdrant(self):
        """Extract raw qdrant_client from mem0 wrapper."""
        for attr in ("vector_store", "_vector_store"):
            vs = getattr(self._memory, attr, None)
            if vs is not None:
                for inner in ("client", "_client", "qdrant_client"):
                    c = getattr(vs, inner, None)
                    if c is not None:
                        return c
        return None

    async def run(self) -> dict[str, int]:
        """
        Find near-duplicate chunks, merge, delete originals.

        Steps:
          1. Scroll all chunks from Qdrant with vectors
          2. Find pairs with cosine similarity > threshold
          3. Merge text, keep highest-quality source metadata
          4. Delete originals, write merged chunk via mem0
        """
        result = ConsolidationResult()
        qdrant = self._get_qdrant()

        if qdrant is None:
            logger.warning("consolidate: qdrant client not accessible — skipping")
            return {"scanned": 0, "merged": 0, "deleted": 0}

        # Discover collection names
        try:
            collections = [c.name for c in qdrant.get_collections().collections]
        except Exception as exc:
            logger.error("consolidate: failed to list collections — %s", exc)
            return {"scanned": 0, "merged": 0, "deleted": 0}

        for collection in collections:
            await self._consolidate_collection(qdrant, collection, result)

        logger.info(
            "consolidate: done — scanned=%d pairs=%d merged=%d deleted=%d errors=%d",
            result.scanned, result.candidate_pairs,
            result.merged, result.deleted, len(result.errors),
        )
        return {
            "scanned": result.scanned,
            "candidate_pairs": result.candidate_pairs,
            "merged": result.merged,
            "deleted": result.deleted,
            "errors": result.errors,
        }

    async def _consolidate_collection(self, qdrant, collection: str, result: ConsolidationResult) -> None:
        """Process one Qdrant collection."""
        points: list[dict] = []

        # Scroll all points with vectors
        offset = None
        while True:
            try:
                batch, next_offset = qdrant.scroll(
                    collection_name=collection,
                    limit=_SCROLL_BATCH,
                    offset=offset,
                    with_vectors=True,
                    with_payload=True,
                )
            except Exception as exc:
                logger.warning("consolidate: scroll failed on %s — %s", collection, exc)
                result.errors.append(f"{collection}: scroll error: {exc}")
                break

            for p in batch:
                if p.vector:
                    points.append({
                        "id": p.id,
                        "vector": p.vector if isinstance(p.vector, list) else list(p.vector.values())[0],
                        "payload": p.payload or {},
                    })

            result.scanned += len(batch)
            if next_offset is None:
                break
            offset = next_offset

        if len(points) < 2:
            return

        # Find near-duplicate pairs (O(n²) — acceptable for personal-scale collections)
        to_delete: set[str] = set()
        merged_chunks: list[dict] = []

        for i in range(len(points)):
            if points[i]["id"] in to_delete:
                continue
            group = [points[i]]

            for j in range(i + 1, len(points)):
                if points[j]["id"] in to_delete:
                    continue
                sim = _cosine_similarity(points[i]["vector"], points[j]["vector"])
                if sim >= self._threshold:
                    result.candidate_pairs += 1
                    group.append(points[j])

            if len(group) > 1:
                # Merge all group members into one chunk
                texts = [p["payload"].get("data", p["payload"].get("text", "")) for p in group]
                merged_text = _merge_texts([t for t in texts if t])
                if not merged_text:
                    continue

                best_meta = max(group, key=lambda p: len(p["payload"].get("data", "")))["payload"]
                merged_chunks.append({
                    "text": merged_text,
                    "metadata": {k: v for k, v in best_meta.items() if k not in ("data",)},
                    "user_id": best_meta.get("user_id", "chris"),
                })
                for p in group:
                    to_delete.add(p["id"])

        # Delete originals
        if to_delete:
            try:
                qdrant.delete(
                    collection_name=collection,
                    points_selector=list(to_delete),
                )
                result.deleted += len(to_delete)
            except Exception as exc:
                logger.error("consolidate: delete failed on %s — %s", collection, exc)
                result.errors.append(f"{collection}: delete error: {exc}")

        # Write merged chunks back via mem0
        for chunk in merged_chunks:
            try:
                self._memory.add(
                    messages=[{"role": "user", "content": chunk["text"]}],
                    user_id=chunk["user_id"],
                    metadata={**chunk["metadata"], "consolidated": True},
                )
                result.merged += 1
            except Exception as exc:
                logger.warning("consolidate: failed to write merged chunk — %s", exc)
                result.errors.append(f"write error: {exc}")
