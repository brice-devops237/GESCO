# app/modules/parametrage/repositories/point_vente_repository.py
# -----------------------------------------------------------------------------
# Repository PointDeVente (couche Infrastructure).
# -----------------------------------------------------------------------------

from datetime import datetime

from sqlalchemy import func, or_, select
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
        inactif_only: bool = False,
        search: str | None = None,
        type_filter: str | None = None,
    ) -> tuple[list[PointDeVente], int]:
        base = select(PointDeVente).where(
            PointDeVente.entreprise_id == entreprise_id,
            PointDeVente.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(PointDeVente).where(
            PointDeVente.entreprise_id == entreprise_id,
            PointDeVente.deleted_at.is_(None),
        )
        if actif_only:
            base = base.where(PointDeVente.actif.is_(True))
            count_q = count_q.where(PointDeVente.actif.is_(True))
        elif inactif_only:
            base = base.where(PointDeVente.actif.is_(False))
            count_q = count_q.where(PointDeVente.actif.is_(False))
        if search and search.strip():
            term = f"%{search.strip()}%"
            cond = or_(
                PointDeVente.code.ilike(term),
                PointDeVente.libelle.ilike(term),
                PointDeVente.ville.ilike(term),
            )
            base = base.where(cond)
            count_q = count_q.where(cond)
        if type_filter and type_filter.strip():
            base = base.where(PointDeVente.type == type_filter.strip())
            count_q = count_q.where(PointDeVente.type == type_filter.strip())
        total = (await self._db.execute(count_q)).scalar_one() or 0
        base = base.order_by(PointDeVente.code).offset(skip).limit(limit)
        r = await self._db.execute(base)
        return list(r.scalars().all()), total

    async def get_stats(self, entreprise_id: int) -> dict:
        """Statistiques des points de vente d'une entreprise (hors supprimés)."""
        base_cond = (PointDeVente.entreprise_id == entreprise_id, PointDeVente.deleted_at.is_(None))
        total_q = select(func.count()).select_from(PointDeVente).where(*base_cond)
        total = (await self._db.execute(total_q)).scalar_one() or 0
        actives_q = select(func.count()).select_from(PointDeVente).where(*base_cond, PointDeVente.actif.is_(True))
        actives = (await self._db.execute(actives_q)).scalar_one() or 0
        type_q = (
            select(PointDeVente.type, func.count(PointDeVente.id))
            .where(PointDeVente.entreprise_id == entreprise_id, PointDeVente.deleted_at.is_(None))
            .group_by(PointDeVente.type)
        )
        type_rows = (await self._db.execute(type_q)).all()
        par_type = {str(t): c for t, c in type_rows if t}
        return {"total": total, "actifs": actives, "inactifs": total - actives, "par_type": par_type}

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

    async def soft_delete(self, entity: PointDeVente) -> None:
        entity.deleted_at = datetime.utcnow()
        await self._db.flush()
        await self._db.refresh(entity)

