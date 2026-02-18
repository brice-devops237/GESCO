# app/modules/auth/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour l'authentification : requête de login et réponse token.
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Corps de la requête POST /auth/login."""
    entreprise_id: int = Field(..., description="ID de l'entreprise (contexte de connexion)")
    login: str = Field(..., min_length=1, max_length=80, description="Identifiant de connexion")
    password: str = Field(..., min_length=1, description="Mot de passe en clair")


class TokenResponse(BaseModel):
    """Réponse standard OAuth2 : token d'accès, optionnellement refresh, et type."""
    access_token: str = Field(..., description="Token JWT à envoyer dans Authorization: Bearer <token>")
    token_type: str = Field(default="bearer", description="Type de token")
    refresh_token: str | None = Field(default=None, description="Token de rafraîchissement (POST /auth/refresh)")


class RefreshRequest(BaseModel):
    """Corps de la requête POST /auth/refresh."""
    refresh_token: str = Field(..., min_length=1, description="Token de rafraîchissement reçu au login")

