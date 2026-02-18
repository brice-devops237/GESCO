# app/modules/paie/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Paie. Extension monde réel : multi-tenant,
# toutes structures, tous secteurs.
# -----------------------------------------------------------------------------
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- Période de paie ---
class PeriodePaieCreate(BaseModel):
    entreprise_id: int = Field(...)
    annee: int = Field(..., ge=2000, le=2100)
    mois: int = Field(..., ge=1, le=12)
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    cloturee: bool = False


class PeriodePaieUpdate(BaseModel):
    date_debut: date | None = None
    date_fin: date | None = None
    cloturee: bool | None = None


class PeriodePaieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    annee: int
    mois: int
    date_debut: date
    date_fin: date
    cloturee: bool
    created_at: datetime


# --- Type d'élément de paie ---
class TypeElementPaieCreate(BaseModel):
    entreprise_id: int = Field(...)
    code: str = Field(..., max_length=30)
    libelle: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(gain|retenue)$")
    ordre_affichage: int = 0
    actif: bool = True


class TypeElementPaieUpdate(BaseModel):
    libelle: str | None = Field(None, max_length=100)
    type: str | None = Field(None, pattern="^(gain|retenue)$")
    ordre_affichage: int | None = None
    actif: bool | None = None


class TypeElementPaieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    type: str
    ordre_affichage: int
    actif: bool
    created_at: datetime


# --- Ligne de bulletin ---
class LigneBulletinPaieCreate(BaseModel):
    type_element_paie_id: int | None = None
    libelle: str = Field(..., max_length=120)
    type: str = Field(..., pattern="^(gain|retenue)$")
    montant: Decimal = Field(..., ge=0)
    ordre: int = 0


class LigneBulletinPaieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bulletin_paie_id: int
    type_element_paie_id: int | None = None
    libelle: str
    type: str
    montant: Decimal
    ordre: int
    created_at: datetime


# --- Bulletin de paie ---
class BulletinPaieCreate(BaseModel):
    entreprise_id: int = Field(...)
    employe_id: int = Field(...)
    periode_paie_id: int = Field(...)
    salaire_brut: Decimal = Field(default=Decimal("0"), ge=0)
    total_gains: Decimal = Field(default=Decimal("0"), ge=0)
    total_retenues: Decimal = Field(default=Decimal("0"), ge=0)
    net_a_payer: Decimal = Field(default=Decimal("0"), ge=0)
    statut: str = Field(default="brouillon", pattern="^(brouillon|valide|paye)$")
    lignes: list[LigneBulletinPaieCreate] = Field(default_factory=list)


class BulletinPaieUpdate(BaseModel):
    salaire_brut: Decimal | None = Field(None, ge=0)
    total_gains: Decimal | None = Field(None, ge=0)
    total_retenues: Decimal | None = Field(None, ge=0)
    net_a_payer: Decimal | None = Field(None, ge=0)
    statut: str | None = Field(None, pattern="^(brouillon|valide|paye)$")
    date_paiement: date | None = None


class BulletinPaieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    periode_paie_id: int
    salaire_brut: Decimal
    total_gains: Decimal
    total_retenues: Decimal
    net_a_payer: Decimal
    statut: str
    date_paiement: date | None = None
    created_at: datetime


class BulletinPaieDetailResponse(BulletinPaieResponse):
    """Bulletin avec ses lignes."""
    lignes: list[LigneBulletinPaieResponse] = []

