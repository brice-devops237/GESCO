# app/modules/tresorerie/services/reglement.py
# -----------------------------------------------------------------------------
# Service métier : règlements (paiements clients / fournisseurs).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tresorerie.models import Reglement, TypeReglement
from app.modules.tresorerie.repositories import ReglementRepository
from app.modules.tresorerie.schemas import ReglementCreate
from app.modules.tresorerie.services.base import BaseTresorerieService
from app.modules.tresorerie.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.partenaires.repositories import TiersRepository
from app.modules.tresorerie.repositories import ModePaiementRepository, CompteTresorerieRepository
from app.modules.commercial.repositories import FactureRepository
from app.modules.achats.repositories import FactureFournisseurRepository


class ReglementService(BaseTresorerieService):
    """Service de gestion des règlements (création, lecture)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ReglementRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._tiers_repo = TiersRepository(db)
        self._mode_repo = ModePaiementRepository(db)
        self._compte_repo = CompteTresorerieRepository(db)
        self._facture_repo = FactureRepository(db)
        self._facture_fournisseur_repo = FactureFournisseurRepository(db)

    def _validate_type_reglement(self, value: str) -> None:
        valid = [e.value for e in TypeReglement]
        if value not in valid:
            self._raise_bad_request(Messages.TYPE_REGLEMENT_INVALIDE.format(valeur=value))

    async def get_by_id(self, id: int) -> Reglement | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Reglement:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.REGLEMENT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        type_reglement: str | None = None,
        tiers_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Reglement], int]:
        from datetime import datetime
        date_from_d = None
        date_to_d = None
        if date_from:
            try:
                date_from_d = datetime.fromisoformat(date_from.replace("Z", "+00:00")).date()
            except (ValueError, AttributeError):
                date_from_d = None
        if date_to:
            try:
                date_to_d = datetime.fromisoformat(date_to.replace("Z", "+00:00")).date()
            except (ValueError, AttributeError):
                date_to_d = None
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            type_reglement=type_reglement,
            tiers_id=tiers_id,
            date_from=date_from_d,
            date_to=date_to_d,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: ReglementCreate, created_by_id: int | None = None) -> Reglement:
        self._validate_type_reglement(data.type_reglement)
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._tiers_repo.find_by_id(data.tiers_id) is None:
            self._raise_not_found(Messages.TIERS_NOT_FOUND)
        if await self._mode_repo.find_by_id(data.mode_paiement_id) is None:
            self._raise_not_found(Messages.MODE_PAIEMENT_NOT_FOUND)
        if await self._compte_repo.find_by_id(data.compte_tresorerie_id) is None:
            self._raise_not_found(Messages.COMPTE_TRESORERIE_NOT_FOUND)
        if data.montant <= 0:
            self._raise_bad_request(Messages.REGLEMENT_MONTANT_POSITIF)
        if data.type_reglement == TypeReglement.client.value:
            if not data.facture_id:
                self._raise_bad_request(Messages.REGLEMENT_FACTURE_OBLIGATOIRE)
            if await self._facture_repo.find_by_id(data.facture_id) is None:
                self._raise_not_found(Messages.FACTURE_NOT_FOUND)
        if data.type_reglement == TypeReglement.fournisseur.value:
            if not data.facture_fournisseur_id:
                self._raise_bad_request(Messages.REGLEMENT_FACTURE_FOURNISSEUR_OBLIGATOIRE)
            if await self._facture_fournisseur_repo.find_by_id(data.facture_fournisseur_id) is None:
                self._raise_not_found(Messages.FACTURE_FOURNISSEUR_NOT_FOUND)
        ent = Reglement(
            entreprise_id=data.entreprise_id,
            type_reglement=data.type_reglement,
            facture_id=data.facture_id,
            facture_fournisseur_id=data.facture_fournisseur_id,
            tiers_id=data.tiers_id,
            montant=data.montant,
            date_reglement=data.date_reglement,
            mode_paiement_id=data.mode_paiement_id,
            compte_tresorerie_id=data.compte_tresorerie_id,
            reference=(data.reference.strip() if data.reference else None),
            notes=(data.notes.strip() if data.notes else None),
            created_by_id=created_by_id,
        )
        return await self._repo.add(ent)
