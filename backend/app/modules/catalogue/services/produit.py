# app/modules/catalogue/services/produit.py
# -----------------------------------------------------------------------------
# Use Case Produit (couche Application).
# -----------------------------------------------------------------------------

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import Produit
from app.modules.catalogue.repositories import (
    FamilleProduitRepository,
    ProduitRepository,
    TauxTvaRepository,
    UniteMesureRepository,
)
from app.modules.catalogue.schemas import ProduitCreate, ProduitUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.shared.regulations import is_pays_code_valide


class ProduitService(BaseCatalogueService):
    """Service de gestion des produits (par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ProduitRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._famille_repo = FamilleProduitRepository(db)
        self._unite_repo = UniteMesureRepository(db)
        self._taux_tva_repo = TauxTvaRepository(db)

    async def _ensure_entreprise_exists(self, entreprise_id: int) -> None:
        ent = await self._entreprise_repo.find_by_id(entreprise_id)
        if ent is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)

    async def get_by_id(self, id: int) -> Produit | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Produit:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.PRODUIT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        famille_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Produit], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            famille_id=famille_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def create(self, data: ProduitCreate) -> Produit:
        await self._ensure_entreprise_exists(data.entreprise_id)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.PRODUIT_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.PRODUIT_CODE_EXISTS.format(code=code))
        if data.famille_id is not None:
            fam = await self._famille_repo.find_by_id(data.famille_id)
            if fam is None or fam.entreprise_id != data.entreprise_id:
                self._raise_bad_request(Messages.PRODUIT_FAMILLE_NOT_FOUND)
        if await self._unite_repo.find_by_id(data.unite_vente_id) is None:
            self._raise_bad_request(Messages.PRODUIT_UNITE_VENTE_NOT_FOUND)
        if data.unite_achat_id is not None and await self._unite_repo.find_by_id(data.unite_achat_id) is None:
            self._raise_bad_request(Messages.PRODUIT_UNITE_ACHAT_NOT_FOUND)
        if data.taux_tva_id is not None and await self._taux_tva_repo.find_by_id(data.taux_tva_id) is None:
            self._raise_bad_request(Messages.PRODUIT_TAUX_TVA_NOT_FOUND)
        if data.pays_origine and not is_pays_code_valide(data.pays_origine):
            self._raise_bad_request(Messages.PRODUIT_PAYS_ORIGINE_INVALIDE)
        ent = Produit(
            entreprise_id=data.entreprise_id,
            famille_id=data.famille_id,
            code=code,
            code_barre=data.code_barre,
            libelle=data.libelle,
            description=data.description,
            type=data.type.value if hasattr(data.type, "value") else data.type,
            marque=data.marque,
            reference_fournisseur=data.reference_fournisseur,
            code_douanier=data.code_douanier,
            pays_origine=data.pays_origine,
            poids_net_kg=data.poids_net_kg,
            unite_vente_id=data.unite_vente_id,
            unite_achat_id=data.unite_achat_id,
            coefficient_achat_vente=data.coefficient_achat_vente,
            prix_achat_ht=data.prix_achat_ht,
            prix_vente_ttc=data.prix_vente_ttc,
            taux_tva_id=data.taux_tva_id,
            seuil_alerte_min=data.seuil_alerte_min,
            seuil_alerte_max=data.seuil_alerte_max,
            gerer_stock=data.gerer_stock,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ProduitUpdate) -> Produit:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            code = (update_data["code"] or "").strip()
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, code, exclude_id=id):
                self._raise_conflict(Messages.PRODUIT_CODE_EXISTS.format(code=code))
        if "famille_id" in update_data and update_data["famille_id"] is not None:
            fam = await self._famille_repo.find_by_id(update_data["famille_id"])
            if fam is None or fam.entreprise_id != ent.entreprise_id:
                self._raise_bad_request(Messages.PRODUIT_FAMILLE_NOT_FOUND)
        if "unite_vente_id" in update_data and await self._unite_repo.find_by_id(update_data["unite_vente_id"]) is None:
            self._raise_bad_request(Messages.PRODUIT_UNITE_VENTE_NOT_FOUND)
        if "unite_achat_id" in update_data and update_data["unite_achat_id"] is not None:
            if await self._unite_repo.find_by_id(update_data["unite_achat_id"]) is None:
                self._raise_bad_request(Messages.PRODUIT_UNITE_ACHAT_NOT_FOUND)
        if "taux_tva_id" in update_data and update_data["taux_tva_id"] is not None:
            if await self._taux_tva_repo.find_by_id(update_data["taux_tva_id"]) is None:
                self._raise_bad_request(Messages.PRODUIT_TAUX_TVA_NOT_FOUND)
        if "pays_origine" in update_data and update_data["pays_origine"] and not is_pays_code_valide(update_data["pays_origine"]):
            self._raise_bad_request(Messages.PRODUIT_PAYS_ORIGINE_INVALIDE)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete_soft(self, id: int) -> None:
        ent = await self.get_or_404(id)
        ent.deleted_at = datetime.now(UTC)
        await self._repo.update(ent)

