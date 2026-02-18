# app/modules/tresorerie/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Trésorerie. Isolation multi-tenant : listes par
# ValidatedEntrepriseId ; GET/PATCH/POST vérifient que la ressource appartient
# à l'entreprise de l'utilisateur. Adapté toute structure, tout secteur.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.core.exceptions import ForbiddenError
from app.modules.parametrage.dependencies import CurrentUser, ValidatedEntrepriseId
from app.modules.tresorerie import schemas
from app.modules.tresorerie.services import (
    CompteTresorerieService,
    ModePaiementService,
    ReglementService,
)

router = APIRouter(prefix="/tresorerie")

TAG_MODES_PAIEMENT = "Trésorerie - Modes de paiement"
TAG_COMPTES_TRESORERIE = "Trésorerie - Comptes trésorerie"
TAG_REGLEMENTS = "Trésorerie - Règlements"


# --- Modes de paiement ---
@router.get("/modes-paiement", response_model=list[schemas.ModePaiementResponse], tags=[TAG_MODES_PAIEMENT])
async def list_modes_paiement(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await ModePaiementService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/modes-paiement/{id}", response_model=schemas.ModePaiementResponse, tags=[TAG_MODES_PAIEMENT])
async def get_mode_paiement(db: DbSession, current_user: CurrentUser, id: int):
    ent = await ModePaiementService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/modes-paiement", response_model=schemas.ModePaiementResponse, status_code=201, tags=[TAG_MODES_PAIEMENT])
async def create_mode_paiement(db: DbSession, current_user: CurrentUser, data: schemas.ModePaiementCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ModePaiementService(db).create(data)


@router.patch("/modes-paiement/{id}", response_model=schemas.ModePaiementResponse, tags=[TAG_MODES_PAIEMENT])
async def update_mode_paiement(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ModePaiementUpdate):
    ent = await ModePaiementService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ModePaiementService(db).update(id, data)


# --- Comptes trésorerie ---
@router.get("/comptes", response_model=list[schemas.CompteTresorerieResponse], tags=[TAG_COMPTES_TRESORERIE])
async def list_comptes_tresorerie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
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


@router.get("/comptes/{id}", response_model=schemas.CompteTresorerieResponse, tags=[TAG_COMPTES_TRESORERIE])
async def get_compte_tresorerie(db: DbSession, current_user: CurrentUser, id: int):
    ent = await CompteTresorerieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/comptes", response_model=schemas.CompteTresorerieResponse, status_code=201, tags=[TAG_COMPTES_TRESORERIE])
async def create_compte_tresorerie(db: DbSession, current_user: CurrentUser, data: schemas.CompteTresorerieCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CompteTresorerieService(db).create(data)


@router.patch("/comptes/{id}", response_model=schemas.CompteTresorerieResponse, tags=[TAG_COMPTES_TRESORERIE])
async def update_compte_tresorerie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CompteTresorerieUpdate):
    ent = await CompteTresorerieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CompteTresorerieService(db).update(id, data)


# --- Règlements ---
@router.get("/reglements", response_model=list[schemas.ReglementResponse], tags=[TAG_REGLEMENTS])
async def list_reglements(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
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


@router.get("/reglements/{id}", response_model=schemas.ReglementResponse, tags=[TAG_REGLEMENTS])
async def get_reglement(db: DbSession, current_user: CurrentUser, id: int):
    ent = await ReglementService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/reglements", response_model=schemas.ReglementResponse, status_code=201, tags=[TAG_REGLEMENTS])
async def create_reglement(db: DbSession, current_user: CurrentUser, data: schemas.ReglementCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ReglementService(db).create(data, created_by_id=getattr(current_user, "id", None))

