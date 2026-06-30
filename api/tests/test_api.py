"""Smoke tests for the OLAP API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

WAREHOUSE = ROOT / "data" / "warehouse.duckdb"


@pytest.fixture(scope="session", autouse=True)
def require_warehouse() -> None:
    if not WAREHOUSE.exists():
        pytest.skip("warehouse.duckdb not found; run scripts/run_pipeline.py first")


@pytest.fixture
def client() -> TestClient:
    from api.main import app

    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["warehouse_ready"] is True


def test_summary(client: TestClient) -> None:
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] > 0
    assert data["total_orders"] > 0


def test_revenue_trend(client: TestClient) -> None:
    response = client.get("/api/metrics/revenue-trend?grain=month")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) > 0
    assert "period" in rows[0]
    assert "revenue" in rows[0]


def test_cube(client: TestClient) -> None:
    response = client.get("/api/cube?dimensions=region,category&measure=revenue")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) > 0
    assert "region" in rows[0]
    assert "category" in rows[0]
    assert "value" in rows[0]


def test_drill(client: TestClient) -> None:
    response = client.get("/api/cube/drill?dimension=date&level=year")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) >= 2
    assert "period" in rows[0]
