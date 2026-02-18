# app/modules/paie/repositories/type_element_paie_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.paie.models import TypeElementPaie


class TypeElementPaieRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> TypeElementPaie | None:
        r = await self._db.execute(select(TypeElementPaie).where(TypeElementPaie.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_code(
        self, entreprise_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        q = select(TypeElementPaie.id).where(
            TypeElementPaie.entreprise_id == entreprise_id,
            TypeElementPaie.code == code,
        )
        if exclude_id is not None:
            q = q.where(TypeElementPaie.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        type_filter: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TypeElementPaie], int]:
        q = select(TypeElementPaie).where(TypeElementPaie.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(TypeElementPaie.actif.is_(True))
        if type_filter:
            q = q.where(TypeElementPaie.type == type_filter)
        count_q = select(func.count()).select_from(TypeElementPaie).where(
            TypeElementPaie.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(TypeElementPaie.actif.is_(True))
        if type_filter:
            count_q = count_q.where(TypeElementPaie.type == type_filter)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(TypeElementPaie.ordre_affichage, TypeElementPaie.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: TypeElementPaie) -> TypeElementPaie:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: TypeElementPaie) -> TypeElementPaie:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

