# app/modules/rh/repositories/solde_conge_repository.py
# -----------------------------------------------------------------------------
# Repository SoldeConge (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import SoldeConge


class SoldeCongeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> SoldeConge | None:
        r = await self._db.execute(select(SoldeConge).where(SoldeConge.id == id))
        return r.scalar_one_or_none()

    async def find_by_employe_type_annee(
        self, entreprise_id: int, employe_id: int, type_conge_id: int, annee: int
    ) -> SoldeConge | None:
        r = await self._db.execute(
            select(SoldeConge).where(
                SoldeConge.entreprise_id == entreprise_id,
                SoldeConge.employe_id == employe_id,
                SoldeConge.type_conge_id == type_conge_id,
                SoldeConge.annee == annee,
            )
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        annee: int | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[SoldeConge], int]:
        q = select(SoldeConge).where(SoldeConge.entreprise_id == entreprise_id)
        if employe_id is not None:
            q = q.where(SoldeConge.employe_id == employe_id)
        if annee is not None:
            q = q.where(SoldeConge.annee == annee)
        count_q = select(func.count()).select_from(SoldeConge).where(
            SoldeConge.entreprise_id == entreprise_id
        )
        if employe_id is not None:
            count_q = count_q.where(SoldeConge.employe_id == employe_id)
        if annee is not None:
            count_q = count_q.where(SoldeConge.annee == annee)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(SoldeConge.employe_id, SoldeConge.type_conge_id, SoldeConge.annee).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: SoldeConge) -> SoldeConge:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: SoldeConge) -> SoldeConge:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

