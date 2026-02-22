# app/modules/catalogue/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Catalogue. Isolation multi-tenant : listes
# par ValidatedEntrepriseId ; GET/PATCH/DELETE et POST vérifient entreprise.
# Adapté toute structure, tout secteur.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.core.exceptions import ForbiddenError
from app.modules.catalogue import schemas
from app.modules.catalogue.services import (
    CanalVenteService,
    ConditionnementService,
    FamilleProduitService,
    PrixProduitService,
    ProduitConditionnementService,
    ProduitService,
    TauxTvaService,
    UniteMesureService,
    VarianteProduitService,
)
from app.modules.parametrage.dependencies import CurrentUser, ValidatedEntrepriseId

router = APIRouter(prefix="/catalogue")

TAG_UNITES_MESURE = "Catalogue - Unités de mesure"
TAG_TAUX_TVA = "Catalogue - Taux TVA"
TAG_FAMILLES_PRODUITS = "Catalogue - Familles de produits"
TAG_CONDITIONNEMENTS = "Catalogue - Conditionnements"
TAG_PRODUITS = "Catalogue - Produits"
TAG_PRODUITS_CONDITIONNEMENTS = "Catalogue - Produits-Conditionnements"
TAG_CANAUX_VENTE = "Catalogue - Canaux de vente"
TAG_PRIX_PRODUITS = "Catalogue - Prix produits"
TAG_VARIANTES_PRODUIT = "Catalogue - Variantes produit"


# --- Unités de mesure ---

@router.get("/unites-mesure", response_model=list[schemas.UniteMesureResponse], tags=[TAG_UNITES_MESURE])
async def list_unites_mesure(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
):
    """Liste des unités de mesure."""
    return await UniteMesureService(db).get_all(skip=skip, limit=limit, actif_only=actif_only)


@router.get("/unites-mesure/{id}", response_model=schemas.UniteMesureResponse, tags=[TAG_UNITES_MESURE])
async def get_unite_mesure(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'une unité de mesure."""
    return await UniteMesureService(db).get_or_404(id)


@router.post("/unites-mesure", response_model=schemas.UniteMesureResponse, status_code=201, tags=[TAG_UNITES_MESURE])
async def create_unite_mesure(db: DbSession, current_user: CurrentUser, data: schemas.UniteMesureCreate):
    """Création d'une unité de mesure."""
    return await UniteMesureService(db).create(data)


@router.patch("/unites-mesure/{id}", response_model=schemas.UniteMesureResponse, tags=[TAG_UNITES_MESURE])
async def update_unite_mesure(db: DbSession, current_user: CurrentUser, id: int, data: schemas.UniteMesureUpdate):
    """Mise à jour partielle d'une unité de mesure."""
    return await UniteMesureService(db).update(id, data)


@router.delete("/unites-mesure/{id}", status_code=204, tags=[TAG_UNITES_MESURE])
async def delete_unite_mesure(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'une unité de mesure."""
    await UniteMesureService(db).delete(id)


# --- Taux TVA ---

@router.get("/taux-tva", response_model=list[schemas.TauxTvaResponse], tags=[TAG_TAUX_TVA])
async def list_taux_tva(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
):
    """Liste des taux de TVA."""
    return await TauxTvaService(db).get_all(skip=skip, limit=limit, actif_only=actif_only)


@router.get("/taux-tva/{id}", response_model=schemas.TauxTvaResponse, tags=[TAG_TAUX_TVA])
async def get_taux_tva(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un taux de TVA."""
    return await TauxTvaService(db).get_or_404(id)


@router.post("/taux-tva", response_model=schemas.TauxTvaResponse, status_code=201, tags=[TAG_TAUX_TVA])
async def create_taux_tva(db: DbSession, current_user: CurrentUser, data: schemas.TauxTvaCreate):
    """Création d'un taux de TVA."""
    return await TauxTvaService(db).create(data)


@router.patch("/taux-tva/{id}", response_model=schemas.TauxTvaResponse, tags=[TAG_TAUX_TVA])
async def update_taux_tva(db: DbSession, current_user: CurrentUser, id: int, data: schemas.TauxTvaUpdate):
    """Mise à jour partielle d'un taux de TVA."""
    return await TauxTvaService(db).update(id, data)


@router.delete("/taux-tva/{id}", status_code=204, tags=[TAG_TAUX_TVA])
async def delete_taux_tva(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'un taux de TVA."""
    await TauxTvaService(db).delete(id)


# --- Familles de produits ---

@router.get("/familles-produits", response_model=list[schemas.FamilleProduitResponse], tags=[TAG_FAMILLES_PRODUITS])
async def list_familles_produits(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des familles de produits."""
    items, _ = await FamilleProduitService(db).get_all(
        entreprise_id=entreprise_id, skip=skip, limit=limit, actif_only=actif_only, search=search
    )
    return items


@router.get("/familles-produits/{id}", response_model=schemas.FamilleProduitResponse, tags=[TAG_FAMILLES_PRODUITS])
async def get_famille_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'une famille de produits."""
    ent = await FamilleProduitService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/familles-produits", response_model=schemas.FamilleProduitResponse, status_code=201, tags=[TAG_FAMILLES_PRODUITS])
async def create_famille_produit(db: DbSession, current_user: CurrentUser, data: schemas.FamilleProduitCreate):
    """Création d'une famille de produits."""
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await FamilleProduitService(db).create(data)


@router.patch("/familles-produits/{id}", response_model=schemas.FamilleProduitResponse, tags=[TAG_FAMILLES_PRODUITS])
async def update_famille_produit(db: DbSession, current_user: CurrentUser, id: int, data: schemas.FamilleProduitUpdate):
    """Mise à jour partielle d'une famille de produits."""
    ent = await FamilleProduitService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await FamilleProduitService(db).update(id, data)


@router.delete("/familles-produits/{id}", status_code=204, tags=[TAG_FAMILLES_PRODUITS])
async def delete_famille_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Soft delete d'une famille de produits."""
    ent = await FamilleProduitService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await FamilleProduitService(db).delete_soft(id)


# --- Conditionnements ---

@router.get("/conditionnements", response_model=list[schemas.ConditionnementResponse], tags=[TAG_CONDITIONNEMENTS])
async def list_conditionnements(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des conditionnements."""
    items, _ = await ConditionnementService(db).get_all(
        entreprise_id=entreprise_id, skip=skip, limit=limit, actif_only=actif_only, search=search
    )
    return items


@router.get("/conditionnements/{id}", response_model=schemas.ConditionnementResponse, tags=[TAG_CONDITIONNEMENTS])
async def get_conditionnement(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un conditionnement."""
    ent = await ConditionnementService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/conditionnements", response_model=schemas.ConditionnementResponse, status_code=201, tags=[TAG_CONDITIONNEMENTS])
async def create_conditionnement(db: DbSession, current_user: CurrentUser, data: schemas.ConditionnementCreate):
    """Création d'un conditionnement."""
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ConditionnementService(db).create(data)


@router.patch("/conditionnements/{id}", response_model=schemas.ConditionnementResponse, tags=[TAG_CONDITIONNEMENTS])
async def update_conditionnement(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ConditionnementUpdate):
    """Mise à jour partielle d'un conditionnement."""
    ent = await ConditionnementService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ConditionnementService(db).update(id, data)


@router.delete("/conditionnements/{id}", status_code=204, tags=[TAG_CONDITIONNEMENTS])
async def delete_conditionnement(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'un conditionnement."""
    ent = await ConditionnementService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await ConditionnementService(db).delete(id)


# --- Produits ---

@router.get("/produits", response_model=list[schemas.ProduitResponse], tags=[TAG_PRODUITS])
async def list_produits(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    famille_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des produits."""
    items, _ = await ProduitService(db).get_all(
        entreprise_id=entreprise_id,
        famille_id=famille_id,
        skip=skip,
        limit=limit,
        actif_only=actif_only,
        search=search,
    )
    return items


@router.post("/produits", response_model=schemas.ProduitResponse, status_code=201, tags=[TAG_PRODUITS])
async def create_produit(db: DbSession, current_user: CurrentUser, data: schemas.ProduitCreate):
    """Création d'un produit."""
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ProduitService(db).create(data)


# Sous-routes produit (avant /produits/{id} pour éviter de capter le path)
@router.get("/produits/{produit_id}/conditionnements", response_model=list[schemas.ProduitConditionnementResponse], tags=[TAG_PRODUITS_CONDITIONNEMENTS])
async def list_produit_conditionnements(
    db: DbSession,
    current_user: CurrentUser,
    produit_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """Liste des conditionnements associés à un produit."""
    prod = await ProduitService(db).get_or_404(produit_id)
    if prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ProduitConditionnementService(db).get_by_produit(produit_id, skip=skip, limit=limit)


@router.get("/produits/{produit_id}/prix", response_model=list[schemas.PrixProduitResponse], tags=[TAG_PRIX_PRODUITS])
async def list_prix_by_produit(
    db: DbSession,
    current_user: CurrentUser,
    produit_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """Liste des prix d'un produit."""
    prod = await ProduitService(db).get_or_404(produit_id)
    if prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    items, _ = await PrixProduitService(db).get_by_produit(produit_id, skip=skip, limit=limit)
    return items


@router.get("/produits/{produit_id}/variantes", response_model=list[schemas.VarianteProduitResponse], tags=[TAG_VARIANTES_PRODUIT])
async def list_variantes_by_produit(
    db: DbSession,
    current_user: CurrentUser,
    produit_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
):
    """Liste des variantes d'un produit."""
    prod = await ProduitService(db).get_or_404(produit_id)
    if prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    items, _ = await VarianteProduitService(db).get_by_produit(
        produit_id, skip=skip, limit=limit, actif_only=actif_only
    )
    return items


@router.get("/produits/{id}", response_model=schemas.ProduitResponse, tags=[TAG_PRODUITS])
async def get_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un produit."""
    ent = await ProduitService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.patch("/produits/{id}", response_model=schemas.ProduitResponse, tags=[TAG_PRODUITS])
async def update_produit(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ProduitUpdate):
    """Mise à jour partielle d'un produit."""
    ent = await ProduitService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ProduitService(db).update(id, data)


@router.delete("/produits/{id}", status_code=204, tags=[TAG_PRODUITS])
async def delete_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Soft delete d'un produit."""
    ent = await ProduitService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await ProduitService(db).delete_soft(id)


# --- Produits-Conditionnements ---

@router.get("/produits-conditionnements/{id}", response_model=schemas.ProduitConditionnementResponse, tags=[TAG_PRODUITS_CONDITIONNEMENTS])
async def get_produit_conditionnement(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'une liaison produit-conditionnement."""
    ent = await ProduitConditionnementService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/produits-conditionnements", response_model=schemas.ProduitConditionnementResponse, status_code=201, tags=[TAG_PRODUITS_CONDITIONNEMENTS])
async def create_produit_conditionnement(db: DbSession, current_user: CurrentUser, data: schemas.ProduitConditionnementCreate):
    """Création d'une liaison produit-conditionnement."""
    prod = await ProduitService(db).get_or_404(data.produit_id)
    if prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ProduitConditionnementService(db).create(data)


@router.patch("/produits-conditionnements/{id}", response_model=schemas.ProduitConditionnementResponse, tags=[TAG_PRODUITS_CONDITIONNEMENTS])
async def update_produit_conditionnement(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ProduitConditionnementUpdate):
    """Mise à jour partielle d'une liaison produit-conditionnement."""
    ent = await ProduitConditionnementService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await ProduitConditionnementService(db).update(id, data)


@router.delete("/produits-conditionnements/{id}", status_code=204, tags=[TAG_PRODUITS_CONDITIONNEMENTS])
async def delete_produit_conditionnement(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'une liaison produit-conditionnement."""
    ent = await ProduitConditionnementService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await ProduitConditionnementService(db).delete(id)


# --- Canaux de vente ---

@router.get("/canaux-vente", response_model=list[schemas.CanalVenteResponse], tags=[TAG_CANAUX_VENTE])
async def list_canaux_vente(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des canaux de vente."""
    items, _ = await CanalVenteService(db).get_all(
        entreprise_id=entreprise_id, skip=skip, limit=limit, actif_only=actif_only, search=search
    )
    return items


@router.get("/canaux-vente/{id}", response_model=schemas.CanalVenteResponse, tags=[TAG_CANAUX_VENTE])
async def get_canal_vente(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un canal de vente."""
    ent = await CanalVenteService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/canaux-vente", response_model=schemas.CanalVenteResponse, status_code=201, tags=[TAG_CANAUX_VENTE])
async def create_canal_vente(db: DbSession, current_user: CurrentUser, data: schemas.CanalVenteCreate):
    """Création d'un canal de vente."""
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CanalVenteService(db).create(data)


@router.patch("/canaux-vente/{id}", response_model=schemas.CanalVenteResponse, tags=[TAG_CANAUX_VENTE])
async def update_canal_vente(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CanalVenteUpdate):
    """Mise à jour partielle d'un canal de vente."""
    ent = await CanalVenteService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CanalVenteService(db).update(id, data)


@router.delete("/canaux-vente/{id}", status_code=204, tags=[TAG_CANAUX_VENTE])
async def delete_canal_vente(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'un canal de vente."""
    ent = await CanalVenteService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await CanalVenteService(db).delete(id)


# --- Prix produits ---

@router.get("/prix-produits", response_model=list[schemas.PrixProduitResponse], tags=[TAG_PRIX_PRODUITS])
async def list_prix_produits(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """Liste des prix produits de l'entreprise."""
    items, _ = await PrixProduitService(db).get_all(entreprise_id=entreprise_id, skip=skip, limit=limit)
    return items


@router.get("/prix-produits/{id}", response_model=schemas.PrixProduitResponse, tags=[TAG_PRIX_PRODUITS])
async def get_prix_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un prix produit."""
    ent = await PrixProduitService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/prix-produits", response_model=schemas.PrixProduitResponse, status_code=201, tags=[TAG_PRIX_PRODUITS])
async def create_prix_produit(db: DbSession, current_user: CurrentUser, data: schemas.PrixProduitCreate):
    """Création d'un prix produit."""
    prod = await ProduitService(db).get_or_404(data.produit_id)
    if prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PrixProduitService(db).create(data)


@router.patch("/prix-produits/{id}", response_model=schemas.PrixProduitResponse, tags=[TAG_PRIX_PRODUITS])
async def update_prix_produit(db: DbSession, current_user: CurrentUser, id: int, data: schemas.PrixProduitUpdate):
    """Mise à jour partielle d'un prix produit."""
    ent = await PrixProduitService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PrixProduitService(db).update(id, data)


@router.delete("/prix-produits/{id}", status_code=204, tags=[TAG_PRIX_PRODUITS])
async def delete_prix_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'un prix produit."""
    ent = await PrixProduitService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await PrixProduitService(db).delete(id)


# --- Variantes produit ---

@router.get("/variantes-produits/{id}", response_model=schemas.VarianteProduitResponse, tags=[TAG_VARIANTES_PRODUIT])
async def get_variante_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'une variante de produit."""
    ent = await VarianteProduitService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/variantes-produits", response_model=schemas.VarianteProduitResponse, status_code=201, tags=[TAG_VARIANTES_PRODUIT])
async def create_variante_produit(db: DbSession, current_user: CurrentUser, data: schemas.VarianteProduitCreate):
    """Création d'une variante de produit."""
    prod = await ProduitService(db).get_or_404(data.produit_id)
    if prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await VarianteProduitService(db).create(data)


@router.patch("/variantes-produits/{id}", response_model=schemas.VarianteProduitResponse, tags=[TAG_VARIANTES_PRODUIT])
async def update_variante_produit(db: DbSession, current_user: CurrentUser, id: int, data: schemas.VarianteProduitUpdate):
    """Mise à jour partielle d'une variante de produit."""
    ent = await VarianteProduitService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await VarianteProduitService(db).update(id, data)


@router.delete("/variantes-produits/{id}", status_code=204, tags=[TAG_VARIANTES_PRODUIT])
async def delete_variante_produit(db: DbSession, current_user: CurrentUser, id: int):
    """Suppression d'une variante de produit."""
    ent = await VarianteProduitService(db).get_or_404(id)
    prod = await ProduitService(db).get_by_id(ent.produit_id)
    if not prod or prod.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await VarianteProduitService(db).delete(id)

