# app/modules/immobilisations/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Immobilisations : catégories, actifs, plans d'amortissement.
# Dépend de Paramétrage (entreprises), Comptabilité (comptes).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
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


# --- Catégorie d'immobilisation -------------------------------------------------
class CategorieImmobilisation(Base):
    """Catégorie d'actif (Matériel informatique, Véhicules, etc.). Table : categories_immobilisation."""
    __tablename__ = "categories_immobilisation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    duree_amortissement_annees: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    taux_amortissement: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)  # optionnel, ex. 20 pour 20%
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_categories_immobilisation_entreprise_code"),
    )


# --- Fiche d'immobilisation (actif) ---------------------------------------------
class Immobilisation(Base):
    """Actif immobilisé (véhicule, machine, etc.). Table : immobilisations."""
    __tablename__ = "immobilisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    categorie_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories_immobilisation.id"), nullable=False)
    compte_comptable_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comptes_comptables.id"), nullable=True)
    compte_amortissement_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comptes_comptables.id"), nullable=True)

    code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    designation: Mapped[str] = mapped_column(String(200), nullable=False)
    date_acquisition: Mapped[date] = mapped_column(Date, nullable=False)
    valeur_acquisition: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    duree_amortissement_annees: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    date_mise_en_service: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_immobilisations_entreprise_code"),
    )


# --- Ligne d'amortissement (annuelle ou mensuelle) -------------------------------
class LigneAmortissement(Base):
    """Ligne d'amortissement (dotations). Table : lignes_amortissement."""
    __tablename__ = "lignes_amortissement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    immobilisation_id: Mapped[int] = mapped_column(Integer, ForeignKey("immobilisations.id"), nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    mois: Mapped[int | None] = mapped_column(Integer, nullable=True)  # null = annuel
    montant_dotation: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    cumul_amortissement: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    valeur_nette: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    ecriture_comptable_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ecritures_comptables.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
