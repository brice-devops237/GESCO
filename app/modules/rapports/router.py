# app/modules/rapports/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Rapports (tableaux de bord, indicateurs).
# -----------------------------------------------------------------------------

from datetime import date
from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.rapports import schemas
from app.modules.rapports.services import get_chiffre_affaires, get_synthese_dashboard

router = APIRouter(prefix="/rapports", tags=["Rapports"])


@router.get("/chiffre-affaires", response_model=schemas.ChiffreAffairesPeriode)
async def rapport_chiffre_affaires(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    date_debut: date = Query(..., description="Début de période"),
    date_fin: date = Query(..., description="Fin de période"),
):
    """Chiffre d'affaires (somme des factures TTC) sur la période."""
    return await get_chiffre_affaires(db, entreprise_id, date_debut, date_fin)


@router.get("/dashboard", response_model=schemas.SyntheseDashboard)
async def rapport_dashboard(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    date_debut: date | None = Query(None, description="Filtre début période (optionnel)"),
    date_fin: date | None = Query(None, description="Filtre fin période (optionnel)"),
):
    """Synthèse tableau de bord : CA, nombre de factures, commandes, employés actifs."""
    return await get_synthese_dashboard(db, entreprise_id, date_debut, date_fin)
