# app/modules/stock/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Stock : stocks (quantités par dépôt/produit/variante),
# mouvements_stock (traçabilité). Dépend de Achats (Depot) et Catalogue (Produit, VarianteProduit).
# Extension monde réel : isolation multi-tenant, toutes structures, tous secteurs.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    ...


class TypeMouvementStock(str, PyEnum):
    """Type de mouvement : entrée, sortie, transfert ou inventaire."""
    entree = "entree"
    sortie = "sortie"
    transfert = "transfert"
    inventaire = "inventaire"


class ReferenceTypeMouvement(str, PyEnum):
    """Origine du mouvement (réception, BL, manuel, inventaire, transfert)."""
    reception = "reception"
    bon_livraison = "bon_livraison"
    manuel = "manuel"
    inventaire = "inventaire"
    transfert = "transfert"


# --- Stock (quantité par dépôt / produit / variante) -------------------------
class Stock(Base):
    """
    Niveau de stock par dépôt, produit et optionnellement variante.
    Table : stocks. Unicité (depot_id, produit_id, variante_id).
    """
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    depot_id: Mapped[int] = mapped_column(Integer, ForeignKey("depots.id"), nullable=False)
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    variante_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("variantes_produits.id"), nullable=True)
    quantite: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False, default=Decimal("0"))
    unite_id: Mapped[int] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("depot_id", "produit_id", "variante_id", name="uq_stocks_depot_produit_variante"),
    )


# --- MouvementStock (traçabilité) ---------------------------------------------
class MouvementStock(Base):
    """
    Ligne de mouvement de stock (entrée, sortie, transfert, inventaire).
    Table : mouvements_stock. Pour transfert : depot_id = origine, depot_dest_id = destination.
    """
    __tablename__ = "mouvements_stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_mouvement: Mapped[str] = mapped_column(String(20), nullable=False)  # TypeMouvementStock
    depot_id: Mapped[int] = mapped_column(Integer, ForeignKey("depots.id"), nullable=False)
    depot_dest_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("depots.id"), nullable=True)  # pour transfert
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    variante_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("variantes_produits.id"), nullable=True)
    quantite: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    lot_serie: Mapped[str | None] = mapped_column(String(80), nullable=True)  # N° lot / série pour traçabilité
    date_peremption: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_mouvement: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    reference_type: Mapped[str] = mapped_column(String(30), nullable=False)  # ReferenceTypeMouvement
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

