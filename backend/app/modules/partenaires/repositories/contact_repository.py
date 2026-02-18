# app/modules/partenaires/repositories/contact_repository.py
# -----------------------------------------------------------------------------
# Repository Contact (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partenaires.models import Contact


class ContactRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Contact | None:
        r = await self._db.execute(select(Contact).where(Contact.id == id))
        return r.scalar_one_or_none()

    async def find_by_tiers(
        self,
        tiers_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> tuple[list[Contact], int]:
        q = select(Contact).where(Contact.tiers_id == tiers_id)
        count_q = select(func.count()).select_from(Contact).where(Contact.tiers_id == tiers_id)
        if actif_only:
            q = q.where(Contact.actif.is_(True))
            count_q = count_q.where(Contact.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Contact.est_principal.desc(), Contact.nom).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Contact) -> Contact:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Contact) -> Contact:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: Contact) -> None:
        await self._db.delete(entity)
        await self._db.flush()

