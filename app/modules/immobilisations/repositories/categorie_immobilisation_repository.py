# app/modules/immobilisations/repositories/categorie_immobilisation_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.immobilisations.models import CategorieImmobilisation


class CategorieImmobilisationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> CategorieImmobilisation | None:
        r = await self._db.execute(select(CategorieImmobilisation).where(CategorieImmobilisation.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(self, entreprise_id: int, code: str, exclude_id: int | None = None) -> bool:
        q = select(CategorieImmobilisation.id).where(
            CategorieImmobilisation.entreprise_id == entreprise_id,
            CategorieImmobilisation.code == code,
        )
        if exclude_id is not None:
            q = q.where(CategorieImmobilisation.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(self, entreprise_id: int, skip: int = 0, limit: int = 100) -> tuple[list[CategorieImmobilisation], int]:
        q = select(CategorieImmobilisation).where(CategorieImmobilisation.entreprise_id == entreprise_id)
        total = (await self._db.execute(select(func.count()).select_from(CategorieImmobilisation).where(CategorieImmobilisation.entreprise_id == entreprise_id))).scalar_one() or 0
        q = q.order_by(CategorieImmobilisation.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: CategorieImmobilisation) -> CategorieImmobilisation:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: CategorieImmobilisation) -> CategorieImmobilisation:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
