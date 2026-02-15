# app/modules/comptabilite/repositories/periode_comptable_repository.py
# -----------------------------------------------------------------------------
# Repository PeriodeComptable (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.comptabilite.models import PeriodeComptable


class PeriodeComptableRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> PeriodeComptable | None:
        r = await self._db.execute(select(PeriodeComptable).where(PeriodeComptable.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PeriodeComptable], int]:
        q = select(PeriodeComptable).where(PeriodeComptable.entreprise_id == entreprise_id)
        count_q = select(func.count()).select_from(PeriodeComptable).where(
            PeriodeComptable.entreprise_id == entreprise_id
        )
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(PeriodeComptable.date_debut.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: PeriodeComptable) -> PeriodeComptable:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: PeriodeComptable) -> PeriodeComptable:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
