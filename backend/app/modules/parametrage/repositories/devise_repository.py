# app/modules/parametrage/repositories/devise_repository.py
# -----------------------------------------------------------------------------
# Repository Devise (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Devise


class DeviseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, devise_id: int) -> Devise | None:
        r = await self._db.execute(select(Devise).where(Devise.id == devise_id))
        return r.scalar_one_or_none()

    async def find_by_code(self, code: str) -> Devise | None:
        r = await self._db.execute(select(Devise).where(Devise.code == code.strip().upper()))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        inactif_only: bool = False,
        search: str | None = None,
        decimales: int | None = None,
    ) -> tuple[list[Devise], int]:
        base = select(Devise)
        count_q = select(func.count()).select_from(Devise)
        if actif_only:
            base = base.where(Devise.actif.is_(True))
            count_q = count_q.where(Devise.actif.is_(True))
        elif inactif_only:
            base = base.where(Devise.actif.is_(False))
            count_q = count_q.where(Devise.actif.is_(False))
        if search and search.strip():
            term = f"%{search.strip()}%"
            cond = or_(
                Devise.code.ilike(term),
                Devise.libelle.ilike(term),
                Devise.symbole.ilike(term),
            )
            base = base.where(cond)
            count_q = count_q.where(cond)
        if decimales is not None:
            base = base.where(Devise.decimales == decimales)
            count_q = count_q.where(Devise.decimales == decimales)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        base = base.order_by(Devise.code).offset(skip).limit(limit)
        r = await self._db.execute(base)
        return list(r.scalars().all()), total

    async def get_stats(self) -> dict:
        """Statistiques globales sur les devises."""
        total_q = select(func.count()).select_from(Devise)
        total = (await self._db.execute(total_q)).scalar_one() or 0
        actives_q = select(func.count()).select_from(Devise).where(Devise.actif.is_(True))
        actives = (await self._db.execute(actives_q)).scalar_one() or 0
        total, actives = int(total), int(actives)
        return {"total": total, "actives": actives, "inactives": total - actives}

    async def add(self, entity: Devise) -> Devise:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Devise) -> Devise:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: Devise) -> None:
        await self._db.delete(entity)
        await self._db.flush()

