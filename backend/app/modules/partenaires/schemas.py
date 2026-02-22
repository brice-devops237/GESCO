# app/modules/partenaires/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Partenaires : validation entrées (Create/Update)
# et sérialisation sorties (Response). Extension monde réel : multi-tenant, tous secteurs.
# -----------------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- TypeTiers -----------------------------------------------------------------

class TypeTiersCreate(BaseModel):
    """Schéma de création d'un type de tiers."""
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=80)


class TypeTiersUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    code: str | None = Field(None, min_length=1, max_length=20)
    libelle: str | None = Field(None, min_length=1, max_length=80)


class TypeTiersResponse(BaseModel):
    """Schéma de réponse pour un type de tiers."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str


# --- Tiers --------------------------------------------------------------------

class TiersCreate(BaseModel):
    """Schéma de création d'un tiers (client/fournisseur) – identification légale et adresse postale."""
    entreprise_id: int
    type_tiers_id: int
    code: str = Field(..., min_length=1, max_length=30)
    raison_sociale: str = Field(..., min_length=1, max_length=255)
    sigle: str | None = Field(None, max_length=50)
    nom_contact: str | None = Field(None, max_length=150)
    niu: str | None = Field(None, max_length=20, description="NIU DGI Cameroun (optionnel)")
    rccm: str | None = Field(None, max_length=50, description="Registre du Commerce OHADA (optionnel)")
    adresse: str | None = None
    code_postal: str | None = Field(None, max_length=20)
    boite_postale: str | None = Field(None, max_length=20, description="Courant en Afrique francophone")
    ville: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    pays: str = Field(default="CMR", max_length=3, description="Code pays ISO 3166-1 alpha-3")
    telephone: str | None = Field(None, max_length=30)
    telephone_secondaire: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    canal_vente_id: int | None = None
    limite_credit: Decimal | None = Field(None, ge=0, decimal_places=2)
    delai_paiement_jours: int | None = Field(None, ge=0)
    compte_bancaire: str | None = Field(None, max_length=50)
    mobile_money_numero: str | None = Field(None, max_length=20)
    mobile_money_operateur: str | None = Field(None, max_length=20)
    segment: str | None = Field(None, max_length=50)
    notes: str | None = None
    actif: bool = True


class TiersUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    type_tiers_id: int | None = None
    code: str | None = Field(None, min_length=1, max_length=30)
    raison_sociale: str | None = Field(None, min_length=1, max_length=255)
    sigle: str | None = Field(None, max_length=50)
    nom_contact: str | None = Field(None, max_length=150)
    niu: str | None = Field(None, max_length=20)
    rccm: str | None = Field(None, max_length=50)
    adresse: str | None = None
    code_postal: str | None = Field(None, max_length=20)
    boite_postale: str | None = Field(None, max_length=20)
    ville: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    pays: str | None = Field(None, max_length=3)
    telephone: str | None = Field(None, max_length=30)
    telephone_secondaire: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    canal_vente_id: int | None = None
    limite_credit: Decimal | None = Field(None, ge=0, decimal_places=2)
    delai_paiement_jours: int | None = Field(None, ge=0)
    compte_bancaire: str | None = Field(None, max_length=50)
    mobile_money_numero: str | None = Field(None, max_length=20)
    mobile_money_operateur: str | None = Field(None, max_length=20)
    segment: str | None = Field(None, max_length=50)
    notes: str | None = None
    actif: bool | None = None


class TiersResponse(BaseModel):
    """Schéma de réponse pour un tiers."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    type_tiers_id: int
    code: str
    raison_sociale: str
    sigle: str | None = None
    nom_contact: str | None = None
    niu: str | None = None
    rccm: str | None = None
    adresse: str | None = None
    code_postal: str | None = None
    boite_postale: str | None = None
    ville: str | None = None
    region: str | None = None
    pays: str
    telephone: str | None = None
    telephone_secondaire: str | None = None
    email: str | None = None
    canal_vente_id: int | None = None
    limite_credit: Decimal | None = None
    delai_paiement_jours: int | None = None
    compte_bancaire: str | None = None
    mobile_money_numero: str | None = None
    mobile_money_operateur: str | None = None
    segment: str | None = None
    notes: str | None = None
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Contact ------------------------------------------------------------------

class ContactCreate(BaseModel):
    """Schéma de création d'un contact (civilité pour courriers et factures)."""
    tiers_id: int
    civilite: str | None = Field(None, max_length=10, description="M., Mme, Mlle, Dr., etc.")
    nom: str = Field(..., min_length=1, max_length=150)
    prenom: str | None = Field(None, max_length=100)
    fonction: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    est_principal: bool = False
    actif: bool = True


class ContactUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    civilite: str | None = Field(None, max_length=10)
    nom: str | None = Field(None, min_length=1, max_length=150)
    prenom: str | None = Field(None, max_length=100)
    fonction: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    est_principal: bool | None = None
    actif: bool | None = None


class ContactResponse(BaseModel):
    """Schéma de réponse pour un contact."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    tiers_id: int
    civilite: str | None = None
    nom: str
    prenom: str | None = None
    fonction: str | None = None
    telephone: str | None = None
    email: str | None = None
    est_principal: bool
    actif: bool
    created_at: datetime
    updated_at: datetime

