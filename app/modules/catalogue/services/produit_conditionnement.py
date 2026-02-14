# app/modules/catalogue/services/produit_conditionnement.py
# -----------------------------------------------------------------------------
# Use Case Produit-Conditionnement (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import ProduitConditionnement
from app.modules.catalogue.repositories import (
    ConditionnementRepository,
    ProduitConditionnementRepository,
    ProduitRepository,
)
from app.modules.catalogue.schemas import ProduitConditionnementCreate, ProduitConditionnementUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages


class ProduitConditionnementService(BaseCatalogueService):
    """Service de gestion des liaisons produit-conditionnement."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ProduitConditionnementRepository(db)
        self._produit_repo = ProduitRepository(db)
        self._conditionnement_repo = ConditionnementRepository(db)

    async def get_by_id(self, id: int) -> ProduitConditionnement | None:
        """Retourne une liaison par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> ProduitConditionnement:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.PRODUIT_CONDITIONNEMENT_NOT_FOUND)
        return ent

    async def get_by_produit(self, produit_id: int, *, skip: int = 0, limit: int = 100) -> list[ProduitConditionnement]:
        return await self._repo.find_by_produit(produit_id, skip=skip, limit=limit)

    async def create(self, data: ProduitConditionnementCreate) -> ProduitConditionnement:
        if await self._produit_repo.find_by_id(data.produit_id) is None:
            self._raise_not_found(Messages.PRODUIT_CONDITIONNEMENT_PRODUIT_NOT_FOUND)
        if await self._conditionnement_repo.find_by_id(data.conditionnement_id) is None:
            self._raise_not_found(Messages.PRODUIT_CONDITIONNEMENT_CONDITIONNEMENT_NOT_FOUND)
        if await self._repo.exists_by_produit_and_conditionnement(data.produit_id, data.conditionnement_id):
            self._raise_conflict(Messages.PRODUIT_CONDITIONNEMENT_EXISTS)
        ent = ProduitConditionnement(
            produit_id=data.produit_id,
            conditionnement_id=data.conditionnement_id,
            quantite_unites=data.quantite_unites,
            prix_vente_ttc=data.prix_vente_ttc,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ProduitConditionnementUpdate) -> ProduitConditionnement:
        ent = await self.get_or_404(id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete(self, id: int) -> None:
        ent = await self.get_or_404(id)
        await self._repo.delete(ent)
