# app/modules/comptabilite/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module Comptabilité.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Compte comptable ---
class CompteComptableCreate(BaseModel):
    entreprise_id: int
    numero: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=150)
    sens_normal: str = Field(default="debit", max_length=10)
    actif: bool = True


class CompteComptableUpdate(BaseModel):
    numero: Optional[str] = Field(None, max_length=20)
    libelle: Optional[str] = Field(None, max_length=150)
    sens_normal: Optional[str] = Field(None, max_length=10)
    actif: Optional[bool] = None


class CompteComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    numero: str
    libelle: str
    sens_normal: str
    actif: bool
    created_at: datetime


# --- Journal comptable ---
class JournalComptableCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=10)
    libelle: str = Field(..., max_length=80)
    actif: bool = True


class JournalComptableUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=10)
    libelle: Optional[str] = Field(None, max_length=80)
    actif: Optional[bool] = None


class JournalComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    actif: bool
    created_at: datetime


# --- Période comptable ---
class PeriodeComptableCreate(BaseModel):
    entreprise_id: int
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    libelle: str = Field(..., max_length=80)


class PeriodeComptableUpdate(BaseModel):
    date_fin: Optional[date] = None
    libelle: Optional[str] = Field(None, max_length=80)
    cloturee: Optional[bool] = None


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
    libelle_ligne: Optional[str] = Field(None, max_length=255)
    debit: Decimal = Field(default=Decimal("0"), ge=0)
    credit: Decimal = Field(default=Decimal("0"), ge=0)


class LigneEcritureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ecriture_id: int
    compte_id: int
    libelle_ligne: Optional[str] = None
    debit: Decimal
    credit: Decimal


# --- Écriture comptable (en-tête + lignes) ---
class EcritureComptableCreate(BaseModel):
    entreprise_id: int
    journal_id: int = Field(...)
    periode_id: Optional[int] = None
    date_ecriture: date = Field(...)
    numero_piece: str = Field(..., max_length=50)
    libelle: Optional[str] = Field(None, max_length=255)
    lignes: list[LigneEcritureCreate] = Field(..., min_length=2)


class EcritureComptableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    journal_id: int
    periode_id: Optional[int] = None
    date_ecriture: date
    numero_piece: str
    libelle: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: datetime


class EcritureComptableDetailResponse(EcritureComptableResponse):
    """Écriture avec ses lignes."""
    lignes: list[LigneEcritureResponse] = []
