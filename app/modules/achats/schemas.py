# app/modules/achats/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CommandeFournisseurCreate(BaseModel):
    entreprise_id: int
    fournisseur_id: int
    depot_id: Optional[int] = None
    numero: str = Field(..., max_length=50)
    numero_fournisseur: Optional[str] = Field(None, max_length=50)
    date_commande: date
    date_livraison_prevue: Optional[date] = None
    etat_id: int
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    notes: Optional[str] = None


class CommandeFournisseurUpdate(BaseModel):
    depot_id: Optional[int] = None
    date_livraison_prevue: Optional[date] = None
    etat_id: Optional[int] = None
    notes: Optional[str] = None


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
    notes: Optional[str] = None


class ReceptionUpdate(BaseModel):
    etat: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


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
    commande_fournisseur_id: Optional[int] = None
    numero_fournisseur: str = Field(..., max_length=50)
    date_facture: date
    date_echeance: Optional[date] = None
    montant_ht: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_tva: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_ttc: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    montant_restant_du: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    devise_id: int
    statut_paiement: str = Field(default="non_paye", max_length=20)
    notes: Optional[str] = None


class FactureFournisseurUpdate(BaseModel):
    date_echeance: Optional[date] = None
    montant_restant_du: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    statut_paiement: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


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
