# zeus/orchestration/swarm/verifier.py
"""Verify a node's work before it is committed.

A node carries a `check` - a shell command run in its worktree that exits 0 when
the work is acceptable (e.g. `pytest -q tests/test_x.py`, `ruff check .`). The
coordinator runs the verifier after the worker edits and before committing; a
failing check drives a retry (with the check output fed back to the worker), so
the swarm iterates to a passing state instead of trusting the worker's word.

Nodes without a `check` use NoopVerifier (pass). CommandVerifier runs the check
in the worktree with a timeout.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Protocol

from pydantic import BaseModel

from zeus.orchestration.swarm.models import TaskNode

logger = logging.getLogger("zeus.swarm.verifier")


class VerifyResult(BaseModel):
    passed: bool
    output: str = ""  # combined stdout/stderr tail, fed back to the worker on failure


class Verifier(Protocol):
    async def verify(self, node: TaskNode, workspace: str) -> VerifyResult: ...


class NoopVerifier:
    async def verify(self, node: TaskNode, workspace: str) -> VerifyResult:
        return VerifyResult(passed=True, output="(no check)")


class CommandVerifier:
    """Run `node.check` in the worktree; exit 0 -> passed. No check -> pass."""

    def __init__(self, *, timeout_s: float = 600, shell: str = "/bin/bash") -> None:
        self._timeout_s = timeout_s
        self._shell = shell

    async def verify(self, node: TaskNode, workspace: str) -> VerifyResult:
        if not node.check.strip():
            return VerifyResult(passed=True, output="(no check)")
        try:
            proc = await asyncio.create_subprocess_exec(
                self._shell, "-c", node.check,
                cwd=workspace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=self._timeout_s)
        except asyncio.TimeoutError:
            return VerifyResult(passed=False, output=f"check timed out after {self._timeout_s}s")
        except OSError as exc:
            return VerifyResult(passed=False, output=f"check could not run: {exc}")
        text = out.decode("utf-8", "replace")
        passed = proc.returncode == 0
        # Keep the tail; enough for the worker to act on, bounded for the store.
        tail = text[-2000:]
        return VerifyResult(passed=passed, output=tail)
