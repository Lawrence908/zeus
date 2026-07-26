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

from pydantic import BaseModel

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.models import TaskNodeSpec

logger = logging.getLogger("zeus.swarm.metis")


class PlanResult(BaseModel):
    nodes: list[TaskNodeSpec]
    cost_usd: float = 0.0  # what Metis spent scoping (captured from the CLI result)
    session_id: str | None = None
    project_check: str = ""  # run-level check for the final gate (P7)

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
 ],
 "project_check": "one command that verifies the WHOLE change on the assembled branch (e.g. the full test suite / build); \"\" if none"}

Rules:
- ids are unique, short, kebab-case; deps reference other ids only (acyclic).
- Keep it minimal: prefer 2-6 nodes. Order by dependency.
- `check` is a real command runnable in the repo (e.g. `pytest -q tests/x.py`,
  `python -c 'import m'`, `ruff check path`). Omit or "" only if truly unverifiable.
- `model`: "local" for a node that just writes ONE small self-contained file
  from the task description alone (a doc, a config, a template) - it runs free on
  a local model with no code exploration, so only use it when no context is
  needed; "haiku" for trivial nodes that still need to read the repo (a rename, a
  small edit); "sonnet" for real logic, multi-file changes, or anything subtle.
  Bias toward "local" then "haiku" to keep runs cheap.
- Set requires_approval:true for a node that deletes files, changes CI/deploy,
  or touches security/auth. Set max_attempts:2-3 for nodes with a `check`.
- tool_scope is the least privilege each node needs.

Goal: {goal}
"""


class Planner(Protocol):
    async def plan(self, goal: str, repo: str) -> PlanResult: ...


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


def parse_project_check(text: str) -> str:
    """Pull the optional top-level `project_check` out of a plan (P7)."""
    try:
        obj = _extract_json(text)
    except (ValueError, json.JSONDecodeError):
        return ""
    return str(obj.get("project_check", "")).strip() if isinstance(obj, dict) else ""


class StubPlanner:
    """Fixed two-node plan; for tests and no-LLM environments."""

    async def plan(self, goal: str, repo: str) -> PlanResult:
        return PlanResult(nodes=[
            TaskNodeSpec(id="implement", title=f"Implement: {goal}", tool_scope=["Read", "Edit", "Write"]),
            TaskNodeSpec(id="verify", title="Add or run tests for the change", deps=["implement"],
                         tool_scope=["Read", "Bash"]),
        ])


class ClaudePlanner:
    """Metis via `claude -p --permission-mode plan` (read-only) in the repo.

    Model + turn budget are configurable (ZEUS_SWARM_PLANNER_MODEL/MAX_TURNS) so
    planning can be run on a cheaper model; the CLI result cost is captured.
    """

    def __init__(self, *, max_turns: int | None = None, model: str | None = None, timeout_s: float = 600) -> None:
        self._max_turns = max_turns
        self._model = model
        self._timeout_s = timeout_s

    async def plan(self, goal: str, repo: str) -> PlanResult:
        if shutil.which("claude") is None:
            raise RuntimeError("`claude` CLI not found on PATH")
        cmd = [
            "claude", "-p", build_planner_prompt(goal),
            "--output-format", "json",
            "--permission-mode", "plan",  # read-only: explore, don't edit
            "--allowedTools", "Read,Grep,Glob",
            "--max-turns", str(self._max_turns or config.planner_max_turns()),
            "--model", self._model or config.planner_model(),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=repo,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=self._timeout_s)
        cost, session = 0.0, None
        try:
            envelope = json.loads(out.decode("utf-8", "replace"))
            if isinstance(envelope, dict):
                result_text = envelope.get("result", "")
                cost = float(envelope.get("total_cost_usd", 0.0) or 0.0)
                session = envelope.get("session_id")
            else:
                result_text = ""
        except json.JSONDecodeError:
            result_text = out.decode("utf-8", "replace")
        if not result_text:
            raise RuntimeError(f"planner produced no output: {err.decode('utf-8','replace')[:300]}")
        return PlanResult(
            nodes=parse_plan(result_text), cost_usd=cost, session_id=session,
            project_check=parse_project_check(result_text),
        )
