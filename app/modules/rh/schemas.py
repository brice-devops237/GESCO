# app/modules/rh/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module RH.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- Département ---
class DepartementCreate(BaseModel):
    entreprise_id: int
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=100)
    actif: bool = True


class DepartementUpdate(BaseModel):
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=100)
    actif: bool | None = None


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
    departement_id: int | None = None
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=100)
    actif: bool = True


class PosteUpdate(BaseModel):
    departement_id: int | None = None
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=100)
    actif: bool | None = None


class PosteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    departement_id: int | None = None
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
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=80)
    actif: bool | None = None


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
    utilisateur_id: int | None = None
    departement_id: int | None = None
    poste_id: int | None = None
    type_contrat_id: int | None = None
    matricule: str = Field(..., max_length=30)
    nom: str = Field(..., max_length=80)
    prenom: str = Field(..., max_length=80)
    date_naissance: date | None = None
    lieu_naissance: str | None = Field(None, max_length=100)
    genre: str | None = Field(None, max_length=1)
    nationalite: str | None = Field(None, max_length=50)
    niu: str | None = Field(None, max_length=30)
    numero_cnps: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=120)
    telephone: str | None = Field(None, max_length=30)
    adresse: str | None = Field(None, max_length=255)
    date_embauche: date = Field(...)
    salaire_base: Decimal = Field(default=Decimal("0"), ge=0)
    devise_id: int | None = None
    compte_bancaire: str | None = Field(None, max_length=50)
    banque: str | None = Field(None, max_length=80)
    actif: bool = True


class EmployeUpdate(BaseModel):
    utilisateur_id: int | None = None
    departement_id: int | None = None
    poste_id: int | None = None
    type_contrat_id: int | None = None
    matricule: str | None = Field(None, max_length=30)
    nom: str | None = Field(None, max_length=80)
    prenom: str | None = Field(None, max_length=80)
    date_naissance: date | None = None
    lieu_naissance: str | None = Field(None, max_length=100)
    genre: str | None = Field(None, max_length=1)
    nationalite: str | None = Field(None, max_length=50)
    niu: str | None = Field(None, max_length=30)
    numero_cnps: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=120)
    telephone: str | None = Field(None, max_length=30)
    adresse: str | None = Field(None, max_length=255)
    date_embauche: date | None = None
    salaire_base: Decimal | None = Field(None, ge=0)
    devise_id: int | None = None
    compte_bancaire: str | None = Field(None, max_length=50)
    banque: str | None = Field(None, max_length=80)
    actif: bool | None = None


class EmployeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    utilisateur_id: int | None = None
    departement_id: int | None = None
    poste_id: int | None = None
    type_contrat_id: int | None = None
    matricule: str
    nom: str
    prenom: str
    date_naissance: date | None = None
    lieu_naissance: str | None = None
    genre: str | None = None
    nationalite: str | None = None
    niu: str | None = None
    numero_cnps: str | None = None
    email: str | None = None
    telephone: str | None = None
    adresse: str | None = None
    date_embauche: date
    salaire_base: Decimal
    devise_id: int | None = None
    compte_bancaire: str | None = None
    banque: str | None = None
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
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=80)
    paye: bool | None = None
    actif: bool | None = None


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
    motif: str | None = Field(None, max_length=255)


class DemandeCongeUpdate(BaseModel):
    statut: str | None = Field(None, max_length=20)
    commentaire_refus: str | None = Field(None, max_length=255)


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
    motif: str | None = None
    commentaire_refus: str | None = None
    approuve_par_id: int | None = None
    date_decision: datetime | None = None
    created_by_id: int | None = None
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
    droits_acquis: int | None = Field(None, ge=0)
    jours_pris: int | None = Field(None, ge=0)


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
    libelle: str | None = Field(None, max_length=150)
    date_fin: date | None = None
    montant_cible: Decimal | None = Field(None, ge=0)
    atteint: bool | None = None


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
    code: str | None = Field(None, max_length=20)
    libelle: str | None = Field(None, max_length=80)
    taux_pct: Decimal | None = Field(None, ge=0, le=100)
    actif: bool | None = None


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
    taux_commission_id: int | None = None
    date_debut: date = Field(...)
    date_fin: date = Field(...)
    montant: Decimal = Field(default=Decimal("0"), ge=0)
    libelle: str | None = Field(None, max_length=255)
    payee: bool = False


class CommissionUpdate(BaseModel):
    montant: Decimal | None = Field(None, ge=0)
    libelle: str | None = Field(None, max_length=255)
    payee: bool | None = None


class CommissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    taux_commission_id: int | None = None
    date_debut: date
    date_fin: date
    montant: Decimal
    libelle: str | None = None
    payee: bool
    created_at: datetime


# --- Avance ---
class AvanceCreate(BaseModel):
    entreprise_id: int
    employe_id: int = Field(...)
    date_avance: date = Field(...)
    montant: Decimal = Field(..., gt=0)
    motif: str | None = Field(None, max_length=255)
    rembourse: bool = False


class AvanceUpdate(BaseModel):
    motif: str | None = Field(None, max_length=255)
    rembourse: bool | None = None


class AvanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    employe_id: int
    date_avance: date
    montant: Decimal
    motif: str | None = None
    rembourse: bool
    created_by_id: int | None = None
    created_at: datetime
