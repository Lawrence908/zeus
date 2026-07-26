# zeus/orchestration/swarm/estimate.py
"""Rough pre-flight cost estimate for a run, shown at the plan gate.

A heuristic, not a promise: per-node base cost by model tier, scaled by how much
work the node implies (tool scope, whether it shells out, retry budget). Its job
is to let you decide before paying and to compare cheap-vs-strong routing - live
`cost_usd` on the nodes is the real number.
"""

from __future__ import annotations

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.models import RunEstimate, TaskNode

# Base $/node by model tier (order-of-magnitude, tuned to observed smokes ~$0.1-0.3).
_CHEAP_BASE = 0.03
_STRONG_BASE = 0.18


def _is_cheap(model: str) -> bool:
    m = (model or config.model_default()).lower()
    return "haiku" in m or m == config.model_cheap().lower()


def estimate_node(node: TaskNode) -> float:
    base = _CHEAP_BASE if _is_cheap(node.model) else _STRONG_BASE
    # More tools / shelling out -> more turns -> more tokens.
    scope = node.tool_scope or ["Edit", "Write", "Read", "Bash"]
    factor = 1.0 + 0.15 * max(0, len(scope) - 2)
    if any(t.lower().startswith("bash") for t in scope):
        factor += 0.4
    # A verify+retry node may run more than once; assume ~half the extra attempts.
    if node.check.strip() and node.max_attempts > 1:
        factor *= 1.0 + 0.5 * (node.max_attempts - 1)
    return round(base * factor, 4)


def estimate_run(nodes: list[TaskNode]) -> RunEstimate:
    per = {n.id: estimate_node(n) for n in nodes}
    return RunEstimate(total_usd=round(sum(per.values()), 4), per_node=per)
