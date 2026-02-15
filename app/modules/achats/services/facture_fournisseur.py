# app/modules/achats/services/facture_fournisseur.py
# -----------------------------------------------------------------------------
# Service métier : factures fournisseurs (création, lecture, mise à jour, validations).
# -----------------------------------------------------------------------------

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import FactureFournisseur, StatutPaiementFournisseur
from app.modules.achats.repositories import (
    CommandeFournisseurRepository,
    FactureFournisseurRepository,
)
from app.modules.achats.schemas import FactureFournisseurCreate, FactureFournisseurUpdate
from app.modules.achats.services.base import BaseAchatsService
from app.modules.achats.services.messages import Messages
from app.modules.parametrage.repositories import DeviseRepository, EntrepriseRepository
from app.modules.partenaires.repositories import TiersRepository


class FactureFournisseurService(BaseAchatsService):
    """Service de gestion des factures fournisseurs (CRUD, validations métier)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = FactureFournisseurRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._tiers_repo = TiersRepository(db)
        self._commande_repo = CommandeFournisseurRepository(db)
        self._devise_repo = DeviseRepository(db)

    async def get_by_id(self, id: int) -> FactureFournisseur | None:
        """Retourne une facture fournisseur par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> FactureFournisseur:
        """Retourne une facture fournisseur par id ou lève 404."""
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.FACTURE_FOURNISSEUR_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        fournisseur_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FactureFournisseur], int]:
        """Liste les factures fournisseurs avec filtres et pagination."""
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            fournisseur_id=fournisseur_id,
            skip=skip,
            limit=limit,
        )

    def _validate_montants(self, montant_ttc: Decimal | None, montant_restant_du: Decimal | None) -> None:
        """Vérifie que le montant restant dû n'excède pas le montant TTC."""
        if montant_ttc is not None and montant_restant_du is not None and montant_restant_du > montant_ttc:
            self._raise_bad_request(Messages.FACTURE_FOURNISSEUR_MONTANT_RESTANT)

    async def create(self, data: FactureFournisseurCreate) -> FactureFournisseur:
        """Crée une facture fournisseur après validation (références, numéro, statut, montants)."""
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._tiers_repo.find_by_id(data.fournisseur_id) is None:
            self._raise_not_found(Messages.FOURNISSEUR_NOT_FOUND)
        if data.commande_fournisseur_id and await self._commande_repo.find_by_id(data.commande_fournisseur_id) is None:
            self._raise_not_found(Messages.COMMANDE_FOURNISSEUR_NOT_FOUND)
        if await self._devise_repo.find_by_id(data.devise_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        numero = (data.numero_fournisseur or "").strip()
        if not numero:
            self._raise_bad_request(Messages.FACTURE_FOURNISSEUR_NUMERO_VIDE)
        self._validate_enum(data.statut_paiement, StatutPaiementFournisseur, Messages.FACTURE_FOURNISSEUR_STATUT_INVALIDE)
        self._validate_montants(data.montant_ttc, data.montant_restant_du)
        ent = FactureFournisseur(
            entreprise_id=data.entreprise_id,
            fournisseur_id=data.fournisseur_id,
            commande_fournisseur_id=data.commande_fournisseur_id,
            numero_fournisseur=numero,
            date_facture=data.date_facture,
            date_echeance=data.date_echeance,
            montant_ht=data.montant_ht,
            montant_tva=data.montant_tva,
            montant_ttc=data.montant_ttc,
            montant_restant_du=data.montant_restant_du,
            devise_id=data.devise_id,
            statut_paiement=data.statut_paiement,
            notes=data.notes,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: FactureFournisseurUpdate) -> FactureFournisseur:
        """Met à jour une facture fournisseur ; valide statut et montants si fournis."""
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "statut_paiement" in update_data and update_data["statut_paiement"] is not None:
            self._validate_enum(
                update_data["statut_paiement"], StatutPaiementFournisseur, Messages.FACTURE_FOURNISSEUR_STATUT_INVALIDE
            )
        montant_ttc = update_data.get("montant_ttc", ent.montant_ttc)
        montant_restant_du = update_data.get("montant_restant_du", ent.montant_restant_du)
        self._validate_montants(montant_ttc, montant_restant_du)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
