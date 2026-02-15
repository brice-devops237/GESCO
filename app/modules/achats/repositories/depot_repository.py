# app/modules/achats/repositories/depot_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import Depot


class DepotRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Depot | None:
        r = await self._db.execute(select(Depot).where(Depot.id == id))
        return r.scalar_one_or_none()
