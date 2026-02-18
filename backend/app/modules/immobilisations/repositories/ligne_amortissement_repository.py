# app/modules/immobilisations/repositories/ligne_amortissement_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.immobilisations.models import LigneAmortissement


class LigneAmortissementRepository:
    """Accès en lecture aux lignes d'amortissement (détail d'une immobilisation)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_immobilisation(
        self,
        immobilisation_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> list[LigneAmortissement]:
        q = (
            select(LigneAmortissement)
            .where(LigneAmortissement.immobilisation_id == immobilisation_id)
            .order_by(LigneAmortissement.annee.desc(), LigneAmortissement.mois.desc().nulls_last())
            .offset(skip)
            .limit(limit)
        )
        r = await self._db.execute(q)
        return list(r.scalars().all())

