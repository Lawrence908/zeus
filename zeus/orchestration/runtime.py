# zeus/orchestration/runtime.py — Agent runtime engine
# Loads ruflo.yaml + all agent/*.yaml definitions, manages agent lifecycle
# (start / stop / status), and exposes swarm state to the orchestration bus.
# Also houses AgentStep / TaskRecord / StepResult models and the TaskRunner
# executor (LAB-144).

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")


# ------------------------------------------------------------------
# Pydantic models for task execution (LAB-331)
# ------------------------------------------------------------------


class AgentStep(BaseModel):
    """A single step in a task plan — calls a tool or endpoint via the bus."""
    name: str
    endpoint: str
    method: str = "POST"
    args: dict[str, Any] = Field(default_factory=dict)
    on_failure: Literal["skip", "retry", "abort"] = "abort"


class StepResult(BaseModel):
    step_name: str
    status: Literal["ok", "skipped", "failed"] = "ok"
    data: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float = 0.0


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class TaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_name: str
    description: str = ""
    steps: list[AgentStep] = Field(default_factory=list)
    results: list[StepResult] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    elapsed_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)


# ------------------------------------------------------------------
# Agent status / definition
# ------------------------------------------------------------------


class AgentStatus(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class AgentDefinition:
    name: str
    description: str
    model: str
    tools: list[str]
    context: list[str]
    safety_policy: str
    endpoints: list[dict]
    triggers: list[dict]
    config: dict
    auto_start: bool = False
    steps: list[AgentStep] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class AgentState:
    definition: AgentDefinition
    status: AgentStatus = AgentStatus.STOPPED
    error: str | None = None


class AgentRuntime:
    """
    Loads and manages the olympian agent swarm defined in ruflo.yaml.

    Usage:
        runtime = AgentRuntime(config_path)
        runtime.load()          # parse configs
        await runtime.start_all_auto()  # bring up auto_start agents
    """

    def __init__(self, config_path: str | Path) -> None:
        self._config_path = Path(config_path)
        self._agents: dict[str, AgentState] = {}
        self._ruflo_config: dict = {}

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Parse ruflo.yaml and every agent YAML it references."""
        if not self._config_path.exists():
            raise FileNotFoundError(f"Ruflo config not found: {self._config_path}")

        with open(self._config_path) as f:
            loaded = yaml.safe_load(f)

        if not isinstance(loaded, dict):
            raise ValueError(f"Ruflo config {self._config_path} is empty or not a YAML mapping")
        self._ruflo_config = loaded

        for entry in self._ruflo_config.get("agents", []):
            name = entry["name"]
            definition_path = self._config_path.parent / entry["definition"]
            auto_start = entry.get("auto_start", False)

            try:
                defn = self._parse_agent_yaml(definition_path, auto_start)
                self._agents[name] = AgentState(definition=defn)
                logger.info("Loaded agent definition: %s (model=%s)", name, defn.model)
            except Exception as exc:
                logger.error("Failed to load agent %s: %s", name, exc)
                self._agents[name] = AgentState(
                    definition=AgentDefinition(
                        name=name,
                        description="",
                        model="",
                        tools=[],
                        context=[],
                        safety_policy="standard",
                        endpoints=[],
                        triggers=[],
                        config={},
                        auto_start=auto_start,
                    ),
                    status=AgentStatus.ERROR,
                    error=str(exc),
                )

    def _parse_agent_yaml(self, path: Path, auto_start: bool) -> AgentDefinition:
        with open(path) as f:
            raw = yaml.safe_load(f)

        if not isinstance(raw, dict) or "name" not in raw:
            raise ValueError(f"Agent YAML {path} is empty or missing required 'name' field")

        # Model block can be a plain string or {dev: ..., prod: ...}
        model_block = raw.get("model", {})
        if isinstance(model_block, dict):
            model = model_block.get(ZEUS_ENV, model_block.get("dev", ""))
        else:
            model = str(model_block)

        # Parse optional steps block into AgentStep objects
        steps: list[AgentStep] = []
        for s in raw.get("steps", []):
            steps.append(AgentStep(**s))

        return AgentDefinition(
            name=raw["name"],
            description=raw.get("description", ""),
            model=model,
            tools=raw.get("tools", []),
            context=raw.get("context", []),
            safety_policy=raw.get("safety", {}).get("policy", "standard"),
            endpoints=raw.get("endpoints", []),
            triggers=raw.get("triggers", []),
            config=raw.get("config", {}),
            auto_start=auto_start,
            steps=steps,
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start_agent(self, name: str) -> None:
        """Mark an agent as running. Hook point for future process management."""
        state = self._get_or_raise(name)
        if state.status == AgentStatus.ERROR:
            raise RuntimeError(f"Agent {name} is in error state: {state.error}")
        state.status = AgentStatus.RUNNING
        logger.info("Agent started: %s", name)

    async def stop_agent(self, name: str) -> None:
        """Mark an agent as stopped."""
        state = self._get_or_raise(name)
        state.status = AgentStatus.STOPPED
        logger.info("Agent stopped: %s", name)

    async def start_all_auto(self) -> None:
        """Start every agent configured with auto_start: true."""
        for name, state in self._agents.items():
            if state.definition.auto_start and state.status != AgentStatus.ERROR:
                await self.start_agent(name)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_agent(self, name: str) -> AgentState | None:
        return self._agents.get(name)

    @property
    def agents(self) -> dict[str, AgentState]:
        return dict(self._agents)

    def get_status(self) -> dict:
        """Return a serialisable snapshot of the whole swarm."""
        # Resolve the actually-active model at call time so runtime model
        # switches (POST /models/active) are reflected across AgentsPage / admin.
        from zeus.core.query import _active_model_name
        active_model = _active_model_name()
        return {
            "environment": ZEUS_ENV,
            "ruflo_version": self._ruflo_config.get("version", "unknown"),
            "active_model": active_model,
            "agents": {
                name: {
                    "status": state.status,
                    "description": state.definition.description,
                    "model": active_model,
                    "models": self._get_model_map(state.definition.raw),
                    "auto_start": state.definition.auto_start,
                    "tools": state.definition.tools,
                    "safety_policy": state.definition.safety_policy,
                    "error": state.error,
                }
                for name, state in self._agents.items()
            },
        }

    @staticmethod
    def _get_model_map(raw: dict) -> dict[str, str]:
        """Extract {dev: ..., prod: ...} model map from raw agent YAML."""
        model_block = raw.get("model", {})
        if isinstance(model_block, dict):
            return {k: str(v) for k, v in model_block.items()}
        return {"dev": str(model_block), "prod": str(model_block)}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_or_raise(self, name: str) -> AgentState:
        state = self._agents.get(name)
        if state is None:
            raise KeyError(f"Unknown agent: {name}")
        return state


# ------------------------------------------------------------------
# TaskRunner — sequential step executor (LAB-332)
# ------------------------------------------------------------------

# Retry backoff schedule (seconds) for on_failure="retry"
_RETRY_DELAYS = [0.5, 1.0, 2.0]
_MAX_RETRIES = 3


class TaskRunner:
    """
    Executes a list of AgentStep objects sequentially, routing each through
    the orchestration bus.  Collects StepResult per step and produces a
    TaskRecord stored in a ring buffer on app.state.task_records.

    Usage:
        runner = TaskRunner(bus_call_fn, task_records_buffer)
        record = await runner.run(agent_name, steps, description)
    """

    def __init__(
        self,
        bus_call_fn: Any,
        task_records: deque[TaskRecord],
    ) -> None:
        self._bus_call = bus_call_fn
        self._task_records = task_records

    async def run(
        self,
        agent_name: str,
        steps: list[AgentStep],
        description: str = "",
    ) -> TaskRecord:
        record = TaskRecord(
            agent_name=agent_name,
            description=description,
            steps=steps,
        )
        self._task_records.append(record)
        record.status = TaskStatus.RUNNING
        t0 = time.monotonic()

        for step in steps:
            result = await self._execute_step(agent_name, step)
            record.results.append(result)

            if result.status == "failed":
                # abort and retry-exhausted both stop the task
                record.status = TaskStatus.FAILED
                record.elapsed_ms = (time.monotonic() - t0) * 1000
                logger.warning(
                    "Task %s failed at step %r (on_failure=%s): %s",
                    record.id, step.name, step.on_failure, result.error,
                )
                return record

        record.status = TaskStatus.DONE
        record.elapsed_ms = (time.monotonic() - t0) * 1000
        logger.info("Task %s completed in %.0fms", record.id, record.elapsed_ms)
        return record

    async def _execute_step(
        self, agent_name: str, step: AgentStep
    ) -> StepResult:
        """Execute a single step, handling retry/skip/abort semantics."""
        attempts = 1 if step.on_failure != "retry" else _MAX_RETRIES
        last_error: str | None = None

        for attempt in range(attempts):
            t0 = time.monotonic()
            try:
                resp = await self._bus_call(
                    target_agent=agent_name,
                    endpoint=step.endpoint,
                    method=step.method,
                    payload=step.args,
                )
                duration = (time.monotonic() - t0) * 1000

                if resp.status == "error":
                    last_error = resp.error or "bus_call returned error"
                    if step.on_failure == "retry" and attempt < _MAX_RETRIES - 1:
                        delay = _RETRY_DELAYS[min(attempt, len(_RETRY_DELAYS) - 1)]
                        logger.info(
                            "Step %r failed (attempt %d/%d), retrying in %.1fs: %s",
                            step.name, attempt + 1, _MAX_RETRIES, delay, last_error,
                        )
                        await asyncio.sleep(delay)
                        continue
                else:
                    return StepResult(
                        step_name=step.name,
                        status="ok",
                        data=resp.data,
                        duration_ms=duration,
                    )
            except Exception as exc:
                duration = (time.monotonic() - t0) * 1000
                last_error = str(exc)
                if step.on_failure == "retry" and attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_DELAYS[min(attempt, len(_RETRY_DELAYS) - 1)]
                    logger.info(
                        "Step %r exception (attempt %d/%d), retrying in %.1fs: %s",
                        step.name, attempt + 1, _MAX_RETRIES, delay, last_error,
                    )
                    await asyncio.sleep(delay)
                    continue

        # All attempts exhausted or non-retry failure
        if step.on_failure == "skip":
            logger.warning("Step %r failed, skipping: %s", step.name, last_error)
            return StepResult(
                step_name=step.name,
                status="skipped",
                error=last_error,
                duration_ms=(time.monotonic() - t0) * 1000,
            )

        return StepResult(
            step_name=step.name,
            status="failed",
            error=last_error,
            duration_ms=(time.monotonic() - t0) * 1000,
        )
