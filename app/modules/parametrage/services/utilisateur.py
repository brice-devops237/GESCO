# app/modules/parametrage/services/utilisateur.py
# -----------------------------------------------------------------------------
# Use Case Utilisateur (couche Application). Hash du mot de passe côté serveur.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.parametrage.models import Utilisateur
from app.modules.parametrage.repositories import (
    EntrepriseRepository,
    PointVenteRepository,
    RoleRepository,
    UtilisateurRepository,
)
from app.modules.parametrage.schemas import UtilisateurCreate, UtilisateurUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class UtilisateurService(BaseParametrageService):
    """Use cases pour l'agrégat Utilisateur."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = UtilisateurRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._role_repo = RoleRepository(db)
        self._pdv_repo = PointVenteRepository(db)

    async def get_utilisateurs(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> list[Utilisateur]:
        """Liste des utilisateurs d'une entreprise."""
        return await self._repo.find_by_entreprise(
            entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def get_or_404(self, utilisateur_id: int) -> Utilisateur:
        user = await self._repo.find_by_id(utilisateur_id)
        if user is None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        return user

    async def create(self, data: UtilisateurCreate) -> Utilisateur:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._role_repo.find_by_id(data.role_id) is None:
            self._raise_not_found(Messages.ROLE_NOT_FOUND)
        if data.point_de_vente_id is not None:
            if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
                self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        login = (data.login or "").strip()
        if not login:
            self._raise_bad_request(Messages.UTILISATEUR_LOGIN_INVALID)
        if await self._repo.find_by_entreprise_and_login(data.entreprise_id, login) is not None:
            self._raise_conflict(Messages.UTILISATEUR_LOGIN_EXISTS.format(login=login))
        entity = Utilisateur(
            entreprise_id=data.entreprise_id,
            point_de_vente_id=data.point_de_vente_id,
            role_id=data.role_id,
            login=login,
            mot_de_passe_hash=hash_password(data.mot_de_passe),
            email=data.email,
            nom=(data.nom or "").strip(),
            prenom=(data.prenom or "").strip() if data.prenom else None,
            telephone=data.telephone,
            actif=data.actif,
        )
        return await self._repo.add(entity)

    async def update(self, utilisateur_id: int, data: UtilisateurUpdate) -> Utilisateur:
        user = await self.get_or_404(utilisateur_id)
        if data.role_id is not None:
            if await self._role_repo.find_by_id(data.role_id) is None:
                self._raise_not_found(Messages.ROLE_NOT_FOUND)
            user.role_id = data.role_id
        if data.point_de_vente_id is not None:
            if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
                self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
            user.point_de_vente_id = data.point_de_vente_id
        if data.email is not None:
            user.email = data.email
        if data.nom is not None:
            user.nom = data.nom.strip() or user.nom
        if data.prenom is not None:
            user.prenom = data.prenom.strip() if data.prenom else None
        if data.telephone is not None:
            user.telephone = data.telephone
        if data.actif is not None:
            user.actif = data.actif
        if data.mot_de_passe is not None and data.mot_de_passe.strip():
            user.mot_de_passe_hash = hash_password(data.mot_de_passe)
        return await self._repo.update(user)
