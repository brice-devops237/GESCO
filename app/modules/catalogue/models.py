# app/modules/catalogue/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Catalogue : unités, TVA, familles, conditionnements,
# produits, variantes, canaux de vente, prix. Dépend de Paramétrage (entreprises, PDV).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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


class TypeUniteMesure(str, PyEnum):
    """Type d'unité de mesure."""
    unite = "unite"
    poids = "poids"
    volume = "volume"
    longueur = "longueur"
    surface = "surface"


class TypeProduit(str, PyEnum):
    """Type de produit."""
    produit = "produit"
    service = "service"
    composant = "composant"


# --- Unité de mesure ---------------------------------------------------------
class UniteMesure(Base):
    """Unité de mesure (kg, L, pièce, etc.). Table : unites_mesure."""
    __tablename__ = "unites_mesure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    symbole: Mapped[str | None] = mapped_column(String(10), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# --- Taux TVA (CGI Cameroun) -------------------------------------------------
class TauxTva(Base):
    """Taux de TVA. Table : taux_tva."""
    __tablename__ = "taux_tva"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    taux: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# --- Famille de produits -----------------------------------------------------
class FamilleProduit(Base):
    """Famille de produits (hiérarchie). Table : familles_produits."""
    __tablename__ = "familles_produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("familles_produits.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    niveau: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ordre_affichage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Conditionnement ---------------------------------------------------------
class Conditionnement(Base):
    """Conditionnement (caisse de 12, etc.). Table : conditionnements."""
    __tablename__ = "conditionnements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    quantite_unites: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unite_id: Mapped[int] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Produit -----------------------------------------------------------------
class Produit(Base):
    """Produit. Table : produits. Soft delete."""
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    famille_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("familles_produits.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    code_barre: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="produit")
    unite_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=False)
    unite_achat_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=True)
    coefficient_achat_vente: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    prix_achat_ht: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    prix_vente_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    taux_tva_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("taux_tva.id"), nullable=True)
    seuil_alerte_min: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False, default=0)
    seuil_alerte_max: Mapped[Decimal | None] = mapped_column(Numeric(18, 3), nullable=True)
    gerer_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# --- Liaison Produit / Conditionnement ---------------------------------------
class ProduitConditionnement(Base):
    """Liaison produit – conditionnement. Table : produits_conditionnements."""
    __tablename__ = "produits_conditionnements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    conditionnement_id: Mapped[int] = mapped_column(Integer, ForeignKey("conditionnements.id"), nullable=False)
    quantite_unites: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    prix_vente_ttc: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)


# --- Canal de vente (par entreprise) ------------------------------------------
class CanalVente(Base):
    """Canal de vente. Table : canaux_vente."""
    __tablename__ = "canaux_vente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_canaux_vente_entreprise_code"),
    )


# --- Prix produit (canal / PDV, période) -------------------------------------
class PrixProduit(Base):
    """Prix d'un produit par canal ou PDV. Table : prix_produits."""
    __tablename__ = "prix_produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    canal_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("canaux_vente.id"), nullable=True)
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)
    prix_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    prix_ht: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Variante produit --------------------------------------------------------
class VarianteProduit(Base):
    """Variante d'un produit. Table : variantes_produits."""
    __tablename__ = "variantes_produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    prix_ttc_supplement: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    stock_separe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
