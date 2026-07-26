# zeus/orchestration/swarm/claude_worker.py
"""Argonaut: a headless Claude Code process that completes one node in a worktree.

Runs `claude -p <prompt> --output-format stream-json --verbose` with cwd set to
the node's git worktree. `--allowedTools`, `--permission-mode`, and `--max-turns`
are the safety surface. The final stream-json `result` event carries
`session_id` and `total_cost_usd`, which flow into WorkerResult -> the usage
ledger + kill-switch.

Set ANTHROPIC_API_KEY in the environment: it overrides subscription auth and
makes spend attributable per run (the plan calls for this regardless of how
subscription billing lands).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil

from zeus.orchestration.swarm.models import Run, TaskNode
from zeus.orchestration.swarm.worker import WorkerResult

logger = logging.getLogger("zeus.swarm.argonaut")

# Conservative default tool scope for a code node. A node's own `tool_scope`
# (from the planner) overrides this when set.
_DEFAULT_ALLOWED_TOOLS = ["Edit", "Write", "Read", "Grep", "Glob", "Bash"]


def claude_available() -> bool:
    return shutil.which("claude") is not None


def build_prompt(node: TaskNode, run: Run, feedback: str | None = None) -> str:
    lines = [
        f"You are completing one task in a larger project: {run.goal}",
        "",
        f"## Task: {node.title}",
    ]
    if node.acceptance:
        lines += ["", f"Acceptance criteria: {node.acceptance}"]
    if node.check:
        lines += ["", f"Your work will be verified by running: {node.check}"]
    if feedback:
        lines += ["", "## A previous attempt did not pass. Fix it:", feedback]
    lines += [
        "",
        "Work only within this repository worktree. Make the change, keep it focused,",
        "and do not touch unrelated files. When done, stop.",
    ]
    return "\n".join(lines)


def build_command(
    prompt: str,
    *,
    allowed_tools: list[str],
    permission_mode: str = "acceptEdits",
    max_turns: int = 30,
    model: str | None = None,
) -> list[str]:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--permission-mode", permission_mode,
        "--max-turns", str(max_turns),
    ]
    if allowed_tools:
        cmd += ["--allowedTools", ",".join(allowed_tools)]
    if model:
        cmd += ["--model", model]
    return cmd


def parse_stream_json(stdout: str) -> dict:
    """Pull the final `result` event out of the JSONL stream.

    Returns {is_error, result, session_id, total_cost_usd, num_turns}. Missing
    result event (crash/no output) -> is_error True.
    """
    final: dict | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(evt, dict) and evt.get("type") == "result":
            final = evt
    if final is None:
        return {"is_error": True, "result": "", "session_id": None,
                "total_cost_usd": 0.0, "num_turns": 0}
    return {
        "is_error": bool(final.get("is_error", False)) or final.get("subtype") != "success",
        "result": final.get("result", ""),
        "session_id": final.get("session_id"),
        "total_cost_usd": float(final.get("total_cost_usd", 0.0) or 0.0),
        "num_turns": final.get("num_turns", 0),
    }


class ClaudeCodeWorker:
    """Spawn `claude -p` in the node's worktree and report the result."""

    def __init__(self, *, permission_mode: str = "acceptEdits", max_turns: int = 30,
                 model: str | None = None, timeout_s: float = 1800) -> None:
        self._permission_mode = permission_mode
        self._max_turns = max_turns
        self._model = model
        self._timeout_s = timeout_s

    async def run(self, node: TaskNode, run: Run, workspace: str | None,
                  feedback: str | None = None) -> WorkerResult:
        if workspace is None:
            return WorkerResult(success=False, error="claude worker requires a worktree")
        if not claude_available():
            return WorkerResult(success=False, error="`claude` CLI not found on PATH")

        allowed = node.tool_scope or _DEFAULT_ALLOWED_TOOLS
        cmd = build_command(
            build_prompt(node, run, feedback),
            allowed_tools=allowed,
            permission_mode=self._permission_mode,
            max_turns=self._max_turns,
            model=node.model or self._model,  # per-node routing (C1)
        )
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=workspace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )
            out, err = await asyncio.wait_for(proc.communicate(), timeout=self._timeout_s)
        except asyncio.TimeoutError:
            return WorkerResult(success=False, error=f"argonaut timed out after {self._timeout_s}s")
        except OSError as exc:
            return WorkerResult(success=False, error=f"spawn failed: {exc}")

        parsed = parse_stream_json(out.decode("utf-8", "replace"))
        if parsed["is_error"]:
            detail = parsed["result"] or err.decode("utf-8", "replace")[:400] or "claude reported error"
            return WorkerResult(
                success=False, error=detail,
                cost_usd=parsed["total_cost_usd"], session_id=parsed["session_id"],
            )
        return WorkerResult(
            success=True, output=parsed["result"],
            cost_usd=parsed["total_cost_usd"], session_id=parsed["session_id"],
        )
