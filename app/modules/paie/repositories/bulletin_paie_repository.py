# app/modules/paie/repositories/bulletin_paie_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.paie.models import BulletinPaie


class BulletinPaieRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> BulletinPaie | None:
        r = await self._db.execute(select(BulletinPaie).where(BulletinPaie.id == id))
        return r.scalar_one_or_none()

    async def find_by_id_with_lignes(self, id: int) -> BulletinPaie | None:
        r = await self._db.execute(
            select(BulletinPaie).where(BulletinPaie.id == id).options(selectinload(BulletinPaie.lignes))
        )
        return r.scalar_one_or_none()

    async def find_by_employe_periode(
        self, entreprise_id: int, employe_id: int, periode_paie_id: int, exclude_id: int | None = None
    ) -> BulletinPaie | None:
        q = select(BulletinPaie).where(
            BulletinPaie.entreprise_id == entreprise_id,
            BulletinPaie.employe_id == employe_id,
            BulletinPaie.periode_paie_id == periode_paie_id,
        )
        if exclude_id is not None:
            q = q.where(BulletinPaie.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        periode_paie_id: int | None = None,
        statut: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[BulletinPaie], int]:
        q = select(BulletinPaie).where(BulletinPaie.entreprise_id == entreprise_id)
        if employe_id is not None:
            q = q.where(BulletinPaie.employe_id == employe_id)
        if periode_paie_id is not None:
            q = q.where(BulletinPaie.periode_paie_id == periode_paie_id)
        if statut is not None:
            q = q.where(BulletinPaie.statut == statut)
        count_q = select(func.count()).select_from(BulletinPaie).where(
            BulletinPaie.entreprise_id == entreprise_id
        )
        if employe_id is not None:
            count_q = count_q.where(BulletinPaie.employe_id == employe_id)
        if periode_paie_id is not None:
            count_q = count_q.where(BulletinPaie.periode_paie_id == periode_paie_id)
        if statut is not None:
            count_q = count_q.where(BulletinPaie.statut == statut)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(BulletinPaie.periode_paie_id.desc(), BulletinPaie.employe_id).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: BulletinPaie) -> BulletinPaie:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: BulletinPaie) -> BulletinPaie:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
