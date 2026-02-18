# app/modules/commercial/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Commercial : états document, devis, commandes, factures,
# bons de livraison. Dépend de Paramétrage (entreprises, points de vente, devises),
# Partenaires (tiers clients). Conçu pour toute structure (PME à grand groupe) et
# tout secteur : champs optionnels (PDV, devis/commande), types facture CGI, mentions légales.
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
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    ...


class TypeFacture(str, PyEnum):
    """Type de facture (CGI)."""
    facture = "facture"
    avoir = "avoir"
    proforma = "proforma"
    duplicata = "duplicata"


# --- État document (par type : devis, commande, facture, BL) ------------------
class EtatDocument(Base):
    """État d'un document (brouillon, validé, annulé, etc.). Table : etats_document."""
    __tablename__ = "etats_document"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_document: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# --- Devis -------------------------------------------------------------------
# Référence client et conditions pour suivi commercial (CGI/OHADA mentions factures).
class Devis(Base):
    """Devis client. Table : devis."""
    __tablename__ = "devis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    reference_client: Mapped[str | None] = mapped_column(String(80), nullable=True)  # N° dossier / ref client
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_devis: Mapped[date] = mapped_column(Date, nullable=False)
    date_validite: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    remise_globale_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    remise_globale_montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    taux_change: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions_generales: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Commande client ---------------------------------------------------------
class Commande(Base):
    """Commande client. Table : commandes."""
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    devis_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("devis.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    reference_client: Mapped[str | None] = mapped_column(String(80), nullable=True)
    adresse_livraison: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Facture client ----------------------------------------------------------
class Facture(Base):
    """Facture client (facture, avoir, proforma, duplicata). Table : factures."""
    __tablename__ = "factures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    commande_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    type_facture: Mapped[str] = mapped_column(String(20), nullable=False, default="facture")
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_restant_du: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    mention_legale: Mapped[str | None] = mapped_column(Text, nullable=True)  # Mentions CGI/OHADA, exonération…
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Bon de livraison --------------------------------------------------------
class BonLivraison(Base):
    """Bon de livraison. Table : bons_livraison."""
    __tablename__ = "bons_livraison"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    commande_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes.id"), nullable=True)
    facture_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("factures.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_livraison: Mapped[date] = mapped_column(Date, nullable=False)
    contact_livraison: Mapped[str | None] = mapped_column(String(150), nullable=True)  # Nom/tél destinataire
    adresse_livraison: Mapped[str | None] = mapped_column(Text, nullable=True)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

