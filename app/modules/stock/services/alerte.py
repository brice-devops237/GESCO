# app/modules/stock/services/alerte.py
# -----------------------------------------------------------------------------
# Service métier : alertes de stock (sous seuil min / au-dessus seuil max).
# S'appuie sur les seuils du catalogue (Produit) et les stocks par dépôt.
# -----------------------------------------------------------------------------

from decimal import Decimal

from sqlalchemy import or_, select

from app.modules.achats.models import Depot
from app.modules.catalogue.models import Produit
from app.modules.stock.models import Stock
from app.modules.stock.schemas import AlerteStockResponse
from app.modules.stock.services.base import BaseStockService


class AlerteService(BaseStockService):
    """Liste des alertes (produits sous seuil min ou au-dessus seuil max)."""

    async def get_alertes(
        self, depot_id: int | None = None, *, skip: int = 0, limit: int = 200
    ) -> list[AlerteStockResponse]:
        """
        Retourne les lignes de stock pour lesquelles le produit a gerer_stock=True
        et (quantite < seuil_alerte_min ou quantite > seuil_alerte_max).
        """
        # Sous seuil min OU au-dessus seuil max (si défini)
        q = (
            select(Stock, Produit, Depot)
            .join(Produit, Stock.produit_id == Produit.id)
            .join(Depot, Stock.depot_id == Depot.id)
            .where(Produit.gerer_stock.is_(True))
            .where(Produit.deleted_at.is_(None))
            .where(
                or_(
                    Stock.quantite < Produit.seuil_alerte_min,
                    (Produit.seuil_alerte_max.isnot(None)) & (Stock.quantite > Produit.seuil_alerte_max),
                )
            )
        )
        if depot_id is not None:
            q = q.where(Stock.depot_id == depot_id)
        q = q.offset(skip).limit(limit)
        r = await self._db.execute(q)
        rows = r.all()
        result: list[AlerteStockResponse] = []
        for stock, produit, depot in rows:
            qte = stock.quantite
            seuil_min = produit.seuil_alerte_min or Decimal("0")
            seuil_max = produit.seuil_alerte_max
            type_alerte = "sous_seuil" if qte < seuil_min else "au_dessus_max"
            result.append(
                AlerteStockResponse(
                    produit_id=produit.id,
                    produit_code=produit.code,
                    produit_libelle=produit.libelle,
                    depot_id=depot.id,
                    depot_libelle=depot.libelle,
                    variante_id=stock.variante_id,
                    variante_libelle=None,
                    quantite=qte,
                    seuil_alerte_min=seuil_min,
                    seuil_alerte_max=seuil_max,
                    type_alerte=type_alerte,
                )
            )
        return result
