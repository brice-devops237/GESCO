# app/modules/achats/services/reception.py
# -----------------------------------------------------------------------------
# Service métier : réceptions (liées aux commandes fournisseurs).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import Reception, StatutReception
from app.modules.achats.repositories import (
    CommandeFournisseurRepository,
    DepotRepository,
    ReceptionRepository,
)
from app.modules.achats.schemas import ReceptionCreate, ReceptionUpdate
from app.modules.achats.services.base import BaseAchatsService
from app.modules.achats.services.messages import Messages


class ReceptionService(BaseAchatsService):
    """Service de gestion des réceptions (création, lecture, mise à jour, validations)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ReceptionRepository(db)
        self._commande_repo = CommandeFournisseurRepository(db)
        self._depot_repo = DepotRepository(db)

    async def get_by_id(self, id: int) -> Reception | None:
        """Retourne une réception par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Reception:
        """Retourne une réception par id ou lève 404."""
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.RECEPTION_NOT_FOUND)
        return ent

    async def get_by_commande(
        self, commande_fournisseur_id: int, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[Reception], int]:
        """Liste les réceptions d'une commande fournisseur avec pagination."""
        return await self._repo.find_by_commande(
            commande_fournisseur_id, skip=skip, limit=limit
        )

    async def create(self, data: ReceptionCreate) -> Reception:
        """Crée une réception après validation (commande, dépôt, numéro, état)."""
        if await self._commande_repo.find_by_id(data.commande_fournisseur_id) is None:
            self._raise_not_found(Messages.COMMANDE_FOURNISSEUR_NOT_FOUND)
        if await self._depot_repo.find_by_id(data.depot_id) is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        numero = (data.numero or "").strip()
        if not numero:
            self._raise_bad_request(Messages.RECEPTION_NUMERO_VIDE)
        self._validate_enum(data.etat, StatutReception, Messages.RECEPTION_ETAT_INVALIDE)
        ent = Reception(
            commande_fournisseur_id=data.commande_fournisseur_id,
            depot_id=data.depot_id,
            numero=numero,
            numero_bl_fournisseur=data.numero_bl_fournisseur,
            date_reception=data.date_reception,
            etat=data.etat,
            notes=data.notes,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ReceptionUpdate) -> Reception:
        """Met à jour une réception ; valide l'état si fourni."""
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "etat" in update_data and update_data["etat"] is not None:
            self._validate_enum(update_data["etat"], StatutReception, Messages.RECEPTION_ETAT_INVALIDE)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

