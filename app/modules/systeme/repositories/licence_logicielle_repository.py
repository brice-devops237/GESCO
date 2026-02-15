# app/modules/systeme/repositories/licence_logicielle_repository.py
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.systeme.models import LicenceLogicielle


class LicenceLogicielleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> LicenceLogicielle | None:
        r = await self._db.execute(select(LicenceLogicielle).where(LicenceLogicielle.id == id))
        return r.scalar_one_or_none()

    async def find_by_entreprise_cle(
        self, entreprise_id: int, cle_licence: str, exclude_id: int | None = None
    ) -> LicenceLogicielle | None:
        q = select(LicenceLogicielle).where(
            LicenceLogicielle.entreprise_id == entreprise_id,
            LicenceLogicielle.cle_licence == cle_licence,
        )
        if exclude_id is not None:
            q = q.where(LicenceLogicielle.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none()

    async def find_licence_valide_entreprise(self, entreprise_id: int) -> LicenceLogicielle | None:
        """Retourne une licence active et encore valide (date_fin >= aujourd'hui) pour l'entreprise."""
        aujourd_hui = date.today()
        r = await self._db.execute(
            select(LicenceLogicielle).where(
                LicenceLogicielle.entreprise_id == entreprise_id,
                LicenceLogicielle.actif.is_(True),
                LicenceLogicielle.date_fin >= aujourd_hui,
            ).order_by(LicenceLogicielle.date_fin.desc()).limit(1)
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int | None = None,
        *,
        actif_only: bool = False,
        valide_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[LicenceLogicielle], int]:
        q = select(LicenceLogicielle)
        if entreprise_id is not None:
            q = q.where(LicenceLogicielle.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(LicenceLogicielle.actif.is_(True))
        if valide_only:
            q = q.where(LicenceLogicielle.date_fin >= date.today())
        count_q = select(func.count()).select_from(LicenceLogicielle)
        if entreprise_id is not None:
            count_q = count_q.where(LicenceLogicielle.entreprise_id == entreprise_id)
        if actif_only:
            count_q = count_q.where(LicenceLogicielle.actif.is_(True))
        if valide_only:
            count_q = count_q.where(LicenceLogicielle.date_fin >= date.today())
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(LicenceLogicielle.date_fin.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: LicenceLogicielle) -> LicenceLogicielle:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: LicenceLogicielle) -> LicenceLogicielle:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
