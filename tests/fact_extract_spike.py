# tests/fact_extract_spike.py — Spike 4: fact-extraction provider shootout.
#
# Runs 20 representative messages through {gemini_paid, anthropic_haiku, ollama}
# with response_format=FactExtraction, min_privacy_tier=1, and reports per-
# provider: schema-invalid rate, facts-per-extraction, avg confidence, PII-flag
# hit rate, latency, and estimated cost. Decides whether the default
# small_llm_call path for PII content should route Gemini paid first (cheap,
# fast) or Claude Haiku first (higher reliability).
#
# Gate with ZEUS_RUN_FACT_SPIKE=1. Output JSON to ZEUS_FACT_SPIKE_OUT if set.

from __future__ import annotations

import asyncio
import json
import os
import statistics
import time
from typing import Any

import pytest


# 20 representative messages — covers identity, preferences, projects, tasks,
# events, relationships (PII), pure-code (should emit []), garbled (should
# emit []), compound sentences, short preferences.
MESSAGES: list[dict[str, str]] = [
    {"id": "m01", "text": "My name is Chris Lawrence and I live in Victoria, BC."},
    {"id": "m02", "text": "I'm a software developer and data-science student finishing my degree in spring 2026."},
    {"id": "m03", "text": "I prefer plain text in Telegram replies, no markdown or emojis."},
    {"id": "m04", "text": "Never use emdashes in generated text for any of my projects."},
    {"id": "m05", "text": "Zeus runs on Olympus (RTX 3080, 10GB VRAM) in prod and the 5080 tower in dev."},
    {"id": "m06", "text": "I use Tailscale to reach my homelab and run OPNsense on a mini-PC for the firewall."},
    {"id": "m07", "text": "Meeting with Sarah Chen (sarah@acmecorp.com) rescheduled to 2026-05-03 at 14:00 PT."},
    {"id": "m08", "text": "I switched from mem0 to a hand-rolled MemoryStore in April 2026 after mem0 shipped breaking changes."},
    {"id": "m09", "text": "Ship the Ruflo v3.5 agent runtime by end of Q2."},
    {"id": "m10", "text": "I believe privacy-preserving local AI will matter more than ever by 2027."},
    {"id": "m11", "text": "Dr. Michael Tang (+1-250-555-0199) is my family physician in Victoria."},
    {"id": "m12", "text": "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)"},
    {"id": "m13", "text": "askdj aslkdjasd 3ip0uweur jlkjj zxcv qwerty asdf hjkl"},
    {"id": "m14", "text": "A hash table supports average-case O(1) lookups and O(n) worst case."},
    {"id": "m15", "text": "I renewed my apartment lease at 123 Fort Street, Victoria, until 2027-03-31."},
    {"id": "m16", "text": "My partner Alex and I adopted a cat named Mochi on 2026-01-15."},
    {"id": "m17", "text": "I use Obsidian for personal notes, VS Code for Python, and Claude Code as my AI coding assistant."},
    {"id": "m18", "text": "The AstrID project is on pause until I finish Zeus's Phase 2 retrieval work."},
    {"id": "m19", "text": "I decided to stop running n8n on daedalus because it conflicted with zeus-core on port 5678."},
    {"id": "m20", "text": "Birthday dinner with mom at The Marina Restaurant on 2026-06-12 at 18:30."},
]


# Providers to test. Chain contains exactly one entry per run so small_llm_call
# routes only to that provider.
PROVIDERS = ["gemini_paid", "anthropic_haiku", "ollama"]


async def _run_one(message: dict[str, str], provider: str) -> dict[str, Any]:
    """Invoke small_llm_call for a single (message, provider) pair."""
    # Force the chain to a single provider by patching the module-level default.
    import zeus.core.small_llm as sll

    saved = sll.DEFAULT_CHAIN
    sll.DEFAULT_CHAIN = (provider,)
    try:
        from zeus.memory.store import FactExtraction
        from zeus.core.prompts import render

        system = render("memory_extract")
        user = (
            f"source_id: spike4:{message['id']}\n"
            f"text:\n{message['text']}"
        )

        t0 = time.perf_counter()
        result = await sll.small_llm_call(
            system=system,
            user=user,
            max_tokens=1024,
            response_format=FactExtraction,
            min_privacy_tier=1,
            caller=f"spike4:{message['id']}",
        )
        wall_ms = round((time.perf_counter() - t0) * 1000)
    except sll.AllProvidersFailed as exc:
        return {
            "message_id": message["id"],
            "provider": provider,
            "ok": False,
            "error": f"all providers failed: {exc}",
            "wall_ms": None,
        }
    except Exception as exc:
        return {
            "message_id": message["id"],
            "provider": provider,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "wall_ms": None,
        }
    finally:
        sll.DEFAULT_CHAIN = saved

    parsed = result.parsed
    facts: list[dict] = []
    if parsed is not None and hasattr(parsed, "facts"):
        facts = [f.model_dump(mode="json") for f in parsed.facts]

    return {
        "message_id": message["id"],
        "provider": provider,
        "ok": parsed is not None,
        "provider_used": result.provider_used,
        "model_used": result.model_used,
        "wall_ms": wall_ms,
        "latency_ms": result.latency_ms,
        "tokens_in": result.tokens_in,
        "tokens_out": result.tokens_out,
        "cost_usd": result.cost_usd,
        "n_facts": len(facts),
        "avg_confidence": (
            round(statistics.mean(f["confidence"] for f in facts), 3)
            if facts
            else None
        ),
        "n_pii": sum(1 for f in facts if f.get("contains_pii")),
        "facts_preview": [
            {
                "text": f["text"][:80],
                "category": f["category"],
                "confidence": f["confidence"],
                "contains_pii": f["contains_pii"],
            }
            for f in facts[:3]
        ],
    }


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-provider metrics over all messages."""
    by_provider: dict[str, list[dict]] = {}
    for r in rows:
        by_provider.setdefault(r["provider"], []).append(r)

    out: dict[str, Any] = {}
    for provider, rs in by_provider.items():
        ok = [r for r in rs if r.get("ok")]
        fails = [r for r in rs if not r.get("ok")]
        lats = [r["latency_ms"] for r in ok if r.get("latency_ms")]
        fact_counts = [r["n_facts"] for r in ok]
        out[provider] = {
            "n": len(rs),
            "schema_ok_rate": round(len(ok) / len(rs), 3),
            "schema_invalid_rate": round(len(fails) / len(rs), 3),
            "mean_facts": round(statistics.mean(fact_counts), 2) if fact_counts else 0.0,
            "median_facts": statistics.median(fact_counts) if fact_counts else 0.0,
            "empty_extractions": sum(1 for c in fact_counts if c == 0),
            "latency_p50_ms": int(statistics.median(lats)) if lats else None,
            "latency_p95_ms": (
                int(sorted(lats)[int(len(lats) * 0.95)])
                if len(lats) >= 5 else (max(lats) if lats else None)
            ),
            "total_cost_usd": round(sum(r.get("cost_usd", 0.0) for r in ok), 4),
            "total_tokens_out": sum(r.get("tokens_out", 0) or 0 for r in ok),
            "avg_confidence": (
                round(
                    statistics.mean(
                        r["avg_confidence"]
                        for r in ok
                        if r.get("avg_confidence") is not None
                    ),
                    3,
                )
                if any(r.get("avg_confidence") is not None for r in ok)
                else None
            ),
            "errors": [r.get("error") for r in fails if r.get("error")][:5],
        }
    return out


@pytest.mark.skipif(
    os.getenv("ZEUS_RUN_FACT_SPIKE") != "1",
    reason="Set ZEUS_RUN_FACT_SPIKE=1 to run Spike 4 (needs provider API keys + Ollama).",
)
def test_fact_extraction_shootout():
    """Run all messages through all providers and produce per-provider metrics."""
    rows: list[dict[str, Any]] = []

    async def _run_all():
        for provider in PROVIDERS:
            for msg in MESSAGES:
                row = await _run_one(msg, provider)
                rows.append(row)
                tag = "OK " if row.get("ok") else "FAIL"
                cost = row.get("cost_usd", 0.0) or 0.0
                n_facts = row.get("n_facts", 0)
                wall = row.get("wall_ms", None)
                print(
                    f"  {tag} {provider:>15} {msg['id']}  "
                    f"facts={n_facts:>2} wall={wall}ms cost=${cost:.4f}"
                )

    print("\n=== Spike 4: fact-extraction shootout ===")
    asyncio.run(_run_all())

    summary = _summarize(rows)
    print("\n=== Spike 4: summary ===")
    print(json.dumps(summary, indent=2))

    out_path = os.getenv("ZEUS_FACT_SPIKE_OUT")
    if out_path:
        with open(out_path, "w") as f:
            json.dump({"summary": summary, "rows": rows}, f, indent=2)
        print(f"\nWrote {out_path}")
