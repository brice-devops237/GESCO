# app/modules/rh/repositories/avance_repository.py
# -----------------------------------------------------------------------------
# Repository Avance (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import Avance


class AvanceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Avance | None:
        r = await self._db.execute(select(Avance).where(Avance.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        rembourse: bool | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Avance], int]:
        q = select(Avance).where(Avance.entreprise_id == entreprise_id)
        if employe_id is not None:
            q = q.where(Avance.employe_id == employe_id)
        if rembourse is not None:
            q = q.where(Avance.rembourse.is_(rembourse))
        count_q = select(func.count()).select_from(Avance).where(
            Avance.entreprise_id == entreprise_id
        )
        if employe_id is not None:
            count_q = count_q.where(Avance.employe_id == employe_id)
        if rembourse is not None:
            count_q = count_q.where(Avance.rembourse.is_(rembourse))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Avance.date_avance.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Avance) -> Avance:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Avance) -> Avance:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
