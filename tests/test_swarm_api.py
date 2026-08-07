# tests/test_swarm_api.py — Argo swarm HTTP surface (/swarm/*)
import os
import tempfile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zeus.orchestration.swarm.api import router
from zeus.orchestration.swarm.coordinator import Coordinator
from zeus.orchestration.swarm.planner import StubPlanner
from zeus.orchestration.swarm.store import SwarmStore
from zeus.orchestration.swarm.worker import StubWorker


def _client() -> TestClient:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SwarmStore(path)
    app = FastAPI()
    app.state.swarm_store = store
    app.state.swarm_coordinator = Coordinator(store, StubWorker())
    app.state.swarm_planner = StubPlanner()
    app.include_router(router)
    return TestClient(app)


def _pending(view: dict, kind: str, node_id=None):
    for a in view["approvals"]:
        if a["state"] == "pending" and a["kind"] == kind and a["node_id"] == node_id:
            return a
    return None


def test_create_approve_complete_over_http(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    c = _client()
    r = c.post("/swarm/runs", json={
        "goal": "do the thing",
        "repo": str(tmp_path),
        "nodes": [
            {"id": "a", "title": "step a"},
            {"id": "b", "title": "step b", "deps": ["a"]},
        ],
    })
    assert r.status_code == 200, r.text
    view = r.json()
    run_id = view["run"]["id"]
    assert view["run"]["status"] == "pending_plan_approval"

    plan = _pending(view, "plan")
    assert plan is not None
    r = c.post(f"/swarm/runs/{run_id}/approve", json={"approval_id": plan["id"], "approve": True})
    view = r.json()
    # No write gates -> both nodes run -> final gate.
    assert view["run"]["status"] == "pending_final_approval"
    assert {n["id"]: n["status"] for n in view["nodes"]} == {"a": "succeeded", "b": "succeeded"}

    final = _pending(view, "final")
    r = c.post(f"/swarm/runs/{run_id}/approve", json={"approval_id": final["id"], "approve": True})
    assert r.json()["run"]["status"] == "completed"

    # list + get
    assert any(run["id"] == run_id for run in c.get("/swarm/runs").json())
    assert c.get(f"/swarm/runs/{run_id}").json()["run"]["status"] == "completed"


def test_rejects_repo_off_allowlist(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    c = _client()
    r = c.post("/swarm/runs", json={
        "goal": "x", "repo": "/etc", "nodes": [{"id": "a", "title": "a"}],
    })
    assert r.status_code == 422


def test_rejects_cyclic_dag(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    c = _client()
    r = c.post("/swarm/runs", json={
        "goal": "x", "repo": str(tmp_path),
        "nodes": [
            {"id": "a", "title": "a", "deps": ["b"]},
            {"id": "b", "title": "b", "deps": ["a"]},
        ],
    })
    assert r.status_code == 422


def test_plan_scopes_goal_into_run(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    c = _client()
    r = c.post("/swarm/plan", json={"goal": "add a /health endpoint", "repo": str(tmp_path)})
    assert r.status_code == 200, r.text
    view = r.json()
    assert view["run"]["status"] == "pending_plan_approval"
    # StubPlanner's fixed DAG
    assert [n["id"] for n in view["nodes"]] == ["implement", "verify"]
    # cost estimate is attached at the plan gate (C2)
    assert view["estimate"]["total_usd"] > 0


# ---- P11 reach: multi-repo allowlist + propose ---------------------------


def test_repos_lists_allowlist(monkeypatch, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", f"{a},{b}")
    c = _client()
    data = c.get("/swarm/repos").json()
    assert str(a) in data["repos"] and str(b) in data["repos"]
    assert data["propose_enabled"] is False


def test_propose_disabled_by_default(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    monkeypatch.delenv("ZEUS_SWARM_PROPOSE_ENABLED", raising=False)
    c = _client()
    r = c.post("/swarm/propose", json={"goal": "do a thing"})
    assert r.status_code == 403


def test_propose_creates_plan_gated_run_with_capped_budget(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    monkeypatch.setenv("ZEUS_SWARM_PROPOSE_ENABLED", "1")
    monkeypatch.setenv("ZEUS_SWARM_PROPOSE_BUDGET_USD", "0.50")
    c = _client()
    # no repo passed -> defaults to the first allowlisted repo; budget capped
    r = c.post("/swarm/propose", json={"goal": "add a health endpoint", "budget_usd": 999})
    assert r.status_code == 200, r.text
    view = r.json()
    assert view["run"]["status"] == "pending_plan_approval"  # never auto-runs
    assert view["run"]["repo"] == str(tmp_path)
    assert view["run"]["budget_usd"] == 0.50  # hard cap enforced, not 999
    assert set(view["estimate"]["per_node"]) == {"implement", "verify"}

    # The Metis-proposed plan IS what you approve at gate 1; then it runs.
    plan = _pending(view, "plan")
    r = c.post(f"/swarm/runs/{view['run']['id']}/approve",
               json={"approval_id": plan["id"], "approve": True})
    assert r.json()["run"]["status"] == "pending_final_approval"


def test_plan_rejects_repo_off_allowlist(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", str(tmp_path))
    c = _client()
    assert c.post("/swarm/plan", json={"goal": "x", "repo": "/etc"}).status_code == 422


def test_missing_run_404():
    c = _client()
    assert c.get("/swarm/runs/nope").status_code == 404


def test_health():
    assert _client().get("/swarm/health").json() == {"enabled": True}
