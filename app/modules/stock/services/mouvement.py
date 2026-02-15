# app/modules/stock/services/mouvement.py
# -----------------------------------------------------------------------------
# Service métier : mouvements de stock (création + mise à jour des stocks).
# -----------------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.repositories import DepotRepository
from app.modules.catalogue.repositories import ProduitRepository, VarianteProduitRepository
from app.modules.stock.models import MouvementStock, TypeMouvementStock, ReferenceTypeMouvement
from app.modules.stock.repositories import MouvementStockRepository, StockRepository
from app.modules.stock.schemas import MouvementStockCreate
from app.modules.stock.services.base import BaseStockService
from app.modules.stock.services.messages import Messages
from app.modules.stock.services.stock import StockService


class MouvementService(BaseStockService):
    """Création de mouvements et mise à jour des niveaux de stock."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = MouvementStockRepository(db)
        self._stock_repo = StockRepository(db)
        self._depot_repo = DepotRepository(db)
        self._produit_repo = ProduitRepository(db)
        self._variante_repo = VarianteProduitRepository(db)
        self._stock_svc = StockService(db)

    def _validate_type_mouvement(self, value: str) -> None:
        valid = [e.value for e in TypeMouvementStock]
        if value not in valid:
            self._raise_bad_request(Messages.TYPE_MOUVEMENT_INVALIDE.format(valeur=value))

    def _validate_reference_type(self, value: str) -> None:
        valid = [e.value for e in ReferenceTypeMouvement]
        if value not in valid:
            self._raise_bad_request(Messages.REFERENCE_TYPE_INVALIDE.format(valeur=value))

    async def get_by_id(self, id: int) -> MouvementStock | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> MouvementStock:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.MOUVEMENT_NOT_FOUND)
        return ent

    async def list_mouvements(
        self,
        *,
        depot_id: int | None = None,
        produit_id: int | None = None,
        type_mouvement: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[MouvementStock], int]:
        date_from_dt = None
        date_to_dt = None
        if date_from is not None:
            try:
                date_from_dt = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                self._raise_bad_request(Messages.DATE_MOUVEMENT_INVALIDE)
        if date_to is not None:
            try:
                date_to_dt = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                self._raise_bad_request(Messages.DATE_MOUVEMENT_INVALIDE)
        return await self._repo.find_all(
            depot_id=depot_id,
            produit_id=produit_id,
            type_mouvement=type_mouvement,
            date_from=date_from_dt,
            date_to=date_to_dt,
            skip=skip,
            limit=limit,
        )

    async def create(
        self, data: MouvementStockCreate, created_by_id: int | None = None
    ) -> MouvementStock:
        self._validate_type_mouvement(data.type_mouvement)
        self._validate_reference_type(data.reference_type)

        if await self._depot_repo.find_by_id(data.depot_id) is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)

        produit = await self._produit_repo.find_by_id(data.produit_id)
        if produit is None:
            self._raise_not_found(Messages.PRODUIT_NOT_FOUND)
        if not produit.gerer_stock:
            self._raise_bad_request(Messages.PRODUIT_STOCK_NON_GERE)

        variante_id = data.variante_id
        if variante_id is not None:
            variante = await self._variante_repo.find_by_id(variante_id)
            if variante is None or variante.produit_id != produit.id:
                self._raise_not_found(Messages.VARIANTE_NOT_FOUND)
            if not variante.stock_separe:
                self._raise_bad_request(Messages.VARIANTE_STOCK_NON_SEPARE)

        unite_id = produit.unite_vente_id
        qte = data.quantite

        if data.type_mouvement == TypeMouvementStock.transfert.value:
            if data.depot_dest_id is None:
                self._raise_bad_request(Messages.TRANSFERT_DEPOT_DEST_OBLIGATOIRE)
            if data.depot_dest_id == data.depot_id:
                self._raise_bad_request(Messages.TRANSFERT_MEME_DEPOT)
            if await self._depot_repo.find_by_id(data.depot_dest_id) is None:
                self._raise_not_found(Messages.DEPOT_NOT_FOUND)

        # Get or create stock rows and apply movement
        if data.type_mouvement == TypeMouvementStock.entree.value:
            stock = await self._stock_svc.get_or_create_stock(
                data.depot_id, data.produit_id, variante_id, unite_id
            )
            stock.quantite += qte
            await self._stock_repo.update(stock)
        elif data.type_mouvement == TypeMouvementStock.sortie.value:
            stock = await self._stock_svc.get_or_create_stock(
                data.depot_id, data.produit_id, variante_id, unite_id
            )
            if stock.quantite < qte:
                self._raise_bad_request(
                    Messages.QUANTITE_INSUFFISANTE.format(
                        depot_id=data.depot_id, produit_id=data.produit_id
                    )
                )
            stock.quantite -= qte
            await self._stock_repo.update(stock)
        elif data.type_mouvement == TypeMouvementStock.transfert.value:
            st_orig = await self._stock_svc.get_or_create_stock(
                data.depot_id, data.produit_id, variante_id, unite_id
            )
            if st_orig.quantite < qte:
                self._raise_bad_request(
                    Messages.QUANTITE_INSUFFISANTE.format(
                        depot_id=data.depot_id, produit_id=data.produit_id
                    )
                )
            st_orig.quantite -= qte
            await self._stock_repo.update(st_orig)
            st_dest = await self._stock_svc.get_or_create_stock(
                data.depot_dest_id, data.produit_id, variante_id, unite_id
            )
            st_dest.quantite += qte
            await self._stock_repo.update(st_dest)
        elif data.type_mouvement == TypeMouvementStock.inventaire.value:
            stock = await self._stock_svc.get_or_create_stock(
                data.depot_id, data.produit_id, variante_id, unite_id
            )
            stock.quantite = qte
            await self._stock_repo.update(stock)
        else:
            self._raise_bad_request(Messages.TYPE_MOUVEMENT_INVALIDE.format(valeur=data.type_mouvement))

        mouvement = MouvementStock(
            type_mouvement=data.type_mouvement,
            depot_id=data.depot_id,
            depot_dest_id=data.depot_dest_id,
            produit_id=data.produit_id,
            variante_id=variante_id,
            quantite=qte,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            notes=data.notes,
            created_by_id=created_by_id,
        )
        return await self._repo.add(mouvement)
