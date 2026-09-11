"""Tests for user management endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_profile(client: AsyncClient, user_headers, test_user):
    """Test retrieving user profile."""
    response = await client.get("/api/v1/users/me", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user.username


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient, user_headers):
    """Test updating user profile."""
    update_data = {
        "full_name": "Updated Name",
        "bio": "Cloud and DevOps enthusiast"
    }
    response = await client.patch("/api/v1/users/me", json=update_data, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["bio"] == "Cloud and DevOps enthusiast"


@pytest.mark.asyncio
async def test_list_users_forbidden_for_regular_user(client: AsyncClient, user_headers):
    """Test that regular users cannot list all users."""
    response = await client.get("/api/v1/users/", headers=user_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_allowed_for_admin(client: AsyncClient, admin_headers):
    """Test that admin users can list all users."""
    response = await client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
