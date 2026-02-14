# app/modules/achats/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Achats : commandes_fournisseurs, receptions,
# factures_fournisseurs. Conformité : montants HT/TVA/TTC (Decimal), devise ISO 4217.
# Depot minimal pour FK (table depots). Table : commandes_fournisseurs, etc.
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
    pass


class StatutReception(str, PyEnum):
    brouillon = "brouillon"
    validee = "validee"
    annulee = "annulee"


class StatutPaiementFournisseur(str, PyEnum):
    non_paye = "non_paye"
    partiel = "partiel"
    paye = "paye"


# --- Depot (minimal, pour FK depuis commandes_fournisseurs / receptions) -------
class Depot(Base):
    """Dépôt (entrepôt) associé à un point de vente. Table : depots."""
    __tablename__ = "depots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Commande fournisseur ------------------------------------------------------
class CommandeFournisseur(Base):
    """Commande passée à un fournisseur. Table : commandes_fournisseurs."""
    __tablename__ = "commandes_fournisseurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    depot_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("depots.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    numero_fournisseur: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "numero", name="uq_commandes_fournisseurs_entreprise_numero"),)


# --- Réception -----------------------------------------------------------------
class Reception(Base):
    """Réception de marchandises. Table : receptions."""
    __tablename__ = "receptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commande_fournisseur_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("commandes_fournisseurs.id"), nullable=False
    )
    depot_id: Mapped[int] = mapped_column(Integer, ForeignKey("depots.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    date_reception: Mapped[date] = mapped_column(Date, nullable=False)
    etat: Mapped[str] = mapped_column(String(20), nullable=False, default="brouillon")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)


# --- Facture fournisseur -------------------------------------------------------
class FactureFournisseur(Base):
    """Facture reçue d'un fournisseur. Table : factures_fournisseurs."""
    __tablename__ = "factures_fournisseurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    commande_fournisseur_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("commandes_fournisseurs.id"), nullable=True
    )
    numero_fournisseur: Mapped[str] = mapped_column(String(50), nullable=False)
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_restant_du: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    statut_paiement: Mapped[str] = mapped_column(String(20), nullable=False, default="non_paye")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
