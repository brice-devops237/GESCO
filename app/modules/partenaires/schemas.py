# app/modules/partenaires/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Partenaires (A.3) : validation entrées (Create/Update)
# et sérialisation sorties (Response).
# -----------------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- TypeTiers -----------------------------------------------------------------

class TypeTiersCreate(BaseModel):
    """Schéma de création d'un type de tiers."""
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=80)


class TypeTiersUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    libelle: Optional[str] = Field(None, min_length=1, max_length=80)


class TypeTiersResponse(BaseModel):
    """Schéma de réponse pour un type de tiers."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str


# --- Tiers --------------------------------------------------------------------

class TiersCreate(BaseModel):
    """Schéma de création d'un tiers (client/fournisseur)."""
    entreprise_id: int
    type_tiers_id: int
    code: str = Field(..., min_length=1, max_length=30)
    raison_sociale: str = Field(..., min_length=1, max_length=255)
    nom_contact: Optional[str] = Field(None, max_length=150)
    niu: Optional[str] = Field(None, max_length=20, description="NIU DGI Cameroun (optionnel)")
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    pays: str = Field(default="CMR", max_length=3, description="Code pays ISO 3166-1 alpha-3")
    telephone: Optional[str] = Field(None, max_length=30)
    telephone_secondaire: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    canal_vente_id: Optional[int] = None
    limite_credit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    delai_paiement_jours: Optional[int] = Field(None, ge=0)
    compte_bancaire: Optional[str] = Field(None, max_length=50)
    mobile_money_numero: Optional[str] = Field(None, max_length=20)
    mobile_money_operateur: Optional[str] = Field(None, max_length=20)
    segment: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    actif: bool = True


class TiersUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    type_tiers_id: Optional[int] = None
    code: Optional[str] = Field(None, min_length=1, max_length=30)
    raison_sociale: Optional[str] = Field(None, min_length=1, max_length=255)
    nom_contact: Optional[str] = Field(None, max_length=150)
    niu: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    pays: Optional[str] = Field(None, max_length=3)
    telephone: Optional[str] = Field(None, max_length=30)
    telephone_secondaire: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    canal_vente_id: Optional[int] = None
    limite_credit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    delai_paiement_jours: Optional[int] = Field(None, ge=0)
    compte_bancaire: Optional[str] = Field(None, max_length=50)
    mobile_money_numero: Optional[str] = Field(None, max_length=20)
    mobile_money_operateur: Optional[str] = Field(None, max_length=20)
    segment: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    actif: Optional[bool] = None


class TiersResponse(BaseModel):
    """Schéma de réponse pour un tiers."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    type_tiers_id: int
    code: str
    raison_sociale: str
    nom_contact: Optional[str] = None
    niu: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    region: Optional[str] = None
    pays: str
    telephone: Optional[str] = None
    telephone_secondaire: Optional[str] = None
    email: Optional[str] = None
    canal_vente_id: Optional[int] = None
    limite_credit: Optional[Decimal] = None
    delai_paiement_jours: Optional[int] = None
    segment: Optional[str] = None
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Contact ------------------------------------------------------------------

class ContactCreate(BaseModel):
    """Schéma de création d'un contact."""
    tiers_id: int
    nom: str = Field(..., min_length=1, max_length=150)
    prenom: Optional[str] = Field(None, max_length=100)
    fonction: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    est_principal: bool = False
    actif: bool = True


class ContactUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    nom: Optional[str] = Field(None, min_length=1, max_length=150)
    prenom: Optional[str] = Field(None, max_length=100)
    fonction: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    est_principal: Optional[bool] = None
    actif: Optional[bool] = None


class ContactResponse(BaseModel):
    """Schéma de réponse pour un contact."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    tiers_id: int
    nom: str
    prenom: Optional[str] = None
    fonction: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    est_principal: bool
    actif: bool
    created_at: datetime
    updated_at: datetime
