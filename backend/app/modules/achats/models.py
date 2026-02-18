# app/modules/achats/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Achats : dépôts, commandes fournisseurs, réceptions,
# factures fournisseurs. Dépend de Paramétrage (entreprises, devises),
# Partenaires (tiers fournisseurs), Commercial (etats_document).
#
# Conçu comme extension du monde réel, adaptable à toutes les structures et
# tous les secteurs (PME, ETI, grands groupes ; commerce, industrie, services) :
# - Multi-structures : depot_id optionnel sur commande (mono-site = sans dépôt,
#   multi-sites = dépôts par lieu) ; facture sans commande = achat direct.
# - Multi-devises : devise_id sur commande et facture (international, import).
# - Référentiel états (etats_document) : chaque entreprise définit son workflow
#   (brouillon, en attente, validé, annulé, etc.) selon sa taille.
# - Délais, dates réception, n° BL fournisseur : traçabilité et conformité
#   (CGI/OHADA, douane, qualité). Champs optionnels pour simplicité PME.
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


class StatutReception(str, PyEnum):
    """Statut d'une réception."""
    brouillon = "brouillon"
    validee = "validee"
    annulee = "annulee"


class StatutPaiementFournisseur(str, PyEnum):
    """Statut de paiement facture fournisseur."""
    non_paye = "non_paye"
    partiel = "partiel"
    paye = "paye"


class TypeFactureFournisseur(str, PyEnum):
    """Type de facture fournisseur (aligné monde réel : facture, avoir, proforma)."""
    facture = "facture"
    avoir = "avoir"
    proforma = "proforma"


# --- Dépôt (entrepôt / lieu de stockage) --------------------------------------
class Depot(Base):
    """
    Dépôt (entrepôt). Table : depots. Lié aux points de vente ou autonome.
    Convient à toute taille : PME (un seul dépôt ou aucun), grands groupes (multi-sites).
    pays / code_postal : international, douane, logistique.
    """
    __tablename__ = "depots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    code_postal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pays: Mapped[str | None] = mapped_column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)


# --- Commande fournisseur -----------------------------------------------------
class CommandeFournisseur(Base):
    """Commande fournisseur. Table : commandes_fournisseurs."""
    __tablename__ = "commandes_fournisseurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    depot_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("depots.id"), nullable=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    numero_fournisseur: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    delai_livraison_jours: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Délai convenu (jours)
    etat_id: Mapped[int] = mapped_column(Integer, ForeignKey("etats_document.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Réception (commande fournisseur) -----------------------------------------
class Reception(Base):
    """Réception (livraison fournisseur). Table : receptions."""
    __tablename__ = "receptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commande_fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("commandes_fournisseurs.id"), nullable=False)
    depot_id: Mapped[int] = mapped_column(Integer, ForeignKey("depots.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    numero_bl_fournisseur: Mapped[str | None] = mapped_column(String(80), nullable=True)  # N° BL du fournisseur
    date_reception: Mapped[date] = mapped_column(Date, nullable=False)
    etat: Mapped[str] = mapped_column(String(20), nullable=False, default="brouillon")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Facture fournisseur -----------------------------------------------------
class FactureFournisseur(Base):
    """
    Facture fournisseur. Table : factures_fournisseurs.
    type_facture : facture (normale), avoir (remboursement/crédit), proforma (devis fournisseur).
    Tous secteurs : industrie, commerce, services (achats de biens ou prestations).
    commande_fournisseur_id optionnel : achat direct sans commande (PME, urgences).
    """
    __tablename__ = "factures_fournisseurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    fournisseur_id: Mapped[int] = mapped_column(Integer, ForeignKey("tiers.id"), nullable=False)
    commande_fournisseur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commandes_fournisseurs.id"), nullable=True)
    numero_fournisseur: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    type_facture: Mapped[str] = mapped_column(String(20), nullable=False, default="facture")  # facture | avoir | proforma
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_tva: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    montant_restant_du: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    devise_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    statut_paiement: Mapped[str] = mapped_column(String(20), nullable=False, default="non_paye")
    date_reception_facture: Mapped[date | None] = mapped_column(Date, nullable=True)  # Date réception document
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

