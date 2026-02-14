# app/modules/parametrage/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Paramétrage : validation des entrées (Create/Update)
# et sérialisation des sorties (Response). Aucun import des models dans les
# champs pour éviter les cycles ; on utilise des IDs et optionnellement des
# sous-objets plats (ex: role_id + role_code dans UtilisateurResponse).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.parametrage.models import ModeGestion, RegimeFiscal, TypePointDeVente


# --- Devise ------------------------------------------------------------------

class DeviseCreate(BaseModel):
    """Schéma de création d'une devise (ISO 4217 : XAF, EUR, USD)."""
    code: str = Field(..., min_length=1, max_length=3, description="Code ISO 4217 (ex. XAF, EUR, USD)")
    libelle: str = Field(..., min_length=1, max_length=50)
    symbole: Optional[str] = Field(None, max_length=10)
    decimales: int = Field(default=0, ge=0, le=6)
    actif: bool = True


class DeviseUpdate(BaseModel):
    """Schéma de mise à jour partielle d'une devise."""
    libelle: Optional[str] = Field(None, min_length=1, max_length=50)
    symbole: Optional[str] = Field(None, max_length=10)
    decimales: Optional[int] = Field(None, ge=0, le=6)
    actif: Optional[bool] = None


class DeviseResponse(BaseModel):
    """Schéma de réponse pour une devise."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str
    symbole: Optional[str] = None
    decimales: int
    actif: bool


# --- Taux de change -----------------------------------------------------------

class TauxChangeCreate(BaseModel):
    """Schéma de création d'un taux de change."""
    devise_from_id: int = Field(..., description="ID devise source")
    devise_to_id: int = Field(..., description="ID devise cible")
    taux: Decimal = Field(..., gt=0, decimal_places=6)
    date_effet: date = Field(..., description="Date d'effet du taux")


class TauxChangeResponse(BaseModel):
    """Schéma de réponse pour un taux de change."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    devise_from_id: int
    devise_to_id: int
    taux: Decimal
    date_effet: date
    created_at: datetime


# --- Entreprise ---------------------------------------------------------------

class EntrepriseCreate(BaseModel):
    """Schéma de création d'une entreprise (conformité CGI/DGI Cameroun, ISO pays/devise)."""
    code: str = Field(..., min_length=1, max_length=20)
    raison_sociale: str = Field(..., min_length=1, max_length=255)
    sigle: Optional[str] = Field(None, max_length=50)
    niu: Optional[str] = Field(None, max_length=20, description="NIU DGI – obligatoire pour opérations économiques au Cameroun")
    regime_fiscal: RegimeFiscal = Field(..., description="Régime fiscal (CGI Cameroun)")
    mode_gestion: ModeGestion
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    pays: str = Field(default="CMR", max_length=3, description="Code pays ISO 3166-1 alpha-3 (ex. CMR)")
    telephone: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    site_web: Optional[str] = Field(None, max_length=255)
    devise_principale: str = Field(default="XAF", max_length=3, description="Code devise ISO 4217 (XAF = CEMAC)")
    logo_url: Optional[str] = Field(None, max_length=500)
    actif: bool = True


class EntrepriseUpdate(BaseModel):
    """Schéma de mise à jour partielle d'une entreprise."""
    raison_sociale: Optional[str] = Field(None, min_length=1, max_length=255)
    sigle: Optional[str] = Field(None, max_length=50)
    niu: Optional[str] = Field(None, max_length=20)
    regime_fiscal: Optional[RegimeFiscal] = None
    mode_gestion: Optional[ModeGestion] = None
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    pays: Optional[str] = Field(None, max_length=3)
    telephone: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    site_web: Optional[str] = Field(None, max_length=255)
    devise_principale: Optional[str] = Field(None, max_length=3)
    logo_url: Optional[str] = Field(None, max_length=500)
    actif: Optional[bool] = None


class EntrepriseResponse(BaseModel):
    """Schéma de réponse pour une entreprise."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    raison_sociale: str
    sigle: Optional[str] = None
    niu: Optional[str] = None
    regime_fiscal: str
    mode_gestion: str
    ville: Optional[str] = None
    pays: str
    devise_principale: str
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Point de vente ----------------------------------------------------------

class PointDeVenteCreate(BaseModel):
    """Schéma de création d'un point de vente."""
    entreprise_id: int
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=100)
    type: TypePointDeVente
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=30)
    est_depot: bool = False
    actif: bool = True


class PointDeVenteUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un point de vente."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    libelle: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[TypePointDeVente] = None
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=30)
    est_depot: Optional[bool] = None
    actif: Optional[bool] = None


class PointDeVenteResponse(BaseModel):
    """Schéma de réponse pour un point de vente."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    type: str
    ville: Optional[str] = None
    est_depot: bool
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Rôle --------------------------------------------------------------------

class RoleCreate(BaseModel):
    """Schéma de création d'un rôle."""
    entreprise_id: Optional[int] = None  # NULL = rôle système
    code: str = Field(..., min_length=1, max_length=50)
    libelle: str = Field(..., min_length=1, max_length=100)


class RoleUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un rôle."""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    libelle: Optional[str] = Field(None, min_length=1, max_length=100)


class RoleResponse(BaseModel):
    """Schéma de réponse pour un rôle."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: Optional[int] = None
    code: str
    libelle: str
    created_at: datetime
    updated_at: datetime


# --- Permission --------------------------------------------------------------

class PermissionCreate(BaseModel):
    """Schéma de création d'une permission."""
    module: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    libelle: str = Field(..., min_length=1, max_length=150)


class PermissionResponse(BaseModel):
    """Schéma de réponse pour une permission."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    module: str
    action: str
    libelle: str


# --- PermissionRole (liaison rôle-permission) --------------------------------

class PermissionRoleCreate(BaseModel):
    """Schéma d'ajout d'une permission à un rôle."""
    role_id: int
    permission_id: int


class PermissionRoleResponse(BaseModel):
    """Schéma de réponse pour une liaison rôle-permission."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_id: int
    permission_id: int


# --- Utilisateur --------------------------------------------------------------

class UtilisateurCreate(BaseModel):
    """Schéma de création d'un utilisateur (mot de passe en clair)."""
    entreprise_id: int
    point_de_vente_id: Optional[int] = None
    role_id: int
    login: str = Field(..., min_length=1, max_length=80)
    mot_de_passe: str = Field(..., min_length=8, max_length=128)
    email: Optional[EmailStr] = None
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=30)
    actif: bool = True


class UtilisateurUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un utilisateur."""
    point_de_vente_id: Optional[int] = None
    role_id: Optional[int] = None
    email: Optional[EmailStr] = None
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=30)
    actif: Optional[bool] = None
    mot_de_passe: Optional[str] = Field(None, min_length=8, max_length=128)


class UtilisateurResponse(BaseModel):
    """Schéma de réponse pour un utilisateur (sans mot de passe)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    point_de_vente_id: Optional[int] = None
    role_id: int
    login: str
    email: Optional[str] = None
    nom: str
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    actif: bool
    derniere_connexion_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# --- Session -----------------------------------------------------------------

class SessionResponse(BaseModel):
    """Schéma de réponse pour une session (lecture seule)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    utilisateur_id: int
    token: str
    identifiant_appareil: Optional[str] = None
    expire_at: datetime
    last_activity_at: Optional[datetime] = None
    created_at: datetime
    closed_at: Optional[datetime] = None


# --- Affectation utilisateur / PDV -------------------------------------------

class AffectationUtilisateurPdvCreate(BaseModel):
    """Schéma de création d'une affectation utilisateur <-> PDV."""
    utilisateur_id: int
    point_de_vente_id: int
    est_principal: bool = False


class AffectationUtilisateurPdvUpdate(BaseModel):
    """Schéma de mise à jour (principalement est_principal)."""
    est_principal: Optional[bool] = None


class AffectationUtilisateurPdvResponse(BaseModel):
    """Schéma de réponse pour une affectation."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    utilisateur_id: int
    point_de_vente_id: int
    est_principal: bool
