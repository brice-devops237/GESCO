# app/modules/comptabilite/services/periode_comptable.py
# -----------------------------------------------------------------------------
# Service métier : périodes comptables.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comptabilite.models import PeriodeComptable
from app.modules.comptabilite.repositories import PeriodeComptableRepository
from app.modules.comptabilite.schemas import PeriodeComptableCreate, PeriodeComptableUpdate
from app.modules.comptabilite.services.base import BaseComptabiliteService
from app.modules.comptabilite.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class PeriodeComptableService(BaseComptabiliteService):
    """Service de gestion des périodes comptables."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = PeriodeComptableRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> PeriodeComptable | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> PeriodeComptable:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.PERIODE_COMPTABLE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PeriodeComptable], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(entreprise_id=entreprise_id, skip=skip, limit=limit)

    async def create(self, data: PeriodeComptableCreate) -> PeriodeComptable:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if data.date_fin <= data.date_debut:
            self._raise_bad_request(Messages.PERIODE_DATES_INCOHERENTES)
        ent = PeriodeComptable(
            entreprise_id=data.entreprise_id,
            date_debut=data.date_debut,
            date_fin=data.date_fin,
            libelle=data.libelle.strip(),
            cloturee=False,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: PeriodeComptableUpdate) -> PeriodeComptable:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "date_fin" in update_data and update_data["date_fin"] is not None:
            if update_data["date_fin"] <= ent.date_debut:
                self._raise_bad_request(Messages.PERIODE_DATES_INCOHERENTES)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
