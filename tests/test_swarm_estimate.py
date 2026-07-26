# tests/test_swarm_estimate.py — cost estimator (C2)
from zeus.orchestration.swarm.estimate import estimate_node, estimate_run
from zeus.orchestration.swarm.models import NodeStatus, TaskNode


def _n(nid, **kw):
    base = dict(run_id="r", id=nid, title="t", status=NodeStatus.BLOCKED)
    base.update(kw)
    return TaskNode(**base)


def test_cheap_cheaper_than_strong():
    assert estimate_node(_n("a", model="haiku")) < estimate_node(_n("a", model="sonnet"))


def test_bash_and_retries_raise_estimate():
    plain = estimate_node(_n("a", model="haiku", tool_scope=["Write"]))
    heavy = estimate_node(_n("a", model="haiku", tool_scope=["Write", "Bash"]))
    assert heavy > plain
    retried = estimate_node(_n("a", model="haiku", tool_scope=["Write"], check="pytest", max_attempts=3))
    assert retried > plain


def test_estimate_run_sums_and_reports_per_node():
    nodes = [_n("a", model="haiku"), _n("b", model="sonnet")]
    est = estimate_run(nodes)
    assert set(est.per_node) == {"a", "b"}
    assert abs(est.total_usd - sum(est.per_node.values())) < 1e-9
    assert est.total_usd > 0
