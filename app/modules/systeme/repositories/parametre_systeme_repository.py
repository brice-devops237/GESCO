# app/modules/systeme/repositories/parametre_systeme_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.systeme.models import ParametreSysteme


class ParametreSystemeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> ParametreSysteme | None:
        r = await self._db.execute(select(ParametreSysteme).where(ParametreSysteme.id == id))
        return r.scalar_one_or_none()

    async def find_by_entreprise_categorie_cle(
        self, entreprise_id: int, categorie: str, cle: str, exclude_id: int | None = None
    ) -> ParametreSysteme | None:
        q = select(ParametreSysteme).where(
            ParametreSysteme.entreprise_id == entreprise_id,
            ParametreSysteme.categorie == categorie,
            ParametreSysteme.cle == cle,
        )
        if exclude_id is not None:
            q = q.where(ParametreSysteme.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none()

    async def exists_by_entreprise_categorie_cle(
        self, entreprise_id: int, categorie: str, cle: str, exclude_id: int | None = None
    ) -> bool:
        return await self.find_by_entreprise_categorie_cle(
            entreprise_id, categorie, cle, exclude_id
        ) is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        categorie: str | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[ParametreSysteme], int]:
        q = select(ParametreSysteme).where(ParametreSysteme.entreprise_id == entreprise_id)
        if categorie is not None:
            q = q.where(ParametreSysteme.categorie == categorie)
        count_q = select(func.count()).select_from(ParametreSysteme).where(
            ParametreSysteme.entreprise_id == entreprise_id
        )
        if categorie is not None:
            count_q = count_q.where(ParametreSysteme.categorie == categorie)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(ParametreSysteme.categorie, ParametreSysteme.cle).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: ParametreSysteme) -> ParametreSysteme:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: ParametreSysteme) -> ParametreSysteme:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
