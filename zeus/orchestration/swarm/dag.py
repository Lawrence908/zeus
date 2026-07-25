# zeus/orchestration/swarm/dag.py
"""Pure helpers over a list of TaskNodes: cycle check, readiness, completion.

The coordinator owns state transitions; these are side-effect-free queries.
"""

from __future__ import annotations

from zeus.orchestration.swarm.models import NodeStatus, TaskNode

_TERMINAL = {NodeStatus.SUCCEEDED, NodeStatus.FAILED, NodeStatus.SKIPPED}


def assert_acyclic(nodes: list[TaskNode]) -> None:
    """Raise ValueError if the dependency graph has a cycle.

    RunSpec already rejects self-deps and unknown deps; this catches multi-node
    cycles (A -> B -> A) via DFS colouring.
    """
    by_id = {n.id: n for n in nodes}
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[str, int] = {n.id: WHITE for n in nodes}

    def visit(nid: str, stack: list[str]) -> None:
        color[nid] = GREY
        for dep in by_id[nid].deps:
            if color.get(dep) == GREY:
                cycle = " -> ".join([*stack, nid, dep])
                raise ValueError(f"dependency cycle: {cycle}")
            if color.get(dep) == WHITE:
                visit(dep, [*stack, nid])
        color[nid] = BLACK

    for n in nodes:
        if color[n.id] == WHITE:
            visit(n.id, [])


def deps_satisfied(node: TaskNode, by_id: dict[str, TaskNode]) -> bool:
    """A node is runnable only once every dependency has SUCCEEDED."""
    return all(by_id[d].status == NodeStatus.SUCCEEDED for d in node.deps)


def newly_ready(nodes: list[TaskNode]) -> list[TaskNode]:
    """BLOCKED nodes whose deps are now all satisfied."""
    by_id = {n.id: n for n in nodes}
    return [
        n for n in nodes
        if n.status == NodeStatus.BLOCKED and deps_satisfied(n, by_id)
    ]


def running_count(nodes: list[TaskNode]) -> int:
    return sum(1 for n in nodes if n.status == NodeStatus.RUNNING)


def dispatchable(nodes: list[TaskNode]) -> list[TaskNode]:
    """READY nodes awaiting a worker."""
    return [n for n in nodes if n.status == NodeStatus.READY]


def is_complete(nodes: list[TaskNode]) -> bool:
    """Every node terminal and none failed (skips allowed)."""
    return all(n.status in _TERMINAL for n in nodes) and not has_failure(nodes)


def has_failure(nodes: list[TaskNode]) -> bool:
    return any(n.status == NodeStatus.FAILED for n in nodes)


def all_terminal(nodes: list[TaskNode]) -> bool:
    return all(n.status in _TERMINAL for n in nodes)


def descendants(node_id: str, nodes: list[TaskNode]) -> list[TaskNode]:
    """All nodes transitively depending on node_id (for cascade-skip)."""
    out: list[TaskNode] = []
    seen: set[str] = set()
    frontier = {node_id}
    while frontier:
        nxt: set[str] = set()
        for n in nodes:
            if n.id in seen:
                continue
            if any(d in frontier for d in n.deps):
                out.append(n)
                seen.add(n.id)
                nxt.add(n.id)
        frontier = nxt
    return out
