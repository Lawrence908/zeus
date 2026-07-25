# tests/test_swarm_planner.py — Metis planner parsing + stub
import asyncio

import pytest

from zeus.orchestration.swarm.planner import (
    StubPlanner,
    build_planner_prompt,
    parse_plan,
)

_RAW = '{"nodes": [{"id": "a", "title": "do a"}, {"id": "b", "title": "do b", "deps": ["a"]}]}'


def test_parse_raw_json():
    specs = parse_plan(_RAW)
    assert [s.id for s in specs] == ["a", "b"]
    assert specs[1].deps == ["a"]


def test_parse_fenced_json():
    text = "Here is the plan:\n```json\n" + _RAW + "\n```\nDone."
    specs = parse_plan(text)
    assert [s.id for s in specs] == ["a", "b"]


def test_parse_prose_wrapped():
    text = "Sure! " + _RAW + " Let me know if you want changes."
    specs = parse_plan(text)
    assert len(specs) == 2


def test_parse_ignores_extra_fields():
    specs = parse_plan('{"nodes":[{"id":"a","title":"t","confidence":0.9,"notes":"x"}]}')
    assert specs[0].id == "a"


def test_parse_no_nodes_raises():
    with pytest.raises(ValueError):
        parse_plan('{"nodes": []}')
    with pytest.raises(ValueError):
        parse_plan("no json here")


def test_build_prompt_has_goal_and_schema():
    p = build_planner_prompt("add a health endpoint")
    assert "add a health endpoint" in p
    assert '"nodes"' in p and "requires_approval" in p


def test_stub_planner():
    async def scenario():
        specs = await StubPlanner().plan("ship X", "/repo")
        assert [s.id for s in specs] == ["implement", "verify"]
        assert specs[1].deps == ["implement"]
    asyncio.run(scenario())
