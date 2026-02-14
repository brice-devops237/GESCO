# app/modules/catalogue/repositories/prix_repository.py
# -----------------------------------------------------------------------------
# Repository PrixProduit (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import PrixProduit


class PrixProduitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> PrixProduit | None:
        r = await self._db.execute(select(PrixProduit).where(PrixProduit.id == id))
        return r.scalar_one_or_none()

    async def find_by_produit(
        self,
        produit_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PrixProduit], int]:
        q = select(PrixProduit).where(PrixProduit.produit_id == produit_id)
        count_q = select(func.count()).select_from(PrixProduit).where(PrixProduit.produit_id == produit_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(PrixProduit.date_debut.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PrixProduit], int]:
        q = select(PrixProduit)
        count_q = select(func.count()).select_from(PrixProduit)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(PrixProduit.produit_id, PrixProduit.date_debut.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: PrixProduit) -> PrixProduit:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: PrixProduit) -> PrixProduit:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: PrixProduit) -> None:
        await self._db.delete(entity)
        await self._db.flush()
