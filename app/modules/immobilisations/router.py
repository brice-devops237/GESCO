# app/modules/immobilisations/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Immobilisations. Préfixe /immobilisations.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.immobilisations import schemas
from app.modules.immobilisations.services import CategorieImmobilisationService, ImmobilisationService

router = APIRouter(prefix="/immobilisations")

TAG_CATEGORIES = "Immobilisations - Catégories"
TAG_IMMOBILISATIONS = "Immobilisations - Immobilisations"
TAG_LIGNES_AMORTISSEMENT = "Immobilisations - Lignes d'amortissement"


# --- Catégories ---
@router.get("/categories", response_model=list[schemas.CategorieImmobilisationResponse], tags=[TAG_CATEGORIES])
async def list_categories(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await CategorieImmobilisationService(db).get_all(entreprise_id, skip=skip, limit=limit)
    return items


@router.get("/categories/{id}", response_model=schemas.CategorieImmobilisationResponse, tags=[TAG_CATEGORIES])
async def get_categorie(db: DbSession, current_user: CurrentUser, id: int):
    return await CategorieImmobilisationService(db).get_or_404(id)


@router.post("/categories", response_model=schemas.CategorieImmobilisationResponse, status_code=201, tags=[TAG_CATEGORIES])
async def create_categorie(db: DbSession, current_user: CurrentUser, data: schemas.CategorieImmobilisationCreate):
    return await CategorieImmobilisationService(db).create(data)


@router.patch("/categories/{id}", response_model=schemas.CategorieImmobilisationResponse, tags=[TAG_CATEGORIES])
async def update_categorie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CategorieImmobilisationUpdate):
    return await CategorieImmobilisationService(db).update(id, data)


# --- Immobilisations ---
@router.get("/actifs", response_model=list[schemas.ImmobilisationResponse], tags=[TAG_IMMOBILISATIONS])
async def list_immobilisations(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    categorie_id: int | None = None,
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await ImmobilisationService(db).get_all(
        entreprise_id=entreprise_id,
        categorie_id=categorie_id,
        actif_only=actif_only,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/actifs/{id}", response_model=schemas.ImmobilisationResponse, tags=[TAG_IMMOBILISATIONS])
async def get_immobilisation(db: DbSession, current_user: CurrentUser, id: int):
    return await ImmobilisationService(db).get_or_404(id)


@router.post("/actifs", response_model=schemas.ImmobilisationResponse, status_code=201, tags=[TAG_IMMOBILISATIONS])
async def create_immobilisation(db: DbSession, current_user: CurrentUser, data: schemas.ImmobilisationCreate):
    return await ImmobilisationService(db).create(data)


@router.patch("/actifs/{id}", response_model=schemas.ImmobilisationResponse, tags=[TAG_IMMOBILISATIONS])
async def update_immobilisation(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ImmobilisationUpdate):
    return await ImmobilisationService(db).update(id, data)


@router.get("/actifs/{id}/lignes-amortissement", response_model=list[schemas.LigneAmortissementResponse], tags=[TAG_LIGNES_AMORTISSEMENT])
async def list_lignes_amortissement(
    db: DbSession,
    current_user: CurrentUser,
    id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    """Lignes d'amortissement de l'actif (lecture seule)."""
    return await ImmobilisationService(db).get_lignes_amortissement(id, skip=skip, limit=limit)
