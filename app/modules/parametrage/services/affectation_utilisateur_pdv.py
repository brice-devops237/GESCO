# app/modules/parametrage/services/affectation_utilisateur_pdv.py
# -----------------------------------------------------------------------------
# Use Case AffectationUtilisateurPdv (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import AffectationUtilisateurPdv
from app.modules.parametrage.repositories import (
    AffectationPdvRepository,
    PointVenteRepository,
    UtilisateurRepository,
)
from app.modules.parametrage.schemas import (
    AffectationUtilisateurPdvCreate,
    AffectationUtilisateurPdvUpdate,
)
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class AffectationUtilisateurPdvService(BaseParametrageService):
    """Service de gestion des affectations utilisateur ↔ point de vente."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = AffectationPdvRepository(db)
        self._utilisateur_repo = UtilisateurRepository(db)
        self._pdv_repo = PointVenteRepository(db)

    async def get_by_id(self, affectation_id: int) -> AffectationUtilisateurPdv | None:
        return await self._repo.find_by_id(affectation_id)

    async def get_or_404(self, affectation_id: int) -> AffectationUtilisateurPdv:
        a = await self._repo.find_by_id(affectation_id)
        if a is None:
            self._raise_not_found(Messages.AFFECTATION_NOT_FOUND)
        return a

    async def get_affectations_by_utilisateur(
        self,
        utilisateur_id: int,
    ) -> list[AffectationUtilisateurPdv]:
        if await self._utilisateur_repo.find_by_id(utilisateur_id) is None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        return await self._repo.find_by_utilisateur(utilisateur_id)

    async def get_affectations_by_point_vente(
        self,
        point_de_vente_id: int,
    ) -> list[AffectationUtilisateurPdv]:
        if await self._pdv_repo.find_by_id(point_de_vente_id) is None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        return await self._repo.find_by_point_vente(point_de_vente_id)

    async def create(self, data: AffectationUtilisateurPdvCreate) -> AffectationUtilisateurPdv:
        if await self._utilisateur_repo.find_by_id(data.utilisateur_id) is None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        if await self._repo.exists_by_utilisateur_and_point_vente(
            data.utilisateur_id,
            data.point_de_vente_id,
        ):
            self._raise_conflict(Messages.AFFECTATION_ALREADY_EXISTS)
        a = AffectationUtilisateurPdv(
            utilisateur_id=data.utilisateur_id,
            point_de_vente_id=data.point_de_vente_id,
            est_principal=data.est_principal,
        )
        return await self._repo.add(a)

    async def update(
        self,
        affectation_id: int,
        data: AffectationUtilisateurPdvUpdate,
    ) -> AffectationUtilisateurPdv:
        a = await self.get_or_404(affectation_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(a, key, value)
        return await self._repo.update(a)

    async def delete(self, affectation_id: int) -> None:
        a = await self.get_or_404(affectation_id)
        await self._repo.delete(a)
