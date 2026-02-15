# app/modules/rh/repositories/objectif_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.rh.models import Objectif


class ObjectifRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Objectif | None:
        r = await self._db.execute(select(Objectif).where(Objectif.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Objectif], int]:
        q = select(Objectif).where(Objectif.entreprise_id == entreprise_id)
        if employe_id is not None:
            q = q.where(Objectif.employe_id == employe_id)
        count_q = select(func.count()).select_from(Objectif).where(
            Objectif.entreprise_id == entreprise_id
        )
        if employe_id is not None:
            count_q = count_q.where(Objectif.employe_id == employe_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Objectif.date_debut.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Objectif) -> Objectif:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Objectif) -> Objectif:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
