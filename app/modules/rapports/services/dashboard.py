# app/modules/rapports/services/dashboard.py
# Agrège des données via les services commercial et RH pour le tableau de bord.
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rapports.schemas import ChiffreAffairesPeriode, SyntheseDashboard
from app.modules.parametrage.repositories import EntrepriseRepository


async def get_chiffre_affaires(
    db: AsyncSession,
    entreprise_id: int,
    date_debut: date,
    date_fin: date,
) -> ChiffreAffairesPeriode:
    """Calcule le CA (somme montant_ttc des factures) sur la période."""
    from app.modules.commercial.services import FactureService

    if await EntrepriseRepository(db).find_by_id(entreprise_id) is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(detail="L'entreprise indiquée n'existe pas.")

    items, total = await FactureService(db).get_all(
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
    db: AsyncSession,
    entreprise_id: int,
    date_debut: date | None = None,
    date_fin: date | None = None,
) -> SyntheseDashboard:
    """Synthèse pour tableau de bord : CA, nb factures, nb commandes, nb employés actifs."""
    from app.modules.commercial.services import FactureService, CommandeService
    from app.modules.rh.services import EmployeService

    if await EntrepriseRepository(db).find_by_id(entreprise_id) is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(detail="L'entreprise indiquée n'existe pas.")

    factures, nb_f = await FactureService(db).get_all(
        entreprise_id=entreprise_id, skip=0, limit=10_000
    )
    commandes, nb_c = await CommandeService(db).get_all(
        entreprise_id=entreprise_id, skip=0, limit=1
    )
    employes, nb_e = await EmployeService(db).get_all(
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
