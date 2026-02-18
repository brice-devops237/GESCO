# app/modules/catalogue/services/unite_mesure.py
# -----------------------------------------------------------------------------
# Use Case Unité de mesure (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import UniteMesure
from app.modules.catalogue.repositories import UniteMesureRepository
from app.modules.catalogue.schemas import UniteMesureCreate, UniteMesureUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages


class UniteMesureService(BaseCatalogueService):
    """Service de gestion des unités de mesure (référentiel)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = UniteMesureRepository(db)

    async def get_by_id(self, id: int) -> UniteMesure | None:
        """Retourne une unité de mesure par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> UniteMesure:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.UNITE_MESURE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> list[UniteMesure]:
        return await self._repo.find_all(skip=skip, limit=limit, actif_only=actif_only)

    async def create(self, data: UniteMesureCreate) -> UniteMesure:
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.UNITE_MESURE_CODE_VIDE)
        if await self._repo.find_by_code(code):
            self._raise_conflict(Messages.UNITE_MESURE_CODE_EXISTS.format(code=code))
        ent = UniteMesure(
            code=code,
            libelle=data.libelle,
            symbole=data.symbole,
            type=data.type,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: UniteMesureUpdate) -> UniteMesure:
        ent = await self.get_or_404(id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

