# app/modules/paie/services/periode_paie.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.paie.models import PeriodePaie
from app.modules.paie.repositories import PeriodePaieRepository
from app.modules.paie.schemas import PeriodePaieCreate, PeriodePaieUpdate
from app.modules.paie.services.base import BasePaieService
from app.modules.paie.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class PeriodePaieService(BasePaieService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = PeriodePaieRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> PeriodePaie | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> PeriodePaie:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.PERIODE_PAIE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        cloturee: bool | None = None,
        skip: int = 0,
        limit: int = 24,
    ) -> tuple[list[PeriodePaie], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            cloturee=cloturee,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: PeriodePaieCreate) -> PeriodePaie:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if data.date_fin <= data.date_debut:
            self._raise_bad_request(Messages.PERIODE_DATES)
        if await self._repo.find_by_entreprise_annee_mois(data.entreprise_id, data.annee, data.mois) is not None:
            self._raise_conflict(Messages.PERIODE_PAIE_EXISTS)
        ent = PeriodePaie(
            entreprise_id=data.entreprise_id,
            annee=data.annee,
            mois=data.mois,
            date_debut=data.date_debut,
            date_fin=data.date_fin,
            cloturee=data.cloturee,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: PeriodePaieUpdate) -> PeriodePaie:
        ent = await self.get_or_404(id)
        if ent.cloturee:
            self._raise_bad_request(Messages.PERIODE_PAIE_CLOTUREE)
        update_data = data.model_dump(exclude_unset=True)
        if "date_fin" in update_data and "date_debut" in update_data:
            if update_data["date_fin"] <= update_data["date_debut"]:
                self._raise_bad_request(Messages.PERIODE_DATES)
        elif "date_fin" in update_data and update_data["date_fin"] <= ent.date_debut or "date_debut" in update_data and ent.date_fin <= update_data["date_debut"]:
            self._raise_bad_request(Messages.PERIODE_DATES)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

