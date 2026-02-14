# app/modules/catalogue/repositories/variante_repository.py
# -----------------------------------------------------------------------------
# Repository VarianteProduit (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import VarianteProduit


class VarianteProduitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> VarianteProduit | None:
        r = await self._db.execute(select(VarianteProduit).where(VarianteProduit.id == id))
        return r.scalar_one_or_none()

    async def find_by_produit(
        self,
        produit_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> tuple[list[VarianteProduit], int]:
        q = select(VarianteProduit).where(VarianteProduit.produit_id == produit_id)
        count_q = select(func.count()).select_from(VarianteProduit).where(VarianteProduit.produit_id == produit_id)
        if actif_only:
            q = q.where(VarianteProduit.actif.is_(True))
            count_q = count_q.where(VarianteProduit.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(VarianteProduit.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_produit_and_code(
        self,
        produit_id: int,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = (
            select(VarianteProduit.id)
            .where(
                VarianteProduit.produit_id == produit_id,
                VarianteProduit.code == code,
            )
            .limit(1)
        )
        if exclude_id is not None:
            q = q.where(VarianteProduit.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: VarianteProduit) -> VarianteProduit:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: VarianteProduit) -> VarianteProduit:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: VarianteProduit) -> None:
        await self._db.delete(entity)
        await self._db.flush()
