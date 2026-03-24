"""Tests for Zeus Context API (Oracle)."""

import pytest
from httpx import ASGITransport, AsyncClient
from zeus.api.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_oracle_status(client: AsyncClient):
    resp = await client.get("/api/v1/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "oracle"
    assert data["status"] == "online"


async def test_oracle_query_empty(client: AsyncClient):
    resp = await client.get("/api/v1/query")
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data


async def test_oracle_query(client: AsyncClient):
    resp = await client.get("/api/v1/query", params={"q": "test query"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "test query"
    assert "results" in data
