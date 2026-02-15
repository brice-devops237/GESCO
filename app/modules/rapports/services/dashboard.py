# app/modules/rapports/services/dashboard.py
# -----------------------------------------------------------------------------
# Service métier Rapports : chiffre d'affaires, synthèse tableau de bord.
# Agrège des données via les services commercial et RH.
# -----------------------------------------------------------------------------
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rapports.schemas import ChiffreAffairesPeriode, SyntheseDashboard
from app.modules.rapports.services.base import BaseRapportsService
from app.modules.rapports.services.messages import Messages


class RapportsService(BaseRapportsService):
    """Service des rapports (CA, dashboard)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_chiffre_affaires(
        self,
        entreprise_id: int,
        date_debut: date,
        date_fin: date,
    ) -> ChiffreAffairesPeriode:
        """Calcule le CA (somme montant_ttc des factures) sur la période."""
        from app.modules.commercial.services import FactureService

        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)

        items, _ = await FactureService(self._db).get_all(
            entreprise_id=entreprise_id, skip=0, limit=10_000
        )
        montant_total = Decimal("0")
        nb = 0
        for f in items:
            if date_debut <= getattr(f, "date_facture", date.min) <= date_fin:
                montant_total += getattr(f, "montant_ttc", 0) or Decimal("0")
                nb += 1
        return ChiffreAffairesPeriode(
            entreprise_id=entreprise_id,
            date_debut=date_debut,
            date_fin=date_fin,
            montant_total_ttc=montant_total,
            nombre_factures=nb,
        )

    async def get_synthese_dashboard(
        self,
        entreprise_id: int,
        date_debut: date | None = None,
        date_fin: date | None = None,
    ) -> SyntheseDashboard:
        """Synthèse tableau de bord : CA, nb factures, nb commandes, nb employés actifs."""
        from app.modules.commercial.services import CommandeService, FactureService
        from app.modules.rh.services import EmployeService

        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)

        factures, nb_f = await FactureService(self._db).get_all(
            entreprise_id=entreprise_id, skip=0, limit=10_000
        )
        commandes, nb_c = await CommandeService(self._db).get_all(
            entreprise_id=entreprise_id, skip=0, limit=1
        )
        employes, nb_e = await EmployeService(self._db).get_all(
            entreprise_id=entreprise_id, actif_only=True, skip=0, limit=10_000
        )

        ca = Decimal("0")
        nb_factures_periode = 0
        for f in factures:
            d = getattr(f, "date_facture", None)
            if d is None:
                continue
            if date_debut is not None and d < date_debut:
                continue
            if date_fin is not None and d > date_fin:
                continue
            ca += getattr(f, "montant_ttc", 0) or Decimal("0")
            nb_factures_periode += 1

        periode_label = None
        if date_debut and date_fin:
            periode_label = f"{date_debut} / {date_fin}"

        return SyntheseDashboard(
            entreprise_id=entreprise_id,
            periode_label=periode_label,
            ca_periode=ca,
            nb_factures=nb_factures_periode,
            nb_commandes=nb_c,
            nb_employes_actifs=nb_e,
        )
