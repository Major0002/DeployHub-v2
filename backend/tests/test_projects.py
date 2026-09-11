"""Tests for project management endpoints."""
import pytest
from httpx import AsyncClient
from core.security import create_access_token
from models.user import User
from core.security import hash_password


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, user_headers):
    """Test creating a new project."""
    payload = {
        "name": "Frontend Web App",
        "description": "React TypeScript Dashboard",
        "repo_url": "https://github.com/example/frontend",
        "repo_branch": "main",
        "language": "typescript",
        "framework": "react",
        "build_command": "npm run build",
        "output_directory": "dist",
        "env_vars": {"VITE_API": "https://api.example.com"}
    }
    response = await client.post("/api/v1/projects/", json=payload, headers=user_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["slug"] == "frontend-web-app"
    assert data["status"] == "idle"
    assert data["framework"] == "react"


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, user_headers):
    """Test listing user projects."""
    # Create project first
    await client.post("/api/v1/projects/", json={"name": "API Service"}, headers=user_headers)

    response = await client.get("/api/v1/projects/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "API Service" for p in data)


@pytest.mark.asyncio
async def test_get_project_detail(client: AsyncClient, user_headers):
    """Test retrieving project details including deployments."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Worker Node"}, headers=user_headers)
    project_id = create_res.json()["id"]

    response = await client.get(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert "deployments" in data


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, user_headers):
    """Test updating project fields."""
    create_res = await client.post("/api/v1/projects/", json={"name": "Old Name"}, headers=user_headers)
    project_id = create_res.json()["id"]

    update_res = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"name": "New Name", "description": "Updated description"},
        headers=user_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"
    assert update_res.json()["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, user_headers):
    """Test deleting a project."""
    create_res = await client.post("/api/v1/projects/", json={"name": "To Delete"}, headers=user_headers)
    project_id = create_res.json()["id"]

    delete_res = await client.delete(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert delete_res.status_code == 204

    # Verify not found
    get_res = await client.get(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_project_user_isolation(client: AsyncClient, user_headers, db_session):
    """Test that a user cannot modify or delete another user's project."""
    # User 1 creates project
    create_res = await client.post("/api/v1/projects/", json={"name": "Private Project"}, headers=user_headers)
    project_id = create_res.json()["id"]

    # Create User 2
    user2 = User(
        email="other@deployhub.dev",
        username="otheruser",
        hashed_password=hash_password("Pass123!"),
        role="user",
        is_active=True
    )
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    user2_token = create_access_token({"sub": str(user2.id), "email": user2.email, "username": user2.username, "role": user2.role})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 tries to access User 1's project -> 403 Forbidden
    access_res = await client.get(f"/api/v1/projects/{project_id}", headers=user2_headers)
    assert access_res.status_code == 403

    # User 2 tries to delete User 1's project -> 403 Forbidden
    delete_res = await client.delete(f"/api/v1/projects/{project_id}", headers=user2_headers)
    assert delete_res.status_code == 403


@pytest.mark.asyncio
async def test_project_stats(client: AsyncClient, user_headers):
    """Test project stats endpoint."""
    await client.post("/api/v1/projects/", json={"name": "Stats Project"}, headers=user_headers)

    response = await client.get("/api/v1/projects/stats", headers=user_headers)
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_projects"] >= 1
    assert "active_projects" in stats
    assert "total_deployments" in stats
