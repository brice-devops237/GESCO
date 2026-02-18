# app/modules/stock/services/stock.py
# -----------------------------------------------------------------------------
# Service métier : stocks (quantités par dépôt/produit/variante).
# -----------------------------------------------------------------------------

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.repositories import DepotRepository
from app.modules.catalogue.repositories import ProduitRepository
from app.modules.stock.models import Stock
from app.modules.stock.repositories import StockRepository
from app.modules.stock.services.base import BaseStockService
from app.modules.stock.services.messages import Messages


class StockService(BaseStockService):
    """Service de gestion des stocks (lecture, get_or_create)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = StockRepository(db)
        self._depot_repo = DepotRepository(db)
        self._produit_repo = ProduitRepository(db)

    async def get_by_id(self, id: int) -> Stock | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Stock:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.STOCK_NOT_FOUND)
        return ent

    async def get_by_id_and_depot(self, stock_id: int, depot_id: int) -> Stock:
        """Retourne le stock par id et dépôt, ou 404 si absent / dépôt incohérent."""
        if await self._depot_repo.find_by_id(depot_id) is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        ent = await self._repo.find_by_id(stock_id)
        if ent is None:
            self._raise_not_found(Messages.STOCK_NOT_FOUND)
        if ent.depot_id != depot_id:
            self._raise_not_found(Messages.STOCK_NOT_FOUND)
        return ent

    async def get_by_depot(
        self, depot_id: int, *, skip: int = 0, limit: int = 200
    ) -> tuple[list[Stock], int]:
        if await self._depot_repo.find_by_id(depot_id) is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        return await self._repo.find_by_depot(depot_id, skip=skip, limit=limit)

    async def get_by_produit(
        self, produit_id: int, *, skip: int = 0, limit: int = 200
    ) -> tuple[list[Stock], int]:
        if await self._produit_repo.find_by_id(produit_id) is None:
            self._raise_not_found(Messages.PRODUIT_NOT_FOUND)
        return await self._repo.find_by_produit(produit_id, skip=skip, limit=limit)

    async def get_quantite(
        self, depot_id: int, produit_id: int, variante_id: int | None = None
    ) -> Decimal:
        """Retourne la quantité en stock (0 si pas de ligne)."""
        if await self._depot_repo.find_by_id(depot_id) is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        if await self._produit_repo.find_by_id(produit_id) is None:
            self._raise_not_found(Messages.PRODUIT_NOT_FOUND)
        row = await self._repo.find_by_depot_produit_variante(
            depot_id, produit_id, variante_id
        )
        return row.quantite if row else Decimal("0")

    async def get_or_create_stock(
        self,
        depot_id: int,
        produit_id: int,
        variante_id: int | None,
        unite_id: int,
    ) -> Stock:
        """Retourne la ligne de stock existante ou en crée une à 0."""
        row = await self._repo.find_by_depot_produit_variante(
            depot_id, produit_id, variante_id
        )
        if row is not None:
            return row
        row = Stock(
            depot_id=depot_id,
            produit_id=produit_id,
            variante_id=variante_id,
            quantite=Decimal("0"),
            unite_id=unite_id,
        )
        return await self._repo.add(row)

