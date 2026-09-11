"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """Test successful user registration."""
    payload = {
        "email": "newuser@deployhub.dev",
        "username": "newuser",
        "password": "Password123!",
        "full_name": "New User"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration failure with duplicate email."""
    payload = {
        "email": test_user.email,
        "username": "unique_username",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """Test registration failure with duplicate username."""
    payload = {
        "email": "another@deployhub.dev",
        "username": test_user.username,
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "Username already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login returning JWT token pair."""
    payload = {
        "email": test_user.email,
        "password": "DevPassword123!"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Test login failure with incorrect password."""
    payload = {
        "email": test_user.email,
        "password": "WrongPassword!"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, test_user):
    """Test refreshing an access token using valid refresh token."""
    login_res = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "DevPassword123!"
    })
    refresh_token = login_res.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_token_refresh_invalid(client: AsyncClient):
    """Test token refresh with invalid token."""
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.jwt.token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, user_headers, test_user):
    """Test getting current user profile with token."""
    response = await client.get("/api/v1/auth/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test accessing protected /auth/me without authorization header."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
