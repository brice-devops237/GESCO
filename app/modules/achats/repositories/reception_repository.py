# app/modules/achats/repositories/reception_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.achats.models import Reception


class ReceptionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Reception | None:
        r = await self._db.execute(select(Reception).where(Reception.id == id))
        return r.scalar_one_or_none()

    async def find_by_commande(
        self, commande_fournisseur_id: int, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[Reception], int]:
        q = select(Reception).where(Reception.commande_fournisseur_id == commande_fournisseur_id)
        count_q = select(func.count()).select_from(Reception).where(
            Reception.commande_fournisseur_id == commande_fournisseur_id
        )
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Reception.date_reception.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Reception) -> Reception:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Reception) -> Reception:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
