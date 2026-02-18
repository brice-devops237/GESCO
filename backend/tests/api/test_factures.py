# tests/api/test_factures.py
# -----------------------------------------------------------------------------
# Tests des endpoints factures (liste, détail, création) avec authentification.
# -----------------------------------------------------------------------------

from datetime import date

import pytest
from httpx import AsyncClient


async def _get_auth_headers(client: AsyncClient) -> dict:
    """Retourne les en-têtes avec Bearer token pour les requêtes authentifiées."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"entreprise_id": 1, "login": "test", "password": "password"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_factures_requires_auth(client: AsyncClient):
    """Sans token, la liste des factures retourne 403 (ou 401)."""
    response = await client.get("/api/v1/commercial/factures")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_factures_success(client: AsyncClient):
    """Avec token valide, la liste des factures retourne 200."""
    headers = await _get_auth_headers(client)
    response = await client.get("/api/v1/commercial/factures", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_facture_not_found(client: AsyncClient):
    """Détail d'une facture inexistante retourne 404."""
    headers = await _get_auth_headers(client)
    response = await client.get("/api/v1/commercial/factures/99999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_facture_success(client: AsyncClient):
    """Création d'une facture avec données valides retourne 201."""
    headers = await _get_auth_headers(client)
    payload = {
        "entreprise_id": 1,
        "point_de_vente_id": 1,
        "client_id": 1,
        "numero": "FAC-TEST-001",
        "date_facture": date.today().isoformat(),
        "etat_id": 1,
        "type_facture": "facture",
        "montant_ht": "1000.00",
        "montant_tva": "197.50",
        "montant_ttc": "1197.50",
        "montant_restant_du": "1197.50",
        "devise_id": 1,
    }
    response = await client.post(
        "/api/v1/commercial/factures",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["numero"] == "FAC-TEST-001"
    assert "id" in data
    assert data["entreprise_id"] == 1

