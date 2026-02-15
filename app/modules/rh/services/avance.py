# app/modules/rh/services/avance.py
# -----------------------------------------------------------------------------
# Service métier : avances sur salaire.
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import Avance
from app.modules.rh.repositories import AvanceRepository
from app.modules.rh.schemas import AvanceCreate, AvanceUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rh.repositories import EmployeRepository


class AvanceService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = AvanceRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._employe_repo = EmployeRepository(db)

    async def get_by_id(self, id: int) -> Avance | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Avance:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.AVANCE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        rembourse: bool | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Avance], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            employe_id=employe_id,
            rembourse=rembourse,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: AvanceCreate, created_by_id: int | None = None) -> Avance:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._employe_repo.find_by_id(data.employe_id) is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        ent = Avance(
            entreprise_id=data.entreprise_id,
            employe_id=data.employe_id,
            date_avance=data.date_avance,
            montant=data.montant,
            motif=data.motif.strip() if data.motif else None,
            rembourse=data.rembourse,
            created_by_id=created_by_id,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: AvanceUpdate) -> Avance:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)
