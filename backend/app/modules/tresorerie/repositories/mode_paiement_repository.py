# app/modules/tresorerie/repositories/mode_paiement_repository.py
# -----------------------------------------------------------------------------
# Repository ModePaiement (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tresorerie.models import ModePaiement


class ModePaiementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> ModePaiement | None:
        r = await self._db.execute(select(ModePaiement).where(ModePaiement.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(
        self, entreprise_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        q = select(ModePaiement.id).where(
            ModePaiement.entreprise_id == entreprise_id,
            ModePaiement.code == code,
        )
        if exclude_id is not None:
            q = q.where(ModePaiement.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[ModePaiement], int]:
        base = select(ModePaiement).where(ModePaiement.entreprise_id == entreprise_id)
        if actif_only:
            base = base.where(ModePaiement.actif.is_(True))
        count_q = select(func.count()).select_from(ModePaiement).where(ModePaiement.entreprise_id == entreprise_id)
        if actif_only:
            count_q = count_q.where(ModePaiement.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = base.order_by(ModePaiement.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: ModePaiement) -> ModePaiement:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: ModePaiement) -> ModePaiement:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

