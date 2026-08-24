#!/usr/bin/env python3
"""Re-embed a Qdrant collection's stored documents.

Two migrations use this (see docs/RETRIEVAL_MIGRATION.md):

  * nomic task prefixes: after setting ZEUS_EMBED_PREFIXES=1, re-embed each dense
    collection in place so stored vectors match prefixed queries.
  * fact-store BM25 hybrid: with --to-hybrid, build a named dense + BM25 sparse
    copy of a dense-only collection (writes <collection>_hybrid, non-destructive).

Dry-run by default. Snapshot the collection first. Nothing is written without
--apply. Re-embedding is idempotent: it recomputes vectors from payload["text"]
and upserts them under the same ids and payloads, so it is safe to re-run.

Usage:
  python3 scripts/reembed_retrieval.py --collection zeus_knowledge          # dry run
  ZEUS_EMBED_PREFIXES=1 python3 scripts/reembed_retrieval.py --collection zeus_knowledge --apply
  python3 scripts/reembed_retrieval.py --collection zeus_memories --to-hybrid --apply
"""
from __future__ import annotations

import argparse
import os
import sys

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from zeus.memory._embed import DEFAULT_EMBED_DIMS, EMBED_PREFIXES, embed_texts

DENSE_VECTOR = "dense"
SPARSE_VECTOR = "bm25"


def _bm25():
    from fastembed import SparseTextEmbedding

    cache_dir = os.getenv("ZEUS_FASTEMBED_CACHE_DIR", "zeus/data/fastembed_cache")
    return SparseTextEmbedding("Qdrant/bm25", cache_dir=cache_dir)


def _sparse_vectors(model, texts: list[str]) -> list[qmodels.SparseVector]:
    return [
        qmodels.SparseVector(indices=e.indices.tolist(), values=e.values.tolist())
        for e in model.embed(texts)
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--collection", required=True, help="source collection name")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--to-hybrid", action="store_true", help="build a named dense + BM25 copy at <collection>_hybrid")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    args = ap.parse_args()

    client = QdrantClient(url=args.qdrant_url)
    src = args.collection
    info = client.get_collection(src)
    total = client.count(collection_name=src, exact=True).count
    vectors_cfg = info.config.params.vectors
    src_named = isinstance(vectors_cfg, dict)
    src_sparse = bool(getattr(info.config.params, "sparse_vectors", None))

    target = f"{src}_hybrid" if args.to_hybrid else src
    want_sparse = args.to_hybrid or src_sparse
    want_named = args.to_hybrid or src_named

    print(f"source:        {src}  ({total} points, named={src_named}, sparse={src_sparse})")
    print(f"target:        {target}  (named={want_named}, sparse={want_sparse})")
    print(f"prefixes:      ZEUS_EMBED_PREFIXES={'on' if EMBED_PREFIXES else 'off'}  (docs use 'search_document: ')")
    if not args.apply:
        print("\nDRY RUN. Re-run with --apply to write. Snapshot the collection first.")
        return 0

    if args.to_hybrid:
        if target in {c.name for c in client.get_collections().collections}:
            print(f"error: {target} already exists; delete it or pick another name", file=sys.stderr)
            return 2
        client.create_collection(
            collection_name=target,
            vectors_config={DENSE_VECTOR: qmodels.VectorParams(size=DEFAULT_EMBED_DIMS, distance=qmodels.Distance.COSINE)},
            sparse_vectors_config={SPARSE_VECTOR: qmodels.SparseVectorParams(modifier=qmodels.Modifier.IDF)},
            optimizers_config=qmodels.OptimizersConfigDiff(indexing_threshold=2000),
        )
        print(f"created hybrid collection {target}")

    bm25 = _bm25() if want_sparse else None
    offset = None
    done = 0
    while True:
        points, offset = client.scroll(
            collection_name=src,
            with_payload=True,
            with_vectors=False,
            limit=args.batch,
            offset=offset,
        )
        if not points:
            break
        texts = [str((p.payload or {}).get("text", "")) for p in points]
        dense = embed_texts(texts, task="document")
        sparse = _sparse_vectors(bm25, texts) if bm25 is not None else [None] * len(texts)

        out: list[qmodels.PointStruct] = []
        for i, p in enumerate(points):
            if want_named:
                vec: object = {DENSE_VECTOR: dense[i]}
                if sparse[i] is not None:
                    vec[SPARSE_VECTOR] = sparse[i]  # type: ignore[index]
            else:
                vec = dense[i]
            out.append(qmodels.PointStruct(id=p.id, vector=vec, payload=p.payload))
        client.upsert(collection_name=target, points=out, wait=True)
        done += len(out)
        print(f"  re-embedded {done}/{total}")
        if offset is None:
            break

    print(f"done: {done} points -> {target}")
    if args.to_hybrid:
        print("next: verify counts, then alias zeus_memories -> zeus_memories_hybrid (see docs) and set ZEUS_MEMORY_HYBRID=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
