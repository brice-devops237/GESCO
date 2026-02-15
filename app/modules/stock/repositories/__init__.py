# app/modules/stock/repositories
# -----------------------------------------------------------------------------
# Couche Infrastructure : repositories du module Stock.
# -----------------------------------------------------------------------------
from app.modules.stock.repositories.stock_repository import StockRepository
from app.modules.stock.repositories.mouvement_stock_repository import MouvementStockRepository

__all__ = [
    "StockRepository",
    "MouvementStockRepository",
]
