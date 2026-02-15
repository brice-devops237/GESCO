# app/modules/achats/models.py
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    ...


class StatutReception(str, PyEnum):
    brouillon = "brouillon"
    validee = "validee"
    annulee = "annulee"


class StatutPaiementFournisseur(str, PyEnum):
    non_paye = "non_paye"
    partiel = "partiel"
    paye = "paye"


class Depot(Base):
    __tablename__ = "depots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)


class CommandeFournisseur(Base):
    __tablename__ = "commandes_fournisseurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    depot_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("depots.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    numero_fournisseur: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Reception(Base):
    __tablename__ = "receptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commande_fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("commandes_fournisseurs.id"), nullable=False)
    depot_id: Mapped[int] = mapped_column(Integer, ForeignKey("depots.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_reception: Mapped[date] = mapped_column(Date, nullable=False)
    etat: Mapped[str] = mapped_column(String(20), nullable=False, default="brouillon")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class FactureFournisseur(Base):
    __tablename__ = "factures_fournisseurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    commande_fournisseur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes_fournisseurs.id"), nullable=True)
    numero_fournisseur: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_restant_du: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    statut_paiement: Mapped[str] = mapped_column(String(20), nullable=False, default="non_paye")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
