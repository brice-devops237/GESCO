# app/modules/achats/schemas.py
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CommandeFournisseurCreate(BaseModel):
    entreprise_id: int
    fournisseur_id: int
    depot_id: int | None = None
    numero: str = Field(..., max_length=50)
    numero_fournisseur: str | None = Field(None, max_length=50)
    date_commande: date
    date_livraison_prevue: date | None = None
    etat_id: int
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    notes: str | None = None


class CommandeFournisseurUpdate(BaseModel):
    depot_id: int | None = None
    date_livraison_prevue: date | None = None
    etat_id: int | None = None
    notes: str | None = None


class CommandeFournisseurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    fournisseur_id: int
    numero: str
    date_commande: date
    etat_id: int
    montant_ttc: Decimal
    created_at: datetime


class ReceptionCreate(BaseModel):
    commande_fournisseur_id: int
    depot_id: int
    numero: str = Field(..., max_length=50)
    date_reception: date
    etat: str = Field(default="brouillon", max_length=20)
    notes: str | None = None


class ReceptionUpdate(BaseModel):
    etat: str | None = Field(None, max_length=20)
    notes: str | None = None


class ReceptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    commande_fournisseur_id: int
    depot_id: int
    numero: str
    date_reception: date
    etat: str
    created_at: datetime


class FactureFournisseurCreate(BaseModel):
    entreprise_id: int
    fournisseur_id: int
    commande_fournisseur_id: int | None = None
    numero_fournisseur: str = Field(..., max_length=50)
    date_facture: date
    date_echeance: date | None = None
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_restant_du: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    statut_paiement: str = Field(default="non_paye", max_length=20)
    notes: str | None = None


class FactureFournisseurUpdate(BaseModel):
    date_echeance: date | None = None
    montant_restant_du: Decimal | None = Field(None, ge=0, decimal_places=2)
    statut_paiement: str | None = Field(None, max_length=20)
    notes: str | None = None


class FactureFournisseurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    fournisseur_id: int
    numero_fournisseur: str
    date_facture: date
    montant_ttc: Decimal
    montant_restant_du: Decimal
    statut_paiement: str
    created_at: datetime
