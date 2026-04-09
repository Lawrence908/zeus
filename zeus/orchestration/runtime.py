# zeus/orchestration/runtime.py — Agent runtime engine
# Loads ruflo.yaml + all agent/*.yaml definitions, manages agent lifecycle
# (start / stop / status), and exposes swarm state to the orchestration bus.

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")


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
        return {
            "environment": ZEUS_ENV,
            "ruflo_version": self._ruflo_config.get("version", "unknown"),
            "agents": {
                name: {
                    "status": state.status,
                    "description": state.definition.description,
                    "model": state.definition.model,
                    "auto_start": state.definition.auto_start,
                    "tools": state.definition.tools,
                    "safety_policy": state.definition.safety_policy,
                    "error": state.error,
                }
                for name, state in self._agents.items()
            },
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_or_raise(self, name: str) -> AgentState:
        state = self._agents.get(name)
        if state is None:
            raise KeyError(f"Unknown agent: {name}")
        return state
