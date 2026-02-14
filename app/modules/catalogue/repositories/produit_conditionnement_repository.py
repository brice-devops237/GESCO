# app/modules/catalogue/repositories/produit_conditionnement_repository.py
# -----------------------------------------------------------------------------
# Repository ProduitConditionnement (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import ProduitConditionnement


class ProduitConditionnementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> ProduitConditionnement | None:
        r = await self._db.execute(
            select(ProduitConditionnement).where(ProduitConditionnement.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_produit(
        self,
        produit_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProduitConditionnement]:
        q = (
            select(ProduitConditionnement)
            .where(ProduitConditionnement.produit_id == produit_id)
            .offset(skip)
            .limit(limit)
        )
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def exists_by_produit_and_conditionnement(
        self,
        produit_id: int,
        conditionnement_id: int,
        exclude_id: int | None = None,
    ) -> bool:
        q = (
            select(ProduitConditionnement.id)
            .where(
                ProduitConditionnement.produit_id == produit_id,
                ProduitConditionnement.conditionnement_id == conditionnement_id,
            )
            .limit(1)
        )
        if exclude_id is not None:
            q = q.where(ProduitConditionnement.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: ProduitConditionnement) -> ProduitConditionnement:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: ProduitConditionnement) -> ProduitConditionnement:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: ProduitConditionnement) -> None:
        await self._db.delete(entity)
        await self._db.flush()
