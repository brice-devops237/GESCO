# app/modules/rh/repositories/departement_repository.py
# -----------------------------------------------------------------------------
# Repository Département (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import Departement


class DepartementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Departement | None:
        r = await self._db.execute(select(Departement).where(Departement.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(
        self, entreprise_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        q = select(Departement.id).where(
            Departement.entreprise_id == entreprise_id,
            Departement.code == code,
        )
        if exclude_id is not None:
            q = q.where(Departement.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Departement], int]:
        q = select(Departement).where(Departement.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(Departement.actif.is_(True))
        count_q = select(func.count()).select_from(Departement).where(
            Departement.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(Departement.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Departement.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Departement) -> Departement:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Departement) -> Departement:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

