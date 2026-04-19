# tests/test_orchestration.py — Orchestration runtime, bus, and hooks tests (LAB-334)
import asyncio
import time
from collections import deque
from unittest.mock import AsyncMock

import pytest

from zeus.orchestration.hooks import (
    BusMetrics,
    HookRegistry,
    _retry_backoff_post_hook,
    _validate_pre_context,
    build_default_registry,
)
from zeus.orchestration.runtime import (
    AgentStep,
    StepResult,
    TaskRecord,
    TaskRunner,
    TaskStatus,
)


# ------------------------------------------------------------------
# Model tests (LAB-331)
# ------------------------------------------------------------------


class TestAgentStep:
    def test_defaults(self):
        step = AgentStep(name="s1", endpoint="/test")
        assert step.method == "POST"
        assert step.args == {}
        assert step.on_failure == "abort"

    def test_custom_values(self):
        step = AgentStep(
            name="query", endpoint="/context/query",
            method="GET", args={"q": "hi"}, on_failure="retry",
        )
        assert step.on_failure == "retry"
        assert step.args == {"q": "hi"}


class TestStepResult:
    def test_ok_result(self):
        r = StepResult(step_name="s1", status="ok", data={"key": "val"}, duration_ms=42.0)
        assert r.status == "ok"
        assert r.error is None

    def test_failed_result(self):
        r = StepResult(step_name="s1", status="failed", error="boom")
        assert r.error == "boom"


class TestTaskRecord:
    def test_auto_id(self):
        r = TaskRecord(agent_name="oracle")
        assert len(r.id) == 12
        assert r.status == TaskStatus.PENDING

    def test_fields(self):
        step = AgentStep(name="s1", endpoint="/x")
        r = TaskRecord(agent_name="iris", steps=[step], description="test")
        assert r.agent_name == "iris"
        assert len(r.steps) == 1


# ------------------------------------------------------------------
# TaskRunner tests (LAB-332)
# ------------------------------------------------------------------


def _make_bus_ok(**data):
    """Return a mock bus_call that always succeeds."""
    from zeus.orchestration.bus import BusCallResponse

    async def _call(**kw):
        return BusCallResponse(
            agent=kw.get("target_agent", "test"),
            endpoint=kw.get("endpoint", "/"),
            status="ok",
            data=data or {"result": "ok"},
        )
    return _call


def _make_bus_fail(error_msg="fail"):
    from zeus.orchestration.bus import BusCallResponse

    async def _call(**kw):
        return BusCallResponse(
            agent=kw.get("target_agent", "test"),
            endpoint=kw.get("endpoint", "/"),
            status="error",
            error=error_msg,
        )
    return _call


class TestTaskRunner:
    def test_run_single_step_ok(self):
        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_make_bus_ok(), task_records=records)
        steps = [AgentStep(name="s1", endpoint="/test")]

        record = asyncio.run(runner.run("oracle", steps, "test task"))
        assert record.status == TaskStatus.DONE
        assert len(record.results) == 1
        assert record.results[0].status == "ok"
        assert record.elapsed_ms > 0

    def test_run_multi_step_ok(self):
        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_make_bus_ok(), task_records=records)
        steps = [
            AgentStep(name="s1", endpoint="/a"),
            AgentStep(name="s2", endpoint="/b"),
            AgentStep(name="s3", endpoint="/c"),
        ]
        record = asyncio.run(runner.run("oracle", steps))
        assert record.status == TaskStatus.DONE
        assert len(record.results) == 3

    def test_abort_on_failure(self):
        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_make_bus_fail("broken"), task_records=records)
        steps = [
            AgentStep(name="s1", endpoint="/a", on_failure="abort"),
            AgentStep(name="s2", endpoint="/b"),
        ]
        record = asyncio.run(runner.run("oracle", steps))
        assert record.status == TaskStatus.FAILED
        assert len(record.results) == 1
        assert record.results[0].status == "failed"

    def test_skip_on_failure(self):
        call_count = 0

        async def _bus(**kw):
            nonlocal call_count
            call_count += 1
            from zeus.orchestration.bus import BusCallResponse
            if call_count == 1:
                return BusCallResponse(agent="t", endpoint="/", status="error", error="e")
            return BusCallResponse(agent="t", endpoint="/", status="ok", data={})

        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_bus, task_records=records)
        steps = [
            AgentStep(name="s1", endpoint="/a", on_failure="skip"),
            AgentStep(name="s2", endpoint="/b"),
        ]
        record = asyncio.run(runner.run("oracle", steps))
        assert record.status == TaskStatus.DONE
        assert record.results[0].status == "skipped"
        assert record.results[1].status == "ok"

    def test_retry_on_failure(self):
        call_count = 0

        async def _bus(**kw):
            nonlocal call_count
            call_count += 1
            from zeus.orchestration.bus import BusCallResponse
            if call_count < 3:
                return BusCallResponse(agent="t", endpoint="/", status="error", error="transient")
            return BusCallResponse(agent="t", endpoint="/", status="ok", data={"recovered": True})

        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_bus, task_records=records)
        steps = [AgentStep(name="s1", endpoint="/a", on_failure="retry")]
        record = asyncio.run(runner.run("oracle", steps))
        assert record.status == TaskStatus.DONE
        assert record.results[0].status == "ok"
        assert call_count == 3

    def test_retry_exhausted(self):
        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_make_bus_fail("persistent"), task_records=records)
        steps = [AgentStep(name="s1", endpoint="/a", on_failure="retry")]
        record = asyncio.run(runner.run("oracle", steps))
        assert record.status == TaskStatus.FAILED
        assert record.results[0].status == "failed"
        assert "persistent" in record.results[0].error

    def test_ring_buffer_limit(self):
        records: deque[TaskRecord] = deque(maxlen=5)
        runner = TaskRunner(bus_call_fn=_make_bus_ok(), task_records=records)
        for i in range(10):
            asyncio.run(runner.run("oracle", [AgentStep(name=f"s{i}", endpoint="/x")]))
        assert len(records) == 5

    def test_exception_in_bus_call(self):
        async def _bus(**kw):
            raise ConnectionError("network down")

        records: deque[TaskRecord] = deque(maxlen=100)
        runner = TaskRunner(bus_call_fn=_bus, task_records=records)
        steps = [AgentStep(name="s1", endpoint="/a", on_failure="abort")]
        record = asyncio.run(runner.run("oracle", steps))
        assert record.status == TaskStatus.FAILED
        assert "network down" in record.results[0].error


# ------------------------------------------------------------------
# Hook tests (LAB-338, LAB-339, LAB-340)
# ------------------------------------------------------------------


class TestRetryBackoffHook:
    def test_flags_502(self):
        ctx = {"response_status": 502, "target_agent": "x", "endpoint": "/y"}
        result = asyncio.run(_retry_backoff_post_hook(ctx))
        assert result["should_retry"] is True

    def test_flags_503(self):
        ctx = {"response_status": 503, "target_agent": "x", "endpoint": "/y"}
        result = asyncio.run(_retry_backoff_post_hook(ctx))
        assert result["should_retry"] is True

    def test_no_flag_on_200(self):
        ctx = {"response_status": 200}
        result = asyncio.run(_retry_backoff_post_hook(ctx))
        assert "should_retry" not in result

    def test_no_flag_on_400(self):
        ctx = {"response_status": 400}
        result = asyncio.run(_retry_backoff_post_hook(ctx))
        assert "should_retry" not in result


class TestBusMetrics:
    def test_record_and_snapshot(self):
        m = BusMetrics()
        m.record("oracle", latency_ms=10.0)
        m.record("oracle", error=True, latency_ms=5.0)
        m.record("iris", latency_ms=20.0)
        snap = m.snapshot()
        assert snap["oracle"]["calls"] == 2
        assert snap["oracle"]["errors"] == 1
        assert snap["oracle"]["latency_total_ms"] == 15.0
        assert snap["iris"]["calls"] == 1


class TestPreHookValidator:
    def test_valid_context_passes(self):
        ctx = {
            "source": "bus", "target_agent": "x", "endpoint": "/y",
            "method": "POST", "payload": {}, "correlation_id": "abc",
        }
        result = asyncio.run(_validate_pre_context(ctx))
        assert result is ctx

    def test_missing_keys_raises_in_dev(self, monkeypatch):
        import zeus.orchestration.hooks as hooks_mod
        monkeypatch.setattr(hooks_mod, "ZEUS_ENV", "dev")
        ctx = {"source": "bus"}
        with pytest.raises(ValueError, match="missing required keys"):
            asyncio.run(_validate_pre_context(ctx))

    def test_missing_keys_warns_in_prod(self, monkeypatch):
        import zeus.orchestration.hooks as hooks_mod
        monkeypatch.setattr(hooks_mod, "ZEUS_ENV", "prod")
        ctx = {"source": "bus"}
        # Should not raise, just warn
        result = asyncio.run(_validate_pre_context(ctx))
        assert result is ctx


class TestHookRegistry:
    def test_build_default_has_hooks(self):
        registry = build_default_registry()
        assert len(registry._pre) >= 2  # validate_context + log
        assert len(registry._post) >= 3  # log + retry + metrics

    def test_pre_and_post_run(self):
        registry = HookRegistry()
        calls = []

        async def pre(ctx):
            calls.append("pre")
            return ctx

        async def post(ctx):
            calls.append("post")
            return ctx

        registry.register_pre("test", pre)
        registry.register_post("test", post)

        ctx = {"source": "t", "target_agent": "a", "endpoint": "/x",
               "method": "POST", "payload": {}, "correlation_id": "c"}
        asyncio.run(registry.run_pre(ctx))
        asyncio.run(registry.run_post(ctx))
        assert calls == ["pre", "post"]


# ------------------------------------------------------------------
# Bus model tests (LAB-335, LAB-336, LAB-337)
# ------------------------------------------------------------------


class TestBusModels:
    def test_correlation_id_on_request(self):
        from zeus.orchestration.bus import BusCallRequest
        req = BusCallRequest(target_agent="oracle", endpoint="/x", correlation_id="abc123")
        assert req.correlation_id == "abc123"

    def test_correlation_id_default_none(self):
        from zeus.orchestration.bus import BusCallRequest
        req = BusCallRequest(target_agent="oracle", endpoint="/x")
        assert req.correlation_id is None

    def test_idempotent_default_false(self):
        from zeus.orchestration.bus import BusCallRequest
        req = BusCallRequest(target_agent="oracle", endpoint="/x")
        assert req.idempotent is False

    def test_response_has_correlation_id(self):
        from zeus.orchestration.bus import BusCallResponse
        resp = BusCallResponse(
            agent="oracle", endpoint="/x", status="ok",
            correlation_id="xyz",
        )
        assert resp.correlation_id == "xyz"


# ------------------------------------------------------------------
# Agent YAML step parsing
# ------------------------------------------------------------------


class TestAgentYAMLSteps:
    def test_parse_steps_from_yaml(self, tmp_path):
        from zeus.orchestration.runtime import AgentRuntime
        # Write a minimal ruflo.yaml + agent yaml with steps
        agent_yaml = tmp_path / "agents" / "test_agent.yaml"
        agent_yaml.parent.mkdir()
        agent_yaml.write_text("""
name: test_agent
description: test
model: test-model
tools: []
safety:
  policy: standard
endpoints: []
steps:
  - name: step_one
    endpoint: /test/query
    method: POST
    args:
      query: hello
    on_failure: retry
  - name: step_two
    endpoint: /test/profile
    method: GET
""")
        ruflo_yaml = tmp_path / "ruflo.yaml"
        ruflo_yaml.write_text(f"""
version: "3.5"
agents:
  - name: test_agent
    definition: agents/test_agent.yaml
    auto_start: false
""")
        rt = AgentRuntime(ruflo_yaml)
        rt.load()
        agent = rt.get_agent("test_agent")
        assert agent is not None
        defn = agent.definition
        assert len(defn.steps) == 2
        assert defn.steps[0].name == "step_one"
        assert defn.steps[0].on_failure == "retry"
        assert defn.steps[0].args == {"query": "hello"}
        assert defn.steps[1].method == "GET"
        assert defn.steps[1].on_failure == "abort"  # default
