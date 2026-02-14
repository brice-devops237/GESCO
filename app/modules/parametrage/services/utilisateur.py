# app/modules/parametrage/services/utilisateur.py
# -----------------------------------------------------------------------------
# Use Case Utilisateur (couche Application).
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
    """Service de gestion des utilisateurs (par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = UtilisateurRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._role_repo = RoleRepository(db)
        self._pdv_repo = PointVenteRepository(db)

    async def get_by_id(self, utilisateur_id: int) -> Utilisateur | None:
        return await self._repo.find_by_id(utilisateur_id)

    async def get_or_404(self, utilisateur_id: int) -> Utilisateur:
        u = await self._repo.find_by_id(utilisateur_id)
        if u is None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        return u

    async def get_by_login(
        self,
        entreprise_id: int,
        login: str,
    ) -> Utilisateur | None:
        return await self._repo.find_by_entreprise_and_login(entreprise_id, login)

    async def get_utilisateurs(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> list[Utilisateur]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_by_entreprise(
            entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def create(self, data: UtilisateurCreate) -> Utilisateur:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._role_repo.find_by_id(data.role_id) is None:
            self._raise_not_found(Messages.ROLE_NOT_FOUND)
        if data.point_de_vente_id is not None:
            if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
                self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        login_clean = (data.login or "").strip()
        if not login_clean:
            self._raise_bad_request(Messages.UTILISATEUR_LOGIN_INVALID)
        if await self._repo.find_by_entreprise_and_login(data.entreprise_id, login_clean):
            self._raise_conflict(
                Messages.UTILISATEUR_LOGIN_EXISTS.format(login=login_clean),
            )
        u = Utilisateur(
            entreprise_id=data.entreprise_id,
            point_de_vente_id=data.point_de_vente_id,
            role_id=data.role_id,
            login=login_clean,
            mot_de_passe_hash=hash_password(data.mot_de_passe),
            email=data.email,
            nom=data.nom,
            prenom=data.prenom,
            telephone=data.telephone,
            actif=data.actif,
        )
        return await self._repo.add(u)

    async def update(
        self,
        utilisateur_id: int,
        data: UtilisateurUpdate,
    ) -> Utilisateur:
        u = await self.get_or_404(utilisateur_id)
        update_data = data.model_dump(exclude_unset=True)
        if "mot_de_passe" in update_data:
            update_data["mot_de_passe_hash"] = hash_password(
                update_data.pop("mot_de_passe"),
            )
        if "role_id" in update_data:
            if await self._role_repo.find_by_id(update_data["role_id"]) is None:
                self._raise_not_found(Messages.ROLE_NOT_FOUND)
        if update_data.get("point_de_vente_id") is not None:
            if await self._pdv_repo.find_by_id(
                update_data["point_de_vente_id"],
            ) is None:
                self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        for key, value in update_data.items():
            setattr(u, key, value)
        return await self._repo.update(u)
