# app/modules/parametrage/repositories/taux_change_repository.py
# -----------------------------------------------------------------------------
# Repository TauxChange (couche Infrastructure).
# -----------------------------------------------------------------------------

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import TauxChange


class TauxChangeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, taux_id: int) -> TauxChange | None:
        r = await self._db.execute(select(TauxChange).where(TauxChange.id == taux_id))
        return r.scalar_one_or_none()

    async def find_for_date(
        self,
        devise_from_id: int,
        devise_to_id: int,
        date_effet: date | None = None,
    ) -> TauxChange | None:
        d = date_effet or date.today()
        q = (
            select(TauxChange)
            .where(
                TauxChange.devise_from_id == devise_from_id,
                TauxChange.devise_to_id == devise_to_id,
                TauxChange.date_effet <= d,
            )
            .order_by(TauxChange.date_effet.desc())
            .limit(1)
        )
        r = await self._db.execute(q)
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        devise_from_id: int | None = None,
        devise_to_id: int | None = None,
    ) -> list[TauxChange]:
        q = select(TauxChange)
        if devise_from_id is not None:
            q = q.where(TauxChange.devise_from_id == devise_from_id)
        if devise_to_id is not None:
            q = q.where(TauxChange.devise_to_id == devise_to_id)
        q = q.order_by(TauxChange.date_effet.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: TauxChange) -> TauxChange:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

