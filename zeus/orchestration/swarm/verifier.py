# zeus/orchestration/swarm/verifier.py
"""Verify a node's work before it is committed.

A node carries a `check` - a shell command run in its worktree that exits 0 when
the work is acceptable (e.g. `pytest -q tests/test_x.py`, `ruff check .`). The
coordinator runs the verifier after the worker edits and before committing; a
failing check drives a retry (with the check output fed back to the worker), so
the swarm iterates to a passing state instead of trusting the worker's word.

Nodes without a `check` use NoopVerifier (pass). The check is LLM-authored, so
running it on the host is a code-execution hole: SandboxedCommandVerifier (P5)
runs it in an ephemeral, capped, network-off container with only the worktree
mounted. CommandVerifier (legacy, host exec) remains for opt-out / no-docker
fallback.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from typing import Protocol

from pydantic import BaseModel

from zeus.orchestration.swarm import config
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


class FailClosedVerifier:
    """Fail any node that has a check; used when sandboxing is required but the
    sandbox can't run and host fallback is disabled. A node with no check passes."""

    async def verify(self, node: TaskNode, workspace: str) -> VerifyResult:
        if not node.check.strip():
            return VerifyResult(passed=True, output="(no check)")
        return VerifyResult(
            passed=False,
            output="verify sandbox required but unavailable; refusing to run the check on the host",
        )


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


def docker_available() -> bool:
    return shutil.which("docker") is not None


def build_verify_docker_command(
    check: str,
    *,
    workspace: str,
    image: str,
    network: str,
    limits: dict[str, str],
    shell: str = "bash",
    run_as_host_user: bool = True,
) -> list[str]:
    """Wrap an LLM-authored `check` in an ephemeral, capped, network-off container.

    The worktree is the only host path exposed (bind-mounted at /work); the
    container drops all capabilities and cannot gain new privileges. HOME is a
    tmpfs so tools with a cache (pytest, ruff) can write outside the worktree.
    """
    cmd = [
        "docker", "run", "--rm", "--init",
        "--network", network,
        "-v", f"{workspace}:/work",
        "-w", "/work",
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",
        "--memory", limits["memory"],
        "--cpus", limits["cpus"],
        "--pids-limit", limits["pids"],
        "--tmpfs", "/home/agent:rw,mode=1777",
        "-e", "HOME=/home/agent",
    ]
    if run_as_host_user:
        cmd += ["--user", f"{os.getuid()}:{os.getgid()}"]
    cmd += [image, shell, "-c", check]
    return cmd


class SandboxedCommandVerifier:
    """Run `node.check` in a container (P5), not on the host.

    The check is authored by the (LLM) planner, so executing it on the host is a
    code-execution hole - it runs as the zeus-core user with full host access.
    This runs it isolated: capped, no new privileges, no network by default, with
    only the node's worktree mounted. The image must carry the repo's test
    toolchain + deps (see docker/verify/Dockerfile).
    """

    def __init__(self, *, timeout_s: float = 600, shell: str = "bash") -> None:
        self._timeout_s = timeout_s
        self._shell = shell

    async def verify(self, node: TaskNode, workspace: str) -> VerifyResult:
        if not node.check.strip():
            return VerifyResult(passed=True, output="(no check)")
        if not docker_available():
            return VerifyResult(passed=False, output="verify sandbox: `docker` not found on PATH")
        cmd = build_verify_docker_command(
            node.check,
            workspace=workspace,
            image=config.verify_image(),
            network=config.verify_network(),
            limits=config.verify_limits(),
            shell=self._shell,
        )
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=self._timeout_s)
        except asyncio.TimeoutError:
            return VerifyResult(passed=False, output=f"check timed out after {self._timeout_s}s")
        except OSError as exc:
            return VerifyResult(passed=False, output=f"verify sandbox could not run: {exc}")
        text = out.decode("utf-8", "replace")
        return VerifyResult(passed=proc.returncode == 0, output=text[-2000:])
