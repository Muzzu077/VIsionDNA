"""
Tests for authentication routes and role-based access control.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_login_success(client: AsyncClient, admin_user: dict):
    response = await client.post(
        "/api/auth/login",
        json={"email": admin_user["user"].email, "password": "adminpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_login_invalid_password(client: AsyncClient, admin_user: dict):
    response = await client.post(
        "/api/auth/login",
        json={"email": admin_user["user"].email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_profile(client: AsyncClient, admin_user: dict):
    response = await client.get("/api/auth/me", headers=admin_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == admin_user["user"].email
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_register_user_admin_only(client: AsyncClient, admin_user: dict, viewer_user: dict):
    # Viewer trying to register -> 403 Forbidden
    resp_forbidden = await client.post(
        "/api/auth/register",
        headers=viewer_user["headers"],
        json={"name": "New User", "email": "newuser@test.com", "password": "password123", "role": "VIEWER"},
    )
    assert resp_forbidden.status_code == 403

    # Admin registering -> 201 Created
    resp_success = await client.post(
        "/api/auth/register",
        headers=admin_user["headers"],
        json={"name": "New User", "email": "newuser@test.com", "password": "password123", "role": "VIEWER"},
    )
    assert resp_success.status_code == 201
    assert resp_success.json()["email"] == "newuser@test.com"
