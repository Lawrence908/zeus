#!/usr/bin/env python3
# scripts/retrieval_check.py — Quick retrieval sanity check for LAB-61
# Bypasses mem0 LLM overhead: embeds query via Ollama REST, searches Qdrant REST directly.
# Usage:
#   python3 scripts/retrieval_check.py
#   python3 scripts/retrieval_check.py --query "your question" --top-k 5
import argparse
import json
import sys
import urllib.request

OLLAMA_URL = "http://localhost:11435"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "zeus_memories"
EMBED_MODEL = "nomic-embed-text:v1.5"

SAMPLE_QUERIES = [
    "What is Zeus and what problem does it solve for Chris?",
    "What are the main Zeus subsystems and their Greek names?",
    "Where does Zeus store memories and what vector DB does it use?",
    "What is my Obsidian vault and how does it get ingested?",
    "How do I run Iris ingest for markdown notes with a dry-run preview?",
]


def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def embed(text: str) -> list[float]:
    try:
        result = _post(f"{OLLAMA_URL}/api/embed", {"model": EMBED_MODEL, "input": text})
        embeddings = result.get("embeddings") or result.get("embedding")
    except Exception:
        # Fall back to older /api/embeddings endpoint
        result = _post(f"{OLLAMA_URL}/api/embeddings", {"model": EMBED_MODEL, "prompt": text})
        embeddings = result.get("embedding")
    if embeddings and isinstance(embeddings[0], list):
        return embeddings[0]
    return embeddings


def search_qdrant(vector: list[float], top_k: int) -> list[dict]:
    result = _post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        {"vector": vector, "limit": top_k, "with_payload": True},
    )
    return result.get("result", [])


def run(query: str, top_k: int) -> None:
    print(f"\nQuery: {query!r}")
    print("Embedding...", end=" ", flush=True)
    vec = embed(query)
    print(f"done ({len(vec)}d)")

    hits = search_qdrant(vec, top_k)
    print(f"Top {top_k} results:")
    for i, hit in enumerate(hits, 1):
        score = hit.get("score", 0)
        payload = hit.get("payload", {})
        source = payload.get("source", "?")
        data = str(payload.get("data", "")).strip()[:120]
        print(f"  {i}. score={score:.4f}  source={source}")
        print(f"     {data}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--query", default="", help="Single query to run (default: runs all sample queries)")
    p.add_argument("--top-k", type=int, default=5)
    args = p.parse_args()

    queries = [args.query] if args.query else SAMPLE_QUERIES

    for q in queries:
        try:
            run(q, args.top_k)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)

    print()


if __name__ == "__main__":
    main()
