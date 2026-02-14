# app/modules/achats/services/commande_fournisseur.py
# -----------------------------------------------------------------------------
# Service métier : commandes fournisseurs (CRUD, validations, unicité numéro).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import CommandeFournisseur
from app.modules.achats.repositories import CommandeFournisseurRepository, DepotRepository
from app.modules.achats.schemas import CommandeFournisseurCreate, CommandeFournisseurUpdate
from app.modules.achats.services.base import BaseAchatsService
from app.modules.achats.services.messages import Messages
from app.modules.commercial.repositories import EtatDocumentRepository
from app.modules.parametrage.repositories import EntrepriseRepository, DeviseRepository
from app.modules.partenaires.repositories import TiersRepository


class CommandeFournisseurService(BaseAchatsService):
    """Service de gestion des commandes fournisseurs (CRUD, validations, unicité numéro)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CommandeFournisseurRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._tiers_repo = TiersRepository(db)
        self._depot_repo = DepotRepository(db)
        self._etat_repo = EtatDocumentRepository(db)
        self._devise_repo = DeviseRepository(db)

    async def get_by_id(self, id: int) -> CommandeFournisseur | None:
        """Retourne une commande fournisseur par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> CommandeFournisseur:
        """Retourne une commande fournisseur par id ou lève 404."""
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.COMMANDE_FOURNISSEUR_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        fournisseur_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CommandeFournisseur], int]:
        """Liste les commandes fournisseurs avec filtres et pagination."""
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            fournisseur_id=fournisseur_id,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: CommandeFournisseurCreate) -> CommandeFournisseur:
        """Crée une commande fournisseur après validation des références, numéro et dates."""
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._tiers_repo.find_by_id(data.fournisseur_id) is None:
            self._raise_not_found(Messages.FOURNISSEUR_NOT_FOUND)
        if data.depot_id and await self._depot_repo.find_by_id(data.depot_id) is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        if await self._etat_repo.find_by_id(data.etat_id) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        if await self._devise_repo.find_by_id(data.devise_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        numero = (data.numero or "").strip()
        if not numero:
            self._raise_bad_request(Messages.COMMANDE_FOURNISSEUR_NUMERO_VIDE)
        if data.date_livraison_prevue is not None and data.date_commande is not None:
            if data.date_livraison_prevue < data.date_commande:
                self._raise_bad_request(Messages.COMMANDE_FOURNISSEUR_DATES_INCOHERENTES)
        if await self._repo.exists_by_entreprise_and_numero(data.entreprise_id, numero):
            self._raise_conflict(Messages.COMMANDE_FOURNISSEUR_NUMERO_EXISTS.format(numero=numero))
        ent = CommandeFournisseur(
            entreprise_id=data.entreprise_id,
            fournisseur_id=data.fournisseur_id,
            depot_id=data.depot_id,
            numero=numero,
            numero_fournisseur=data.numero_fournisseur,
            date_commande=data.date_commande,
            date_livraison_prevue=data.date_livraison_prevue,
            etat_id=data.etat_id,
            montant_ht=data.montant_ht,
            montant_tva=data.montant_tva,
            montant_ttc=data.montant_ttc,
            devise_id=data.devise_id,
            notes=data.notes,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CommandeFournisseurUpdate) -> CommandeFournisseur:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "depot_id" in update_data and update_data["depot_id"] is not None:
            if await self._depot_repo.find_by_id(update_data["depot_id"]) is None:
                self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        if "etat_id" in update_data and await self._etat_repo.find_by_id(update_data["etat_id"]) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
