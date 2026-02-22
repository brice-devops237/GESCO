# app/modules/parametrage/repositories/taux_change_repository.py
# -----------------------------------------------------------------------------
# Repository TauxChange (couche Infrastructure).
# -----------------------------------------------------------------------------

from datetime import date

from sqlalchemy import func, or_, select
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
        date_effet_min: date | None = None,
        date_effet_max: date | None = None,
    ) -> tuple[list[TauxChange], int]:
        q = select(TauxChange)
        count_q = select(func.count()).select_from(TauxChange)
        if devise_from_id is not None:
            q = q.where(TauxChange.devise_from_id == devise_from_id)
            count_q = count_q.where(TauxChange.devise_from_id == devise_from_id)
        if devise_to_id is not None:
            q = q.where(TauxChange.devise_to_id == devise_to_id)
            count_q = count_q.where(TauxChange.devise_to_id == devise_to_id)
        if date_effet_min is not None:
            q = q.where(TauxChange.date_effet >= date_effet_min)
            count_q = count_q.where(TauxChange.date_effet >= date_effet_min)
        if date_effet_max is not None:
            q = q.where(TauxChange.date_effet <= date_effet_max)
            count_q = count_q.where(TauxChange.date_effet <= date_effet_max)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(TauxChange.date_effet.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def get_stats(self) -> dict:
        """Statistiques globales : total de taux de change."""
        q = select(func.count()).select_from(TauxChange)
        total = (await self._db.execute(q)).scalar_one() or 0
        return {"total": int(total)}

    async def add(self, entity: TauxChange) -> TauxChange:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: TauxChange) -> TauxChange:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: TauxChange) -> None:
        await self._db.delete(entity)
        await self._db.flush()

    async def count_by_devise_id(self, devise_id: int) -> int:
        """Nombre de taux de change qui référencent cette devise (source ou cible)."""
        q = select(func.count()).select_from(TauxChange).where(
            or_(
                TauxChange.devise_from_id == devise_id,
                TauxChange.devise_to_id == devise_id,
            )
        )
        r = await self._db.execute(q)
        return r.scalar() or 0

