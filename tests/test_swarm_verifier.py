# tests/test_swarm_verifier.py — CommandVerifier / NoopVerifier
import asyncio

from zeus.orchestration.swarm.models import NodeStatus, TaskNode
from zeus.orchestration.swarm.verifier import CommandVerifier, NoopVerifier


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
