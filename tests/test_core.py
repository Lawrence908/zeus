from fastapi.testclient import TestClient
from zeus import __version__
from zeus.core.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == __version__


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Zeus"
    assert "version" in data


def test_services():
    response = client.get("/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert len(data["services"]) > 0
    names = [s["name"] for s in data["services"]]
    assert "mnemosyne" in names
    assert "hermes" in names
    assert "apollo" in names
