# app/modules/catalogue/services/prix.py
# -----------------------------------------------------------------------------
# Use Case Prix produit (canal / PDV) (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import PrixProduit
from app.modules.catalogue.repositories import (
    CanalVenteRepository,
    PrixProduitRepository,
    ProduitRepository,
)
from app.modules.catalogue.schemas import PrixProduitCreate, PrixProduitUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages
from app.modules.parametrage.repositories import PointVenteRepository


class PrixProduitService(BaseCatalogueService):
    """Service de gestion des prix produits (canal / point de vente)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = PrixProduitRepository(db)
        self._produit_repo = ProduitRepository(db)
        self._canal_repo = CanalVenteRepository(db)
        self._pdv_repo = PointVenteRepository(db)

    async def get_by_id(self, id: int) -> PrixProduit | None:
        """Retourne un prix produit par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> PrixProduit:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.PRIX_PRODUIT_NOT_FOUND)
        return ent

    async def get_by_produit(
        self,
        produit_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PrixProduit], int]:
        return await self._repo.find_by_produit(produit_id, skip=skip, limit=limit)

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PrixProduit], int]:
        return await self._repo.find_all(entreprise_id=entreprise_id, skip=skip, limit=limit)

    async def create(self, data: PrixProduitCreate) -> PrixProduit:
        if await self._produit_repo.find_by_id(data.produit_id) is None:
            self._raise_not_found(Messages.PRIX_PRODUIT_PRODUIT_NOT_FOUND)
        if data.canal_vente_id is not None and await self._canal_repo.find_by_id(data.canal_vente_id) is None:
            self._raise_not_found(Messages.PRIX_PRODUIT_CANAL_NOT_FOUND)
        if data.point_de_vente_id is not None and await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
            self._raise_not_found(Messages.PRIX_PRODUIT_PDV_NOT_FOUND)
        if data.date_fin is not None and data.date_fin < data.date_debut:
            self._raise_bad_request(Messages.PRIX_PRODUIT_DATES_INVALIDES)
        ent = PrixProduit(
            produit_id=data.produit_id,
            canal_vente_id=data.canal_vente_id,
            point_de_vente_id=data.point_de_vente_id,
            prix_ttc=data.prix_ttc,
            prix_ht=data.prix_ht,
            date_debut=data.date_debut,
            date_fin=data.date_fin,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: PrixProduitUpdate) -> PrixProduit:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "canal_vente_id" in update_data and update_data["canal_vente_id"] is not None:
            if await self._canal_repo.find_by_id(update_data["canal_vente_id"]) is None:
                self._raise_bad_request(Messages.PRIX_PRODUIT_CANAL_NOT_FOUND)
        if "point_de_vente_id" in update_data and update_data["point_de_vente_id"] is not None:
            if await self._pdv_repo.find_by_id(update_data["point_de_vente_id"]) is None:
                self._raise_bad_request(Messages.PRIX_PRODUIT_PDV_NOT_FOUND)
        date_debut = update_data.get("date_debut", ent.date_debut)
        date_fin = update_data.get("date_fin", ent.date_fin)
        if date_fin is not None and date_fin < date_debut:
            self._raise_bad_request(Messages.PRIX_PRODUIT_DATES_INVALIDES)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete(self, id: int) -> None:
        ent = await self.get_or_404(id)
        await self._repo.delete(ent)

