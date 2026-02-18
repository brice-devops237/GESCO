# app/modules/parametrage/repositories/utilisateur_repository.py
# -----------------------------------------------------------------------------
# Repository Utilisateur (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Utilisateur


class UtilisateurRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, utilisateur_id: int) -> Utilisateur | None:
        r = await self._db.execute(
            select(Utilisateur).where(Utilisateur.id == utilisateur_id)
        )
        return r.scalar_one_or_none()

    async def find_by_entreprise_and_login(
        self,
        entreprise_id: int,
        login: str,
    ) -> Utilisateur | None:
        login_clean = (login or "").strip()
        if not login_clean:
            return None
        r = await self._db.execute(
            select(Utilisateur).where(
                Utilisateur.entreprise_id == entreprise_id,
                Utilisateur.login == login_clean,
                Utilisateur.deleted_at.is_(None),
            )
        )
        return r.scalar_one_or_none()

    async def find_by_entreprise_and_login_or_email(
        self,
        entreprise_id: int,
        login_or_email: str,
    ) -> Utilisateur | None:
        """Retourne l'utilisateur dont le login ou l'email correspond (pour connexion)."""
        term = (login_or_email or "").strip()
        if not term:
            return None
        r = await self._db.execute(
            select(Utilisateur).where(
                Utilisateur.entreprise_id == entreprise_id,
                or_(
                    Utilisateur.login == term,
                    Utilisateur.email == term,
                ),
                Utilisateur.deleted_at.is_(None),
            )
        )
        return r.scalar_one_or_none()

    async def find_by_login_or_email_global(self, login_or_email: str) -> Utilisateur | None:
        """Retourne le premier utilisateur actif dont le login ou l'email correspond (toutes entreprises)."""
        term = (login_or_email or "").strip()
        if not term:
            return None
        r = await self._db.execute(
            select(Utilisateur).where(
                or_(
                    Utilisateur.login == term,
                    Utilisateur.email == term,
                ),
                Utilisateur.deleted_at.is_(None),
                Utilisateur.actif.is_(True),
            ).order_by(Utilisateur.id).limit(1)
        )
        return r.scalar_one_or_none()

    async def find_by_entreprise(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> list[Utilisateur]:
        q = select(Utilisateur).where(
            Utilisateur.entreprise_id == entreprise_id,
            Utilisateur.deleted_at.is_(None),
        )
        if actif_only:
            q = q.where(Utilisateur.actif.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            q = q.where(
                or_(
                    Utilisateur.login.ilike(term),
                    Utilisateur.nom.ilike(term),
                    Utilisateur.prenom.ilike(term),
                    Utilisateur.email.ilike(term),
                )
            )
        q = q.order_by(Utilisateur.nom, Utilisateur.login).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: Utilisateur) -> Utilisateur:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Utilisateur) -> Utilisateur:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

