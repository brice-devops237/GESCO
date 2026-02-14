# app/modules/commercial/services/commande.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.commercial.models import Commande
from app.modules.commercial.repositories import CommandeRepository, DevisRepository, EtatDocumentRepository
from app.modules.commercial.schemas import CommandeCreate, CommandeUpdate
from app.modules.commercial.services.base import BaseCommercialService
from app.modules.commercial.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository, PointVenteRepository, DeviseRepository
from app.modules.partenaires.repositories import TiersRepository


class CommandeService(BaseCommercialService):
    """Service de gestion des commandes clients."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CommandeRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._pdv_repo = PointVenteRepository(db)
        self._tiers_repo = TiersRepository(db)
        self._devis_repo = DevisRepository(db)
        self._etat_repo = EtatDocumentRepository(db)
        self._devise_repo = DeviseRepository(db)

    async def get_by_id(self, id: int) -> Commande | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Commande:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.COMMANDE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        client_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Commande], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
        )

    async def create(self, data: CommandeCreate) -> Commande:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        if await self._tiers_repo.find_by_id(data.client_id) is None:
            self._raise_not_found(Messages.CLIENT_NOT_FOUND)
        if data.devis_id and await self._devis_repo.find_by_id(data.devis_id) is None:
            self._raise_not_found(Messages.DEVIS_NOT_FOUND)
        if await self._etat_repo.find_by_id(data.etat_id) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        if await self._devise_repo.find_by_id(data.devise_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        numero = (data.numero or "").strip()
        if not numero:
            self._raise_bad_request(Messages.DONNEES_INVALIDES)
        if await self._repo.exists_by_entreprise_and_numero(data.entreprise_id, numero):
            self._raise_conflict(Messages.COMMANDE_NUMERO_EXISTS.format(numero=numero))
        ent = Commande(
            entreprise_id=data.entreprise_id,
            point_de_vente_id=data.point_de_vente_id,
            client_id=data.client_id,
            devis_id=data.devis_id,
            numero=numero,
            date_commande=data.date_commande,
            date_livraison_prevue=data.date_livraison_prevue,
            etat_id=data.etat_id,
            montant_ht=data.montant_ht,
            montant_tva=data.montant_tva,
            montant_ttc=data.montant_ttc,
            remise_globale_pct=data.remise_globale_pct,
            remise_globale_montant=data.remise_globale_montant,
            devise_id=data.devise_id,
            adresse_livraison=data.adresse_livraison,
            notes=data.notes,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CommandeUpdate) -> Commande:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "etat_id" in update_data and await self._etat_repo.find_by_id(update_data["etat_id"]) is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
