# app/modules/rh/services/objectif.py
# -----------------------------------------------------------------------------
# Service métier : objectifs (commerciaux / performance).
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rh.models import Objectif
from app.modules.rh.repositories import EmployeRepository, ObjectifRepository
from app.modules.rh.schemas import ObjectifCreate, ObjectifUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages


class ObjectifService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ObjectifRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._employe_repo = EmployeRepository(db)

    async def get_by_id(self, id: int) -> Objectif | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Objectif:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.OBJECTIF_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Objectif], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            employe_id=employe_id,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: ObjectifCreate) -> Objectif:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._employe_repo.find_by_id(data.employe_id) is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        if data.date_fin < data.date_debut:
            self._raise_bad_request(Messages.OBJECTIF_DATES)
        ent = Objectif(
            entreprise_id=data.entreprise_id,
            employe_id=data.employe_id,
            libelle=data.libelle.strip(),
            date_debut=data.date_debut,
            date_fin=data.date_fin,
            montant_cible=data.montant_cible,
            atteint=data.atteint,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ObjectifUpdate) -> Objectif:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "date_fin" in update_data and "date_debut" not in update_data:
            if update_data["date_fin"] < ent.date_debut:
                self._raise_bad_request(Messages.OBJECTIF_DATES)
        elif "date_debut" in update_data and "date_fin" not in update_data:
            if ent.date_fin < update_data["date_debut"]:
                self._raise_bad_request(Messages.OBJECTIF_DATES)
        elif "date_debut" in update_data and "date_fin" in update_data:
            if update_data["date_fin"] < update_data["date_debut"]:
                self._raise_bad_request(Messages.OBJECTIF_DATES)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
