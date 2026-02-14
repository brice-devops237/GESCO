# app/modules/parametrage/dependencies.py
# -----------------------------------------------------------------------------
# Dépendances FastAPI spécifiques au module Paramétrage : get_current_user
# (extraction du JWT et chargement de l'utilisateur depuis la base).
# Placé ici (et non dans core) pour éviter que core dépende des modules métier,
# ce qui supprimerait tout risque d'import circulaire.
# -----------------------------------------------------------------------------

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.modules.parametrage.models import Utilisateur
from app.modules.parametrage.repositories import UtilisateurRepository
from app.modules.parametrage.services.messages import Messages

# Schéma d'authentification : Bearer <token> dans le header Authorization
_http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_http_bearer)],
) -> Utilisateur:
    """
    Dépendance FastAPI : récupère l'utilisateur authentifié à partir du token JWT.
    - Si pas de token ou token invalide/expiré : lève UnauthorizedError (401).
    - Sinon charge l'utilisateur via le repository et le retourne.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedError(detail="Token manquant ou invalide")
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError(detail="Token invalide ou expiré")
    user_id_str = payload["sub"]
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedError(detail="Token invalide")
    repo = UtilisateurRepository(db)
    user = await repo.find_by_id(user_id)
    if not user:
        raise UnauthorizedError(detail="Utilisateur non trouvé")
    if not user.actif:
        raise UnauthorizedError(detail=Messages.UTILISATEUR_DESACTIVATED)
    return user


# Alias pour annotation dans les routes : CurrentUser = Depends(get_current_user)
CurrentUser = Annotated[Utilisateur, Depends(get_current_user)]
