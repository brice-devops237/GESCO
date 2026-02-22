# app/modules/partenaires/repositories/type_tiers_repository.py
# -----------------------------------------------------------------------------
# Repository TypeTiers (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partenaires.models import TypeTiers


class TypeTiersRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> TypeTiers | None:
        r = await self._db.execute(select(TypeTiers).where(TypeTiers.id == id))
        return r.scalar_one_or_none()

    async def find_by_code(self, code: str) -> TypeTiers | None:
        r = await self._db.execute(
            select(TypeTiers).where(TypeTiers.code == code.strip().upper())
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TypeTiers]:
        q = select(TypeTiers).order_by(TypeTiers.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: TypeTiers) -> TypeTiers:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: TypeTiers) -> TypeTiers:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: TypeTiers) -> None:
        await self._db.delete(entity)
        await self._db.flush()

