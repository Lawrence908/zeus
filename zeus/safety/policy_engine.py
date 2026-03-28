# zeus/safety/policy_engine.py — YAML rule evaluation for Aegis (LAB-119)
#
# Full NVIDIA NemoClaw + OpenShell is installed on the host (installer + Docker
# sandboxes per https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html).
# Zeus applies this in-process policy layer on Core outputs regardless; optional
# NEMOCLAW_RUNTIME_URL is reserved for a future HTTP sidecar if NVIDIA exposes one.
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger("zeus.aegis")

_POLICIES_DIR = Path(__file__).resolve().parent / "policies"


@dataclass
class SafetyOutcome:
    status: str  # "ok" | "rejected"
    text: str
    flags: list[str] = field(default_factory=list)
    message: str | None = None


def aegis_enabled() -> bool:
    v = os.getenv("ZEUS_AEGIS_ENABLED", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def active_policy_name() -> str:
    return (
        os.getenv("ZEUS_AEGIS_POLICY", "").strip()
        or os.getenv("NEMOCLAW_POLICY", "").strip()
        or "standard"
    ).removesuffix(".yaml")


class AegisPolicyEngine:
    """Load a named policy from ``zeus/safety/policies/<name>.yaml`` and evaluate text."""

    def __init__(self, policy: str | None = None) -> None:
        self.policy_name = (policy or active_policy_name()).strip() or "standard"
        self.policy_name = self.policy_name.removesuffix(".yaml")
        self._doc = self._load(self.policy_name)
        raw_rules = self._doc.get("rules")
        self._rules: list[dict] = raw_rules if isinstance(raw_rules, list) else []

    def _load(self, name: str) -> dict:
        path = _POLICIES_DIR / f"{name}.yaml"
        if not path.is_file():
            logger.warning(
                "Aegis policy %r missing (%s); falling back to ingest (permissive)",
                name,
                path,
            )
            path = _POLICIES_DIR / "ingest.yaml"
            if not path.is_file():
                return {}
        with open(path, encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        return loaded if isinstance(loaded, dict) else {}

    def evaluate(self, text: str) -> SafetyOutcome:
        flags: list[str] = []
        for rule in self._rules:
            pattern = rule.get("pattern")
            if not pattern or not isinstance(pattern, str):
                continue
            try:
                rx = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            except re.error as exc:
                logger.error("Invalid regex in rule %r: %s", rule.get("name"), exc)
                continue
            if not rx.search(text):
                continue
            action = str(rule.get("action") or "flag").lower().replace("-", "_")
            rname = str(rule.get("name") or "unnamed")
            if action == "reject":
                msg = rule.get("message")
                msg_s = str(msg) if msg else "Output blocked by Aegis policy."
                logger.warning(
                    "Aegis reject policy=%s rule=%s",
                    self.policy_name,
                    rname,
                )
                return SafetyOutcome(
                    status="rejected",
                    text="",
                    flags=flags,
                    message=msg_s,
                )
            if action in ("flag", "flag_for_review"):
                flags.append(rname)
                logger.info("Aegis flag policy=%s rule=%s", self.policy_name, rname)
        return SafetyOutcome(status="ok", text=text, flags=flags)


def evaluate_text(text: str, policy_name: str | None = None) -> SafetyOutcome:
    if not aegis_enabled():
        return SafetyOutcome(status="ok", text=text, flags=[])
    engine = AegisPolicyEngine(policy=policy_name)
    return engine.evaluate(text)
