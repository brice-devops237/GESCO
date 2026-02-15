# app/modules/paie/repositories/periode_paie_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.paie.models import PeriodePaie


class PeriodePaieRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> PeriodePaie | None:
        r = await self._db.execute(select(PeriodePaie).where(PeriodePaie.id == id))
        return r.scalar_one_or_none()

    async def find_by_entreprise_annee_mois(
        self, entreprise_id: int, annee: int, mois: int
    ) -> PeriodePaie | None:
        r = await self._db.execute(
            select(PeriodePaie).where(
                PeriodePaie.entreprise_id == entreprise_id,
                PeriodePaie.annee == annee,
                PeriodePaie.mois == mois,
            )
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        cloturee: bool | None = None,
        skip: int = 0,
        limit: int = 24,
    ) -> tuple[list[PeriodePaie], int]:
        q = select(PeriodePaie).where(PeriodePaie.entreprise_id == entreprise_id)
        if cloturee is not None:
            q = q.where(PeriodePaie.cloturee.is_(cloturee))
        count_q = select(func.count()).select_from(PeriodePaie).where(
            PeriodePaie.entreprise_id == entreprise_id
        )
        if cloturee is not None:
            count_q = count_q.where(PeriodePaie.cloturee.is_(cloturee))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(PeriodePaie.annee.desc(), PeriodePaie.mois.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: PeriodePaie) -> PeriodePaie:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: PeriodePaie) -> PeriodePaie:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
