# tests/test_swarm_transcript_ci.py — P8b transcript surfacing + CI poll
import asyncio
import json
import os

from zeus.orchestration.swarm import ci
from zeus.orchestration.swarm.ci import CiCheck, _rollup, pr_ci_status
from zeus.orchestration.swarm.transcript import find_transcript, read_transcript


# ---- transcripts ----------------------------------------------------------


def _write_transcript(root, session_id, events):
    proj = os.path.join(root, "projects", "-home-chris-repo")
    os.makedirs(proj, exist_ok=True)
    path = os.path.join(proj, f"{session_id}.jsonl")
    with open(path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return path


def test_find_and_read_transcript(tmp_path, monkeypatch):
    monkeypatch.setenv("ZEUS_SWARM_TRANSCRIPT_DIR", str(tmp_path / "projects"))
    _write_transcript(str(tmp_path), "sess-1", [
        {"type": "user", "message": {"role": "user", "content": "build the thing"}},
        {"type": "assistant", "message": {"role": "assistant",
         "content": [{"type": "text", "text": "done"}, {"type": "tool_use", "name": "Edit"}]}},
        {"type": "result", "result": "completed successfully"},
    ])
    assert find_transcript("sess-1") is not None
    out = read_transcript("sess-1")
    assert out["exists"] is True
    texts = [e["text"] for e in out["events"]]
    assert "build the thing" in texts[0]
    assert "done" in texts[1] and "tool_use Edit" in texts[1]
    assert out["events"][-1]["type"] == "result"


def test_missing_transcript_is_benign(tmp_path, monkeypatch):
    monkeypatch.setenv("ZEUS_SWARM_TRANSCRIPT_DIR", str(tmp_path / "projects"))
    out = read_transcript("nope")
    assert out == {"exists": False, "events": []}
    assert read_transcript("")["exists"] is False


# ---- CI rollup ------------------------------------------------------------


def test_ci_rollup():
    assert _rollup([]) == "none"
    assert _rollup([CiCheck(name="a", state="success")]) == "passing"
    assert _rollup([CiCheck(name="a", state="success"), CiCheck(name="b", state="pending")]) == "pending"
    assert _rollup([CiCheck(name="a", state="success"), CiCheck(name="b", state="fail")]) == "failing"


def test_ci_no_pr():
    async def scenario():
        assert (await pr_ci_status(None)).status == "no_pr"
    asyncio.run(scenario())


def test_ci_parses_gh_output(monkeypatch):
    monkeypatch.setattr(ci.shutil, "which", lambda _: "/usr/bin/gh")

    class _Proc:
        returncode = 0

        async def communicate(self):
            payload = json.dumps([
                {"name": "build", "state": "success"},
                {"name": "test", "state": "pending"},
            ]).encode()
            return (payload, b"")

    async def _fake_exec(*cmd, **kw):
        assert "pr" in cmd and "checks" in cmd
        return _Proc()

    monkeypatch.setattr(ci.asyncio, "create_subprocess_exec", _fake_exec)

    async def scenario():
        st = await pr_ci_status("https://github.com/x/y/pull/1")
        assert st.status == "pending"
        assert {c.name for c in st.checks} == {"build", "test"}

    asyncio.run(scenario())


def test_ci_no_gh(monkeypatch):
    monkeypatch.setattr(ci.shutil, "which", lambda _: None)

    async def scenario():
        assert (await pr_ci_status("https://github.com/x/y/pull/1")).status == "no_gh"
    asyncio.run(scenario())
