"""Tests for health and readiness probes."""

from __future__ import annotations

from httpx import AsyncClient

from app import __version__


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "version": __version__}


async def test_ready_checks_database(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"
