# app/modules/auth/router.py
# -----------------------------------------------------------------------------
# Routes d'authentification : login (POST), refresh (POST) sans authentification préalable.
# Enregistré sous prefix API_V1_PREFIX (ex. /api/v1) → GET /api/v1/auth/entreprises,
# POST /api/v1/auth/login, POST /api/v1/auth/refresh.
# GET /auth/entreprises : liste publique des entreprises actives (id, raison_sociale) pour le select de connexion.
# -----------------------------------------------------------------------------

from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.modules.auth import schemas as auth_schemas
from app.modules.auth.service import login as auth_login, refresh_access_token as auth_refresh
from app.modules.parametrage.services.entreprise import EntrepriseService

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.get(
    "/entreprises",
    response_model=list[auth_schemas.EntrepriseOption],
    summary="Liste des entreprises (connexion)",
    description="Liste publique des entreprises actives pour le select de la page de connexion. Sans authentification. URL complète : GET /api/v1/auth/entreprises",
)
async def list_entreprises_login(db: DbSession):
    """Retourne id et raison_sociale des entreprises actives (pour le formulaire de login)."""
    service = EntrepriseService(db)
    items, _ = await service.get_entreprises(skip=0, limit=500, actif_only=True)
    return [auth_schemas.EntrepriseOption(id=e.id, raison_sociale=e.raison_sociale) for e in items]


@router.post(
    "/login",
    response_model=auth_schemas.TokenResponse,
    summary="Connexion",
    description="Authentification par entreprise, login et mot de passe. Retourne un JWT et un refresh token.",
    response_description="Token JWT, refresh token et type (bearer).",
)
async def login(
    db: DbSession,
    data: auth_schemas.LoginRequest,
):
    """Authentification : vérifie entreprise_id, login et mot de passe. Retourne access_token et refresh_token."""
    access_token, refresh_token = await auth_login(
        db,
        entreprise_id=data.entreprise_id,
        login=data.login,
        password=data.password,
    )
    return auth_schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=auth_schemas.TokenResponse,
    summary="Rafraîchir le token",
    description="Échange un refresh_token valide contre un nouveau access_token et un nouveau refresh_token.",
    response_description="Nouveaux tokens JWT.",
)
async def refresh(
    db: DbSession,
    data: auth_schemas.RefreshRequest,
):
    """Rafraîchit les tokens : valide le refresh_token et retourne de nouveaux access et refresh tokens."""
    access_token, new_refresh_token = await auth_refresh(db, data.refresh_token)
    return auth_schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
    )

