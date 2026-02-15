# app/modules/stock/repositories/mouvement_stock_repository.py
# -----------------------------------------------------------------------------
# Repository MouvementStock (couche Infrastructure).
# -----------------------------------------------------------------------------
from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.stock.models import MouvementStock


class MouvementStockRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> MouvementStock | None:
        r = await self._db.execute(select(MouvementStock).where(MouvementStock.id == id))
        return r.scalar_one_or_none()

    def _base_query(
        self,
        depot_id: int | None = None,
        produit_id: int | None = None,
        type_mouvement: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        q = select(MouvementStock)
        if depot_id is not None:
            q = q.where(
                (MouvementStock.depot_id == depot_id) | (MouvementStock.depot_dest_id == depot_id)
            )
        if produit_id is not None:
            q = q.where(MouvementStock.produit_id == produit_id)
        if type_mouvement is not None:
            q = q.where(MouvementStock.type_mouvement == type_mouvement)
        if date_from is not None:
            q = q.where(MouvementStock.date_mouvement >= date_from)
        if date_to is not None:
            q = q.where(MouvementStock.date_mouvement <= date_to)
        return q

    async def find_all(
        self,
        *,
        depot_id: int | None = None,
        produit_id: int | None = None,
        type_mouvement: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[MouvementStock], int]:
        q = self._base_query(depot_id=depot_id, produit_id=produit_id, type_mouvement=type_mouvement, date_from=date_from, date_to=date_to)
        count_q = select(func.count()).select_from(MouvementStock)
        if depot_id is not None:
            count_q = count_q.where(
                (MouvementStock.depot_id == depot_id) | (MouvementStock.depot_dest_id == depot_id)
            )
        if produit_id is not None:
            count_q = count_q.where(MouvementStock.produit_id == produit_id)
        if type_mouvement is not None:
            count_q = count_q.where(MouvementStock.type_mouvement == type_mouvement)
        if date_from is not None:
            count_q = count_q.where(MouvementStock.date_mouvement >= date_from)
        if date_to is not None:
            count_q = count_q.where(MouvementStock.date_mouvement <= date_to)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(MouvementStock.date_mouvement.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: MouvementStock) -> MouvementStock:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
