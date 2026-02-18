# app/modules/partenaires/repositories/tiers_repository.py
# -----------------------------------------------------------------------------
# Repository Tiers (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partenaires.models import Tiers


class TiersRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Tiers | None:
        r = await self._db.execute(
            select(Tiers).where(
                Tiers.id == id,
                Tiers.deleted_at.is_(None),
            )
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        type_tiers_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Tiers], int]:
        base = Tiers.deleted_at.is_(None)
        q = select(Tiers).where(base)
        count_q = select(func.count()).select_from(Tiers).where(base)
        if entreprise_id is not None:
            q = q.where(Tiers.entreprise_id == entreprise_id)
            count_q = count_q.where(Tiers.entreprise_id == entreprise_id)
        if type_tiers_id is not None:
            q = q.where(Tiers.type_tiers_id == type_tiers_id)
            count_q = count_q.where(Tiers.type_tiers_id == type_tiers_id)
        if actif_only:
            q = q.where(Tiers.actif.is_(True))
            count_q = count_q.where(Tiers.actif.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            f = or_(
                Tiers.code.ilike(term),
                Tiers.raison_sociale.ilike(term),
                Tiers.niu.ilike(term),
            )
            q = q.where(f)
            count_q = count_q.where(f)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Tiers.raison_sociale).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_code(
        self,
        entreprise_id: int,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = (
            select(Tiers.id)
            .where(
                Tiers.entreprise_id == entreprise_id,
                Tiers.code == code,
                Tiers.deleted_at.is_(None),
            )
            .limit(1)
        )
        if exclude_id is not None:
            q = q.where(Tiers.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Tiers) -> Tiers:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Tiers) -> Tiers:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

