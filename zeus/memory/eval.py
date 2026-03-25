"""zeus/memory/eval.py — Retrieval evaluation harness (ground-truth queries).

Run:
  python3 -m zeus.memory.eval --query-set zeus/data/eval/queries.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from zeus.memory.config import get_memory_client
from zeus.memory.search import search_memories


@dataclass(frozen=True)
class EvalCase:
    query: str
    expected_sources: list[str]
    tags: list[str]


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _source_of(mem: dict) -> str:
    md = mem.get("metadata", {}) or {}
    return str(md.get("source") or "")


def _matches_expected(actual_source: str, expected: str) -> bool:
    a = _norm(actual_source)
    e = _norm(expected)
    if not a or not e:
        return False
    return e in a


def _first_rank(results: list[dict], expected_sources: list[str]) -> int | None:
    if not expected_sources:
        return None
    for idx, mem in enumerate(results, 1):
        src = _source_of(mem)
        if any(_matches_expected(src, exp) for exp in expected_sources):
            return idx
    return None


def _recall_at_k(results: list[dict], expected_sources: list[str], k: int) -> float:
    if not expected_sources:
        return 1.0
    top = results[:k]
    found = 0
    for exp in expected_sources:
        if any(_matches_expected(_source_of(mem), exp) for mem in top):
            found += 1
    return found / max(len(expected_sources), 1)


def load_query_set(path: Path) -> list[EvalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("query set must be a JSON array")

    cases: list[EvalCase] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        query = str(item.get("query") or "").strip()
        if not query:
            continue
        expected = item.get("expected_sources") or []
        tags = item.get("tags") or []
        if not isinstance(expected, list):
            expected = []
        if not isinstance(tags, list):
            tags = []
        cases.append(
            EvalCase(
                query=query,
                expected_sources=[str(x) for x in expected if str(x).strip()],
                tags=[str(x) for x in tags if str(x).strip()],
            )
        )
    return cases


def run_eval(*, cases: list[EvalCase], top_k: int) -> dict[str, Any]:
    memory = get_memory_client()

    per_case: list[dict[str, Any]] = []
    r5_sum = r10_sum = 0.0
    mrr_sum = 0.0

    for c in cases:
        results = search_memories(memory=memory, query=c.query, user_id="chris", top_k=top_k)
        rank = _first_rank(results, c.expected_sources)
        r5 = _recall_at_k(results, c.expected_sources, 5)
        r10 = _recall_at_k(results, c.expected_sources, 10)
        rr = 0.0 if rank is None else 1.0 / float(rank)

        r5_sum += r5
        r10_sum += r10
        mrr_sum += rr

        per_case.append(
            {
                "query": c.query,
                "tags": c.tags,
                "expected_sources": c.expected_sources,
                "rank_first_hit": rank,
                "recall@5": r5,
                "recall@10": r10,
                "rr": rr,
                "retrieved_sources": [_source_of(m) for m in results],
            }
        )

    n = max(len(cases), 1)
    return {
        "count": len(cases),
        "top_k": top_k,
        "recall@5": r5_sum / n,
        "recall@10": r10_sum / n,
        "mrr": mrr_sum / n,
        "cases": per_case,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Zeus retrieval evaluation harness")
    p.add_argument(
        "--query-set",
        default="zeus/data/eval/queries.json",
        help="Path to ground-truth query set JSON (default: zeus/data/eval/queries.json)",
    )
    p.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="How many memories to retrieve per query (default: 10)",
    )
    p.add_argument(
        "--out",
        default="",
        help="Optional output path for JSON report (default: print only)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    query_set_path = Path(args.query_set)
    cases = load_query_set(query_set_path)
    report = run_eval(cases=cases, top_k=int(args.top_k))

    out = json.dumps(report, indent=2, sort_keys=False)
    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()

