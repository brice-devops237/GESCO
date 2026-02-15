# app/modules/rh/repositories/taux_commission_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import TauxCommission


class TauxCommissionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> TauxCommission | None:
        r = await self._db.execute(select(TauxCommission).where(TauxCommission.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(
        self, entreprise_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        q = select(TauxCommission.id).where(
            TauxCommission.entreprise_id == entreprise_id,
            TauxCommission.code == code,
        )
        if exclude_id is not None:
            q = q.where(TauxCommission.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[TauxCommission], int]:
        q = select(TauxCommission).where(TauxCommission.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(TauxCommission.actif.is_(True))
        count_q = select(func.count()).select_from(TauxCommission).where(
            TauxCommission.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(TauxCommission.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(TauxCommission.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: TauxCommission) -> TauxCommission:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: TauxCommission) -> TauxCommission:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
