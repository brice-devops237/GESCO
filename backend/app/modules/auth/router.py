# app/modules/auth/router.py
# -----------------------------------------------------------------------------
# Routes d'authentification : login (POST), refresh (POST) sans authentification préalable.
# Les autres modules (parametrage) utilisent get_current_user pour protéger leurs routes.
# -----------------------------------------------------------------------------

from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.modules.auth import schemas as auth_schemas
from app.modules.auth.service import login as auth_login, refresh_access_token as auth_refresh

router = APIRouter(prefix="/auth", tags=["Authentification"])


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

