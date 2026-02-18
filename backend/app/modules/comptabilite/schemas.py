# app/modules/comptabilite/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module Comptabilité : validation entrées (Create/Update)
# et sérialisation sorties (Response). Conçus pour toute structure et tout secteur
# (OHADA/CEMAC, écritures avec lignes, périodes).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- Compte comptable ---
class CompteComptableCreate(BaseModel):
    entreprise_id: int
    numero: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=150)
    type_compte: str | None = Field(None, max_length=20)
    sens_normal: str = Field(default="debit", max_length=10)
    actif: bool = True


class CompteComptableUpdate(BaseModel):
    numero: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=150)
    type_compte: str | None = Field(None, max_length=20)
    sens_normal: str | None = Field(None, max_length=10)
    actif: bool | None = None


class CompteComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    numero: str
    libelle: str
    type_compte: str | None = None
    sens_normal: str
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Journal comptable ---
class JournalComptableCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=10)
    libelle: str = Field(..., max_length=80)
    actif: bool = True


class JournalComptableUpdate(BaseModel):
    code: str | None = Field(None, max_length=10)
    libelle: str | None = Field(None, max_length=80)
    actif: bool | None = None


class JournalComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Période comptable ---
class PeriodeComptableCreate(BaseModel):
    entreprise_id: int
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    libelle: str = Field(..., max_length=80)


class PeriodeComptableUpdate(BaseModel):
    date_fin: date | None = None
    libelle: str | None = Field(None, max_length=80)
    cloturee: bool | None = None


class PeriodeComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    date_debut: date
    date_fin: date
    libelle: str
    cloturee: bool
    created_at: datetime


# --- Ligne d'écriture (détail) ---
class LigneEcritureCreate(BaseModel):
    compte_id: int = Field(...)
    libelle_ligne: str | None = Field(None, max_length=255)
    debit: Decimal = Field(default=Decimal("0"), ge=0)
    credit: Decimal = Field(default=Decimal("0"), ge=0)


class LigneEcritureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ecriture_id: int
    compte_id: int
    libelle_ligne: str | None = None
    debit: Decimal
    credit: Decimal


# --- Écriture comptable (en-tête + lignes) ---
class EcritureComptableCreate(BaseModel):
    entreprise_id: int
    journal_id: int = Field(...)
    periode_id: int | None = None
    date_ecriture: date = Field(...)
    numero_piece: str = Field(..., max_length=50)
    piece_jointe_ref: str | None = Field(None, max_length=255)
    libelle: str | None = Field(None, max_length=255)
    lignes: list[LigneEcritureCreate] = Field(..., min_length=2)


class EcritureComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    journal_id: int
    periode_id: int | None = None
    date_ecriture: date
    numero_piece: str
    piece_jointe_ref: str | None = None
    libelle: str | None = None
    created_by_id: int | None = None
    created_at: datetime


class EcritureComptableDetailResponse(EcritureComptableResponse):
    """Écriture avec ses lignes."""
    lignes: list[LigneEcritureResponse] = []

