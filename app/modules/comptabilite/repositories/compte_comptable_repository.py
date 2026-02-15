# app/modules/comptabilite/repositories/compte_comptable_repository.py
# -----------------------------------------------------------------------------
# Repository CompteComptable (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.comptabilite.models import CompteComptable


class CompteComptableRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> CompteComptable | None:
        r = await self._db.execute(select(CompteComptable).where(CompteComptable.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_numero(
        self, entreprise_id: int, numero: str, exclude_id: int | None = None
    ) -> bool:
        q = select(CompteComptable.id).where(
            CompteComptable.entreprise_id == entreprise_id,
            CompteComptable.numero == numero,
        )
        if exclude_id is not None:
            q = q.where(CompteComptable.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[CompteComptable], int]:
        q = select(CompteComptable).where(CompteComptable.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(CompteComptable.actif.is_(True))
        count_q = select(func.count()).select_from(CompteComptable).where(
            CompteComptable.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(CompteComptable.actif.is_(True))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(CompteComptable.numero).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: CompteComptable) -> CompteComptable:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: CompteComptable) -> CompteComptable:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
