# app/modules/parametrage/dependencies.py
# -----------------------------------------------------------------------------
# Dépendances FastAPI spécifiques au module Paramétrage : get_current_user,
# isolation multi-tenant (entreprise_id validé), autorisation par permissions.
# Placé ici (et non dans core) pour éviter que core dépende des modules métier,
# ce qui supprimerait tout risque d'import circulaire.
# -----------------------------------------------------------------------------

from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.modules.parametrage.models import Utilisateur
from app.modules.parametrage.repositories import UtilisateurRepository
from app.modules.parametrage.services.messages import Messages

# Schéma d'authentification : Bearer <token> dans le header Authorization.
# scheme_name="BearerAuth" pour correspondre au schéma OpenAPI dans /docs (Authorize).
_http_bearer = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


def _extract_token(credentials: HTTPAuthorizationCredentials | None, request: Request) -> str | None:
    """Extrait le token JWT depuis HTTPBearer ou depuis le header Authorization brut."""
    if credentials and credentials.credentials:
        raw = credentials.credentials.strip()
    else:
        raw = request.headers.get("Authorization") or ""
        raw = raw.strip()
    if not raw:
        return None
    if raw.upper().startswith("BEARER "):
        return raw[7:].strip()
    return raw


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_http_bearer)],
) -> Utilisateur:
    """
    Dépendance FastAPI : récupère l'utilisateur authentifié à partir du token JWT.
    - Token depuis Authorization: Bearer <token> ou Authorization: <token>.
    - Si pas de token ou token invalide/expiré : lève UnauthorizedError (401).
    """
    token = _extract_token(credentials, request)
    if not token:
        raise UnauthorizedError(detail="Token manquant ou invalide")
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError(detail="Token invalide ou expiré")
    user_id_str = payload["sub"]
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError) as err:
        raise UnauthorizedError(detail="Token invalide") from err
    repo = UtilisateurRepository(db)
    user = await repo.find_by_id(user_id)
    if not user:
        raise UnauthorizedError(detail="Utilisateur non trouvé")
    if not user.actif:
        raise UnauthorizedError(detail=Messages.UTILISATEUR_DESACTIVATED)
    return user


# Alias pour annotation dans les routes : CurrentUser = Depends(get_current_user)
CurrentUser = Annotated[Utilisateur, Depends(get_current_user)]


def get_validated_entreprise_id(
    current_user: CurrentUser,
    entreprise_id: int | None = Query(None, description="Filtre par entreprise (doit être l'entreprise de l'utilisateur)"),
) -> int:
    """
    Retourne l'entreprise_id de l'utilisateur. Si entreprise_id est fourni en query,
    vérifie qu'il correspond à l'utilisateur (isolation multi-tenant) et lève 403 sinon.
    """
    if entreprise_id is None:
        return current_user.entreprise_id
    if entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return entreprise_id


# Alias pour les routes : entreprise_id toujours égal à celle du token
ValidatedEntrepriseId = Annotated[int, Depends(get_validated_entreprise_id)]


# --- Autorisation par permission (module / action) ---------------------------


async def _check_permission(
    current_user: Utilisateur,
    db: AsyncSession,
    module: str,
    action: str,
) -> None:
    """
    Vérifie que le rôle de l'utilisateur possède la permission (module, action).
    Si le rôle n'a aucune permission affectée (perms vide), l'accès est autorisé (rétrocompatibilité).
    Sinon lève ForbiddenError si (module, action) n'est pas dans la liste.
    """
    from app.modules.parametrage.repositories import PermissionRepository

    repo = PermissionRepository(db)
    perms = await repo.find_permissions_by_role_id(current_user.role_id)
    if not perms:
        return  # Aucune permission définie pour ce rôle : accès autorisé (comportement par défaut)
    if (module, action) not in perms:
        raise ForbiddenError(
            detail=f"Permission requise : {module}.{action}",
            code="FORBIDDEN_PERMISSION",
        )


def RequirePermission(module: str, action: str):  # noqa: N802
    """
    Dépendance FastAPI : exige la permission (module, action) pour le rôle de l'utilisateur.
    À utiliser après CurrentUser : RequirePermission("parametrage", "read").
    """
    async def _dep(
        current_user: Annotated[Utilisateur, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        await _check_permission(current_user, db, module, action)

    return Depends(_dep)

