# app/modules/immobilisations/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategorieImmobilisationCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=100)
    duree_amortissement_annees: int = Field(default=5, ge=1, le=50)
    taux_amortissement: Optional[Decimal] = Field(None, ge=0, le=100)


class CategorieImmobilisationUpdate(BaseModel):
    libelle: Optional[str] = Field(None, max_length=100)
    duree_amortissement_annees: Optional[int] = Field(None, ge=1, le=50)
    taux_amortissement: Optional[Decimal] = Field(None, ge=0, le=100)


class CategorieImmobilisationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    duree_amortissement_annees: int
    taux_amortissement: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime


class ImmobilisationCreate(BaseModel):
    entreprise_id: int
    categorie_id: int
    compte_comptable_id: Optional[int] = None
    compte_amortissement_id: Optional[int] = None
    code: str = Field(..., max_length=30)
    designation: str = Field(..., max_length=200)
    date_acquisition: date
    valeur_acquisition: Decimal = Field(..., ge=0)
    duree_amortissement_annees: int = Field(default=5, ge=1, le=50)
    date_mise_en_service: Optional[date] = None
    notes: Optional[str] = None


class ImmobilisationUpdate(BaseModel):
    designation: Optional[str] = Field(None, max_length=200)
    date_mise_en_service: Optional[date] = None
    notes: Optional[str] = None
    actif: Optional[bool] = None


class ImmobilisationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    categorie_id: int
    code: str
    designation: str
    date_acquisition: date
    valeur_acquisition: Decimal
    duree_amortissement_annees: int
    date_mise_en_service: Optional[date] = None
    actif: bool
    created_at: datetime
    updated_at: datetime


class LigneAmortissementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    immobilisation_id: int
    annee: int
    mois: Optional[int] = None
    montant_dotation: Decimal
    cumul_amortissement: Decimal
    valeur_nette: Decimal
    created_at: datetime
