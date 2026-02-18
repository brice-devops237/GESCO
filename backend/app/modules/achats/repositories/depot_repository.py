# app/modules/achats/repositories/depot_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import Depot


class DepotRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Depot | None:
        r = await self._db.execute(select(Depot).where(Depot.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self, *, entreprise_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Depot], int]:
        q = select(Depot).where(Depot.entreprise_id == entreprise_id)
        count_q = select(func.count()).select_from(Depot).where(Depot.entreprise_id == entreprise_id)
        total = (await self._db.execute(count_q)).scalar() or 0
        q = q.order_by(Depot.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_code(self, entreprise_id: int, code: str, exclude_id: int | None = None) -> bool:
        q = select(Depot.id).where(Depot.entreprise_id == entreprise_id, Depot.code == code)
        if exclude_id is not None:
            q = q.where(Depot.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Depot) -> Depot:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Depot) -> Depot:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

