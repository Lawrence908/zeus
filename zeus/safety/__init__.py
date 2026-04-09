# zeus/safety/__init__.py — Aegis (LAB-119): in-process policy engine + bus hooks
from zeus.safety.policy_engine import (
    AegisPolicyEngine,
    SafetyOutcome,
    aegis_enabled,
    active_policy_name,
    evaluate_text,
)
from zeus.safety.integration import register_aegis_bus_post_hook

__all__ = [
    "AegisPolicyEngine",
    "SafetyOutcome",
    "aegis_enabled",
    "active_policy_name",
    "evaluate_text",
    "register_aegis_bus_post_hook",
]
