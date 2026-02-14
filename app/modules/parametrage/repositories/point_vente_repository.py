# app/modules/parametrage/repositories/point_vente_repository.py
# -----------------------------------------------------------------------------
# Repository PointDeVente (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import PointDeVente


class PointVenteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, point_vente_id: int) -> PointDeVente | None:
        r = await self._db.execute(
            select(PointDeVente).where(PointDeVente.id == point_vente_id)
        )
        return r.scalar_one_or_none()

    async def find_by_entreprise(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> list[PointDeVente]:
        q = select(PointDeVente).where(
            PointDeVente.entreprise_id == entreprise_id,
            PointDeVente.deleted_at.is_(None),
        )
        if actif_only:
            q = q.where(PointDeVente.actif.is_(True))
        q = q.order_by(PointDeVente.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def exists_by_entreprise_and_code(
        self,
        entreprise_id: int,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = select(PointDeVente.id).where(
            PointDeVente.entreprise_id == entreprise_id,
            PointDeVente.code == code,
        ).limit(1)
        if exclude_id is not None:
            q = q.where(PointDeVente.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: PointDeVente) -> PointDeVente:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: PointDeVente) -> PointDeVente:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
