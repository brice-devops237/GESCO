# app/modules/achats/repositories/facture_fournisseur_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import FactureFournisseur


class FactureFournisseurRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> FactureFournisseur | None:
        r = await self._db.execute(select(FactureFournisseur).where(FactureFournisseur.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        fournisseur_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FactureFournisseur], int]:
        q = select(FactureFournisseur)
        count_q = select(func.count()).select_from(FactureFournisseur)
        if entreprise_id is not None:
            q = q.where(FactureFournisseur.entreprise_id == entreprise_id)
            count_q = count_q.where(FactureFournisseur.entreprise_id == entreprise_id)
        if fournisseur_id is not None:
            q = q.where(FactureFournisseur.fournisseur_id == fournisseur_id)
            count_q = count_q.where(FactureFournisseur.fournisseur_id == fournisseur_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(FactureFournisseur.date_facture.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: FactureFournisseur) -> FactureFournisseur:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: FactureFournisseur) -> FactureFournisseur:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

