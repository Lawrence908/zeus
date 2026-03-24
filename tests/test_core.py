"""Tests for Zeus Core API bus."""

import pytest
from httpx import ASGITransport, AsyncClient
from zeus.core.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Welcome to Zeus"
    assert "version" in data


async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Zeus"


async def test_list_services(client: AsyncClient):
    resp = await client.get("/services/")
    assert resp.status_code == 200
    data = resp.json()
    assert "services" in data
    assert "mnemosyne" in data["services"]


async def test_get_service(client: AsyncClient):
    resp = await client.get("/services/oracle")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Zeus Context API"


async def test_unknown_service(client: AsyncClient):
    resp = await client.get("/services/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data
