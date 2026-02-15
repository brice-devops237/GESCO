# app/modules/comptabilite/repositories/journal_comptable_repository.py
# -----------------------------------------------------------------------------
# Repository JournalComptable (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comptabilite.models import JournalComptable


class JournalComptableRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> JournalComptable | None:
        r = await self._db.execute(select(JournalComptable).where(JournalComptable.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(
        self, entreprise_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        q = select(JournalComptable.id).where(
            JournalComptable.entreprise_id == entreprise_id,
            JournalComptable.code == code,
        )
        if exclude_id is not None:
            q = q.where(JournalComptable.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[JournalComptable], int]:
        q = select(JournalComptable).where(JournalComptable.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(JournalComptable.actif.is_(True))
        count_q = select(func.count()).select_from(JournalComptable).where(
            JournalComptable.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(JournalComptable.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(JournalComptable.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: JournalComptable) -> JournalComptable:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: JournalComptable) -> JournalComptable:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
