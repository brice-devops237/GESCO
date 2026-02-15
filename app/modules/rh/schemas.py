# app/modules/rh/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module RH.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Département ---
class DepartementCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=100)
    actif: bool = True


class DepartementUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    libelle: Optional[str] = Field(None, max_length=100)
    actif: Optional[bool] = None


class DepartementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    actif: bool
    created_at: datetime


# --- Poste ---
class PosteCreate(BaseModel):
    entreprise_id: int
    departement_id: Optional[int] = None
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=100)
    actif: bool = True


class PosteUpdate(BaseModel):
    departement_id: Optional[int] = None
    code: Optional[str] = Field(None, max_length=20)
    libelle: Optional[str] = Field(None, max_length=100)
    actif: Optional[bool] = None


class PosteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    departement_id: Optional[int] = None
    code: str
    libelle: str
    actif: bool
    created_at: datetime


# --- Type de contrat ---
class TypeContratCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=80)
    actif: bool = True


class TypeContratUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    libelle: Optional[str] = Field(None, max_length=80)
    actif: Optional[bool] = None


class TypeContratResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    actif: bool
    created_at: datetime


# --- Employé ---
class EmployeCreate(BaseModel):
    entreprise_id: int
    utilisateur_id: Optional[int] = None
    departement_id: Optional[int] = None
    poste_id: Optional[int] = None
    type_contrat_id: Optional[int] = None
    matricule: str = Field(..., max_length=30)
    nom: str = Field(..., max_length=80)
    prenom: str = Field(..., max_length=80)
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=1)
    nationalite: Optional[str] = Field(None, max_length=50)
    niu: Optional[str] = Field(None, max_length=30)
    numero_cnps: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    telephone: Optional[str] = Field(None, max_length=30)
    adresse: Optional[str] = Field(None, max_length=255)
    date_embauche: date = Field(...)
    salaire_base: Decimal = Field(default=Decimal("0"), ge=0)
    devise_id: Optional[int] = None
    compte_bancaire: Optional[str] = Field(None, max_length=50)
    banque: Optional[str] = Field(None, max_length=80)
    actif: bool = True


class EmployeUpdate(BaseModel):
    utilisateur_id: Optional[int] = None
    departement_id: Optional[int] = None
    poste_id: Optional[int] = None
    type_contrat_id: Optional[int] = None
    matricule: Optional[str] = Field(None, max_length=30)
    nom: Optional[str] = Field(None, max_length=80)
    prenom: Optional[str] = Field(None, max_length=80)
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=1)
    nationalite: Optional[str] = Field(None, max_length=50)
    niu: Optional[str] = Field(None, max_length=30)
    numero_cnps: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    telephone: Optional[str] = Field(None, max_length=30)
    adresse: Optional[str] = Field(None, max_length=255)
    date_embauche: Optional[date] = None
    salaire_base: Optional[Decimal] = Field(None, ge=0)
    devise_id: Optional[int] = None
    compte_bancaire: Optional[str] = Field(None, max_length=50)
    banque: Optional[str] = Field(None, max_length=80)
    actif: Optional[bool] = None


class EmployeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    utilisateur_id: Optional[int] = None
    departement_id: Optional[int] = None
    poste_id: Optional[int] = None
    type_contrat_id: Optional[int] = None
    matricule: str
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = None
    genre: Optional[str] = None
    nationalite: Optional[str] = None
    niu: Optional[str] = None
    numero_cnps: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    date_embauche: date
    salaire_base: Decimal
    devise_id: Optional[int] = None
    compte_bancaire: Optional[str] = None
    banque: Optional[str] = None
    actif: bool
    created_at: datetime


# --- Type de congé ---
class TypeCongeCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=80)
    paye: bool = True
    actif: bool = True


class TypeCongeUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    libelle: Optional[str] = Field(None, max_length=80)
    paye: Optional[bool] = None
    actif: Optional[bool] = None


class TypeCongeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    paye: bool
    actif: bool
    created_at: datetime


# --- Demande de congé ---
class DemandeCongeCreate(BaseModel):
    entreprise_id: int
    employe_id: int = Field(...)
    type_conge_id: int = Field(...)
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    nombre_jours: int = Field(..., ge=1)
    statut: str = Field(default="en_attente", max_length=20)
    motif: Optional[str] = Field(None, max_length=255)


class DemandeCongeUpdate(BaseModel):
    statut: Optional[str] = Field(None, max_length=20)
    commentaire_refus: Optional[str] = Field(None, max_length=255)


class DemandeCongeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    type_conge_id: int
    date_debut: date
    date_fin: date
    nombre_jours: int
    statut: str
    motif: Optional[str] = None
    commentaire_refus: Optional[str] = None
    approuve_par_id: Optional[int] = None
    date_decision: Optional[datetime] = None
    created_by_id: Optional[int] = None
    created_at: datetime


# --- Solde de congé ---
class SoldeCongeCreate(BaseModel):
    entreprise_id: int
    employe_id: int = Field(...)
    type_conge_id: int = Field(...)
    annee: int = Field(..., ge=2000, le=2100)
    droits_acquis: int = Field(default=0, ge=0)
    jours_pris: int = Field(default=0, ge=0)


class SoldeCongeUpdate(BaseModel):
    droits_acquis: Optional[int] = Field(None, ge=0)
    jours_pris: Optional[int] = Field(None, ge=0)


class SoldeCongeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    type_conge_id: int
    annee: int
    droits_acquis: int
    jours_pris: int
    created_at: datetime


# --- Objectif ---
class ObjectifCreate(BaseModel):
    entreprise_id: int
    employe_id: int = Field(...)
    libelle: str = Field(..., max_length=150)
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    montant_cible: Decimal = Field(default=Decimal("0"), ge=0)
    atteint: bool = False


class ObjectifUpdate(BaseModel):
    libelle: Optional[str] = Field(None, max_length=150)
    date_fin: Optional[date] = None
    montant_cible: Optional[Decimal] = Field(None, ge=0)
    atteint: Optional[bool] = None


class ObjectifResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    libelle: str
    date_debut: date
    date_fin: date
    montant_cible: Decimal
    atteint: bool
    created_at: datetime


# --- Taux de commission ---
class TauxCommissionCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=80)
    taux_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    actif: bool = True


class TauxCommissionUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    libelle: Optional[str] = Field(None, max_length=80)
    taux_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    actif: Optional[bool] = None


class TauxCommissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    taux_pct: Decimal
    actif: bool
    created_at: datetime


# --- Commission ---
class CommissionCreate(BaseModel):
    entreprise_id: int
    employe_id: int = Field(...)
    taux_commission_id: Optional[int] = None
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    montant: Decimal = Field(default=Decimal("0"), ge=0)
    libelle: Optional[str] = Field(None, max_length=255)
    payee: bool = False


class CommissionUpdate(BaseModel):
    montant: Optional[Decimal] = Field(None, ge=0)
    libelle: Optional[str] = Field(None, max_length=255)
    payee: Optional[bool] = None


class CommissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    taux_commission_id: Optional[int] = None
    date_debut: date
    date_fin: date
    montant: Decimal
    libelle: Optional[str] = None
    payee: bool
    created_at: datetime


# --- Avance ---
class AvanceCreate(BaseModel):
    entreprise_id: int
    employe_id: int = Field(...)
    date_avance: date = Field(...)
    montant: Decimal = Field(..., gt=0)
    motif: Optional[str] = Field(None, max_length=255)
    rembourse: bool = False


class AvanceUpdate(BaseModel):
    motif: Optional[str] = Field(None, max_length=255)
    rembourse: Optional[bool] = None


class AvanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    date_avance: date
    montant: Decimal
    motif: Optional[str] = None
    rembourse: bool
    created_by_id: Optional[int] = None
    created_at: datetime
