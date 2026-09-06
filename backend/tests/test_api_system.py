"""
Tests for System Health and Metrics API routes.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_health(client: AsyncClient):
    response = await client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "uptime_seconds" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_system_metrics(client: AsyncClient, viewer_user: dict):
    response = await client.get("/api/system/metrics", headers=viewer_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert "inference_fps" in data
    assert "process" in data
    assert "memory_rss_mb" in data["process"]
