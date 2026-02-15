# app/modules/comptabilite/repositories/ligne_ecriture_repository.py
# -----------------------------------------------------------------------------
# Repository LigneEcriture (couche Infrastructure).
# -----------------------------------------------------------------------------
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.comptabilite.models import LigneEcriture


class LigneEcritureRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_ecriture(self, ecriture_id: int) -> list[LigneEcriture]:
        r = await self._db.execute(
            select(LigneEcriture).where(LigneEcriture.ecriture_id == ecriture_id).order_by(LigneEcriture.id)
        )
        return list(r.scalars().all())

    async def add(self, entity: LigneEcriture) -> LigneEcriture:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
