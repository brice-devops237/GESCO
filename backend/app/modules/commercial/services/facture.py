# app/modules/commercial/services/facture.py
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import Facture, TypeFacture
from app.modules.commercial.repositories import (
    CommandeRepository,
    EtatDocumentRepository,
    FactureRepository,
)
from app.modules.commercial.schemas import FactureCreate, FactureUpdate
from app.modules.commercial.services.base import BaseCommercialService
from app.modules.commercial.services.messages import Messages
from app.modules.parametrage.repositories import (
    DeviseRepository,
    EntrepriseRepository,
    PointVenteRepository,
)
from app.modules.partenaires.repositories import TiersRepository


class FactureService(BaseCommercialService):
    """Service de gestion des factures clients."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = FactureRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._pdv_repo = PointVenteRepository(db)
        self._tiers_repo = TiersRepository(db)
        self._commande_repo = CommandeRepository(db)
        self._etat_repo = EtatDocumentRepository(db)
        self._devise_repo = DeviseRepository(db)

    async def get_by_id(self, id: int) -> Facture | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Facture:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.FACTURE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        client_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Facture], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
        )

    async def create(self, data: FactureCreate) -> Facture:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        if await self._tiers_repo.find_by_id(data.client_id) is None:
            self._raise_not_found(Messages.CLIENT_NOT_FOUND)
        if data.commande_id and await self._commande_repo.find_by_id(data.commande_id) is None:
            self._raise_not_found(Messages.COMMANDE_NOT_FOUND)
        if await self._etat_repo.find_by_id(data.etat_id) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        if await self._devise_repo.find_by_id(data.devise_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        self._validate_enum(data.type_facture, TypeFacture, Messages.FACTURE_TYPE_INVALIDE)
        numero = (data.numero or "").strip()
        if not numero:
            self._raise_bad_request(Messages.FACTURE_NUMERO_VIDE)
        if await self._repo.exists_by_entreprise_and_numero(data.entreprise_id, numero):
            self._raise_conflict(Messages.FACTURE_NUMERO_EXISTS.format(numero=numero))
        ent = Facture(
            entreprise_id=data.entreprise_id,
            point_de_vente_id=data.point_de_vente_id,
            client_id=data.client_id,
            commande_id=data.commande_id,
            numero=numero,
            date_facture=data.date_facture,
            date_echeance=data.date_echeance,
            etat_id=data.etat_id,
            type_facture=data.type_facture,
            montant_ht=data.montant_ht,
            montant_tva=data.montant_tva,
            montant_ttc=data.montant_ttc,
            montant_restant_du=data.montant_restant_du,
            remise_globale_pct=Decimal("0"),
            remise_globale_montant=Decimal("0"),
            devise_id=data.devise_id,
            mention_legale=data.mention_legale,
            notes=data.notes,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: FactureUpdate) -> Facture:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "type_facture" in update_data and update_data["type_facture"] is not None:
            self._validate_enum(update_data["type_facture"], TypeFacture, Messages.FACTURE_TYPE_INVALIDE)
        if "etat_id" in update_data and await self._etat_repo.find_by_id(update_data["etat_id"]) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

