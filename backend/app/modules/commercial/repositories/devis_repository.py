# app/modules/commercial/repositories/devis_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import Devis


class DevisRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Devis | None:
        r = await self._db.execute(select(Devis).where(Devis.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        client_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Devis], int]:
        q = select(Devis)
        count_q = select(func.count()).select_from(Devis)
        if entreprise_id is not None:
            q = q.where(Devis.entreprise_id == entreprise_id)
            count_q = count_q.where(Devis.entreprise_id == entreprise_id)
        if client_id is not None:
            q = q.where(Devis.client_id == client_id)
            count_q = count_q.where(Devis.client_id == client_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Devis.date_devis.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_numero(
        self, entreprise_id: int, numero: str, exclude_id: int | None = None
    ) -> bool:
        q = select(Devis.id).where(Devis.entreprise_id == entreprise_id, Devis.numero == numero).limit(1)
        if exclude_id is not None:
            q = q.where(Devis.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Devis) -> Devis:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Devis) -> Devis:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

