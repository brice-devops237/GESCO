# app/modules/achats/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Achats (A.5). Chaque route instancie
# le service concerné avec la session DB et appelle les méthodes de la classe.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query
from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.achats import schemas
from app.modules.achats.services import (
    CommandeFournisseurService,
    ReceptionService,
    FactureFournisseurService,
)

router = APIRouter(prefix="/achats", tags=["Achats"])


# --- Commandes fournisseurs ---
@router.get("/commandes-fournisseurs", response_model=list[schemas.CommandeFournisseurResponse])
async def list_commandes_fournisseurs(
    db: DbSession, current_user: CurrentUser,
    entreprise_id: int | None = None, fournisseur_id: int | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await CommandeFournisseurService(db).get_all(
        entreprise_id=entreprise_id, fournisseur_id=fournisseur_id, skip=skip, limit=limit
    )
    return items


@router.get("/commandes-fournisseurs/{commande_id}/receptions", response_model=list[schemas.ReceptionResponse])
async def list_receptions_by_commande(
    db: DbSession, current_user: CurrentUser, commande_id: int,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await ReceptionService(db).get_by_commande(commande_id, skip=skip, limit=limit)
    return items


@router.get("/commandes-fournisseurs/{id}", response_model=schemas.CommandeFournisseurResponse)
async def get_commande_fournisseur(db: DbSession, current_user: CurrentUser, id: int):
    return await CommandeFournisseurService(db).get_or_404(id)


@router.post("/commandes-fournisseurs", response_model=schemas.CommandeFournisseurResponse, status_code=201)
async def create_commande_fournisseur(db: DbSession, current_user: CurrentUser, data: schemas.CommandeFournisseurCreate):
    return await CommandeFournisseurService(db).create(data)


@router.patch("/commandes-fournisseurs/{id}", response_model=schemas.CommandeFournisseurResponse)
async def update_commande_fournisseur(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CommandeFournisseurUpdate):
    return await CommandeFournisseurService(db).update(id, data)


# --- Réceptions ---
@router.post("/receptions", response_model=schemas.ReceptionResponse, status_code=201)
async def create_reception(db: DbSession, current_user: CurrentUser, data: schemas.ReceptionCreate):
    return await ReceptionService(db).create(data)


@router.get("/receptions/{id}", response_model=schemas.ReceptionResponse)
async def get_reception(db: DbSession, current_user: CurrentUser, id: int):
    return await ReceptionService(db).get_or_404(id)


@router.patch("/receptions/{id}", response_model=schemas.ReceptionResponse)
async def update_reception(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ReceptionUpdate):
    return await ReceptionService(db).update(id, data)


# --- Factures fournisseurs ---
@router.get("/factures-fournisseurs", response_model=list[schemas.FactureFournisseurResponse])
async def list_factures_fournisseurs(
    db: DbSession, current_user: CurrentUser,
    entreprise_id: int | None = None, fournisseur_id: int | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await FactureFournisseurService(db).get_all(
        entreprise_id=entreprise_id, fournisseur_id=fournisseur_id, skip=skip, limit=limit
    )
    return items


@router.get("/factures-fournisseurs/{id}", response_model=schemas.FactureFournisseurResponse)
async def get_facture_fournisseur(db: DbSession, current_user: CurrentUser, id: int):
    return await FactureFournisseurService(db).get_or_404(id)


@router.post("/factures-fournisseurs", response_model=schemas.FactureFournisseurResponse, status_code=201)
async def create_facture_fournisseur(db: DbSession, current_user: CurrentUser, data: schemas.FactureFournisseurCreate):
    return await FactureFournisseurService(db).create(data)


@router.patch("/factures-fournisseurs/{id}", response_model=schemas.FactureFournisseurResponse)
async def update_facture_fournisseur(db: DbSession, current_user: CurrentUser, id: int, data: schemas.FactureFournisseurUpdate):
    return await FactureFournisseurService(db).update(id, data)
