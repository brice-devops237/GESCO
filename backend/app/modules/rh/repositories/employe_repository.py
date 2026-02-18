# app/modules/rh/repositories/employe_repository.py
# -----------------------------------------------------------------------------
# Repository Employe (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import Employe


class EmployeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Employe | None:
        r = await self._db.execute(select(Employe).where(Employe.id == id))
        return r.scalar_one_or_none()

    async def exists_by_entreprise_and_matricule(
        self, entreprise_id: int, matricule: str, exclude_id: int | None = None
    ) -> bool:
        q = select(Employe.id).where(
            Employe.entreprise_id == entreprise_id,
            Employe.matricule == matricule,
        )
        if exclude_id is not None:
            q = q.where(Employe.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def find_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        departement_id: int | None = None,
        poste_id: int | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[Employe], int]:
        q = select(Employe).where(Employe.entreprise_id == entreprise_id)
        if actif_only:
            q = q.where(Employe.actif.is_(True))
        if departement_id is not None:
            q = q.where(Employe.departement_id == departement_id)
        if poste_id is not None:
            q = q.where(Employe.poste_id == poste_id)
        count_q = select(func.count()).select_from(Employe).where(
            Employe.entreprise_id == entreprise_id
        )
        if actif_only:
            count_q = count_q.where(Employe.actif.is_(True))
        if departement_id is not None:
            count_q = count_q.where(Employe.departement_id == departement_id)
        if poste_id is not None:
            count_q = count_q.where(Employe.poste_id == poste_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Employe.matricule).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Employe) -> Employe:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Employe) -> Employe:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

