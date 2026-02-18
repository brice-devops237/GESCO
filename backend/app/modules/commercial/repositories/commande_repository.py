# app/modules/commercial/repositories/commande_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import Commande


class CommandeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Commande | None:
        r = await self._db.execute(select(Commande).where(Commande.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        client_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Commande], int]:
        q = select(Commande)
        count_q = select(func.count()).select_from(Commande)
        if entreprise_id is not None:
            q = q.where(Commande.entreprise_id == entreprise_id)
            count_q = count_q.where(Commande.entreprise_id == entreprise_id)
        if client_id is not None:
            q = q.where(Commande.client_id == client_id)
            count_q = count_q.where(Commande.client_id == client_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Commande.date_commande.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_numero(
        self, entreprise_id: int, numero: str, exclude_id: int | None = None
    ) -> bool:
        q = select(Commande.id).where(Commande.entreprise_id == entreprise_id, Commande.numero == numero).limit(1)
        if exclude_id is not None:
            q = q.where(Commande.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Commande) -> Commande:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Commande) -> Commande:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

