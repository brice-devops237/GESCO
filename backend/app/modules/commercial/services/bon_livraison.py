# app/modules/commercial/services/bon_livraison.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import BonLivraison
from app.modules.commercial.repositories import (
    BonLivraisonRepository,
    CommandeRepository,
    EtatDocumentRepository,
    FactureRepository,
)
from app.modules.commercial.schemas import BonLivraisonCreate, BonLivraisonUpdate
from app.modules.commercial.services.base import BaseCommercialService
from app.modules.commercial.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository, PointVenteRepository
from app.modules.partenaires.repositories import TiersRepository


class BonLivraisonService(BaseCommercialService):
    """Service de gestion des bons de livraison."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = BonLivraisonRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._pdv_repo = PointVenteRepository(db)
        self._tiers_repo = TiersRepository(db)
        self._commande_repo = CommandeRepository(db)
        self._facture_repo = FactureRepository(db)
        self._etat_repo = EtatDocumentRepository(db)

    async def get_by_id(self, id: int) -> BonLivraison | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> BonLivraison:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.BON_LIVRAISON_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        client_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BonLivraison], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
        )

    async def create(self, data: BonLivraisonCreate) -> BonLivraison:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        if await self._tiers_repo.find_by_id(data.client_id) is None:
            self._raise_not_found(Messages.CLIENT_NOT_FOUND)
        if data.commande_id and await self._commande_repo.find_by_id(data.commande_id) is None:
            self._raise_not_found(Messages.COMMANDE_NOT_FOUND)
        if data.facture_id and await self._facture_repo.find_by_id(data.facture_id) is None:
            self._raise_not_found(Messages.FACTURE_NOT_FOUND)
        if await self._etat_repo.find_by_id(data.etat_id) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        numero = (data.numero or "").strip()
        if not numero:
            self._raise_bad_request(Messages.DONNEES_INVALIDES)
        if await self._repo.exists_by_entreprise_and_numero(data.entreprise_id, numero):
            self._raise_conflict(Messages.BON_LIVRAISON_NUMERO_EXISTS.format(numero=numero))
        ent = BonLivraison(
            entreprise_id=data.entreprise_id,
            point_de_vente_id=data.point_de_vente_id,
            commande_id=data.commande_id,
            facture_id=data.facture_id,
            client_id=data.client_id,
            numero=numero,
            date_livraison=data.date_livraison,
            contact_livraison=data.contact_livraison,
            adresse_livraison=data.adresse_livraison,
            etat_id=data.etat_id,
            notes=data.notes,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: BonLivraisonUpdate) -> BonLivraison:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "etat_id" in update_data and await self._etat_repo.find_by_id(update_data["etat_id"]) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

