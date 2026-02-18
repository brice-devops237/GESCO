# app/modules/rh/repositories/poste_repository.py
# -----------------------------------------------------------------------------
# Repository Poste (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import Poste


class PosteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Poste | None:
        r = await self._db.execute(select(Poste).where(Poste.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(
        self, entreprise_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        q = select(Poste.id).where(
            Poste.entreprise_id == entreprise_id,
            Poste.code == code,
        )
        if exclude_id is not None:
            q = q.where(Poste.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        departement_id: int | None = None,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Poste], int]:
        q = select(Poste).where(Poste.entreprise_id == entreprise_id)
        if departement_id is not None:
            q = q.where(Poste.departement_id == departement_id)
        if actif_only:
            q = q.where(Poste.actif.is_(True))
        count_q = select(func.count()).select_from(Poste).where(
            Poste.entreprise_id == entreprise_id
        )
        if departement_id is not None:
            count_q = count_q.where(Poste.departement_id == departement_id)
        if actif_only:
            count_q = count_q.where(Poste.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Poste.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Poste) -> Poste:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Poste) -> Poste:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

