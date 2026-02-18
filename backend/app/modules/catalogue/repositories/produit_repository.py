# app/modules/catalogue/repositories/produit_repository.py
# -----------------------------------------------------------------------------
# Repository Produit (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import Produit


class ProduitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Produit | None:
        r = await self._db.execute(
            select(Produit).where(
                Produit.id == id,
                Produit.deleted_at.is_(None),
            )
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        famille_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Produit], int]:
        base = Produit.deleted_at.is_(None)
        q = select(Produit).where(base)
        count_q = select(func.count()).select_from(Produit).where(base)
        if entreprise_id is not None:
            q = q.where(Produit.entreprise_id == entreprise_id)
            count_q = count_q.where(Produit.entreprise_id == entreprise_id)
        if famille_id is not None:
            q = q.where(Produit.famille_id == famille_id)
            count_q = count_q.where(Produit.famille_id == famille_id)
        if actif_only:
            q = q.where(Produit.actif.is_(True))
            count_q = count_q.where(Produit.actif.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            f = or_(
                Produit.code.ilike(term),
                Produit.libelle.ilike(term),
                Produit.code_barre.ilike(term),
            )
            q = q.where(f)
            count_q = count_q.where(f)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Produit.libelle).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_code(
        self,
        entreprise_id: int,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = (
            select(Produit.id)
            .where(
                Produit.entreprise_id == entreprise_id,
                Produit.code == code,
                Produit.deleted_at.is_(None),
            )
            .limit(1)
        )
        if exclude_id is not None:
            q = q.where(Produit.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Produit) -> Produit:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Produit) -> Produit:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

