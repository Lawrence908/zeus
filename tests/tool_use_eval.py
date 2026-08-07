# tests/tool_use_eval.py — Tool-use decision + quality regression harness.
#
# Phase 0 of the tool-use-loop productionization (see zeus/docs/tool-use-spec.md).
# Answers the question that gates flipping ZEUS_TOOLS_ENABLED on by default:
# does the active chat model call the RIGHT tool when a prompt needs one, and
# does it correctly STAY QUIET on chit-chat that needs none?
#
# The corpus is two bands:
#   - "needs_tool": the prompt can only be answered well by calling one of an
#     accepted set of tools. Scored on tool-selection accuracy.
#   - "no_tool": the prompt is chit-chat / memory recall / meta. Any tool call
#     is a false positive. Scored on false-positive rate.
#
# Metrics per run (against whichever provider ZEUS_ENV/ZEUS_LLM selects):
#   selection_accuracy   correct tool chosen / needs_tool cases that were runnable
#   false_positive_rate  no_tool cases where any tool fired / no_tool cases
#   answer_hit_rate      cases whose reply contained an expected keyword (soft)
#   latency p50/p95      wall time per case, in ms
#
# Run both providers to get the flip-on decision data:
#   ZEUS_ENV=dev  ZEUS_LLM=claude  ZEUS_RUN_TOOL_EVAL=1 pytest tests/tool_use_eval.py -s
#   ZEUS_ENV=prod ZEUS_LLM=ollama  ZEUS_RUN_TOOL_EVAL=1 pytest tests/tool_use_eval.py -s
# Or as a script (prints a report, optionally writes a baseline):
#   ZEUS_LLM=claude python -m tests.tool_use_eval
#   ZEUS_WRITE_TOOL_EVAL_BASELINE=1 ZEUS_LLM=claude python -m tests.tool_use_eval
#
# Requires the selected LLM reachable (Anthropic key for claude, Ollama up for
# ollama) plus Core deps for whichever tools actually execute. Tool RESULTS may
# fail in a bare test env (e.g. calendar endpoint down); that's fine — this
# harness scores tool SELECTION and reply quality, not downstream tool success.

from __future__ import annotations

import asyncio
import json
import os
import socket
import time
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

# Load .env so the harness runs against the same OLLAMA_URL / ZEUS_EMBED_MODEL /
# provider config as the app (override=False keeps CLI env like ZEUS_LLM ahead).
load_dotenv()

# Force the tool path on for this process before importing query helpers so
# _build_tools_section() renders the tool list into the system prompt.
os.environ.setdefault("ZEUS_TOOLS_ENABLED", "1")

BASELINE_PATH = Path(__file__).with_name("tool_use_eval_baseline.json")

# Per-query tool-call budget for the eval. Kept low so a mis-behaving model
# that loops on tool calls doesn't blow up wall time; 3 is enough for any
# single-tool case in the corpus.
EVAL_MAX_CALLS = 3
EVAL_MAX_TOKENS = 1024


# Each case: prompt, band, and either `expected_tools` (accepted answers for a
# needs_tool case) or nothing (no_tool case must call zero tools). `keywords`
# are soft answer-quality signals — presence of ANY marks an answer hit.
GROUND_TRUTH: list[dict[str, Any]] = [
    # -- needs_tool: time --
    {
        "prompt": "What time is it right now?",
        "band": "needs_tool",
        "expected_tools": ["current_time"],
        "keywords": [":", "20", "utc", "am", "pm"],
    },
    {
        "prompt": "What's today's date and the current day of the week?",
        "band": "needs_tool",
        "expected_tools": ["current_time"],
        "keywords": ["2026", "day", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    },
    # -- needs_tool: calendar --
    {
        "prompt": "What's on my calendar today?",
        "band": "needs_tool",
        "expected_tools": ["zeus_calendar_today"],
        "keywords": ["calendar", "event", "today", "nothing", "no events"],
    },
    {
        "prompt": "Do I have any meetings scheduled for today?",
        "band": "needs_tool",
        "expected_tools": ["zeus_calendar_today"],
        "keywords": ["meeting", "calendar", "event", "no ", "nothing"],
    },
    # -- needs_tool: news (news_search preferred, web_search acceptable) --
    {
        "prompt": "Search my news index for anything about congressional trading.",
        "band": "needs_tool",
        "expected_tools": ["zeus_news_search", "web_search"],
        "keywords": ["news", "congress", "trad", "found", "no "],
    },
    {
        "prompt": "What recent news do you have about AI regulation?",
        "band": "needs_tool",
        "expected_tools": ["zeus_news_search", "web_search"],
        "keywords": ["news", "ai", "regulation", "found", "no "],
    },
    # -- needs_tool: web search (only scored if registered) --
    {
        "prompt": "Look up the current weather in London on the web.",
        "band": "needs_tool",
        "expected_tools": ["web_search"],
        "keywords": ["weather", "london", "temperature", "unavailable"],
    },
    # -- needs_tool: file search over the vault --
    {
        "prompt": "Find files in my notes that mention the Aegis safety policy.",
        "band": "needs_tool",
        "expected_tools": ["olympian_file_search"],
        "keywords": ["file", "aegis", "found", "no "],
    },
    # -- needs_tool: newsletter --
    {
        "prompt": "What's in my latest newsletter digest?",
        "band": "needs_tool",
        "expected_tools": ["zeus_newsletter_latest"],
        "keywords": ["newsletter", "digest", "latest", "no "],
    },
    # -- needs_tool: service health / status --
    {
        "prompt": "Are all my homelab services healthy right now?",
        "band": "needs_tool",
        "expected_tools": ["olympian_server_health"],
        "keywords": ["health", "service", "up", "down", "ok", "status"],
    },
    {
        "prompt": "Read my status file and tell me what it says.",
        "band": "needs_tool",
        "expected_tools": ["olympian_status_read"],
        "keywords": ["status", "file", "no ", "empty"],
    },
    # -- no_tool: chit-chat --
    {
        "prompt": "Hey, how are you doing today?",
        "band": "no_tool",
        "keywords": ["good", "well", "help", "hi", "hello", "doing"],
    },
    {
        "prompt": "Thanks, that was really helpful!",
        "band": "no_tool",
        "keywords": ["welcome", "glad", "happy", "anytime", "no problem"],
    },
    {
        "prompt": "Tell me a short one-line joke.",
        "band": "no_tool",
        "keywords": ["?", "!", "."],
    },
    {
        "prompt": "Summarize in one sentence what you can help me with.",
        "band": "no_tool",
        "keywords": ["help", "assist", "memory", "question", "task"],
    },
    {
        "prompt": "Explain what a vector database is in two sentences.",
        "band": "no_tool",
        "keywords": ["vector", "embedding", "similarity", "database"],
    },
    {
        "prompt": "What does the acronym HTTP stand for?",
        "band": "no_tool",
        "keywords": ["hypertext", "transfer", "protocol"],
    },
]


def _register_tools() -> list[str]:
    """Register the chat-path tools exactly as zeus/core/main.py does at startup."""
    from zeus.core.tools import registry as tool_registry
    from zeus.core.tools.action_run import register as _register_action_pack
    from zeus.core.tools.calendar_today import register as _register_calendar_today
    from zeus.core.tools.current_time import register as _register_current_time
    from zeus.core.tools.deep_research import register as _register_deep_research
    from zeus.core.tools.file_read import register as _register_file_read
    from zeus.core.tools.file_search import register as _register_file_search
    from zeus.core.tools.inbox_append import register as _register_inbox_append
    from zeus.core.tools.newsletter_latest import register as _register_newsletter_latest
    from zeus.core.tools.news_search import register as _register_news_search
    from zeus.core.tools.server_health import register as _register_server_health
    from zeus.core.tools.status_read import register as _register_status_read
    from zeus.core.tools.web_search import register_if_configured as _register_web_search

    _register_current_time()
    _register_web_search()
    _register_status_read()
    _register_server_health()
    _register_file_read()
    _register_file_search()
    _register_inbox_append()
    _register_action_pack()
    _register_calendar_today()
    _register_newsletter_latest()
    _register_deep_research()
    _register_news_search()
    return [spec.name for spec in tool_registry.list_specs()]


async def _run_case(case: dict[str, Any], *, use_claude: bool) -> dict[str, Any]:
    """Run one prompt through the tool loop and score selection + quality."""
    from zeus.core.query import _build_system_prompt, _build_tools_section
    from zeus.core.tools import registry as tool_registry
    from zeus.core.tools.loop import run_tool_loop

    system = _build_system_prompt(
        profile_section="",
        memory_section="",
        conversation_section="",
        knowledge_section="",
        reference_section="",
        tools_section=_build_tools_section(),
    )

    started = time.perf_counter()
    error = ""
    called: list[str] = []
    reply = ""
    iterations = 0
    truncated = False
    try:
        result = await run_tool_loop(
            system=system,
            user_prompt=case["prompt"],
            tools=tool_registry.list_specs(),
            max_tokens=EVAL_MAX_TOKENS,
            max_calls=EVAL_MAX_CALLS,
            use_claude=use_claude,
        )
        called = [c.name for c in result.tool_calls]
        reply = result.reply or ""
        iterations = result.iterations
        truncated = result.truncated
    except Exception as exc:  # noqa: BLE001 — record and continue the sweep
        error = f"{type(exc).__name__}: {exc}"
    latency_ms = int((time.perf_counter() - started) * 1000)

    called_set = list(dict.fromkeys(called))  # de-dupe, keep order
    reply_lc = reply.lower()
    answer_hit = any(kw.lower() in reply_lc for kw in case.get("keywords", []))

    band = case["band"]
    record: dict[str, Any] = {
        "prompt": case["prompt"],
        "band": band,
        "called_tools": called_set,
        "n_calls": len(called),
        "iterations": iterations,
        "truncated": truncated,
        "answer_hit": answer_hit,
        "latency_ms": latency_ms,
        "error": error,
        "reply_preview": reply[:160],
    }

    if band == "needs_tool":
        expected = case["expected_tools"]
        record["expected_tools"] = expected
        record["correct_selection"] = any(t in called_set for t in expected)
        record["called_any_tool"] = bool(called_set)
    else:  # no_tool
        record["false_positive"] = bool(called_set)

    return record


async def run_eval() -> dict[str, Any]:
    from zeus.core.query import _active_model_name, _chat_use_claude

    registered = _register_tools()
    if not registered:
        raise RuntimeError("No chat tools registered — cannot run tool-use eval.")
    use_claude = _chat_use_claude()

    per_case: list[dict[str, Any]] = []
    for case in GROUND_TRUTH:
        # An expected tool that isn't registered (e.g. web_search without a
        # BRAVE_API_KEY) can't be selected — mark it so it's excluded from the
        # selection denominator rather than counted as a miss.
        rec = await _run_case(case, use_claude=use_claude)
        if case["band"] == "needs_tool":
            rec["runnable"] = any(t in registered for t in case["expected_tools"])
        per_case.append(rec)

    needs = [r for r in per_case if r["band"] == "needs_tool"]
    runnable = [r for r in needs if r.get("runnable")]
    no_tool = [r for r in per_case if r["band"] == "no_tool"]
    latencies = [r["latency_ms"] for r in per_case if not r["error"]]

    def _rate(num: int, den: int) -> float:
        return round(num / den, 4) if den else 0.0

    def _pct(values: list[int], q: float) -> int:
        if not values:
            return 0
        ordered = sorted(values)
        idx = min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))
        return ordered[idx]

    summary = {
        "n_cases": len(per_case),
        "n_needs_tool_runnable": len(runnable),
        "n_no_tool": len(no_tool),
        "selection_accuracy": _rate(sum(1 for r in runnable if r["correct_selection"]), len(runnable)),
        "false_positive_rate": _rate(sum(1 for r in no_tool if r["false_positive"]), len(no_tool)),
        "answer_hit_rate": _rate(sum(1 for r in per_case if r["answer_hit"]), len(per_case)),
        "n_errors": sum(1 for r in per_case if r["error"]),
        "latency_ms_p50": _pct(latencies, 0.50),
        "latency_ms_p95": _pct(latencies, 0.95),
        "config": {
            "provider": "claude" if use_claude else "ollama",
            "model": _active_model_name(),
            "max_calls": EVAL_MAX_CALLS,
            "registered_tools": registered,
            "host": socket.gethostname(),
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        },
    }
    return {"summary": summary, "per_case": per_case}


def _print_report(report: dict[str, Any]) -> None:
    s = report["summary"]
    print("\n=== Tool-use eval ===")
    print(f"provider={s['config']['provider']} model={s['config']['model']}")
    print(f"selection_accuracy   {s['selection_accuracy']:.3f}  ({s['n_needs_tool_runnable']} runnable needs-tool cases)")
    print(f"false_positive_rate  {s['false_positive_rate']:.3f}  ({s['n_no_tool']} no-tool cases)")
    print(f"answer_hit_rate      {s['answer_hit_rate']:.3f}  ({s['n_cases']} cases)")
    print(f"latency p50/p95      {s['latency_ms_p50']} / {s['latency_ms_p95']} ms")
    print(f"errors               {s['n_errors']}")
    print("\n--- per case ---")
    for r in report["per_case"]:
        if r["band"] == "needs_tool":
            mark = "ok " if r.get("correct_selection") else ("--" if not r.get("runnable") else "MISS")
            detail = f"want={r['expected_tools']} got={r['called_tools']}"
        else:
            mark = "FP  " if r["false_positive"] else "ok "
            detail = f"got={r['called_tools']}"
        err = f" ERR={r['error']}" if r["error"] else ""
        print(f"[{mark}] {r['latency_ms']:>6}ms  {r['prompt'][:52]:<52} {detail}{err}")


def main() -> None:
    report = asyncio.run(run_eval())
    _print_report(report)
    if os.getenv("ZEUS_WRITE_TOOL_EVAL_BASELINE", "0").strip().lower() in ("1", "true", "yes", "on"):
        BASELINE_PATH.write_text(json.dumps(report, indent=2))
        print(f"\nwrote baseline -> {BASELINE_PATH}")


@pytest.mark.skipif(
    os.getenv("ZEUS_RUN_TOOL_EVAL", "0").strip().lower() not in ("1", "true", "yes", "on"),
    reason="Set ZEUS_RUN_TOOL_EVAL=1 (requires the selected LLM reachable) to run the tool-use eval.",
)
def test_tool_use_eval() -> None:
    report = asyncio.run(run_eval())
    _print_report(report)

    # Optional regression gates — set these to the recorded baseline for the
    # provider under test before changing tool descriptions or the loop.
    min_selection = os.getenv("ZEUS_TOOL_EVAL_MIN_SELECTION")
    max_fp = os.getenv("ZEUS_TOOL_EVAL_MAX_FALSE_POSITIVE")
    s = report["summary"]
    if min_selection is not None:
        assert s["selection_accuracy"] >= float(min_selection), (
            f"selection_accuracy {s['selection_accuracy']} < {min_selection}"
        )
    if max_fp is not None:
        assert s["false_positive_rate"] <= float(max_fp), (
            f"false_positive_rate {s['false_positive_rate']} > {max_fp}"
        )


if __name__ == "__main__":
    main()
