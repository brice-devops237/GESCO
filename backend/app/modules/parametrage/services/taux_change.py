# app/modules/parametrage/services/taux_change.py
# -----------------------------------------------------------------------------
# Use Case TauxChange (couche Application).
# -----------------------------------------------------------------------------

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import TauxChange
from app.modules.parametrage.repositories import DeviseRepository, TauxChangeRepository
from app.modules.parametrage.schemas import TauxChangeCreate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class TauxChangeService(BaseParametrageService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = TauxChangeRepository(db)
        self._devise_repo = DeviseRepository(db)

    async def get_by_id(self, taux_id: int) -> TauxChange | None:
        return await self._repo.find_by_id(taux_id)

    async def get_or_404(self, taux_id: int) -> TauxChange:
        t = await self._repo.find_by_id(taux_id)
        if t is None:
            self._raise_not_found(Messages.TAUX_CHANGE_NOT_FOUND)
        return t

    async def get_taux_for_date(
        self,
        devise_from_id: int,
        devise_to_id: int,
        date_effet: date | None = None,
    ) -> TauxChange | None:
        return await self._repo.find_for_date(
            devise_from_id,
            devise_to_id,
            date_effet,
        )

    async def get_taux_changes(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        devise_from_id: int | None = None,
        devise_to_id: int | None = None,
    ) -> list[TauxChange]:
        return await self._repo.find_all(
            skip=skip,
            limit=limit,
            devise_from_id=devise_from_id,
            devise_to_id=devise_to_id,
        )

    async def create(self, data: TauxChangeCreate) -> TauxChange:
        if data.devise_from_id == data.devise_to_id:
            self._raise_bad_request(Messages.TAUX_CHANGE_SAME_DEVISE)
        if data.taux <= 0:
            self._raise_bad_request(Messages.TAUX_CHANGE_INVALID)
        if await self._devise_repo.find_by_id(data.devise_from_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        if await self._devise_repo.find_by_id(data.devise_to_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        t = TauxChange(
            devise_from_id=data.devise_from_id,
            devise_to_id=data.devise_to_id,
            taux=data.taux,
            date_effet=data.date_effet,
            source=data.source,
        )
        return await self._repo.add(t)

