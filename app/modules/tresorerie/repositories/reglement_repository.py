# app/modules/tresorerie/repositories/reglement_repository.py
# -----------------------------------------------------------------------------
# Repository Reglement (couche Infrastructure).
# -----------------------------------------------------------------------------
from datetime import date
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.tresorerie.models import Reglement


class ReglementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Reglement | None:
        r = await self._db.execute(select(Reglement).where(Reglement.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        type_reglement: str | None = None,
        tiers_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Reglement], int]:
        q = select(Reglement)
        if entreprise_id is not None:
            q = q.where(Reglement.entreprise_id == entreprise_id)
        if type_reglement is not None:
            q = q.where(Reglement.type_reglement == type_reglement)
        if tiers_id is not None:
            q = q.where(Reglement.tiers_id == tiers_id)
        if date_from is not None:
            q = q.where(Reglement.date_reglement >= date_from)
        if date_to is not None:
            q = q.where(Reglement.date_reglement <= date_to)
        count_q = select(func.count()).select_from(Reglement)
        if entreprise_id is not None:
            count_q = count_q.where(Reglement.entreprise_id == entreprise_id)
        if type_reglement is not None:
            count_q = count_q.where(Reglement.type_reglement == type_reglement)
        if tiers_id is not None:
            count_q = count_q.where(Reglement.tiers_id == tiers_id)
        if date_from is not None:
            count_q = count_q.where(Reglement.date_reglement >= date_from)
        if date_to is not None:
            count_q = count_q.where(Reglement.date_reglement <= date_to)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Reglement.date_reglement.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Reglement) -> Reglement:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
