# app/modules/auth/service.py
# -----------------------------------------------------------------------------
# Logique d'authentification : vérification login/mot de passe et création du
# token JWT. Utilise UtilisateurService (parametrage) et core.security.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.modules.parametrage.services.messages import Messages
from app.modules.parametrage.services.utilisateur import UtilisateurService


async def login(
    db: AsyncSession,
    entreprise_id: int,
    login: str,
    password: str,
) -> str:
    """
    Vérifie les identifiants et retourne un token JWT si OK.
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
    token = create_access_token(
        subject=user.id,
        extra_claims={"entreprise_id": user.entreprise_id},
    )
    return token
