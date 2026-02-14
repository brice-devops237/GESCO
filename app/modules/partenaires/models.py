# app/modules/partenaires/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Partenaires (A.3) : types_tiers, tiers, contacts.
# Conformité : NIU DGI Cameroun, code pays ISO 3166-1 alpha-3 (CMR par défaut).
# -----------------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
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


# --- Référentiel type de tiers ------------------------------------------------

class TypeTiers(Base):
    """
    Type de tiers (client, fournisseur, client et fournisseur).
    Table : types_tiers.
    """
    __tablename__ = "types_tiers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)

    tiers: Mapped[list["Tiers"]] = relationship("Tiers", back_populates="type_tiers")


# --- Tiers (client / fournisseur) ---------------------------------------------

class Tiers(Base):
    """
    Partenaire (client et/ou fournisseur) : raison sociale, coordonnées, NIU (DGI),
    canal de vente, limite de crédit. Pays : ISO 3166-1 alpha-3. Table : tiers.
    """
    __tablename__ = "tiers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    type_tiers_id: Mapped[int] = mapped_column(Integer, ForeignKey("types_tiers.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    raison_sociale: Mapped[str] = mapped_column(String(255), nullable=False)
    nom_contact: Mapped[str | None] = mapped_column(String(150), nullable=True)
    niu: Mapped[str | None] = mapped_column(String(20), nullable=True)  # NIU DGI Cameroun
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pays: Mapped[str] = mapped_column(String(3), nullable=False, default="CMR")  # ISO 3166-1 alpha-3
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    telephone_secondaire: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canal_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("canaux_vente.id"), nullable=True)
    limite_credit: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    delai_paiement_jours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compte_bancaire: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mobile_money_numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mobile_money_operateur: Mapped[str | None] = mapped_column(String(20), nullable=True)
    segment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_tiers_entreprise_code"),)

    type_tiers: Mapped["TypeTiers"] = relationship("TypeTiers", back_populates="tiers")
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="tiers")


# --- Contact (personne rattachée à un tiers) ----------------------------------

class Contact(Base):
    """
    Personne de contact rattachée à un tiers (client ou fournisseur).
    Table : contacts.
    """
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tiers_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    prenom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fonction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    est_principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    tiers: Mapped["Tiers"] = relationship("Tiers", back_populates="contacts")
