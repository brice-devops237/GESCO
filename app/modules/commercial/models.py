# app/modules/commercial/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Commercial (A.4) : etats_document, devis, commandes,
# factures, bons_livraison. Conformité : CGI/OHADA (mentions factures, HT/TVA/TTC).
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    pass


class TypeFacture(str, PyEnum):
    """Type de facture (facture, avoir, proforma, duplicata)."""
    facture = "facture"
    avoir = "avoir"
    proforma = "proforma"
    duplicata = "duplicata"


# --- Référentiel états document -------------------------------------------------

class EtatDocument(Base):
    """
    Référentiel des états de documents (DEVIS, COMMANDE, FACTURE, BL).
    Table : etats_document.
    """
    __tablename__ = "etats_document"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_document: Mapped[str] = mapped_column(String(30), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("type_document", "code", name="uq_etats_document_type_code"),)


# --- Devis ---------------------------------------------------------------------

class Devis(Base):
    """
    Devis client : numéro, date, validité, montants, remises.
    Table : devis.
    """
    __tablename__ = "devis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    date_devis: Mapped[date] = mapped_column(Date, nullable=False)
    date_validite: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    remise_globale_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    remise_globale_montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    taux_change: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("1"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions_generales: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    commande_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "numero", name="uq_devis_entreprise_numero"),)


# --- Commande ------------------------------------------------------------------

class Commande(Base):
    """
    Commande client : numéro, date, client, montants, adresse livraison.
    Table : commandes.
    """
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    devis_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("devis.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    remise_globale_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    remise_globale_montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    taux_change: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("1"))
    adresse_livraison: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    vendeur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "numero", name="uq_commandes_entreprise_numero"),)


# --- Facture -------------------------------------------------------------------

class Facture(Base):
    """
    Facture client (facture, avoir, proforma, duplicata) : numéro, date, montants HT/TVA/TTC.
    Structure compatible CGI Cameroun et bonnes pratiques (identification, montants, devise).
    Table : factures.
    """
    __tablename__ = "factures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    commande_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    type_facture: Mapped[str] = mapped_column(String(20), nullable=False, default="facture")
    facture_origine_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("factures.id"), nullable=True)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    montant_restant_du: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    remise_globale_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    remise_globale_montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    taux_change: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("1"))
    conditions_paiement: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    vendeur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "numero", name="uq_factures_entreprise_numero"),)


# --- Bon de livraison ----------------------------------------------------------

class BonLivraison(Base):
    """
    Bon de livraison : numéro, date, client, lien commande/facture.
    Table : bons_livraison.
    """
    __tablename__ = "bons_livraison"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    commande_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes.id"), nullable=True)
    facture_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("factures.id"), nullable=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    date_livraison: Mapped[date] = mapped_column(Date, nullable=False)
    adresse_livraison: Mapped[str | None] = mapped_column(Text, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    signature_livreur: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature_client: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    livreur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("entreprise_id", "numero", name="uq_bons_livraison_entreprise_numero"),)
