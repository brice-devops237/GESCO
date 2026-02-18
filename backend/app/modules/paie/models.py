# app/modules/paie/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Paie : périodes, types d'éléments (gains/retenues),
# bulletins de paie et lignes. Contexte camerounais (CNPS, IR, XAF).
# Dépend de Paramétrage (entreprises), RH (employes).
# Extension monde réel : isolation multi-tenant, toutes structures, tous secteurs.
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
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    ...


# --- Période de paie ----------------------------------------------------------
class PeriodePaie(Base):
    """
    Période de paie (mois/année) par entreprise. Une fois clôturée, plus de modification.
    Table : periodes_paie.
    """
    __tablename__ = "periodes_paie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    mois: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    cloturee: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "annee", "mois", name="uq_periodes_paie_entreprise_annee_mois"),
    )


# --- Type d'élément de paie (référentiel) -------------------------------------
class TypeElementPaie(Base):
    """
    Type d'élément de paie (Salaire de base, Prime, CNPS salarié, IR, Avances, etc.).
    Table : types_element_paie.
    """
    __tablename__ = "types_element_paie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # gain | retenue
    ordre_affichage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_types_element_paie_entreprise_code"),
    )


# --- Bulletin de paie ---------------------------------------------------------
class BulletinPaie(Base):
    """
    Bulletin de paie d'un employé pour une période. Totaux et statut (brouillon, validé, payé).
    Table : bulletins_paie.
    """
    __tablename__ = "bulletins_paie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    employe_id: Mapped[int] = mapped_column(Integer, ForeignKey("employes.id"), nullable=False)
    periode_paie_id: Mapped[int] = mapped_column(Integer, ForeignKey("periodes_paie.id"), nullable=False)
    salaire_brut: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    total_gains: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    total_retenues: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    net_a_payer: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="brouillon")  # brouillon, valide, paye
    date_paiement: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "employe_id", "periode_paie_id", name="uq_bulletins_paie_emp_periode"),
    )

    lignes: Mapped[list["LigneBulletinPaie"]] = relationship("LigneBulletinPaie", back_populates="bulletin_paie", cascade="all, delete-orphan")


# --- Ligne de bulletin (détail des gains et retenues) -------------------------
class LigneBulletinPaie(Base):
    """
    Ligne détaillée d'un bulletin (un gain ou une retenue).
    Table : lignes_bulletin_paie.
    """
    __tablename__ = "lignes_bulletin_paie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bulletin_paie_id: Mapped[int] = mapped_column(Integer, ForeignKey("bulletins_paie.id"), nullable=False)
    type_element_paie_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("types_element_paie.id"), nullable=True)
    libelle: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # gain | retenue
    montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    bulletin_paie: Mapped["BulletinPaie"] = relationship("BulletinPaie", back_populates="lignes")

