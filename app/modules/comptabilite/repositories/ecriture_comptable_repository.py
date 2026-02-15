# app/modules/comptabilite/repositories/ecriture_comptable_repository.py
# -----------------------------------------------------------------------------
# Repository EcritureComptable (couche Infrastructure).
# -----------------------------------------------------------------------------
from datetime import date
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.comptabilite.models import EcritureComptable


class EcritureComptableRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> EcritureComptable | None:
        r = await self._db.execute(select(EcritureComptable).where(EcritureComptable.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        journal_id: int | None = None,
        periode_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[EcritureComptable], int]:
        q = select(EcritureComptable)
        if entreprise_id is not None:
            q = q.where(EcritureComptable.entreprise_id == entreprise_id)
        if journal_id is not None:
            q = q.where(EcritureComptable.journal_id == journal_id)
        if periode_id is not None:
            q = q.where(EcritureComptable.periode_id == periode_id)
        if date_from is not None:
            q = q.where(EcritureComptable.date_ecriture >= date_from)
        if date_to is not None:
            q = q.where(EcritureComptable.date_ecriture <= date_to)
        count_q = select(func.count()).select_from(EcritureComptable)
        if entreprise_id is not None:
            count_q = count_q.where(EcritureComptable.entreprise_id == entreprise_id)
        if journal_id is not None:
            count_q = count_q.where(EcritureComptable.journal_id == journal_id)
        if periode_id is not None:
            count_q = count_q.where(EcritureComptable.periode_id == periode_id)
        if date_from is not None:
            count_q = count_q.where(EcritureComptable.date_ecriture >= date_from)
        if date_to is not None:
            count_q = count_q.where(EcritureComptable.date_ecriture <= date_to)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(EcritureComptable.date_ecriture.desc(), EcritureComptable.id.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: EcritureComptable) -> EcritureComptable:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
