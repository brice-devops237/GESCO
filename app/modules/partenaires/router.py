# app/modules/partenaires/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Partenaires (A.3). Chaque route instancie
# le service concerné avec la session DB et appelle les méthodes de la classe.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.partenaires import schemas
from app.modules.partenaires.services import ContactService, TiersService, TypeTiersService

router = APIRouter(prefix="/partenaires")

TAG_TYPES_TIERS = "Partenaires - Types de tiers"
TAG_TIERS = "Partenaires - Tiers"
TAG_CONTACTS = "Partenaires - Contacts"


# --- Types de tiers ---

@router.get("/types-tiers", response_model=list[schemas.TypeTiersResponse], tags=[TAG_TYPES_TIERS])
async def list_types_tiers(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """Liste des types de tiers (client, fournisseur, etc.)."""
    return await TypeTiersService(db).get_all(skip=skip, limit=limit)


@router.get("/types-tiers/{id}", response_model=schemas.TypeTiersResponse, tags=[TAG_TYPES_TIERS])
async def get_type_tiers(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un type de tiers."""
    return await TypeTiersService(db).get_or_404(id)


@router.post("/types-tiers", response_model=schemas.TypeTiersResponse, status_code=201, tags=[TAG_TYPES_TIERS])
async def create_type_tiers(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.TypeTiersCreate,
):
    """Création d'un type de tiers."""
    return await TypeTiersService(db).create(data)


@router.patch("/types-tiers/{id}", response_model=schemas.TypeTiersResponse, tags=[TAG_TYPES_TIERS])
async def update_type_tiers(
    db: DbSession,
    current_user: CurrentUser,
    id: int,
    data: schemas.TypeTiersUpdate,
):
    """Mise à jour partielle d'un type de tiers."""
    return await TypeTiersService(db).update(id, data)


# --- Tiers (clients / fournisseurs) ---

@router.get("/tiers", response_model=list[schemas.TiersResponse], tags=[TAG_TIERS])
async def list_tiers(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int | None = None,
    type_tiers_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des tiers (clients, fournisseurs)."""
    items, _ = await TiersService(db).get_all(
        entreprise_id=entreprise_id,
        type_tiers_id=type_tiers_id,
        skip=skip,
        limit=limit,
        actif_only=actif_only,
        search=search,
    )
    return items


@router.post("/tiers", response_model=schemas.TiersResponse, status_code=201, tags=[TAG_TIERS])
async def create_tiers(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.TiersCreate,
):
    """Création d'un tiers (client ou fournisseur)."""
    return await TiersService(db).create(data)


@router.get("/tiers/{tiers_id}/contacts", response_model=list[schemas.ContactResponse], tags=[TAG_CONTACTS])
async def list_contacts_by_tiers(
    db: DbSession,
    current_user: CurrentUser,
    tiers_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
):
    """Liste des contacts d'un tiers."""
    items, _ = await ContactService(db).get_by_tiers(
        tiers_id, skip=skip, limit=limit, actif_only=actif_only
    )
    return items


@router.get("/tiers/{id}", response_model=schemas.TiersResponse, tags=[TAG_TIERS])
async def get_tiers(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un tiers."""
    return await TiersService(db).get_or_404(id)


@router.patch("/tiers/{id}", response_model=schemas.TiersResponse, tags=[TAG_TIERS])
async def update_tiers(
    db: DbSession,
    current_user: CurrentUser,
    id: int,
    data: schemas.TiersUpdate,
):
    """Mise à jour partielle d'un tiers."""
    return await TiersService(db).update(id, data)


@router.delete("/tiers/{id}", status_code=204, tags=[TAG_TIERS])
async def delete_tiers(db: DbSession, current_user: CurrentUser, id: int):
    """Soft delete d'un tiers."""
    await TiersService(db).delete_soft(id)


# --- Contacts ---

@router.post("/contacts", response_model=schemas.ContactResponse, status_code=201, tags=[TAG_CONTACTS])
async def create_contact(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.ContactCreate,
):
    """Création d'un contact."""
    return await ContactService(db).create(data)


@router.get("/contacts/{id}", response_model=schemas.ContactResponse, tags=[TAG_CONTACTS])
async def get_contact(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un contact."""
    return await ContactService(db).get_or_404(id)


@router.patch("/contacts/{id}", response_model=schemas.ContactResponse, tags=[TAG_CONTACTS])
async def update_contact(
    db: DbSession,
    current_user: CurrentUser,
    id: int,
    data: schemas.ContactUpdate,
):
    """Mise à jour partielle d'un contact."""
    return await ContactService(db).update(id, data)


@router.delete("/contacts/{id}", status_code=204, tags=[TAG_CONTACTS])
async def delete_contact(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'un contact."""
    await ContactService(db).delete(id)
