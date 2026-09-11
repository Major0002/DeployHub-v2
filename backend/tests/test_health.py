"""Tests for health check endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root informational endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "DeployHub" in data["name"]
    assert data["api_v1"] == "/api/v1"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test /api/v1/health/ basic health status."""
    response = await client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.asyncio
async def test_health_readiness(client: AsyncClient):
    """Test /api/v1/health/ready readiness check."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_health_liveness(client: AsyncClient):
    """Test /api/v1/health/live Kubernetes liveness probe."""
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_top_level_health(client: AsyncClient):
    """Test top-level /health endpoints for container healthchecks."""
    response = await client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
