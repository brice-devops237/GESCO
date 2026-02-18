# app/modules/catalogue/services/taux_tva.py
# -----------------------------------------------------------------------------
# Use Case Taux TVA (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import TauxTva
from app.modules.catalogue.repositories import TauxTvaRepository
from app.modules.catalogue.schemas import TauxTvaCreate, TauxTvaUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages


class TauxTvaService(BaseCatalogueService):
    """Service de gestion des taux de TVA (référentiel)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = TauxTvaRepository(db)

    async def get_by_id(self, id: int) -> TauxTva | None:
        """Retourne un taux TVA par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> TauxTva:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.TAUX_TVA_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> list[TauxTva]:
        return await self._repo.find_all(skip=skip, limit=limit, actif_only=actif_only)

    async def create(self, data: TauxTvaCreate) -> TauxTva:
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.TAUX_TVA_CODE_VIDE)
        if await self._repo.find_by_code(code):
            self._raise_conflict(Messages.TAUX_TVA_CODE_EXISTS.format(code=code))
        ent = TauxTva(
            code=code,
            taux=data.taux,
            libelle=data.libelle,
            nature=data.nature.value if data.nature else None,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: TauxTvaUpdate) -> TauxTva:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "nature" in update_data and update_data["nature"] is not None and hasattr(update_data["nature"], "value"):
            update_data["nature"] = update_data["nature"].value
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

