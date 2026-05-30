# zeus/core/tools/action_run.py — Olympian action runner (chat-path)
#
# Two specs registered from this file: olympian_action_list (read) and
# olympian_action_run (write). Both wrap the /actions/* endpoints. The list
# tool is intentionally separate so the LLM can discover available actions
# before invoking one — same pattern as ls + exec.
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.action_run")


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


_LIST_SPEC = ToolSpec(
    name="olympian_action_list",
    description=(
        "List the operator-curated scripts in ZEUS_ACTIONS_DIR (default "
        "~/.zeus/actions/). Returns name, mtime, and a `# desc:` line if "
        "the script declares one. Call this before olympian_action_run "
        "when you don't already know what's available, or when the user "
        "asks 'what can you do?' / 'what scripts are wired up?'."
    ),
    parameters={
        "type": "object",
        "properties": {},
    },
    aegis_policy="tool_arguments",
    timeout_seconds=5.0,
    cacheable=False,
)


_RUN_SPEC = ToolSpec(
    name="olympian_action_run",
    description=(
        "Execute one named script from the operator-curated actions "
        "directory. The directory contents are the allowlist — you can "
        "only call scripts that already exist there. Args are positional "
        "and not shell-interpreted. Output is capped at 64 KB per stream. "
        "Use only when the user explicitly asks to run a known action "
        "(e.g. 'restart zeus', 'run the backup'); never invent action "
        "names. If unsure what exists, call olympian_action_list first."
    ),
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Action name (script basename, no .sh suffix).",
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Positional args (each <=256 chars, max 16).",
            },
        },
        "required": ["name"],
    },
    aegis_policy="file_access",
    timeout_seconds=120.0,
    cacheable=False,
)


async def _list_handler(args: dict[str, Any]) -> ToolResult:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{_core_url()}/actions/list")
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_LIST_SPEC.name,
            content=f"olympian_action_list failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code >= 400:
        try:
            detail = (r.json() or {}).get("detail", r.text)
        except ValueError:
            detail = r.text
        return ToolResult(
            call_id="",
            name=_LIST_SPEC.name,
            content=f"olympian_action_list HTTP {r.status_code}: {str(detail)[:300]}",
            is_error=True,
        )
    data = r.json() or {}
    actions = data.get("actions") or []
    if not actions:
        return ToolResult(
            call_id="",
            name=_LIST_SPEC.name,
            content=f"No actions in {data.get('directory')}.",
        )
    lines = []
    for a in actions:
        desc = a.get("description") or "(no description)"
        flag = "" if a.get("executable") else "  [NOT EXECUTABLE]"
        lines.append(f"- {a.get('name')}: {desc}{flag}")
    return ToolResult(
        call_id="",
        name=_LIST_SPEC.name,
        content="\n".join(lines),
    )


async def _run_handler(args: dict[str, Any]) -> ToolResult:
    name = str(args.get("name") or "").strip()
    if not name:
        return ToolResult(
            call_id="",
            name=_RUN_SPEC.name,
            content="olympian_action_run requires non-empty 'name'.",
            is_error=True,
        )
    raw_args = args.get("args") or []
    if not isinstance(raw_args, list):
        return ToolResult(
            call_id="",
            name=_RUN_SPEC.name,
            content="olympian_action_run: 'args' must be a list of strings.",
            is_error=True,
        )
    payload = {"name": name, "args": [str(a) for a in raw_args]}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{_core_url()}/actions/run", json=payload)
    except httpx.HTTPError as exc:
        return ToolResult(
            call_id="",
            name=_RUN_SPEC.name,
            content=f"olympian_action_run failed to reach Zeus core: {exc}",
            is_error=True,
        )
    if r.status_code >= 400:
        try:
            detail = (r.json() or {}).get("detail", r.text)
        except ValueError:
            detail = r.text
        return ToolResult(
            call_id="",
            name=_RUN_SPEC.name,
            content=f"olympian_action_run HTTP {r.status_code}: {str(detail)[:300]}",
            is_error=True,
        )
    data = r.json() or {}
    exit_code = data.get("exit_code")
    duration = data.get("duration_ms")
    stdout = (data.get("stdout") or "").rstrip()
    stderr = (data.get("stderr") or "").rstrip()
    body_parts = [f"exit={exit_code} duration={duration}ms"]
    if stdout:
        body_parts.append(f"stdout:\n{stdout}")
    if stderr:
        body_parts.append(f"stderr:\n{stderr}")
    body = "\n\n".join(body_parts)
    is_error = isinstance(exit_code, int) and exit_code != 0
    return ToolResult(
        call_id="",
        name=_RUN_SPEC.name,
        content=body,
        is_error=is_error,
    )


def register() -> None:
    """Register both olympian_action_list and olympian_action_run.

    Server-side gates (ZEUS_ACTIONS_ENABLED, ZEUS_MCP_ALLOW_WRITE) decide
    whether either call actually runs; the chat-path tool surface is always
    registered so the LLM can attempt them and surface a clean error.
    """
    registry.register(_LIST_SPEC, _list_handler)
    registry.register(_RUN_SPEC, _run_handler)
    logger.info("olympian_action_list + olympian_action_run registered")
