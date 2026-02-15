# app/modules/stock/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Stock. Préfixe /stock.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.stock import schemas
from app.modules.stock.services import StockService, MouvementService, AlerteService

router = APIRouter(prefix="/stock")

TAG_STOCKS = "Stock - Stocks"
TAG_MOUVEMENTS = "Stock - Mouvements de stock"
TAG_ALERTES = "Stock - Alertes"


# --- Stocks par dépôt ---
@router.get("/depots/{depot_id}/stocks", response_model=list[schemas.StockResponse], tags=[TAG_STOCKS])
async def list_stocks_by_depot(
    db: DbSession,
    current_user: CurrentUser,
    depot_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await StockService(db).get_by_depot(depot_id, skip=skip, limit=limit)
    return items


@router.get("/depots/{depot_id}/stocks/{stock_id}", response_model=schemas.StockResponse, tags=[TAG_STOCKS])
async def get_stock(db: DbSession, current_user: CurrentUser, depot_id: int, stock_id: int):
    return await StockService(db).get_by_id_and_depot(stock_id, depot_id)


@router.get(
    "/depots/{depot_id}/produits/{produit_id}/quantite",
    response_model=schemas.QuantiteStockResponse,
    summary="Quantité en stock (dépôt × produit × variante optionnelle)",
    tags=[TAG_STOCKS],
)
async def get_quantite_stock(
    db: DbSession,
    current_user: CurrentUser,
    depot_id: int,
    produit_id: int,
    variante_id: int | None = Query(None, description="Variante (si stock séparé)"),
):
    """Retourne la quantité en stock pour un dépôt, produit et optionnellement une variante."""
    qte = await StockService(db).get_quantite(depot_id, produit_id, variante_id)
    return schemas.QuantiteStockResponse(
        depot_id=depot_id, produit_id=produit_id, variante_id=variante_id, quantite=qte
    )


# --- Stocks par produit ---
@router.get("/produits/{produit_id}/stocks", response_model=list[schemas.StockResponse], tags=[TAG_STOCKS])
async def list_stocks_by_produit(
    db: DbSession,
    current_user: CurrentUser,
    produit_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await StockService(db).get_by_produit(produit_id, skip=skip, limit=limit)
    return items


# --- Mouvements ---
@router.get("/mouvements", response_model=list[schemas.MouvementStockResponse], tags=[TAG_MOUVEMENTS])
async def list_mouvements(
    db: DbSession,
    current_user: CurrentUser,
    depot_id: int | None = None,
    produit_id: int | None = None,
    type_mouvement: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await MouvementService(db).list_mouvements(
        depot_id=depot_id,
        produit_id=produit_id,
        type_mouvement=type_mouvement,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/mouvements/{id}", response_model=schemas.MouvementStockResponse, tags=[TAG_MOUVEMENTS])
async def get_mouvement(db: DbSession, current_user: CurrentUser, id: int):
    return await MouvementService(db).get_or_404(id)


@router.post("/mouvements", response_model=schemas.MouvementStockResponse, status_code=201, tags=[TAG_MOUVEMENTS])
async def create_mouvement(
    db: DbSession, current_user: CurrentUser, data: schemas.MouvementStockCreate
):
    return await MouvementService(db).create(data, created_by_id=getattr(current_user, "id", None))


# --- Alertes ---
@router.get("/alertes", response_model=list[schemas.AlerteStockResponse], tags=[TAG_ALERTES])
async def list_alertes(
    db: DbSession,
    current_user: CurrentUser,
    depot_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    return await AlerteService(db).get_alertes(depot_id=depot_id, skip=skip, limit=limit)
