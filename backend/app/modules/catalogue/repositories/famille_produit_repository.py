# app/modules/catalogue/repositories/famille_produit_repository.py
# -----------------------------------------------------------------------------
# Repository FamilleProduit (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import FamilleProduit


class FamilleProduitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> FamilleProduit | None:
        r = await self._db.execute(
            select(FamilleProduit).where(
                FamilleProduit.id == id,
                FamilleProduit.deleted_at.is_(None),
            )
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[FamilleProduit], int]:
        base = FamilleProduit.deleted_at.is_(None)
        q = select(FamilleProduit).where(base)
        count_q = select(func.count()).select_from(FamilleProduit).where(base)
        if entreprise_id is not None:
            q = q.where(FamilleProduit.entreprise_id == entreprise_id)
            count_q = count_q.where(FamilleProduit.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(FamilleProduit.actif.is_(True))
            count_q = count_q.where(FamilleProduit.actif.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            f = or_(
                FamilleProduit.code.ilike(term),
                FamilleProduit.libelle.ilike(term),
            )
            q = q.where(f)
            count_q = count_q.where(f)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(FamilleProduit.ordre_affichage, FamilleProduit.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_code(
        self,
        entreprise_id: int,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = (
            select(FamilleProduit.id)
            .where(
                FamilleProduit.entreprise_id == entreprise_id,
                FamilleProduit.code == code,
                FamilleProduit.deleted_at.is_(None),
            )
            .limit(1)
        )
        if exclude_id is not None:
            q = q.where(FamilleProduit.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: FamilleProduit) -> FamilleProduit:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: FamilleProduit) -> FamilleProduit:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

