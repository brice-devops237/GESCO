# app/modules/achats/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Achats. Adaptés à toute structure (PME à grand
# groupe) et tout secteur : champs optionnels où pertinent (depot_id, commande
# sur facture, délais, dates), multi-devises, types facture/avoir/proforma.
# -----------------------------------------------------------------------------
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- Dépôt ---
class DepotCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=100)
    adresse: str | None = None
    ville: str | None = Field(None, max_length=100)
    code_postal: str | None = Field(None, max_length=20)
    pays: str | None = Field(None, max_length=3, description="ISO 3166-1 alpha-3")
    point_de_vente_id: int | None = None


class DepotUpdate(BaseModel):
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=100)
    adresse: str | None = None
    ville: str | None = Field(None, max_length=100)
    code_postal: str | None = Field(None, max_length=20)
    pays: str | None = Field(None, max_length=3)
    point_de_vente_id: int | None = None


class DepotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    adresse: str | None = None
    ville: str | None = None
    code_postal: str | None = None
    pays: str | None = None
    point_de_vente_id: int | None = None


# --- Commande fournisseur ---
class CommandeFournisseurCreate(BaseModel):
    entreprise_id: int
    fournisseur_id: int
    depot_id: int | None = None
    numero: str = Field(..., max_length=50)
    numero_fournisseur: str | None = Field(None, max_length=50)
    date_commande: date
    date_livraison_prevue: date | None = None
    delai_livraison_jours: int | None = None
    etat_id: int
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    notes: str | None = None


class CommandeFournisseurUpdate(BaseModel):
    depot_id: int | None = None
    date_livraison_prevue: date | None = None
    delai_livraison_jours: int | None = None
    etat_id: int | None = None
    notes: str | None = None


class CommandeFournisseurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    fournisseur_id: int
    depot_id: int | None = None
    numero: str
    numero_fournisseur: str | None = None
    date_commande: date
    date_livraison_prevue: date | None = None
    delai_livraison_jours: int | None = None
    etat_id: int
    montant_ht: Decimal
    montant_tva: Decimal
    montant_ttc: Decimal
    devise_id: int
    notes: str | None = None
    created_at: datetime


class ReceptionCreate(BaseModel):
    commande_fournisseur_id: int
    depot_id: int
    numero: str = Field(..., max_length=50)
    numero_bl_fournisseur: str | None = Field(None, max_length=80)
    date_reception: date
    etat: str = Field(default="brouillon", max_length=20)
    notes: str | None = None


class ReceptionUpdate(BaseModel):
    numero_bl_fournisseur: str | None = Field(None, max_length=80)
    etat: str | None = Field(None, max_length=20)
    notes: str | None = None


class ReceptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    commande_fournisseur_id: int
    depot_id: int
    numero: str
    numero_bl_fournisseur: str | None = None
    date_reception: date
    etat: str
    notes: str | None = None
    created_at: datetime


class FactureFournisseurCreate(BaseModel):
    entreprise_id: int
    fournisseur_id: int
    commande_fournisseur_id: int | None = None
    numero_fournisseur: str = Field(..., max_length=50)
    type_facture: str = Field(default="facture", max_length=20, description="facture | avoir | proforma")
    date_facture: date
    date_echeance: date | None = None
    date_reception_facture: date | None = None
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_restant_du: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    statut_paiement: str = Field(default="non_paye", max_length=20)
    notes: str | None = None


class FactureFournisseurUpdate(BaseModel):
    type_facture: str | None = Field(None, max_length=20)
    date_echeance: date | None = None
    date_reception_facture: date | None = None
    montant_restant_du: Decimal | None = Field(None, ge=0, decimal_places=2)
    statut_paiement: str | None = Field(None, max_length=20)
    notes: str | None = None


class FactureFournisseurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    fournisseur_id: int
    commande_fournisseur_id: int | None = None
    numero_fournisseur: str
    type_facture: str = "facture"
    date_facture: date
    date_echeance: date | None = None
    date_reception_facture: date | None = None
    montant_ttc: Decimal
    montant_restant_du: Decimal
    statut_paiement: str
    created_at: datetime

