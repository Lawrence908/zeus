#!/usr/bin/env python3
"""A/B a candidate embedding model against the incumbent, on the real corpus.

Motivation: MTEB tells you a model is better on MTEB. It does not tell you the
gain survives on your documents, your chunk sizes, and your query style. Before
paying for a re-embed and a cutover, measure on the actual index.

METHOD -- known-item retrieval, labels derived from the corpus itself.
Each document in zeus_knowledge is chunked, and every chunk payload carries the
document's `title` and a shared `source_id`. So:

    query = the document title
    gold  = any chunk whose source_id matches that document

That yields thousands of labelled queries with no annotation. It measures
"given the name of a thing, can the index find that thing".

LABEL HYGIENE -- this dominates the result, so it is enforced, not optional.
Titles are NOT unique in this corpus: of 1739 candidate documents, 832 (48%)
shared a title with another document ("README" x156, "readme" x99, "CHANGELOG"
x21). For those, the gold source_id is arbitrary among the duplicates, so a
correct retrieval scores as a miss and both arms are graded partly on luck.
Measured cost of ignoring this: nomic 0.145 -> 0.205 and qwen3 0.440 -> 0.790
recall@10 once duplicates are dropped. Documents whose title is not unique are
therefore excluded; --keep-ambiguous-titles restores the old behaviour only for
demonstrating the effect.

This is a relative comparison run under an identical protocol for both arms, so
the bias applies equally and the DELTA is the meaningful output. Treat the
absolute values as protocol-specific, not as a benchmark score.

Usage:
  python3 scripts/eval_embedding_ab.py \
      --a zeus_knowledge      --a-model nomic-embed-text:v1.5 --a-dims 768 \
      --b zeus_knowledge_qwen3 --b-model qwen3-embedding:4b   --b-dims 2560 \
      --queries 300
"""
from __future__ import annotations

import argparse
import os
import random
from collections import Counter, defaultdict

from qdrant_client import QdrantClient


def _embed_query(text: str, *, model: str, dims: int, url: str) -> list[float]:
    """Embed one query with the prefix convention the collection was built with."""
    import zeus.memory._embed as E

    # embed_texts validates width against the module-level constant, so pin it to
    # this arm's dimension rather than whatever the ambient env says.
    prev_dims, prev_model = E.DEFAULT_EMBED_DIMS, os.environ.get("ZEUS_EMBED_MODEL")
    E.DEFAULT_EMBED_DIMS = dims
    os.environ["ZEUS_EMBED_MODEL"] = model
    try:
        return E.embed_texts([text], ollama_url=url, model=model, task="query")[0]
    finally:
        E.DEFAULT_EMBED_DIMS = prev_dims
        if prev_model is None:
            os.environ.pop("ZEUS_EMBED_MODEL", None)
        else:
            os.environ["ZEUS_EMBED_MODEL"] = prev_model


def _is_named(client: QdrantClient, coll: str) -> bool:
    return isinstance(client.get_collection(coll).config.params.vectors, dict)


def _build_tasks(client: QdrantClient, coll: str, *, keep_ambiguous: bool, limit: int, seed: int):
    """Collect (title -> gold source_id) pairs, dropping non-unique titles."""
    by_source: dict[str, dict] = defaultdict(lambda: {"title": None, "chunks": 0})
    offset = None
    scanned = 0
    while scanned < limit:
        pts, offset = client.scroll(
            collection_name=coll, with_payload=True, with_vectors=False, limit=1000, offset=offset
        )
        if not pts:
            break
        for p in pts:
            pl = p.payload or {}
            sid, title = pl.get("source_id"), pl.get("title")
            if not sid or not title:
                continue
            e = by_source[str(sid)]
            e["title"] = str(title)
            e["chunks"] += 1
        scanned += len(pts)
        if offset is None:
            break
    # Need >=2 chunks so the gold set isn't a single trivial point.
    tasks = [(v["title"], sid) for sid, v in by_source.items() if v["chunks"] >= 2 and v["title"]]
    if not keep_ambiguous:
        counts = Counter(t for t, _ in tasks)
        kept = [(t, s) for t, s in tasks if counts[t] == 1]
        print(f"labels:    {len(kept)} unambiguous of {len(tasks)} candidates "
              f"({len(tasks) - len(kept)} dropped for duplicate titles)")
        tasks = kept
    random.Random(seed).shuffle(tasks)
    return tasks


def _score(client, coll, named, tasks, *, model, dims, url, k):
    hits = 0
    rr = 0.0
    for title, gold_sid in tasks:
        vec = _embed_query(title, model=model, dims=dims, url=url)
        kw = {"using": "dense"} if named else {}
        res = client.query_points(
            collection_name=coll, query=vec, limit=k, with_payload=True, **kw
        ).points
        rank = next(
            (i for i, h in enumerate(res, 1) if str((h.payload or {}).get("source_id")) == gold_sid),
            None,
        )
        if rank:
            hits += 1
            rr += 1.0 / rank
    n = len(tasks)
    return hits / n, rr / n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, help="incumbent collection")
    ap.add_argument("--a-model", required=True)
    ap.add_argument("--a-dims", type=int, required=True)
    ap.add_argument("--b", required=True, help="candidate collection")
    ap.add_argument("--b-model", required=True)
    ap.add_argument("--b-dims", type=int, required=True)
    ap.add_argument("--queries", type=int, default=200)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--scan", type=int, default=40000, help="points scanned to build the task set")
    ap.add_argument("--keep-ambiguous-titles", action="store_true",
                    help="do NOT drop duplicate-titled docs; only for demonstrating label noise")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    ap.add_argument("--ollama-url", default=os.getenv("OLLAMA_URL", "http://localhost:11435"))
    args = ap.parse_args()

    client = QdrantClient(url=args.qdrant_url, timeout=120)
    tasks = _build_tasks(
        client, args.a, keep_ambiguous=args.keep_ambiguous_titles, limit=args.scan, seed=args.seed
    )[: args.queries]
    if not tasks:
        print("No (title, source_id) tasks found; does this collection carry those payload fields?")
        return 1

    print(f"protocol:  known-item retrieval, query=title, gold=source_id, k={args.k}")
    print(f"tasks:     {len(tasks)} documents")
    print()

    rows = []
    for label, coll, model, dims in (
        ("A", args.a, args.a_model, args.a_dims),
        ("B", args.b, args.b_model, args.b_dims),
    ):
        recall, mrr = _score(
            client, coll, _is_named(client, coll), tasks,
            model=model, dims=dims, url=args.ollama_url, k=args.k,
        )
        rows.append((label, coll, model, recall, mrr))
        print(f"  {label}  {coll:26s} {model:24s} recall@{args.k}={recall:.4f}  MRR@{args.k}={mrr:.4f}")

    (_, _, _, ra, ma), (_, _, _, rb, mb) = rows
    print()
    print(f"delta (B - A):  recall {rb - ra:+.4f}   MRR {mb - ma:+.4f}")
    if rb > ra:
        print("  candidate wins on this protocol.")
    elif rb < ra:
        print("  INCUMBENT WINS. The re-embed does not pay for itself here.")
    else:
        print("  tie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
