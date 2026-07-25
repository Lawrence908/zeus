# tests/test_swarm_sandbox.py — sandboxed argonaut command build + guards
import asyncio

from zeus.orchestration.swarm import sandbox
from zeus.orchestration.swarm.models import NodeStatus, Run, RunStatus, TaskNode
from zeus.orchestration.swarm.sandbox import SandboxedClaudeWorker, build_docker_command


def _node():
    return TaskNode(run_id="r", id="a", title="t", status=NodeStatus.RUNNING)


def _run():
    return Run(id="r", goal="g", repo="/repo", status=RunStatus.RUNNING)


def test_build_docker_command_shape():
    argv = ["claude", "-p", "do it", "--output-format", "stream-json"]
    cmd = build_docker_command(
        argv, workspace="/host/wt", image="argonaut:latest",
        network="bridge", limits={"memory": "2g", "cpus": "2", "pids": "512"},
    )
    assert cmd[:3] == ["docker", "run", "--rm"]
    assert "-v" in cmd and "/host/wt:/work" in cmd
    assert cmd[cmd.index("--network") + 1] == "bridge"
    assert "--security-opt" in cmd and "no-new-privileges" in cmd
    assert cmd[cmd.index("--memory") + 1] == "2g"
    assert cmd[cmd.index("--pids-limit") + 1] == "512"
    # key passed by name, not value
    ei = [i for i, x in enumerate(cmd) if x == "-e"]
    assert any(cmd[i + 1] == "ANTHROPIC_API_KEY" for i in ei)
    # image immediately precedes the claude argv, which is appended verbatim
    assert cmd[-len(argv):] == argv
    assert cmd[-len(argv) - 1] == "argonaut:latest"


def test_worker_requires_worktree():
    async def scenario():
        res = await SandboxedClaudeWorker().run(_node(), _run(), None)
        assert not res.success and "worktree" in (res.error or "")
    asyncio.run(scenario())


def test_worker_requires_api_key(monkeypatch):
    monkeypatch.setattr(sandbox, "docker_available", lambda: True)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    async def scenario():
        res = await SandboxedClaudeWorker().run(_node(), _run(), "/host/wt")
        assert not res.success and "ANTHROPIC_API_KEY" in (res.error or "")
    asyncio.run(scenario())


def test_worker_requires_docker(monkeypatch):
    monkeypatch.setattr(sandbox, "docker_available", lambda: False)

    async def scenario():
        res = await SandboxedClaudeWorker().run(_node(), _run(), "/host/wt")
        assert not res.success and "docker" in (res.error or "")
    asyncio.run(scenario())
