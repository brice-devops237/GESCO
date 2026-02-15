# app/modules/comptabilite/services/ecriture.py
# -----------------------------------------------------------------------------
# Service métier : écritures comptables (en-tête + lignes, équilibre débit/crédit).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comptabilite.models import EcritureComptable, LigneEcriture
from app.modules.comptabilite.repositories import (
    CompteComptableRepository,
    EcritureComptableRepository,
    JournalComptableRepository,
    LigneEcritureRepository,
    PeriodeComptableRepository,
)
from app.modules.comptabilite.schemas import EcritureComptableCreate
from app.modules.comptabilite.services.base import BaseComptabiliteService
from app.modules.comptabilite.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class EcritureComptableService(BaseComptabiliteService):
    """Service de gestion des écritures comptables (création avec lignes, équilibre)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = EcritureComptableRepository(db)
        self._ligne_repo = LigneEcritureRepository(db)
        self._compte_repo = CompteComptableRepository(db)
        self._journal_repo = JournalComptableRepository(db)
        self._periode_repo = PeriodeComptableRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> EcritureComptable | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> EcritureComptable:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.ECRITURE_COMPTABLE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        journal_id: int | None = None,
        periode_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[EcritureComptable], int]:
        from datetime import datetime as dt
        date_from_d = None
        date_to_d = None
        if date_from:
            try:
                date_from_d = dt.fromisoformat(date_from.replace("Z", "+00:00")).date()
            except (ValueError, AttributeError):
                pass
        if date_to:
            try:
                date_to_d = dt.fromisoformat(date_to.replace("Z", "+00:00")).date()
            except (ValueError, AttributeError):
                pass
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            journal_id=journal_id,
            periode_id=periode_id,
            date_from=date_from_d,
            date_to=date_to_d,
            skip=skip,
            limit=limit,
        )

    async def get_with_lignes(self, id: int) -> tuple[EcritureComptable, list[LigneEcriture]]:
        ent = await self.get_or_404(id)
        lignes = await self._ligne_repo.find_by_ecriture(ent.id)
        return ent, lignes

    async def create(self, data: EcritureComptableCreate, created_by_id: int | None = None) -> EcritureComptable:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        journal = await self._journal_repo.find_by_id(data.journal_id)
        if journal is None or journal.entreprise_id != data.entreprise_id:
            self._raise_not_found(Messages.JOURNAL_COMPTABLE_NOT_FOUND)
        if not (data.numero_piece or "").strip():
            self._raise_bad_request(Messages.ECRITURE_NUMERO_PIECE_VIDE)
        if len(data.lignes) < 2:
            self._raise_bad_request(Messages.ECRITURE_LIGNES_MIN)
        total_debit = sum(ligne.debit for ligne in data.lignes)
        total_credit = sum(ligne.credit for ligne in data.lignes)
        if total_debit != total_credit:
            self._raise_bad_request(Messages.ECRITURE_NON_EQUILIBREE)
        if total_debit <= 0:
            self._raise_bad_request(Messages.ECRITURE_MONTANT_ZERO)
        periode = None
        if data.periode_id is not None:
            periode = await self._periode_repo.find_by_id(data.periode_id)
            if periode is None or periode.entreprise_id != data.entreprise_id:
                self._raise_not_found(Messages.PERIODE_COMPTABLE_NOT_FOUND)
            if periode.cloturee:
                self._raise_bad_request(Messages.PERIODE_CLOTUREE)
            if not (periode.date_debut <= data.date_ecriture <= periode.date_fin):
                self._raise_bad_request(Messages.PERIODE_DATE_HORS_PERIODE)
        for ligne in data.lignes:
            compte = await self._compte_repo.find_by_id(ligne.compte_id)
            if compte is None or compte.entreprise_id != data.entreprise_id:
                self._raise_not_found(Messages.COMPTE_COMPTABLE_NOT_FOUND)
        ent = EcritureComptable(
            entreprise_id=data.entreprise_id,
            journal_id=data.journal_id,
            periode_id=data.periode_id,
            date_ecriture=data.date_ecriture,
            numero_piece=(data.numero_piece or "").strip(),
            libelle=(data.libelle or "").strip() or None,
            created_by_id=created_by_id,
        )
        ent = await self._repo.add(ent)
        for ligne in data.lignes:
            lig = LigneEcriture(
                ecriture_id=ent.id,
                compte_id=ligne.compte_id,
                libelle_ligne=(ligne.libelle_ligne or "").strip() or None,
                debit=ligne.debit,
                credit=ligne.credit,
            )
            await self._ligne_repo.add(lig)
        return ent
