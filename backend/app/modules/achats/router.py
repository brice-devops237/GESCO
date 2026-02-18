# app/modules/achats/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Achats. Isolation multi-tenant : toutes les
# lectures/mises à jour par id vérifient que la ressource appartient à
# l'entreprise de l'utilisateur. Adapté toute structure, tout secteur.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.core.exceptions import ForbiddenError
from app.modules.achats import schemas
from app.modules.achats.services import (
    CommandeFournisseurService,
    DepotService,
    FactureFournisseurService,
    ReceptionService,
)
from app.modules.parametrage.dependencies import CurrentUser, ValidatedEntrepriseId

router = APIRouter(prefix="/achats")

TAG_DEPOTS = "Achats - Dépôts"
TAG_COMMANDES_FOURNISSEURS = "Achats - Commandes fournisseurs"
TAG_RECEPTIONS = "Achats - Réceptions"
TAG_FACTURES_FOURNISSEURS = "Achats - Factures fournisseurs"


# --- Dépôts (entrepôts) ---
@router.get("/depots", response_model=list[schemas.DepotResponse], tags=[TAG_DEPOTS])
async def list_depots(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await DepotService(db).get_all(entreprise_id=entreprise_id, skip=skip, limit=limit)
    return items


@router.get("/depots/{id}", response_model=schemas.DepotResponse, tags=[TAG_DEPOTS])
async def get_depot(db: DbSession, current_user: CurrentUser, id: int):
    ent = await DepotService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/depots", response_model=schemas.DepotResponse, status_code=201, tags=[TAG_DEPOTS])
async def create_depot(db: DbSession, current_user: CurrentUser, data: schemas.DepotCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await DepotService(db).create(data)


@router.patch("/depots/{id}", response_model=schemas.DepotResponse, tags=[TAG_DEPOTS])
async def update_depot(db: DbSession, current_user: CurrentUser, id: int, data: schemas.DepotUpdate):
    ent = await DepotService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await DepotService(db).update(id, data)


# --- Commandes fournisseurs ---
@router.get("/commandes-fournisseurs", response_model=list[schemas.CommandeFournisseurResponse], tags=[TAG_COMMANDES_FOURNISSEURS])
async def list_commandes_fournisseurs(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    fournisseur_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await CommandeFournisseurService(db).get_all(
        entreprise_id=entreprise_id, fournisseur_id=fournisseur_id, skip=skip, limit=limit
    )
    return items


@router.get("/commandes-fournisseurs/{commande_id}/receptions", response_model=list[schemas.ReceptionResponse], tags=[TAG_RECEPTIONS])
async def list_receptions_by_commande(
    db: DbSession, current_user: CurrentUser, commande_id: int,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    cmd = await CommandeFournisseurService(db).get_or_404(commande_id)
    if cmd.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    items, _ = await ReceptionService(db).get_by_commande(commande_id, skip=skip, limit=limit)
    return items


@router.get("/commandes-fournisseurs/{id}", response_model=schemas.CommandeFournisseurResponse, tags=[TAG_COMMANDES_FOURNISSEURS])
async def get_commande_fournisseur(db: DbSession, current_user: CurrentUser, id: int):
    ent = await CommandeFournisseurService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/commandes-fournisseurs", response_model=schemas.CommandeFournisseurResponse, status_code=201, tags=[TAG_COMMANDES_FOURNISSEURS])
async def create_commande_fournisseur(db: DbSession, current_user: CurrentUser, data: schemas.CommandeFournisseurCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CommandeFournisseurService(db).create(data)


@router.patch("/commandes-fournisseurs/{id}", response_model=schemas.CommandeFournisseurResponse, tags=[TAG_COMMANDES_FOURNISSEURS])
async def update_commande_fournisseur(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CommandeFournisseurUpdate):
    ent = await CommandeFournisseurService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CommandeFournisseurService(db).update(id, data)


# --- Réceptions ---
@router.post("/receptions", response_model=schemas.ReceptionResponse, status_code=201, tags=[TAG_RECEPTIONS])
async def create_reception(db: DbSession, current_user: CurrentUser, data: schemas.ReceptionCreate):
    cmd = await CommandeFournisseurService(db).get_or_404(data.commande_fournisseur_id)
    if cmd.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    depot = await DepotService(db).get_or_404(data.depot_id)
    if depot.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ReceptionService(db).create(data)


@router.get("/receptions/{id}", response_model=schemas.ReceptionResponse, tags=[TAG_RECEPTIONS])
async def get_reception(db: DbSession, current_user: CurrentUser, id: int):
    ent = await ReceptionService(db).get_or_404(id)
    cmd = await CommandeFournisseurService(db).get_by_id(ent.commande_fournisseur_id)
    if not cmd or cmd.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.patch("/receptions/{id}", response_model=schemas.ReceptionResponse, tags=[TAG_RECEPTIONS])
async def update_reception(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ReceptionUpdate):
    ent = await ReceptionService(db).get_or_404(id)
    cmd = await CommandeFournisseurService(db).get_by_id(ent.commande_fournisseur_id)
    if not cmd or cmd.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ReceptionService(db).update(id, data)


# --- Factures fournisseurs ---
@router.get("/factures-fournisseurs", response_model=list[schemas.FactureFournisseurResponse], tags=[TAG_FACTURES_FOURNISSEURS])
async def list_factures_fournisseurs(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    fournisseur_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await FactureFournisseurService(db).get_all(
        entreprise_id=entreprise_id, fournisseur_id=fournisseur_id, skip=skip, limit=limit
    )
    return items


@router.get("/factures-fournisseurs/{id}", response_model=schemas.FactureFournisseurResponse, tags=[TAG_FACTURES_FOURNISSEURS])
async def get_facture_fournisseur(db: DbSession, current_user: CurrentUser, id: int):
    ent = await FactureFournisseurService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/factures-fournisseurs", response_model=schemas.FactureFournisseurResponse, status_code=201, tags=[TAG_FACTURES_FOURNISSEURS])
async def create_facture_fournisseur(db: DbSession, current_user: CurrentUser, data: schemas.FactureFournisseurCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await FactureFournisseurService(db).create(data)


@router.patch("/factures-fournisseurs/{id}", response_model=schemas.FactureFournisseurResponse, tags=[TAG_FACTURES_FOURNISSEURS])
async def update_facture_fournisseur(db: DbSession, current_user: CurrentUser, id: int, data: schemas.FactureFournisseurUpdate):
    ent = await FactureFournisseurService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await FactureFournisseurService(db).update(id, data)

