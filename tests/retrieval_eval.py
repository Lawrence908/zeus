# tests/retrieval_eval.py — Retrieval regression harness for Zeus knowledge layer.
#
# Thirty hand-written (query, expected_keywords) pairs over the real ingested
# corpus (chatgpt, obsidian, markdown, homelab, git, newsletter). Each live run
# computes hit@1 / hit@5 / hit@10 and MRR against KnowledgeStore (dense or
# dense+BM25+rerank depending on env flags) and prints a per-query + summary
# report.
#
# Gate with ZEUS_RUN_RETRIEVAL_EVAL=1 (requires Qdrant + Ollama up). Optional
# ZEUS_RETRIEVAL_MIN_HIT5=<float> fails the test if mean hit@5 drops below the
# threshold — set this to the current baseline before changing retrieval config.

from __future__ import annotations

import json
import os
import re
from typing import Any

import pytest

# 30 benchmark pairs: query → keywords that should appear in any top-k hit.
# Coverage: Zeus system docs, astronomy/coursework, homelab/Atlas/Hephaestus,
# personal workflows, chatgpt convos, git commits, TLDR newsletter.
GROUND_TRUTH: list[dict[str, Any]] = [
    # -- Zeus system --
    {"query": "What is the Zeus project?", "expected_keywords": ["zeus", "assistant", "homelab"]},
    {"query": "How does Zeus handle voice input and output?", "expected_keywords": ["orpheus", "tts", "stt", "whisper"]},
    {"query": "Aegis safety policies and guardrails", "expected_keywords": ["aegis", "policy", "safety", "nemoclaw"]},
    {"query": "What embedding model does Zeus use?", "expected_keywords": ["nomic", "embed", "768"]},
    {"query": "Ruflo agent orchestration", "expected_keywords": ["ruflo", "agent", "swarm"]},

    # -- Astronomy / ASTR coursework --
    {"query": "How do stars form from a solar nebula?", "expected_keywords": ["star", "nebula", "solar"]},
    {"query": "Early galaxies and collisional events", "expected_keywords": ["galaxies", "collisional", "ellipticals"]},
    {"query": "Copernicus Brahe Kepler heliocentric model", "expected_keywords": ["copernicus", "kepler", "brahe"]},
    {"query": "Binary stars and stellar groupings", "expected_keywords": ["binary", "stellar", "star"]},

    # -- Math / proof coursework --
    {"query": "Steps to solve a definite integral", "expected_keywords": ["integral", "antiderivative", "bounds"]},
    {"query": "Proof step summaries for lemmas and theorems", "expected_keywords": ["lemma", "theorem", "proof"]},

    # -- Homelab / Atlas / Hephaestus --
    {"query": "Atlas physical network interfaces", "expected_keywords": ["atlas", "eno1", "networking"]},
    {"query": "Hephaestus fresh server directory structure", "expected_keywords": ["hephaestus", "github", "directory"]},
    {"query": "Caddy proxy diagnostics troubleshooting", "expected_keywords": ["caddy", "proxy", "diagnostics"]},
    {"query": "ZFS pool RAIDZ2 mount setup", "expected_keywords": ["zfs", "pool", "raidz2"]},
    {"query": "SSH fail2ban hardening", "expected_keywords": ["fail2ban", "ssh", "systemctl"]},

    # -- Personal workflows --
    {"query": "Gmail OAuth trigger for rent receipts", "expected_keywords": ["gmail", "oauth", "rent"]},
    {"query": "InboxCast personalized inbox summary", "expected_keywords": ["inboxcast", "summary", "inbox"]},

    # -- ChatGPT coding conversations --
    {"query": "Azure VM xfce4 session setup", "expected_keywords": ["azure", "xfce4", "session"]},
    {"query": "WSL update in PowerShell", "expected_keywords": ["wsl", "powershell", "update"]},
    {"query": "Portfolio of tools I have built", "expected_keywords": ["portfolio", "tools", "platforms"]},
    {"query": "Resume for software developer data scientist student", "expected_keywords": ["resume", "software", "developer"]},
    {"query": "C floating point addition function", "expected_keywords": ["floating", "fp_number", "add_floating_point"]},
    {"query": "Team Arena PlayerNFT Linear checklist", "expected_keywords": ["playernft", "linear", "checklist"]},
    {"query": "Lulu webhook email order integration", "expected_keywords": ["lulu", "webhook", "order"]},

    # -- Philosophy / ethics --
    {"query": "Plato Republic summary life lessons", "expected_keywords": ["plato", "republic", "lessons"]},
    {"query": "AI deception risks ethical dilemma", "expected_keywords": ["deception", "ethical", "dilemma"]},

    # -- TLDR newsletter --
    {"query": "Physical Intelligence robotics research", "expected_keywords": ["physical intelligence", "robots", "robotics"]},
    {"query": "Amazon Leo in-flight antenna vs Starlink", "expected_keywords": ["amazon", "leo", "antenna", "starlink"]},

    # -- Git commits --
    {"query": "Add Telegram integration feature", "expected_keywords": ["telegram", "integration"]},
]


def _keywords_hit(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    # Use plain substring for multi-word phrases; word-boundary for single tokens.
    for k in keywords:
        kl = k.lower()
        if " " in kl:
            if kl in low:
                return True
        elif re.search(rf"\b{re.escape(kl)}\b", low):
            return True
    return False


def test_ground_truth_minimum_size():
    assert len(GROUND_TRUTH) >= 30


def test_ground_truth_shape():
    for row in GROUND_TRUTH:
        assert isinstance(row.get("query"), str) and row["query"].strip()
        kws = row.get("expected_keywords")
        assert isinstance(kws, list) and len(kws) >= 1
        assert all(isinstance(k, str) and k.strip() for k in kws)


@pytest.mark.skipif(
    os.getenv("ZEUS_RUN_RETRIEVAL_EVAL") != "1",
    reason="Set ZEUS_RUN_RETRIEVAL_EVAL=1 to run live retrieval eval (needs Qdrant + Ollama).",
)
def test_live_retrieval_metrics(capsys):
    """Compute hit@1/5/10 and MRR over the 30-query set against KnowledgeStore."""
    from zeus.memory.search import search_knowledge

    top_k = 10
    per_query: list[dict[str, Any]] = []
    hit1 = hit5 = hit10 = 0
    mrr_sum = 0.0
    n = len(GROUND_TRUTH)

    for row in GROUND_TRUTH:
        q = str(row["query"])
        kws = list(row["expected_keywords"])
        hits = search_knowledge(query=q, user_id="chris", top_k=top_k)
        first_rank = 0  # 1-indexed; 0 means no hit
        for i, h in enumerate(hits):
            text = str(h.get("memory", ""))
            if _keywords_hit(text, kws):
                first_rank = i + 1
                break
        rr = (1.0 / first_rank) if first_rank else 0.0
        mrr_sum += rr
        if 1 <= first_rank <= 1:
            hit1 += 1
        if 1 <= first_rank <= 5:
            hit5 += 1
        if 1 <= first_rank <= 10:
            hit10 += 1
        per_query.append(
            {
                "query": q,
                "keywords": kws,
                "first_rank": first_rank,
                "rr": round(rr, 4),
                "n_hits": len(hits),
                "top1_source": str((hits[0].get("metadata", {}) or {}).get("source", "")) if hits else "",
                "top1_path": str((hits[0].get("metadata", {}) or {}).get("file", "")) if hits else "",
            }
        )

    summary = {
        "n_queries": n,
        "hit@1": round(hit1 / n, 4),
        "hit@5": round(hit5 / n, 4),
        "hit@10": round(hit10 / n, 4),
        "mrr@10": round(mrr_sum / n, 4),
        "config": {
            "ZEUS_KNOWLEDGE_HYBRID": os.getenv("ZEUS_KNOWLEDGE_HYBRID", "1"),
            "ZEUS_KNOWLEDGE_RERANK": os.getenv("ZEUS_KNOWLEDGE_RERANK", "0"),
            "ZEUS_EMBED_MODEL": os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text"),
        },
    }

    # Per-query report — makes failing queries immediately actionable.
    print("\n=== retrieval_eval: per-query ===")
    for row in per_query:
        flag = "OK " if row["first_rank"] else "MISS"
        print(
            f"  {flag} rank={row['first_rank']:>2} rr={row['rr']:.3f}  "
            f"{row['query'][:60]:60}  -> {row['top1_source']}/{row['top1_path'][:40]}"
        )
    print("=== retrieval_eval: summary ===")
    print(json.dumps(summary, indent=2))

    # Optional write to disk for tracking across runs.
    out_path = os.getenv("ZEUS_RETRIEVAL_EVAL_OUT")
    if out_path:
        with open(out_path, "w") as f:
            json.dump({"summary": summary, "per_query": per_query}, f, indent=2)

    # Optional regression gate.
    min_hit5 = os.getenv("ZEUS_RETRIEVAL_MIN_HIT5")
    if min_hit5:
        threshold = float(min_hit5)
        assert summary["hit@5"] >= threshold, (
            f"hit@5 {summary['hit@5']} below threshold {threshold}"
        )
