# app/modules/catalogue/repositories/unite_mesure_repository.py
# -----------------------------------------------------------------------------
# Repository UniteMesure (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import UniteMesure


class UniteMesureRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> UniteMesure | None:
        r = await self._db.execute(select(UniteMesure).where(UniteMesure.id == id))
        return r.scalar_one_or_none()

    async def find_by_code(self, code: str) -> UniteMesure | None:
        r = await self._db.execute(
            select(UniteMesure).where(UniteMesure.code == code.strip())
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> list[UniteMesure]:
        q = select(UniteMesure)
        if actif_only:
            q = q.where(UniteMesure.actif.is_(True))
        q = q.order_by(UniteMesure.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: UniteMesure) -> UniteMesure:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: UniteMesure) -> UniteMesure:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

