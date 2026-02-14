# app/modules/parametrage/repositories/devise_repository.py
# -----------------------------------------------------------------------------
# Repository Devise (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Devise


class DeviseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, devise_id: int) -> Devise | None:
        r = await self._db.execute(select(Devise).where(Devise.id == devise_id))
        return r.scalar_one_or_none()

    async def find_by_code(self, code: str) -> Devise | None:
        r = await self._db.execute(select(Devise).where(Devise.code == code.strip().upper()))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> list[Devise]:
        q = select(Devise)
        if actif_only:
            q = q.where(Devise.actif.is_(True))
        q = q.order_by(Devise.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: Devise) -> Devise:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Devise) -> Devise:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
