# app/modules/catalogue/repositories/conditionnement_repository.py
# -----------------------------------------------------------------------------
# Repository Conditionnement (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import Conditionnement


class ConditionnementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Conditionnement | None:
        r = await self._db.execute(select(Conditionnement).where(Conditionnement.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Conditionnement], int]:
        q = select(Conditionnement)
        count_q = select(func.count()).select_from(Conditionnement)
        if entreprise_id is not None:
            q = q.where(Conditionnement.entreprise_id == entreprise_id)
            count_q = count_q.where(Conditionnement.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(Conditionnement.actif.is_(True))
            count_q = count_q.where(Conditionnement.actif.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            f = or_(
                Conditionnement.code.ilike(term),
                Conditionnement.libelle.ilike(term),
            )
            q = q.where(f)
            count_q = count_q.where(f)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Conditionnement.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_code(
        self,
        entreprise_id: int,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = (
            select(Conditionnement.id)
            .where(
                Conditionnement.entreprise_id == entreprise_id,
                Conditionnement.code == code,
            )
            .limit(1)
        )
        if exclude_id is not None:
            q = q.where(Conditionnement.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Conditionnement) -> Conditionnement:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Conditionnement) -> Conditionnement:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: Conditionnement) -> None:
        await self._db.delete(entity)
        await self._db.flush()

