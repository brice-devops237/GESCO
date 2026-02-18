# app/modules/parametrage/repositories/entreprise_repository.py
# -----------------------------------------------------------------------------
# Repository Entreprise (Clean Architecture : couche Infrastructure).
# Encapsule tout l'accès aux données pour l'agrégat Entreprise.
# -----------------------------------------------------------------------------

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Entreprise


class EntrepriseRepository:
    """Accès données pour les entreprises (table entreprises)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, entreprise_id: int) -> Entreprise | None:
        result = await self._db.execute(select(Entreprise).where(Entreprise.id == entreprise_id))
        return result.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Entreprise], int]:
        base = Entreprise.deleted_at.is_(None)
        q = select(Entreprise).where(base)
        count_q = select(func.count()).select_from(Entreprise).where(base)
        if actif_only:
            q = q.where(Entreprise.actif.is_(True))
            count_q = count_q.where(Entreprise.actif.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            f = or_(
                Entreprise.raison_sociale.ilike(term),
                Entreprise.code.ilike(term),
                Entreprise.niu.ilike(term),
            )
            q = q.where(f)
            count_q = count_q.where(f)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Entreprise.raison_sociale).offset(skip).limit(limit)
        result = await self._db.execute(q)
        return list(result.scalars().all()), total

    async def exists_by_code(self, code: str) -> bool:
        r = await self._db.execute(select(Entreprise.id).where(Entreprise.code == code).limit(1))
        return r.scalar_one_or_none() is not None

    async def exists_by_niu(self, niu: str, exclude_id: int | None = None) -> bool:
        q = select(Entreprise.id).where(Entreprise.niu == niu).limit(1)
        if exclude_id is not None:
            q = q.where(Entreprise.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Entreprise) -> Entreprise:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Entreprise) -> Entreprise:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

