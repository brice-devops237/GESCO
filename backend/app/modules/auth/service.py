# app/modules/auth/service.py
# -----------------------------------------------------------------------------
# Logique d'authentification : vérification login/mot de passe et création du
# token JWT. Utilise UtilisateurService (parametrage) et core.security.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.modules.parametrage.services.messages import Messages
from app.modules.parametrage.services.utilisateur import UtilisateurService


async def login(
    db: AsyncSession,
    entreprise_id: int,
    login: str,
    password: str,
) -> tuple[str, str]:
    """
    Vérifie les identifiants et retourne (access_token, refresh_token) si OK.
    Lève UnauthorizedError avec message personnalisé si utilisateur absent,
    désactivé ou mot de passe incorrect.
    """
    service = UtilisateurService(db)
    user = await service.get_by_login(entreprise_id, login)
    if not user:
        raise UnauthorizedError(detail="Identifiants incorrects.")
    if not user.actif:
        raise UnauthorizedError(detail=Messages.UTILISATEUR_DESACTIVATED)
    if not verify_password(password, user.mot_de_passe_hash):
        raise UnauthorizedError(detail="Identifiants incorrects.")
    access_token = create_access_token(
        subject=user.id,
        extra_claims={"entreprise_id": user.entreprise_id},
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        extra_claims={"entreprise_id": user.entreprise_id},
    )
    return access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> tuple[str, str]:
    """
    Valide le refresh token et retourne un nouveau (access_token, refresh_token).
    Lève UnauthorizedError si le token est invalide ou si l'utilisateur n'existe plus / est désactivé.
    """
    payload = decode_refresh_token(refresh_token_str)
    if not payload or "sub" not in payload:
        raise UnauthorizedError(detail="Token de rafraîchissement invalide ou expiré.")
    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise UnauthorizedError(detail="Token de rafraîchissement invalide.")
    from app.modules.parametrage.repositories import UtilisateurRepository
    repo = UtilisateurRepository(db)
    user = await repo.find_by_id(user_id)
    if not user:
        raise UnauthorizedError(detail="Utilisateur non trouvé.")
    if not user.actif:
        raise UnauthorizedError(detail=Messages.UTILISATEUR_DESACTIVATED)
    access_token = create_access_token(
        subject=user.id,
        extra_claims={"entreprise_id": user.entreprise_id},
    )
    new_refresh_token = create_refresh_token(
        subject=user.id,
        extra_claims={"entreprise_id": user.entreprise_id},
    )
    return access_token, new_refresh_token

