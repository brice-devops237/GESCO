# app/modules/rapports/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Rapports (tableaux de bord, indicateurs).
# Isolation multi-tenant : entreprise_id validé (ValidatedEntrepriseId).
# Extension monde réel : toutes structures, tous secteurs.
# -----------------------------------------------------------------------------

from datetime import date

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser, ValidatedEntrepriseId
from app.modules.rapports import schemas
from app.modules.rapports.services import RapportsService

router = APIRouter(prefix="/rapports")

TAG_CHIFFRE_AFFAIRES = "Rapports - Chiffre d'affaires"
TAG_DASHBOARD = "Rapports - Tableau de bord"


@router.get("/chiffre-affaires", response_model=schemas.ChiffreAffairesPeriode, tags=[TAG_CHIFFRE_AFFAIRES])
async def rapport_chiffre_affaires(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    date_debut: date = Query(..., description="Début de période"),
    date_fin: date = Query(..., description="Fin de période"),
):
    """Chiffre d'affaires (somme des factures TTC) sur la période."""
    return await RapportsService(db).get_chiffre_affaires(entreprise_id, date_debut, date_fin)


@router.get("/dashboard", response_model=schemas.SyntheseDashboard, tags=[TAG_DASHBOARD])
async def rapport_dashboard(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    date_debut: date | None = Query(None, description="Filtre début période (optionnel)"),
    date_fin: date | None = Query(None, description="Filtre fin période (optionnel)"),
):
    """Synthèse tableau de bord : CA, nombre de factures, commandes, employés actifs."""
    return await RapportsService(db).get_synthese_dashboard(entreprise_id, date_debut, date_fin)

