# app/modules/commercial/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Commercial (A.4). Chaque route instancie
# le service concerné avec la session DB et appelle les méthodes de la classe.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query
from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.commercial import schemas
from app.modules.commercial.services import (
    BonLivraisonService,
    CommandeService,
    DevisService,
    EtatDocumentService,
    FactureService,
)

router = APIRouter(prefix="/commercial", tags=["Commercial"])


# --- Etats document ---
@router.get("/etats-document", response_model=list[schemas.EtatDocumentResponse])
async def list_etats_document(
    db: DbSession, current_user: CurrentUser,
    type_document: str | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    return await EtatDocumentService(db).get_all(type_document=type_document, skip=skip, limit=limit)


@router.get("/etats-document/{id}", response_model=schemas.EtatDocumentResponse)
async def get_etat_document(db: DbSession, current_user: CurrentUser, id: int):
    return await EtatDocumentService(db).get_or_404(id)


@router.post("/etats-document", response_model=schemas.EtatDocumentResponse, status_code=201)
async def create_etat_document(db: DbSession, current_user: CurrentUser, data: schemas.EtatDocumentCreate):
    return await EtatDocumentService(db).create(data)


@router.patch("/etats-document/{id}", response_model=schemas.EtatDocumentResponse)
async def update_etat_document(db: DbSession, current_user: CurrentUser, id: int, data: schemas.EtatDocumentUpdate):
    return await EtatDocumentService(db).update(id, data)


# --- Devis ---
@router.get("/devis", response_model=list[schemas.DevisResponse])
async def list_devis(
    db: DbSession, current_user: CurrentUser,
    entreprise_id: int | None = None, client_id: int | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await DevisService(db).get_all(
        entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
    )
    return items


@router.get("/devis/{id}", response_model=schemas.DevisResponse)
async def get_devis(db: DbSession, current_user: CurrentUser, id: int):
    return await DevisService(db).get_or_404(id)


@router.post("/devis", response_model=schemas.DevisResponse, status_code=201)
async def create_devis(db: DbSession, current_user: CurrentUser, data: schemas.DevisCreate):
    return await DevisService(db).create(data)


@router.patch("/devis/{id}", response_model=schemas.DevisResponse)
async def update_devis(db: DbSession, current_user: CurrentUser, id: int, data: schemas.DevisUpdate):
    return await DevisService(db).update(id, data)


# --- Commandes ---
@router.get("/commandes", response_model=list[schemas.CommandeResponse])
async def list_commandes(
    db: DbSession, current_user: CurrentUser,
    entreprise_id: int | None = None, client_id: int | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await CommandeService(db).get_all(
        entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
    )
    return items


@router.get("/commandes/{id}", response_model=schemas.CommandeResponse)
async def get_commande(db: DbSession, current_user: CurrentUser, id: int):
    return await CommandeService(db).get_or_404(id)


@router.post("/commandes", response_model=schemas.CommandeResponse, status_code=201)
async def create_commande(db: DbSession, current_user: CurrentUser, data: schemas.CommandeCreate):
    return await CommandeService(db).create(data)


@router.patch("/commandes/{id}", response_model=schemas.CommandeResponse)
async def update_commande(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CommandeUpdate):
    return await CommandeService(db).update(id, data)


# --- Factures ---
@router.get("/factures", response_model=list[schemas.FactureResponse])
async def list_factures(
    db: DbSession, current_user: CurrentUser,
    entreprise_id: int | None = None, client_id: int | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await FactureService(db).get_all(
        entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
    )
    return items


@router.get("/factures/{id}", response_model=schemas.FactureResponse)
async def get_facture(db: DbSession, current_user: CurrentUser, id: int):
    return await FactureService(db).get_or_404(id)


@router.post("/factures", response_model=schemas.FactureResponse, status_code=201)
async def create_facture(db: DbSession, current_user: CurrentUser, data: schemas.FactureCreate):
    return await FactureService(db).create(data)


@router.patch("/factures/{id}", response_model=schemas.FactureResponse)
async def update_facture(db: DbSession, current_user: CurrentUser, id: int, data: schemas.FactureUpdate):
    return await FactureService(db).update(id, data)


# --- Bons de livraison ---
@router.get("/bons-livraison", response_model=list[schemas.BonLivraisonResponse])
async def list_bons_livraison(
    db: DbSession, current_user: CurrentUser,
    entreprise_id: int | None = None, client_id: int | None = None,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
):
    items, _ = await BonLivraisonService(db).get_all(
        entreprise_id=entreprise_id, client_id=client_id, skip=skip, limit=limit
    )
    return items


@router.get("/bons-livraison/{id}", response_model=schemas.BonLivraisonResponse)
async def get_bon_livraison(db: DbSession, current_user: CurrentUser, id: int):
    return await BonLivraisonService(db).get_or_404(id)


@router.post("/bons-livraison", response_model=schemas.BonLivraisonResponse, status_code=201)
async def create_bon_livraison(db: DbSession, current_user: CurrentUser, data: schemas.BonLivraisonCreate):
    return await BonLivraisonService(db).create(data)


@router.patch("/bons-livraison/{id}", response_model=schemas.BonLivraisonResponse)
async def update_bon_livraison(db: DbSession, current_user: CurrentUser, id: int, data: schemas.BonLivraisonUpdate):
    return await BonLivraisonService(db).update(id, data)
