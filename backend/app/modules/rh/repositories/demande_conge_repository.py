# app/modules/rh/repositories/demande_conge_repository.py
# -----------------------------------------------------------------------------
# Repository DemandeConge (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import DemandeConge


class DemandeCongeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> DemandeConge | None:
        r = await self._db.execute(select(DemandeConge).where(DemandeConge.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        statut: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[DemandeConge], int]:
        q = select(DemandeConge).where(DemandeConge.entreprise_id == entreprise_id)
        if employe_id is not None:
            q = q.where(DemandeConge.employe_id == employe_id)
        if statut is not None:
            q = q.where(DemandeConge.statut == statut)
        count_q = select(func.count()).select_from(DemandeConge).where(
            DemandeConge.entreprise_id == entreprise_id
        )
        if employe_id is not None:
            count_q = count_q.where(DemandeConge.employe_id == employe_id)
        if statut is not None:
            count_q = count_q.where(DemandeConge.statut == statut)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(DemandeConge.date_debut.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: DemandeConge) -> DemandeConge:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: DemandeConge) -> DemandeConge:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

