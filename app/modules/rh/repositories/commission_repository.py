# app/modules/rh/repositories/commission_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.rh.models import Commission


class CommissionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Commission | None:
        r = await self._db.execute(select(Commission).where(Commission.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        payee: bool | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Commission], int]:
        q = select(Commission).where(Commission.entreprise_id == entreprise_id)
        if employe_id is not None:
            q = q.where(Commission.employe_id == employe_id)
        if payee is not None:
            q = q.where(Commission.payee.is_(payee))
        count_q = select(func.count()).select_from(Commission).where(
            Commission.entreprise_id == entreprise_id
        )
        if employe_id is not None:
            count_q = count_q.where(Commission.employe_id == employe_id)
        if payee is not None:
            count_q = count_q.where(Commission.payee.is_(payee))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Commission.date_fin.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Commission) -> Commission:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Commission) -> Commission:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
