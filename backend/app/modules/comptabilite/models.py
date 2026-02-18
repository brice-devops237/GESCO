# app/modules/comptabilite/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Comptabilité : plan comptable (comptes), journaux,
# périodes comptables, écritures et lignes d'écriture. Conforme OHADA/CEMAC.
# Dépend de Paramétrage (entreprises, utilisateurs). Conçu pour toute structure
# (PME à grand groupe) et tout secteur : plan/journaux/périodes par entreprise,
# période optionnelle sur écriture, traçabilité.
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
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    ...


class SensCompte(str, PyEnum):
    """Sens normal du compte (débit ou crédit)."""
    debit = "debit"
    credit = "credit"


# --- Compte comptable (plan comptable) ---------------------------------------
class CompteComptable(Base):
    """
    Compte du plan comptable (OHADA/CEMAC). Numéro + libellé par entreprise.
    Table : comptes_comptables.
    """
    __tablename__ = "comptes_comptables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    type_compte: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Ex. classe OHADA (1-8), analytique
    sens_normal: Mapped[str] = mapped_column(String(10), nullable=False, default="debit")  # SensCompte
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "numero", name="uq_comptes_comptables_entreprise_numero"),
    )


# --- Journal comptable -------------------------------------------------------
class JournalComptable(Base):
    """
    Journal comptable (Ventes, Achats, Banque, Caisse, OD).
    Table : journaux_comptables.
    """
    __tablename__ = "journaux_comptables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_journaux_comptables_entreprise_code"),
    )


# --- Période comptable -------------------------------------------------------
class PeriodeComptable(Base):
    """
    Période d'exercice (date_debut, date_fin). Clôture = plus d'écritures.
    Table : periodes_comptables.
    """
    __tablename__ = "periodes_comptables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    cloturee: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "date_debut", name="uq_periodes_comptables_entreprise_debut"),
    )


# --- Écriture comptable (en-tête) --------------------------------------------
class EcritureComptable(Base):
    """
    En-tête d'une écriture (journal, date, numéro de pièce, libellé).
    Table : ecritures_comptables.
    """
    __tablename__ = "ecritures_comptables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    journal_id: Mapped[int] = mapped_column(Integer, ForeignKey("journaux_comptables.id"), nullable=False)
    periode_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("periodes_comptables.id"), nullable=True)
    date_ecriture: Mapped[date] = mapped_column(Date, nullable=False)
    numero_piece: Mapped[str] = mapped_column(String(50), nullable=False)
    piece_jointe_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Réf. pièce jointe / justificatif
    libelle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Ligne d'écriture (détail) ----------------------------------------------
class LigneEcriture(Base):
    """
    Ligne d'écriture : compte, libellé, débit, crédit. Somme débit = somme crédit par écriture.
    Table : lignes_ecritures.
    """
    __tablename__ = "lignes_ecritures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ecriture_id: Mapped[int] = mapped_column(Integer, ForeignKey("ecritures_comptables.id"), nullable=False)
    compte_id: Mapped[int] = mapped_column(Integer, ForeignKey("comptes_comptables.id"), nullable=False)
    libelle_ligne: Mapped[str | None] = mapped_column(String(255), nullable=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))

