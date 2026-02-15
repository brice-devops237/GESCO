# app/modules/stock/repositories/stock_repository.py
# -----------------------------------------------------------------------------
# Repository Stock (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.stock.models import Stock


class StockRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Stock | None:
        r = await self._db.execute(select(Stock).where(Stock.id == id))
        return r.scalar_one_or_none()

    async def find_by_depot_produit_variante(
        self, depot_id: int, produit_id: int, variante_id: int | None
    ) -> Stock | None:
        q = select(Stock).where(
            Stock.depot_id == depot_id,
            Stock.produit_id == produit_id,
            (Stock.variante_id == variante_id) if variante_id is not None else Stock.variante_id.is_(None),
        )
        r = await self._db.execute(q)
        return r.scalar_one_or_none()

    async def find_by_depot(
        self, depot_id: int, *, skip: int = 0, limit: int = 200
    ) -> tuple[list[Stock], int]:
        base = select(Stock).where(Stock.depot_id == depot_id)
        total = (await self._db.execute(select(func.count()).select_from(Stock).where(Stock.depot_id == depot_id))).scalar_one() or 0
        q = base.offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def find_by_produit(
        self, produit_id: int, *, skip: int = 0, limit: int = 200
    ) -> tuple[list[Stock], int]:
        base = select(Stock).where(Stock.produit_id == produit_id)
        total = (await self._db.execute(select(func.count()).select_from(Stock).where(Stock.produit_id == produit_id))).scalar_one() or 0
        q = base.offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Stock) -> Stock:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Stock) -> Stock:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
