# tests/api/test_auth.py
# -----------------------------------------------------------------------------
# Tests d'authentification : login et refresh token.
# -----------------------------------------------------------------------------

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Connexion avec identifiants valides retourne access_token et refresh_token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "entreprise_id": 1,
            "login": "test",
            "password": "password",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    assert data.get("refresh_token") is not None
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Connexion avec mot de passe incorrect retourne 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "entreprise_id": 1,
            "login": "test",
            "password": "wrong",
        },
    )
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient):
    """Connexion avec utilisateur inexistant retourne 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "entreprise_id": 1,
            "login": "nonexistent",
            "password": "password",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_payload(client: AsyncClient):
    """Connexion sans champs requis retourne 422."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"entreprise_id": 1},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    """Refresh avec un token valide retourne de nouveaux tokens."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"entreprise_id": 1, "login": "test", "password": "password"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data.get("refresh_token") is not None
    assert data["access_token"] != login_resp.json()["access_token"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Refresh avec un token invalide retourne 401."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.jwt.token"},
    )
    assert response.status_code == 401

