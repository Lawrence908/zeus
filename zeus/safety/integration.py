# zeus/safety/integration.py — Orchestration bus post-hook for Aegis
from __future__ import annotations

import json
import logging
from typing import Any

from zeus.orchestration.hooks import HookRegistry
from zeus.safety.policy_engine import aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.aegis")


def _response_to_scanable(data: Any) -> str:
    if isinstance(data, str):
        return data
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(data)


async def aegis_bus_post_hook(context: dict[str, Any]) -> dict[str, Any]:
    if not aegis_enabled():
        return context
    policy = str(context.get("safety_policy") or "standard")
    data = context.get("response_data")
    text = _response_to_scanable(data)
    outcome = evaluate_text(text, policy_name=policy)
    if outcome.status != "rejected":
        return context
    logger.warning(
        "Aegis blocked bus response target=%s endpoint=%s policy=%s",
        context.get("target_agent"),
        context.get("endpoint"),
        policy,
    )
    context["response_data"] = {
        "error": outcome.message or "Output blocked by Aegis policy.",
        "aegis_rejected": True,
        "aegis_policy": policy,
    }
    return context


def register_aegis_bus_post_hook(registry: HookRegistry) -> None:
    registry.register_post("aegis_output_filter", aegis_bus_post_hook)
