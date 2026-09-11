"""Tests for deployment lifecycle endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trigger_deployment_via_project(client: AsyncClient, user_headers):
    """Test triggering a deployment via /projects/{id}/deploy."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Deployable App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    deploy_res = await client.post(
        f"/api/v1/projects/{project_id}/deploy",
        json={"branch": "staging", "commit_sha": "abc1234"},
        headers=user_headers
    )
    assert deploy_res.status_code == 201
    deployment = deploy_res.json()
    assert deployment["status"] == "pending"
    assert deployment["project_id"] == project_id
    assert deployment["branch"] == "staging"
    assert deployment["commit_sha"] == "abc1234"

    # Verify project status transitioned to building
    project_res = await client.get(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert project_res.json()["status"] == "building"


@pytest.mark.asyncio
async def test_trigger_deployment_via_deployments_router(client: AsyncClient, user_headers):
    """Test triggering a deployment via /deployments/project/{id}."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Second App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    deploy_res = await client.post(
        f"/api/v1/deployments/project/{project_id}",
        json={"branch": "main"},
        headers=user_headers
    )
    assert deploy_res.status_code == 201
    assert deploy_res.json()["project_id"] == project_id


@pytest.mark.asyncio
async def test_list_and_get_deployment(client: AsyncClient, user_headers):
    """Test listing deployments for a project and fetching specific deployment details."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Third App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    deploy_res = await client.post(f"/api/v1/projects/{project_id}/deploy", headers=user_headers)
    deployment_id = deploy_res.json()["id"]

    # List
    list_res = await client.get(f"/api/v1/deployments/project/{project_id}", headers=user_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Get single
    get_res = await client.get(f"/api/v1/deployments/{deployment_id}", headers=user_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == deployment_id


@pytest.mark.asyncio
async def test_update_deployment_status(client: AsyncClient, user_headers):
    """Test updating deployment status to success and checking parent project sync."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Status Sync App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    deploy_res = await client.post(f"/api/v1/projects/{project_id}/deploy", headers=user_headers)
    deployment_id = deploy_res.json()["id"]

    # Update status to success
    update_res = await client.patch(
        f"/api/v1/deployments/{deployment_id}/status",
        json={
            "status": "success",
            "container_id": "cont-123456",
            "production_url": "https://status-sync.example.com",
            "build_duration_ms": 15000,
            "deploy_duration_ms": 3000
        },
        headers=user_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "success"
    assert update_res.json()["container_id"] == "cont-123456"

    # Verify project status updated to deployed and healthy
    project_res = await client.get(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert project_res.json()["status"] == "deployed"
    assert project_res.json()["health_status"] == "healthy"


@pytest.mark.asyncio
async def test_cancel_deployment(client: AsyncClient, user_headers):
    """Test cancelling an in-progress deployment."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Cancel App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    deploy_res = await client.post(f"/api/v1/projects/{project_id}/deploy", headers=user_headers)
    deployment_id = deploy_res.json()["id"]

    cancel_res = await client.post(f"/api/v1/deployments/{deployment_id}/cancel", headers=user_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_rollback_deployment(client: AsyncClient, user_headers):
    """Test rolling back to a previous deployment."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Rollback App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    first_deploy = await client.post(
        f"/api/v1/projects/{project_id}/deploy",
        json={"commit_sha": "v1.0.0-sha", "branch": "main"},
        headers=user_headers
    )
    first_deploy_id = first_deploy.json()["id"]

    rollback_res = await client.post(f"/api/v1/deployments/{first_deploy_id}/rollback", headers=user_headers)
    assert rollback_res.status_code == 201
    new_deployment = rollback_res.json()
    assert new_deployment["commit_sha"] == "v1.0.0-sha"
    assert "Rollback" in new_deployment["commit_message"]


@pytest.mark.asyncio
async def test_get_deployment_logs(client: AsyncClient, user_headers):
    """Test retrieving deployment build and runtime logs."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Logs App"}, headers=user_headers)
    project_id = create_res.json()["id"]

    deploy_res = await client.post(f"/api/v1/projects/{project_id}/deploy", headers=user_headers)
    deployment_id = deploy_res.json()["id"]

    logs_res = await client.get(f"/api/v1/deployments/{deployment_id}/logs", headers=user_headers)
    assert logs_res.status_code == 200
    data = logs_res.json()
    assert "build_logs" in data
    assert "runtime_logs" in data
