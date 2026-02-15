# app/modules/achats/repositories/commande_fournisseur_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import CommandeFournisseur


class CommandeFournisseurRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> CommandeFournisseur | None:
        r = await self._db.execute(select(CommandeFournisseur).where(CommandeFournisseur.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        entreprise_id: int | None = None,
        fournisseur_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CommandeFournisseur], int]:
        q = select(CommandeFournisseur)
        count_q = select(func.count()).select_from(CommandeFournisseur)
        if entreprise_id is not None:
            q = q.where(CommandeFournisseur.entreprise_id == entreprise_id)
            count_q = count_q.where(CommandeFournisseur.entreprise_id == entreprise_id)
        if fournisseur_id is not None:
            q = q.where(CommandeFournisseur.fournisseur_id == fournisseur_id)
            count_q = count_q.where(CommandeFournisseur.fournisseur_id == fournisseur_id)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(CommandeFournisseur.date_commande.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def exists_by_entreprise_and_numero(
        self, entreprise_id: int, numero: str, exclude_id: int | None = None
    ) -> bool:
        q = select(CommandeFournisseur.id).where(
            CommandeFournisseur.entreprise_id == entreprise_id,
            CommandeFournisseur.numero == numero,
        ).limit(1)
        if exclude_id is not None:
            q = q.where(CommandeFournisseur.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: CommandeFournisseur) -> CommandeFournisseur:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: CommandeFournisseur) -> CommandeFournisseur:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
