# app/modules/immobilisations/repositories/immobilisation_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.immobilisations.models import Immobilisation


class ImmobilisationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Immobilisation | None:
        r = await self._db.execute(select(Immobilisation).where(Immobilisation.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(self, entreprise_id: int, code: str, exclude_id: int | None = None) -> bool:
        q = select(Immobilisation.id).where(
            Immobilisation.entreprise_id == entreprise_id,
            Immobilisation.code == code,
        )
        if exclude_id is not None:
            q = q.where(Immobilisation.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        categorie_id: int | None = None,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Immobilisation], int]:
        q = select(Immobilisation).where(Immobilisation.entreprise_id == entreprise_id)
        if categorie_id is not None:
            q = q.where(Immobilisation.categorie_id == categorie_id)
        if actif_only:
            q = q.where(Immobilisation.actif.is_(True))
        count_q = select(func.count()).select_from(Immobilisation).where(Immobilisation.entreprise_id == entreprise_id)
        if categorie_id is not None:
            count_q = count_q.where(Immobilisation.categorie_id == categorie_id)
        if actif_only:
            count_q = count_q.where(Immobilisation.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Immobilisation.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Immobilisation) -> Immobilisation:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Immobilisation) -> Immobilisation:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
