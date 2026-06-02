# zeus/core/tools/deep_research.py — Chat-path entry to the deep-research Kronos job.
#
# The job itself is heavy (2-30 minutes). Blocking the chat reply on it is
# unworkable, so this tool fires-and-forgets: it POSTs a one-off Kronos job
# with run_at ~5s in the future, returns the job id and expected output path
# to the chat LLM, and lets the scheduler tick + executor run the actual
# research in the background. Subsequent chat turns can check /jobs or read
# the file directly.
#
# Mirrors the inbox_append/action_run pattern of POSTing to the local API
# rather than reaching into the registry directly, so the same Aegis pre/post
# hooks and ZEUS_KRONOS_ALLOW_WRITE gate apply.
from __future__ import annotations

import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.deep_research")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


def _reports_dir() -> str:
    return os.getenv("ZEUS_DEEP_RESEARCH_DIR", "/home/chris/zeus/docs/research").rstrip("/")


_SPEC = ToolSpec(
    name="deep_research",
    description=(
        "Kick off a multi-agent deep-research run on a topic and return a "
        "job id immediately. The job decomposes the topic into sub-questions, "
        "fans out parallel web searches, synthesizes a cited report, and "
        "writes it to zeus/docs/research/<date>-<slug>.md. Use this for "
        "overnight research, NotebookLM/ChatGPT-deep-research replacements, "
        "or any topic that needs a referenced writeup rather than an inline "
        "answer. Runs take 2-30 minutes depending on depth, so this tool "
        "DOES NOT block the chat — it returns immediately. Tell the user to "
        "check /jobs for status or read the report file once it appears. "
        "Server requires ZEUS_KRONOS_ALLOW_WRITE=1."
    ),
    parameters={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": (
                    "What to research. Be specific; report quality scales "
                    "with topic clarity. A full sentence works better than "
                    "a single keyword."
                ),
            },
            "depth": {
                "type": "string",
                "enum": ["quick", "standard", "deep"],
                "description": (
                    "quick: 3 sub-questions, ~5 min, ~6 web queries. "
                    "standard: 5 sub-questions + optional gap pass, ~15 min, "
                    "~15 queries. deep: 8 sub-questions + mandatory gap "
                    "pass, 30+ min, ~30 queries. Default 'standard'."
                ),
            },
            "format": {
                "type": "string",
                "enum": ["markdown", "brief", "outline", "qa"],
                "description": (
                    "Report format. markdown (default) is full structured "
                    "report. brief is one-page exec summary. outline is "
                    "hierarchical bullets. qa is question-answer keyed to "
                    "sub-questions."
                ),
            },
        },
        "required": ["topic"],
    },
    aegis_policy="tool_arguments",
    timeout_seconds=15.0,
    cacheable=False,
)


_TIMEOUT_BY_DEPTH = {"quick": 600, "standard": 1800, "deep": 3600}


def _slug(topic: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return s[:max_len] or "untitled"


async def _handler(args: dict[str, Any]) -> ToolResult:
    topic = str(args.get("topic") or "").strip()
    if not topic:
        return ToolResult(
            call_id="", name=_SPEC.name,
            content="deep_research requires a non-empty 'topic'.",
            is_error=True,
        )

    depth = str(args.get("depth") or "standard").lower()
    if depth not in _TIMEOUT_BY_DEPTH:
        depth = "standard"

    fmt = str(args.get("format") or "markdown").lower()
    if fmt not in {"markdown", "brief", "outline", "qa"}:
        fmt = "markdown"

    today = datetime.now(timezone.utc).date().isoformat()
    short_id = uuid.uuid4().hex[:6]
    job_id = f"deep-research-{today}-{_slug(topic, 30)}-{short_id}"
    run_at = (datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat()
    timeout_seconds = _TIMEOUT_BY_DEPTH[depth]

    body = {
        "id": job_id,
        "name": f"Deep research: {topic[:100]}",
        "description": (
            f"One-off research run created via chat tool. "
            f"depth={depth}, format={fmt}."
        ),
        "category": "research",
        "schedule": {"run_at": run_at},
        "executor": "zeus.kronos.jobs.deep_research.run_deep_research",
        "params": {"topic": topic, "depth": depth, "format": fmt},
        "safety_policy": "standard",
        "timeout_seconds": timeout_seconds,
        "max_retries": 0,
        "tags": ["research", "chat-triggered", depth],
        "enabled": True,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{_core_url()}/kronos/jobs", json=body)
    except httpx.HTTPError as exc:
        logger.warning("deep_research: kronos POST failed: %s", exc)
        return ToolResult(
            call_id="", name=_SPEC.name,
            content=(
                f"Could not create research job: "
                f"{type(exc).__name__}: {exc}. Is zeus-core running and "
                f"reachable at {_core_url()}?"
            ),
            is_error=True,
        )

    if r.status_code in (401, 403):
        return ToolResult(
            call_id="", name=_SPEC.name,
            content=(
                "Research job not created: writes are disabled on /kronos/*. "
                "Set ZEUS_KRONOS_ALLOW_WRITE=1 server-side and restart "
                "zeus-core."
            ),
            is_error=True,
        )
    if r.status_code >= 400:
        return ToolResult(
            call_id="", name=_SPEC.name,
            content=(
                f"Kronos refused job creation ({r.status_code}): "
                f"{r.text[:300]}"
            ),
            is_error=True,
        )

    expected_path = f"{_reports_dir()}/{today}-{_slug(topic)}.md"
    return ToolResult(
        call_id="", name=_SPEC.name,
        content=(
            f"Research job started.\n"
            f"job_id: {job_id}\n"
            f"topic: {topic}\n"
            f"depth: {depth}, format: {fmt}\n"
            f"timeout: {timeout_seconds}s\n"
            f"expected output: {expected_path}\n\n"
            f"The job runs in the background — do not wait on it in this "
            f"reply. Tell the user the job has started and they can check "
            f"the /jobs page for live status, or open the report file once "
            f"the run completes (the file does not exist yet)."
        ),
    )


def register() -> None:
    registry.register(_SPEC, _handler)
    logger.info("deep_research tool registered")
