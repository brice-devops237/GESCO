# app/modules/parametrage/repositories/affectation_pdv_repository.py
# -----------------------------------------------------------------------------
# Repository AffectationUtilisateurPdv (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import AffectationUtilisateurPdv


class AffectationPdvRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, affectation_id: int) -> AffectationUtilisateurPdv | None:
        r = await self._db.execute(
            select(AffectationUtilisateurPdv).where(
                AffectationUtilisateurPdv.id == affectation_id
            )
        )
        return r.scalar_one_or_none()

    async def find_by_utilisateur(
        self,
        utilisateur_id: int,
    ) -> list[AffectationUtilisateurPdv]:
        q = (
            select(AffectationUtilisateurPdv)
            .where(AffectationUtilisateurPdv.utilisateur_id == utilisateur_id)
            .order_by(AffectationUtilisateurPdv.est_principal.desc())
        )
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def find_by_point_vente(
        self,
        point_de_vente_id: int,
    ) -> list[AffectationUtilisateurPdv]:
        q = (
            select(AffectationUtilisateurPdv)
            .where(AffectationUtilisateurPdv.point_de_vente_id == point_de_vente_id)
            .order_by(AffectationUtilisateurPdv.est_principal.desc())
        )
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def exists_by_utilisateur_and_point_vente(
        self,
        utilisateur_id: int,
        point_de_vente_id: int,
    ) -> bool:
        r = await self._db.execute(
            select(AffectationUtilisateurPdv.id).where(
                AffectationUtilisateurPdv.utilisateur_id == utilisateur_id,
                AffectationUtilisateurPdv.point_de_vente_id == point_de_vente_id,
            ).limit(1)
        )
        return r.scalar_one_or_none() is not None

    async def add(self, entity: AffectationUtilisateurPdv) -> AffectationUtilisateurPdv:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(
        self,
        entity: AffectationUtilisateurPdv,
    ) -> AffectationUtilisateurPdv:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def delete(self, entity: AffectationUtilisateurPdv) -> None:
        await self._db.delete(entity)
        await self._db.flush()
