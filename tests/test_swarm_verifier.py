# tests/test_swarm_verifier.py — CommandVerifier / NoopVerifier / SandboxedCommandVerifier
import asyncio

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.models import NodeStatus, TaskNode
from zeus.orchestration.swarm.verifier import (
    CommandVerifier,
    FailClosedVerifier,
    NoopVerifier,
    SandboxedCommandVerifier,
    build_verify_docker_command,
)


def _node(check=""):
    return TaskNode(run_id="r", id="a", title="t", check=check, status=NodeStatus.RUNNING)


def test_passing_check(tmp_path):
    async def scenario():
        r = await CommandVerifier().verify(_node("true"), str(tmp_path))
        assert r.passed
    asyncio.run(scenario())


def test_failing_check_captures_output(tmp_path):
    async def scenario():
        r = await CommandVerifier().verify(_node("echo nope >&2; exit 1"), str(tmp_path))
        assert not r.passed
        assert "nope" in r.output
    asyncio.run(scenario())


def test_check_runs_in_workspace(tmp_path):
    (tmp_path / "marker").write_text("x")
    async def scenario():
        assert (await CommandVerifier().verify(_node("test -f marker"), str(tmp_path))).passed
        assert not (await CommandVerifier().verify(_node("test -f absent"), str(tmp_path))).passed
    asyncio.run(scenario())


def test_no_check_passes(tmp_path):
    async def scenario():
        assert (await CommandVerifier().verify(_node(""), str(tmp_path))).passed
        assert (await NoopVerifier().verify(_node("exit 1"), str(tmp_path))).passed
    asyncio.run(scenario())


# ---- P5: sandboxed verifier ----------------------------------------------


def test_verify_docker_command_is_isolated():
    cmd = build_verify_docker_command(
        "pytest -q", workspace="/ws", image="img:latest",
        network="none", limits={"memory": "2g", "cpus": "2", "pids": "512"},
    )
    s = " ".join(cmd)
    # ephemeral, capped, no new privileges, no network, worktree-only mount
    assert cmd[:3] == ["docker", "run", "--rm"]
    assert "--network none" in s
    assert "no-new-privileges" in s
    assert "--cap-drop ALL" in s
    assert "-v /ws:/work" in s and "-w /work" in s
    assert "--memory 2g" in s and "--pids-limit 512" in s
    # the check is the terminal argv, run under a shell in the image
    assert cmd[-4:] == ["img:latest", "bash", "-c", "pytest -q"]


def test_sandboxed_verifier_no_check_passes_without_docker(tmp_path):
    async def scenario():
        # No check -> passes even with no docker (never shells out).
        assert (await SandboxedCommandVerifier().verify(_node(""), str(tmp_path))).passed
    asyncio.run(scenario())


def test_sandboxed_verifier_fails_when_docker_missing(monkeypatch, tmp_path):
    from zeus.orchestration.swarm import verifier as v

    monkeypatch.setattr(v.shutil, "which", lambda _: None)  # docker absent

    async def scenario():
        r = await SandboxedCommandVerifier().verify(_node("true"), str(tmp_path))
        assert not r.passed and "docker" in r.output

    asyncio.run(scenario())


def test_sandboxed_verifier_builds_expected_command(monkeypatch, tmp_path):
    from zeus.orchestration.swarm import verifier as v

    captured = {}

    class _Proc:
        returncode = 0

        async def communicate(self):
            return (b"ok", b"")

    async def _fake_exec(*cmd, **kw):
        captured["cmd"] = cmd
        return _Proc()

    monkeypatch.setattr(v.shutil, "which", lambda _: "/usr/bin/docker")
    monkeypatch.setattr(v.asyncio, "create_subprocess_exec", _fake_exec)
    monkeypatch.setenv("ZEUS_SWARM_VERIFY_IMAGE", "zeus-swarm-verify:latest")
    monkeypatch.setenv("ZEUS_SWARM_VERIFY_NETWORK", "none")

    async def scenario():
        r = await SandboxedCommandVerifier().verify(_node("pytest -q"), str(tmp_path))
        assert r.passed
        argv = " ".join(captured["cmd"])
        assert argv.startswith("docker run --rm")
        assert config.verify_image() in argv
        assert "--network none" in argv
        assert captured["cmd"][-1] == "pytest -q"

    asyncio.run(scenario())


def test_fail_closed_verifier():
    async def scenario():
        assert (await FailClosedVerifier().verify(_node(""), "/ws")).passed  # no check
        r = await FailClosedVerifier().verify(_node("pytest"), "/ws")
        assert not r.passed and "host" in r.output

    asyncio.run(scenario())
