# app/modules/auth/router.py
# -----------------------------------------------------------------------------
# Routes d'authentification : login (POST) sans authentification préalable.
# Les autres modules (parametrage) utilisent get_current_user pour protéger leurs routes.
# -----------------------------------------------------------------------------

from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.modules.auth import schemas as auth_schemas
from app.modules.auth.service import login as auth_login

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post(
    "/login",
    response_model=auth_schemas.TokenResponse,
    summary="Connexion",
    description="Authentification par entreprise, login et mot de passe. Retourne un JWT à passer dans l'en-tête Authorization: Bearer <token>.",
    response_description="Token JWT et type (bearer).",
)
async def login(
    db: DbSession,
    data: auth_schemas.LoginRequest,
):
    """Authentification : vérifie entreprise_id, login et mot de passe. Retourne un token JWT."""
    access_token = await auth_login(
        db,
        entreprise_id=data.entreprise_id,
        login=data.login,
        password=data.password,
    )
    return auth_schemas.TokenResponse(access_token=access_token, token_type="bearer")
