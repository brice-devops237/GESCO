# app/modules/commercial/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Commercial (A.4).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# --- EtatDocument ---

class EtatDocumentCreate(BaseModel):
    type_document: str = Field(..., max_length=30)
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=80)
    ordre: int = 0


class EtatDocumentUpdate(BaseModel):
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=80)
    ordre: int | None = None


class EtatDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type_document: str
    code: str
    libelle: str
    ordre: int


# --- Devis ---

class DevisCreate(BaseModel):
    entreprise_id: int
    point_de_vente_id: int | None = None
    client_id: int
    numero: str = Field(..., max_length=50)
    date_devis: date
    date_validite: date | None = None
    etat_id: int
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    remise_globale_pct: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    remise_globale_montant: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    taux_change: Decimal = Field(default=Decimal("1"), gt=0, decimal_places=6)
    notes: str | None = None
    conditions_generales: str | None = None


class DevisUpdate(BaseModel):
    point_de_vente_id: int | None = None
    date_validite: date | None = None
    etat_id: int | None = None
    montant_ht: Decimal | None = Field(None, ge=0, decimal_places=2)
    montant_tva: Decimal | None = Field(None, ge=0, decimal_places=2)
    montant_ttc: Decimal | None = Field(None, ge=0, decimal_places=2)
    notes: str | None = None


class DevisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    client_id: int
    numero: str
    date_devis: date
    etat_id: int
    montant_ttc: Decimal
    created_at: datetime


# --- Commande ---

class CommandeCreate(BaseModel):
    entreprise_id: int
    point_de_vente_id: int
    client_id: int
    devis_id: int | None = None
    numero: str = Field(..., max_length=50)
    date_commande: date
    date_livraison_prevue: date | None = None
    etat_id: int
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    adresse_livraison: str | None = None
    notes: str | None = None


class CommandeUpdate(BaseModel):
    date_livraison_prevue: date | None = None
    etat_id: int | None = None
    adresse_livraison: str | None = None
    notes: str | None = None


class CommandeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    point_de_vente_id: int
    client_id: int
    numero: str
    date_commande: date
    etat_id: int
    montant_ttc: Decimal
    created_at: datetime


# --- Facture ---

class FactureCreate(BaseModel):
    entreprise_id: int
    point_de_vente_id: int
    client_id: int
    commande_id: int | None = None
    numero: str = Field(..., max_length=50)
    date_facture: date
    date_echeance: date | None = None
    etat_id: int
    type_facture: str = Field(default="facture", max_length=20, description="facture, avoir, proforma ou duplicata (CGI)")
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_restant_du: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    notes: str | None = None


class FactureUpdate(BaseModel):
    date_echeance: date | None = None
    etat_id: int | None = None
    montant_restant_du: Decimal | None = Field(None, ge=0, decimal_places=2)
    notes: str | None = None


class FactureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    client_id: int
    numero: str
    date_facture: date
    etat_id: int
    type_facture: str
    montant_ttc: Decimal
    montant_restant_du: Decimal
    created_at: datetime


# --- BonLivraison ---

class BonLivraisonCreate(BaseModel):
    entreprise_id: int
    point_de_vente_id: int
    client_id: int
    commande_id: int | None = None
    facture_id: int | None = None
    numero: str = Field(..., max_length=50)
    date_livraison: date
    adresse_livraison: str | None = None
    etat_id: int
    notes: str | None = None


class BonLivraisonUpdate(BaseModel):
    adresse_livraison: str | None = None
    etat_id: int | None = None
    notes: str | None = None


class BonLivraisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    client_id: int
    numero: str
    date_livraison: date
    etat_id: int
    created_at: datetime
