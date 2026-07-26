# tests/test_swarm_claude_worker.py — argonaut command build + stream-json parse
import asyncio
import json

from zeus.orchestration.swarm.claude_worker import (
    ClaudeCodeWorker,
    build_command,
    build_prompt,
    parse_stream_json,
)
from zeus.orchestration.swarm.models import NodeStatus, Run, RunStatus, TaskNode


def _node(**kw):
    base = dict(run_id="r", id="a", title="add a helper", status=NodeStatus.RUNNING)
    base.update(kw)
    return TaskNode(**base)


def _run():
    return Run(id="r", goal="ship the feature", repo="/repo", status=RunStatus.RUNNING)


def test_build_command_has_safety_surface():
    cmd = build_command("do it", allowed_tools=["Edit", "Bash"], permission_mode="acceptEdits", max_turns=12)
    assert cmd[:3] == ["claude", "-p", "do it"]
    assert "--output-format" in cmd and "stream-json" in cmd
    assert "--verbose" in cmd
    i = cmd.index("--allowedTools")
    assert cmd[i + 1] == "Edit,Bash"
    assert cmd[cmd.index("--permission-mode") + 1] == "acceptEdits"
    assert cmd[cmd.index("--max-turns") + 1] == "12"


def test_build_prompt_includes_task_and_acceptance():
    p = build_prompt(_node(acceptance="tests pass"), _run())
    assert "add a helper" in p
    assert "ship the feature" in p
    assert "tests pass" in p


def test_parse_success_result():
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "s1"}),
        json.dumps({"type": "assistant", "message": {"content": "..."}}),
        json.dumps({
            "type": "result", "subtype": "success", "is_error": False,
            "result": "created zeus/core/new.py", "session_id": "s1",
            "total_cost_usd": 0.0123, "num_turns": 4,
        }),
    ])
    r = parse_stream_json(stream)
    assert r["is_error"] is False
    assert r["session_id"] == "s1"
    assert r["total_cost_usd"] == 0.0123
    assert "new.py" in r["result"]


def test_parse_error_subtype():
    stream = json.dumps({
        "type": "result", "subtype": "error_max_turns", "is_error": True,
        "result": "", "session_id": "s2", "total_cost_usd": 0.5,
    })
    r = parse_stream_json(stream)
    assert r["is_error"] is True
    assert r["total_cost_usd"] == 0.5


def test_parse_no_result_event_is_error():
    r = parse_stream_json(json.dumps({"type": "system", "subtype": "init"}))
    assert r["is_error"] is True


def test_worker_without_workspace_fails():
    async def scenario():
        res = await ClaudeCodeWorker().run(_node(), _run(), None)
        assert not res.success and "worktree" in (res.error or "")
    asyncio.run(scenario())


def test_node_model_routes_to_claude_model_flag(monkeypatch):
    # C1: a node's model must reach the spawned `claude --model <m>` argv.
    import asyncio as _aio

    from zeus.orchestration.swarm import claude_worker as cw

    captured = {}

    class _FakeProc:
        async def communicate(self):
            return (json.dumps({"type": "result", "subtype": "success", "is_error": False,
                                "result": "ok", "session_id": "s", "total_cost_usd": 0.0}).encode(), b"")

    async def _fake_exec(*cmd, **kw):
        captured["cmd"] = list(cmd)
        return _FakeProc()

    monkeypatch.setattr(cw, "claude_available", lambda: True)
    monkeypatch.setattr(_aio, "create_subprocess_exec", _fake_exec)

    async def scenario():
        # worker default is "sonnet"; the node overrides to "haiku"
        res = await ClaudeCodeWorker(model="sonnet").run(_node(model="haiku"), _run(), "/tmp")
        assert res.success
        cmd = captured["cmd"]
        assert cmd[cmd.index("--model") + 1] == "haiku"

    asyncio.run(scenario())
