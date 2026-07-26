# zeus/orchestration/swarm/planner.py
"""Metis: turn a project goal into a task DAG (the plan you approve at Gate 1).

Metis is itself a read-only Claude Code invocation - `claude -p --permission-mode
plan` in the target repo - so it can explore the codebase before decomposing the
goal, and cannot edit anything. It emits a JSON object describing the DAG, which
we parse into TaskNodeSpecs. Parsing is defensive: LLMs wrap JSON in prose or
```json fences.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
from typing import Protocol

from zeus.orchestration.swarm.models import TaskNodeSpec

logger = logging.getLogger("zeus.swarm.metis")

_PLAN_INSTRUCTIONS = """\
You are Metis, the planner for an autonomous software swarm. Analyse this
repository, then decompose the goal below into the SMALLEST sensible DAG of
implementation tasks a coding agent can each complete independently.

Output ONLY a single JSON object, no prose, of the form:
{"nodes": [
  {"id": "kebab-id", "title": "imperative task", "deps": ["other-id"],
   "acceptance": "how to know it's done",
   "check": "shell command that exits 0 when this node is correct",
   "tool_scope": ["Read","Edit","Write","Bash"], "model": "haiku",
   "requires_approval": false, "max_attempts": 2}
]}

Rules:
- ids are unique, short, kebab-case; deps reference other ids only (acyclic).
- Keep it minimal: prefer 2-6 nodes. Order by dependency.
- `check` is a real command runnable in the repo (e.g. `pytest -q tests/x.py`,
  `python -c 'import m'`, `ruff check path`). Omit or "" only if truly unverifiable.
- `model`: "haiku" for trivial nodes (docs, config, a rename, a single small
  file); "sonnet" for real logic, multi-file changes, or anything subtle. Bias
  toward "haiku" to keep runs cheap.
- Set requires_approval:true for a node that deletes files, changes CI/deploy,
  or touches security/auth. Set max_attempts:2-3 for nodes with a `check`.
- tool_scope is the least privilege each node needs.

Goal: {goal}
"""


class Planner(Protocol):
    async def plan(self, goal: str, repo: str) -> list[TaskNodeSpec]: ...


def build_planner_prompt(goal: str) -> str:
    return _PLAN_INSTRUCTIONS.replace("{goal}", goal)


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of an LLM answer (raw, fenced, or prose-wrapped)."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    # Fall back to the outermost brace span.
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("no JSON object found in planner output")


def parse_plan(text: str) -> list[TaskNodeSpec]:
    obj = _extract_json(text)
    raw_nodes = obj.get("nodes") if isinstance(obj, dict) else obj
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValueError("planner produced no nodes")
    return [TaskNodeSpec(**n) for n in raw_nodes]


class StubPlanner:
    """Fixed two-node plan; for tests and no-LLM environments."""

    async def plan(self, goal: str, repo: str) -> list[TaskNodeSpec]:
        return [
            TaskNodeSpec(id="implement", title=f"Implement: {goal}", tool_scope=["Read", "Edit", "Write"]),
            TaskNodeSpec(id="verify", title="Add or run tests for the change", deps=["implement"],
                         tool_scope=["Read", "Bash"]),
        ]


class ClaudePlanner:
    """Metis via `claude -p --permission-mode plan` (read-only) in the repo."""

    def __init__(self, *, max_turns: int = 20, model: str | None = None, timeout_s: float = 600) -> None:
        self._max_turns = max_turns
        self._model = model
        self._timeout_s = timeout_s

    async def plan(self, goal: str, repo: str) -> list[TaskNodeSpec]:
        if shutil.which("claude") is None:
            raise RuntimeError("`claude` CLI not found on PATH")
        cmd = [
            "claude", "-p", build_planner_prompt(goal),
            "--output-format", "json",
            "--permission-mode", "plan",  # read-only: explore, don't edit
            "--allowedTools", "Read,Grep,Glob",
            "--max-turns", str(self._max_turns),
        ]
        if self._model:
            cmd += ["--model", self._model]
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=repo,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=self._timeout_s)
        try:
            envelope = json.loads(out.decode("utf-8", "replace"))
            result_text = envelope.get("result", "") if isinstance(envelope, dict) else ""
        except json.JSONDecodeError:
            result_text = out.decode("utf-8", "replace")
        if not result_text:
            raise RuntimeError(f"planner produced no output: {err.decode('utf-8','replace')[:300]}")
        return parse_plan(result_text)
