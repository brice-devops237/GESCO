# app/modules/commercial/repositories/bon_livraison_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import BonLivraison


class BonLivraisonRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> BonLivraison | None:
        r = await self._db.execute(select(BonLivraison).where(BonLivraison.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        client_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BonLivraison], int]:
        q = select(BonLivraison)
        count_q = select(func.count()).select_from(BonLivraison)
        if entreprise_id is not None:
            q = q.where(BonLivraison.entreprise_id == entreprise_id)
            count_q = count_q.where(BonLivraison.entreprise_id == entreprise_id)
        if client_id is not None:
            q = q.where(BonLivraison.client_id == client_id)
            count_q = count_q.where(BonLivraison.client_id == client_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(BonLivraison.date_livraison.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_numero(
        self, entreprise_id: int, numero: str, exclude_id: int | None = None
    ) -> bool:
        q = select(BonLivraison.id).where(
            BonLivraison.entreprise_id == entreprise_id, BonLivraison.numero == numero
        ).limit(1)
        if exclude_id is not None:
            q = q.where(BonLivraison.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: BonLivraison) -> BonLivraison:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: BonLivraison) -> BonLivraison:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

