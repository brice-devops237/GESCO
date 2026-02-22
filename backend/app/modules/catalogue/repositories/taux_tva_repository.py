# app/modules/catalogue/repositories/taux_tva_repository.py
# -----------------------------------------------------------------------------
# Repository TauxTva (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import TauxTva


class TauxTvaRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> TauxTva | None:
        r = await self._db.execute(select(TauxTva).where(TauxTva.id == id))
        return r.scalar_one_or_none()

    async def find_by_code(self, code: str) -> TauxTva | None:
        r = await self._db.execute(
            select(TauxTva).where(TauxTva.code == code.strip())
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> list[TauxTva]:
        q = select(TauxTva)
        if actif_only:
            q = q.where(TauxTva.actif.is_(True))
        q = q.order_by(TauxTva.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: TauxTva) -> TauxTva:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: TauxTva) -> TauxTva:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: TauxTva) -> None:
        await self._db.delete(entity)
        await self._db.flush()

