# app/modules/catalogue/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Catalogue (A.2) : familles_produits, unites_mesure,
# conditionnements, produits, taux_tva, produits_conditionnements, canaux_vente,
# prix_produits, variantes_produits. Noms de tables explicites (spécification).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    pass


# --- Enums (spécification A.2) ------------------------------------------------

class TypeUniteMesure(str, PyEnum):
    """Type d'unité de mesure."""
    unite = "unite"
    poids = "poids"
    volume = "volume"
    longueur = "longueur"
    autre = "autre"


class TypeProduit(str, PyEnum):
    """Type de produit (produit, service, composé)."""
    produit = "produit"
    service = "service"
    compose = "compose"


# --- Référentiels sans FK vers autres tables catalogue ------------------------

class UniteMesure(Base):
    """
    Référentiel des unités de mesure (PCE, KG, L, SACHET).
    Table : unites_mesure.
    """
    __tablename__ = "unites_mesure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    symbole: Mapped[str | None] = mapped_column(String(10), nullable=True)
    type: Mapped[str] = mapped_column(Enum(TypeUniteMesure), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class TauxTva(Base):
    """
    Référentiel des taux de TVA (CGI Cameroun : 0 %, 9,75 %, 10 %, 19,25 % ; Loi 2026 : 17,5 %).
    Conformité fiscale Cameroun / CEMAC. Table : taux_tva.
    """
    __tablename__ = "taux_tva"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    taux: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# --- Entités scopées entreprise (FK vers entreprises) -------------------------

class FamilleProduit(Base):
    """
    Catégorie ou famille de produits (hiérarchique via parent_id).
    Table : familles_produits.
    """
    __tablename__ = "familles_produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("familles_produits.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    niveau: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ordre_affichage: Mapped[int] = mapped_column(Integer, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_familles_produits_entreprise_code"),)

    parent: Mapped["FamilleProduit | None"] = relationship(
        "FamilleProduit", remote_side="FamilleProduit.id", back_populates="enfants"
    )
    enfants: Mapped[list["FamilleProduit"]] = relationship("FamilleProduit", back_populates="parent")
    produits: Mapped[list["Produit"]] = relationship("Produit", back_populates="famille")


class Conditionnement(Base):
    """
    Conditionnement de vente (carton, palette) : quantite_unites + unite_id.
    Table : conditionnements.
    """
    __tablename__ = "conditionnements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    quantite_unites: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unite_id: Mapped[int] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_conditionnements_entreprise_code"),)

    unite: Mapped["UniteMesure"] = relationship("UniteMesure")
    produits_conditionnements: Mapped[list["ProduitConditionnement"]] = relationship(
        "ProduitConditionnement", back_populates="conditionnement"
    )


class Produit(Base):
    """
    Article ou service vendu : code, libellé, unités, TVA, seuils, etc.
    Table : produits.
    """
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    famille_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("familles_produits.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    code_barre: Mapped[str | None] = mapped_column(String(50), nullable=True)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(Enum(TypeProduit), nullable=False, default=TypeProduit.produit)
    unite_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=False)
    unite_achat_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("unites_mesure.id"), nullable=True)
    coefficient_achat_vente: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1"))
    prix_achat_ht: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    prix_vente_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    taux_tva_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("taux_tva.id"), nullable=True)
    seuil_alerte_min: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0"))
    seuil_alerte_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    gerer_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_produits_entreprise_code"),)

    famille: Mapped["FamilleProduit | None"] = relationship("FamilleProduit", back_populates="produits")
    unite_vente: Mapped["UniteMesure"] = relationship("UniteMesure", foreign_keys=[unite_vente_id])
    unite_achat: Mapped["UniteMesure | None"] = relationship("UniteMesure", foreign_keys=[unite_achat_id])
    taux_tva: Mapped["TauxTva | None"] = relationship("TauxTva")
    produits_conditionnements: Mapped[list["ProduitConditionnement"]] = relationship(
        "ProduitConditionnement", back_populates="produit"
    )
    prix_produits: Mapped[list["PrixProduit"]] = relationship("PrixProduit", back_populates="produit")
    variantes: Mapped[list["VarianteProduit"]] = relationship("VarianteProduit", back_populates="produit")


class CanalVente(Base):
    """
    Canal de vente (détail, demi-gros, gros).
    Table : canaux_vente.
    """
    __tablename__ = "canaux_vente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_canaux_vente_entreprise_code"),)


# --- Liaison produit <-> conditionnement ---------------------------------------

class ProduitConditionnement(Base):
    """
    Liaison many-to-many produit / conditionnement : quantite + prix optionnel.
    Table : produits_conditionnements.
    """
    __tablename__ = "produits_conditionnements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    conditionnement_id: Mapped[int] = mapped_column(Integer, ForeignKey("conditionnements.id"), nullable=False)
    quantite_unites: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    prix_vente_ttc: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    __table_args__ = (
        UniqueConstraint("produit_id", "conditionnement_id", name="uq_produits_conditionnements_produit_cond"),
    )

    produit: Mapped["Produit"] = relationship("Produit", back_populates="produits_conditionnements")
    conditionnement: Mapped["Conditionnement"] = relationship("Conditionnement", back_populates="produits_conditionnements")


# --- Prix par canal / PDV -----------------------------------------------------

class PrixProduit(Base):
    """
    Prix de vente d'un produit selon canal et/ou point de vente (période validité).
    Table : prix_produits.
    """
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

    produit: Mapped["Produit"] = relationship("Produit", back_populates="prix_produits")


# --- Variantes produit --------------------------------------------------------

class VarianteProduit(Base):
    """
    Variante d'un produit (taille, couleur) avec supplément prix et stock séparé.
    Table : variantes_produits.
    """
    __tablename__ = "variantes_produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produit_id: Mapped[int] = mapped_column(Integer, ForeignKey("produits.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    prix_ttc_supplement: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    stock_separe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("produit_id", "code", name="uq_variantes_produits_produit_code"),)

    produit: Mapped["Produit"] = relationship("Produit", back_populates="variantes")
