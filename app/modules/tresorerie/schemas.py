# app/modules/tresorerie/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module Trésorerie : modes paiement, comptes, règlements.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- Mode de paiement ---
class ModePaiementCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=80)
    actif: bool = True


class ModePaiementUpdate(BaseModel):
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=80)
    actif: bool | None = None


class ModePaiementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Compte trésorerie ---
class CompteTresorerieCreate(BaseModel):
    entreprise_id: int
    type_compte: str = Field(..., max_length=20)  # caisse | bancaire
    libelle: str = Field(..., max_length=100)
    devise_id: int
    actif: bool = True


class CompteTresorerieUpdate(BaseModel):
    type_compte: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=100)
    devise_id: int | None = None
    actif: bool | None = None


class CompteTresorerieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    type_compte: str
    libelle: str
    devise_id: int
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Règlement ---
class ReglementCreate(BaseModel):
    entreprise_id: int
    type_reglement: str = Field(..., max_length=20)  # client | fournisseur
    facture_id: int | None = None
    facture_fournisseur_id: int | None = None
    tiers_id: int = Field(...)
    montant: Decimal = Field(..., gt=0)
    date_reglement: date = Field(...)
    mode_paiement_id: int = Field(...)
    compte_tresorerie_id: int = Field(...)
    reference: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=2000)


class ReglementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    type_reglement: str
    facture_id: int | None = None
    facture_fournisseur_id: int | None = None
    tiers_id: int
    montant: Decimal
    date_reglement: date
    mode_paiement_id: int
    compte_tresorerie_id: int
    reference: str | None = None
    notes: str | None = None
    created_by_id: int | None = None
    created_at: datetime
