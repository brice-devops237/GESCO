# app/modules/tresorerie/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Trésorerie. Préfixe /tresorerie.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.tresorerie import schemas
from app.modules.tresorerie.services import (
    ModePaiementService,
    CompteTresorerieService,
    ReglementService,
)

router = APIRouter(prefix="/tresorerie", tags=["Trésorerie"])


# --- Modes de paiement ---
@router.get("/modes-paiement", response_model=list[schemas.ModePaiementResponse])
async def list_modes_paiement(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await ModePaiementService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/modes-paiement/{id}", response_model=schemas.ModePaiementResponse)
async def get_mode_paiement(db: DbSession, current_user: CurrentUser, id: int):
    return await ModePaiementService(db).get_or_404(id)


@router.post("/modes-paiement", response_model=schemas.ModePaiementResponse, status_code=201)
async def create_mode_paiement(db: DbSession, current_user: CurrentUser, data: schemas.ModePaiementCreate):
    return await ModePaiementService(db).create(data)


@router.patch("/modes-paiement/{id}", response_model=schemas.ModePaiementResponse)
async def update_mode_paiement(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ModePaiementUpdate):
    return await ModePaiementService(db).update(id, data)


# --- Comptes trésorerie ---
@router.get("/comptes", response_model=list[schemas.CompteTresorerieResponse])
async def list_comptes_tresorerie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    actif_only: bool = False,
    type_compte: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await CompteTresorerieService(db).get_all(
        entreprise_id=entreprise_id,
        actif_only=actif_only,
        type_compte=type_compte,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/comptes/{id}", response_model=schemas.CompteTresorerieResponse)
async def get_compte_tresorerie(db: DbSession, current_user: CurrentUser, id: int):
    return await CompteTresorerieService(db).get_or_404(id)


@router.post("/comptes", response_model=schemas.CompteTresorerieResponse, status_code=201)
async def create_compte_tresorerie(db: DbSession, current_user: CurrentUser, data: schemas.CompteTresorerieCreate):
    return await CompteTresorerieService(db).create(data)


@router.patch("/comptes/{id}", response_model=schemas.CompteTresorerieResponse)
async def update_compte_tresorerie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CompteTresorerieUpdate):
    return await CompteTresorerieService(db).update(id, data)


# --- Règlements ---
@router.get("/reglements", response_model=list[schemas.ReglementResponse])
async def list_reglements(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int | None = None,
    type_reglement: str | None = None,
    tiers_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await ReglementService(db).get_all(
        entreprise_id=entreprise_id,
        type_reglement=type_reglement,
        tiers_id=tiers_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/reglements/{id}", response_model=schemas.ReglementResponse)
async def get_reglement(db: DbSession, current_user: CurrentUser, id: int):
    return await ReglementService(db).get_or_404(id)


@router.post("/reglements", response_model=schemas.ReglementResponse, status_code=201)
async def create_reglement(db: DbSession, current_user: CurrentUser, data: schemas.ReglementCreate):
    return await ReglementService(db).create(data, created_by_id=getattr(current_user, "id", None))
