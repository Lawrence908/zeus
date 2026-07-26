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


# ---- egress policy (worker-sandbox lockdown) ------------------------------


def test_build_docker_command_injects_proxy_env():
    argv = ["claude", "-p", "x"]
    cmd = build_docker_command(
        argv, workspace="/wt", image="img", network="zeus-swarm-egress",
        limits={"memory": "2g", "cpus": "2", "pids": "512"},
        proxy="http://proxy:8888", no_proxy="localhost,127.0.0.1",
    )
    s = " ".join(cmd)
    assert "--network zeus-swarm-egress" in s
    assert "HTTPS_PROXY=http://proxy:8888" in s and "https_proxy=http://proxy:8888" in s
    assert "NO_PROXY=localhost,127.0.0.1" in s


def test_build_docker_command_no_proxy_by_default():
    cmd = build_docker_command(
        ["claude"], workspace="/wt", image="img", network="bridge",
        limits={"memory": "2g", "cpus": "2", "pids": "512"},
    )
    assert not any("PROXY" in x.upper() for x in cmd)


def test_egress_config_modes(monkeypatch):
    from zeus.orchestration.swarm import config

    monkeypatch.delenv("ZEUS_SWARM_SANDBOX_EGRESS", raising=False)
    assert config.sandbox_egress()["mode"] == "open"

    monkeypatch.setenv("ZEUS_SWARM_SANDBOX_EGRESS", "none")
    assert config.sandbox_egress()["network"] == "none"

    monkeypatch.setenv("ZEUS_SWARM_SANDBOX_EGRESS", "proxy")
    monkeypatch.setenv("ZEUS_SWARM_EGRESS_PROXY", "http://proxy:8888")
    monkeypatch.setenv("ZEUS_SWARM_SANDBOX_NETWORK", "zeus-swarm-egress")
    eg = config.sandbox_egress()
    assert eg["mode"] == "proxy" and eg["network"] == "zeus-swarm-egress"
    assert eg["proxy"] == "http://proxy:8888"


def test_worker_proxy_mode_requires_proxy_url(monkeypatch):
    monkeypatch.setattr(sandbox, "docker_available", lambda: True)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setenv("ZEUS_SWARM_SANDBOX_EGRESS", "proxy")
    monkeypatch.delenv("ZEUS_SWARM_EGRESS_PROXY", raising=False)

    async def scenario():
        res = await SandboxedClaudeWorker().run(_node(), _run(), "/host/wt")
        assert not res.success and "ZEUS_SWARM_EGRESS_PROXY" in (res.error or "")
    asyncio.run(scenario())
