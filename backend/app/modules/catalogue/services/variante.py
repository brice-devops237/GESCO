# app/modules/catalogue/services/variante.py
# -----------------------------------------------------------------------------
# Use Case Variante de produit (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import VarianteProduit
from app.modules.catalogue.repositories import ProduitRepository, VarianteProduitRepository
from app.modules.catalogue.schemas import VarianteProduitCreate, VarianteProduitUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages


class VarianteProduitService(BaseCatalogueService):
    """Service de gestion des variantes de produit (par produit)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = VarianteProduitRepository(db)
        self._produit_repo = ProduitRepository(db)

    async def get_by_id(self, id: int) -> VarianteProduit | None:
        """Retourne une variante par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> VarianteProduit:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.VARIANTE_NOT_FOUND)
        return ent

    async def get_by_produit(
        self,
        produit_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> tuple[list[VarianteProduit], int]:
        return await self._repo.find_by_produit(
            produit_id, skip=skip, limit=limit, actif_only=actif_only
        )

    async def create(self, data: VarianteProduitCreate) -> VarianteProduit:
        if await self._produit_repo.find_by_id(data.produit_id) is None:
            self._raise_not_found(Messages.VARIANTE_PRODUIT_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.VARIANTE_CODE_VIDE)
        if await self._repo.exists_by_produit_and_code(data.produit_id, code):
            self._raise_conflict(Messages.VARIANTE_CODE_EXISTS.format(code=code))
        ent = VarianteProduit(
            produit_id=data.produit_id,
            code=code,
            libelle=data.libelle,
            prix_ttc_supplement=data.prix_ttc_supplement,
            stock_separe=data.stock_separe,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: VarianteProduitUpdate) -> VarianteProduit:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            code = (update_data["code"] or "").strip()
            if not code:
                self._raise_bad_request(Messages.VARIANTE_CODE_VIDE)
            if await self._repo.exists_by_produit_and_code(ent.produit_id, code, exclude_id=id):
                self._raise_conflict(Messages.VARIANTE_CODE_EXISTS.format(code=code))
            update_data["code"] = code
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete(self, id: int) -> None:
        ent = await self.get_or_404(id)
        await self._repo.delete(ent)

