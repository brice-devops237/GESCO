# app/modules/tresorerie/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Trésorerie : modes de paiement, comptes trésorerie,
# règlements (clients / fournisseurs). Dépend de Paramétrage, Partenaires,
# Commercial (factures), Achats (factures fournisseurs).
# Extension monde réel : isolation multi-tenant, toutes structures, tous secteurs.
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


class TypeCompteTresorerie(str, PyEnum):
    """Type de compte trésorerie (caisse ou bancaire)."""
    caisse = "caisse"
    bancaire = "bancaire"


class TypeReglement(str, PyEnum):
    """Type de règlement : client ou fournisseur."""
    client = "client"
    fournisseur = "fournisseur"


# --- Mode de paiement (référentiel par entreprise) ---------------------------
class ModePaiement(Base):
    """
    Mode de paiement (espèces, chèque, virement, mobile money, carte).
    Table : modes_paiement.
    """
    __tablename__ = "modes_paiement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    code_operateur: Mapped[str | None] = mapped_column(String(30), nullable=True)  # Ex. code Opérateur mobile money
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_modes_paiement_entreprise_code"),
    )


# --- Compte trésorerie (caisse ou compte bancaire) ---------------------------
class CompteTresorerie(Base):
    """
    Compte de trésorerie (caisse physique ou compte bancaire).
    Table : comptes_tresorerie.
    """
    __tablename__ = "comptes_tresorerie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    type_compte: Mapped[str] = mapped_column(String(20), nullable=False)  # TypeCompteTresorerie
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    numero_compte: Mapped[str | None] = mapped_column(String(50), nullable=True)  # N° compte bancaire
    iban: Mapped[str | None] = mapped_column(String(34), nullable=True)  # IBAN si applicable
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "libelle", name="uq_comptes_tresorerie_entreprise_libelle"),
    )


# --- Règlement (paiement client ou fournisseur) -------------------------------
class Reglement(Base):
    """
    Enregistrement d'un paiement : facture client ou facture fournisseur.
    Table : reglements.
    """
    __tablename__ = "reglements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    type_reglement: Mapped[str] = mapped_column(String(20), nullable=False)  # TypeReglement
    facture_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("factures.id"), nullable=True)  # client
    facture_fournisseur_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("factures_fournisseurs.id"), nullable=True
    )  # fournisseur
    tiers_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    date_reglement: Mapped[date] = mapped_column(Date, nullable=False)
    date_valeur: Mapped[date | None] = mapped_column(Date, nullable=True)  # Date de valeur (bancaire)
    mode_paiement_id: Mapped[int] = mapped_column(Integer, ForeignKey("modes_paiement.id"), nullable=False)
    compte_tresorerie_id: Mapped[int] = mapped_column(Integer, ForeignKey("comptes_tresorerie.id"), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)  # n° chèque, référence virement, etc.
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

