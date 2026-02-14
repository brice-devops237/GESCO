# app/modules/partenaires/services/type_tiers.py
# -----------------------------------------------------------------------------
# Use Case Type de tiers (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partenaires.models import TypeTiers
from app.modules.partenaires.repositories import TypeTiersRepository
from app.modules.partenaires.schemas import TypeTiersCreate, TypeTiersUpdate
from app.modules.partenaires.services.base import BasePartenairesService
from app.modules.partenaires.services.messages import Messages


class TypeTiersService(BasePartenairesService):
    """Service de gestion des types de tiers (client, fournisseur, etc.)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = TypeTiersRepository(db)

    async def get_by_id(self, id: int) -> TypeTiers | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> TypeTiers:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.TYPE_TIERS_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TypeTiers]:
        return await self._repo.find_all(skip=skip, limit=limit)

    async def create(self, data: TypeTiersCreate) -> TypeTiers:
        code = (data.code or "").strip().upper()
        if not code:
            self._raise_bad_request(Messages.TYPE_TIERS_CODE_VIDE)
        if await self._repo.find_by_code(code):
            self._raise_conflict(Messages.TYPE_TIERS_CODE_EXISTS.format(code=code))
        ent = TypeTiers(
            code=code,
            libelle=data.libelle,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: TypeTiersUpdate) -> TypeTiers:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            code = (update_data["code"] or "").strip().upper()
            if not code:
                self._raise_bad_request(Messages.TYPE_TIERS_CODE_VIDE)
            existing = await self._repo.find_by_code(code)
            if existing and existing.id != id:
                self._raise_conflict(Messages.TYPE_TIERS_CODE_EXISTS.format(code=code))
            update_data["code"] = code
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
