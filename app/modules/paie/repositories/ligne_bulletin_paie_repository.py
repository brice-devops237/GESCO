# app/modules/paie/repositories/ligne_bulletin_paie_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.paie.models import LigneBulletinPaie


class LigneBulletinPaieRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_bulletin(self, bulletin_paie_id: int) -> list[LigneBulletinPaie]:
        r = await self._db.execute(
            select(LigneBulletinPaie).where(LigneBulletinPaie.bulletin_paie_id == bulletin_paie_id).order_by(LigneBulletinPaie.ordre, LigneBulletinPaie.id)
        )
        return list(r.scalars().all())

    async def add(self, entity: LigneBulletinPaie) -> LigneBulletinPaie:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete_by_bulletin(self, bulletin_paie_id: int) -> None:
        from sqlalchemy import delete
        await self._db.execute(delete(LigneBulletinPaie).where(LigneBulletinPaie.bulletin_paie_id == bulletin_paie_id))
        await self._db.flush()
