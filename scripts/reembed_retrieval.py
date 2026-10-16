#!/usr/bin/env python3
"""Re-embed a Qdrant collection's stored documents.

Two migrations use this (see docs/RETRIEVAL_MIGRATION.md):

  * nomic task prefixes: after setting ZEUS_EMBED_PREFIXES=1, re-embed each dense
    collection so stored vectors match prefixed queries.
  * fact-store BM25 hybrid: with --to-hybrid, build a named dense + BM25 sparse
    copy of a dense-only collection (writes <collection>_hybrid).

For a large, live collection use --target to write to a NEW collection so live
retrieval keeps serving until an atomic cutover.

Resilient and resumable, since a 307K-point job spans hours and will hit
transient Ollama disconnects: embed calls retry with backoff, and re-running
against an existing --target skips points already copied (upserts use the source
point ids), so a crash costs only the in-flight batch.

Dry-run by default. Snapshot first. Nothing writes without --apply.

Usage:
  python3 scripts/reembed_retrieval.py --collection zeus_knowledge --target zeus_knowledge_prefixed         # dry run
  ZEUS_EMBED_PREFIXES=1 python3 scripts/reembed_retrieval.py --collection zeus_knowledge --target zeus_knowledge_prefixed --apply
  python3 scripts/reembed_retrieval.py --collection zeus_memories --to-hybrid --apply
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from zeus.memory._embed import DEFAULT_EMBED_DIMS, embed_texts, prefix_style

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


def _retry(fn, *, what: str, retries: int = 12):
    """Run fn(), retrying transient failures with exponential backoff.

    Patient by default: on a shared GPU, Ollama can 500 for a couple of minutes
    while it swaps the chat model against nomic. 12 attempts with backoff capped
    at 180s rides out a ~15 min wedge before giving up.
    """
    delay = 3.0
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - migration tool, surface + retry
            if attempt == retries:
                raise
            print(f"  {what} failed ({attempt}/{retries}): {exc}; retry in {delay:.0f}s", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 180.0)


# Bigger chunks mean fewer HTTP round trips against Ollama. Measured on 256 real
# zeus_knowledge chunks (mean 909 chars) with qwen3-embedding:4b:
#   chunk=32 -> 7.16 pts/s     chunk=256 -> 9.47 pts/s
# The trade-off is retry granularity: a failed chunk re-embeds all of it. 128 is
# the compromise. Override with --embed-chunk.
DEFAULT_EMBED_CHUNK = 128


def _embed_dense(texts: list[str], chunk: int = DEFAULT_EMBED_CHUNK) -> list[list[float]]:
    """Dense-embed in chunks so a retry re-does at most `chunk` items."""
    out: list[list[float]] = []
    for i in range(0, len(texts), chunk):
        sub = texts[i : i + chunk]
        out.extend(_retry(lambda s=sub: embed_texts(s, task="document", batch_size=chunk), what="embed"))
    return out


def _existing_ids(client: QdrantClient, coll: str) -> set:
    ids: set = set()
    offset = None
    while True:
        pts, offset = _retry(
            lambda o=offset: client.scroll(
                collection_name=coll, with_payload=False, with_vectors=False, limit=1000, offset=o
            ),
            what="scroll-existing",
        )
        ids.update(p.id for p in pts)
        if offset is None or not pts:
            break
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--collection", required=True, help="source collection name")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--to-hybrid", action="store_true", help="build a named dense + BM25 copy at <collection>_hybrid")
    ap.add_argument("--target", help="write to this collection instead of in place (preserves source shape; safe for live cutover)")
    ap.add_argument("--batch", type=int, default=256, help="points scrolled/upserted per round")
    ap.add_argument("--embed-chunk", type=int, default=DEFAULT_EMBED_CHUNK, help="texts per Ollama call")
    ap.add_argument(
        "--upsert-wait",
        action="store_true",
        help="block until Qdrant indexes each batch (slower; measured 6.3s vs 2.2s per 256). "
        "Off by default: the run verifies the final count anyway, and the job is resumable.",
    )
    ap.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    ap.add_argument(
        "--qdrant-timeout",
        type=float,
        default=120.0,
        help="seconds. The client default (~5s) is far too low here: while Qdrant's "
        "optimizer indexes wide (2560-dim) vectors, scroll and count routinely "
        "exceed it, and a timeout on the source read used to kill the whole run.",
    )
    args = ap.parse_args()

    client = QdrantClient(url=args.qdrant_url, timeout=args.qdrant_timeout)
    src = args.collection
    info = client.get_collection(src)
    total = client.count(collection_name=src, exact=True).count
    vectors_cfg = info.config.params.vectors
    src_named = isinstance(vectors_cfg, dict)
    src_sparse = bool(getattr(info.config.params, "sparse_vectors", None))

    if args.target:
        target = args.target
    elif args.to_hybrid:
        target = f"{src}_hybrid"
    else:
        target = src
    want_sparse = args.to_hybrid or src_sparse
    want_named = args.to_hybrid or src_named
    existing_colls = {c.name for c in client.get_collections().collections}
    resuming = target != src and target in existing_colls

    src_dims = (
        vectors_cfg[DENSE_VECTOR].size if src_named else getattr(vectors_cfg, "size", None)
    )
    print(f"source:    {src}  ({total} points, named={src_named}, sparse={src_sparse}, dims={src_dims})")
    print(f"target:    {target}  (named={want_named}, sparse={want_sparse}, dims={DEFAULT_EMBED_DIMS})"
          f"{'  [RESUME]' if resuming else ''}")
    print(f"model:     {os.getenv('ZEUS_EMBED_MODEL', 'nomic-embed-text:v1.5')}  (prefix style: {prefix_style()})")
    if src_dims is not None and src_dims != DEFAULT_EMBED_DIMS and target == src:
        print(
            f"\nREFUSING: in-place re-embed would write {DEFAULT_EMBED_DIMS}-dim vectors "
            f"into a {src_dims}-dim collection. Use --target for a new collection."
        )
        return 2
    if not args.apply:
        print("\nDRY RUN. Re-run with --apply to write. Snapshot the collection first.")
        return 0

    if target != src and not resuming:
        vectors_config = (
            {DENSE_VECTOR: qmodels.VectorParams(size=DEFAULT_EMBED_DIMS, distance=qmodels.Distance.COSINE)}
            if want_named
            else qmodels.VectorParams(size=DEFAULT_EMBED_DIMS, distance=qmodels.Distance.COSINE)
        )
        create_kwargs: dict = dict(
            collection_name=target,
            vectors_config=vectors_config,
            optimizers_config=qmodels.OptimizersConfigDiff(indexing_threshold=2000),
        )
        if want_sparse:
            create_kwargs["sparse_vectors_config"] = {
                SPARSE_VECTOR: qmodels.SparseVectorParams(modifier=qmodels.Modifier.IDF)
            }
        client.create_collection(**create_kwargs)
        print(f"created collection {target} (named={want_named}, sparse={want_sparse})")

    done_ids = _existing_ids(client, target) if resuming else set()
    if done_ids:
        print(f"resuming: {len(done_ids)} points already in {target}; skipping them")

    bm25 = _bm25() if want_sparse else None
    offset = None
    done = len(done_ids)
    while True:
        # Retried like the embed/upsert calls below. This read used to be the one
        # unguarded network call in the loop, so a single transient Qdrant timeout
        # aborted a multi-hour job (observed at 98,560/307,451).
        points, offset = _retry(
            lambda o=offset: client.scroll(
                collection_name=src,
                with_payload=True,
                with_vectors=False,
                limit=args.batch,
                offset=o,
            ),
            what="scroll",
        )
        if not points:
            break
        todo = [p for p in points if p.id not in done_ids] if done_ids else points
        if todo:
            texts = [str((p.payload or {}).get("text", "")) for p in todo]
            dense = _embed_dense(texts, chunk=args.embed_chunk)
            sparse = _sparse_vectors(bm25, texts) if bm25 is not None else [None] * len(texts)
            out: list[qmodels.PointStruct] = []
            for i, p in enumerate(todo):
                if want_named:
                    vec: object = {DENSE_VECTOR: dense[i]}
                    if sparse[i] is not None:
                        vec[SPARSE_VECTOR] = sparse[i]  # type: ignore[index]
                else:
                    vec = dense[i]
                out.append(qmodels.PointStruct(id=p.id, vector=vec, payload=p.payload))
            _retry(
                lambda o=out: client.upsert(collection_name=target, points=o, wait=args.upsert_wait),
                what="upsert",
            )
            done += len(out)
            print(f"  re-embedded {done}/{total}", flush=True)
        if offset is None:
            break

    # With wait=False the last upserts may still be indexing, so confirm the
    # target actually landed every point rather than trusting the loop counter.
    deadline = time.time() + 300
    final = client.count(collection_name=target, exact=True).count
    while final < total and time.time() < deadline:
        time.sleep(5)
        final = client.count(collection_name=target, exact=True).count
    print(f"done: {done} embedded; {target} holds {final}/{total} points", flush=True)
    if final != total:
        print(f"WARNING: {target} has {final} of {total} points. Re-run to resume the gap.")
        return 1
    if args.to_hybrid:
        print("next: verify counts, then point QDRANT_COLLECTION at the hybrid collection and set ZEUS_MEMORY_HYBRID=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
