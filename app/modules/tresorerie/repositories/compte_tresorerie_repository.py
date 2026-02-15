# app/modules/tresorerie/repositories/compte_tresorerie_repository.py
# -----------------------------------------------------------------------------
# Repository CompteTresorerie (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.tresorerie.models import CompteTresorerie


class CompteTresorerieRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> CompteTresorerie | None:
        r = await self._db.execute(select(CompteTresorerie).where(CompteTresorerie.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        type_compte: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[CompteTresorerie], int]:
        q = select(CompteTresorerie).where(CompteTresorerie.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(CompteTresorerie.actif.is_(True))
        if type_compte is not None:
            q = q.where(CompteTresorerie.type_compte == type_compte)
        count_q = select(func.count()).select_from(CompteTresorerie).where(
            CompteTresorerie.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(CompteTresorerie.actif.is_(True))
        if type_compte is not None:
            count_q = count_q.where(CompteTresorerie.type_compte == type_compte)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(CompteTresorerie.libelle).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: CompteTresorerie) -> CompteTresorerie:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: CompteTresorerie) -> CompteTresorerie:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
