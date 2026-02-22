# app/modules/parametrage/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Paramétrage : validation des entrées (Create/Update)
# et sérialisation des sorties (Response). Aucun import des models dans les
# champs pour éviter les cycles ; on utilise des IDs et optionnellement des
# sous-objets plats (ex: role_id + role_code dans UtilisateurResponse).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.parametrage.models import FormeJuridique, ModeGestion, RegimeFiscal, TypePointDeVente

# --- Devise ------------------------------------------------------------------

class DeviseCreate(BaseModel):
    """Schéma de création d'une devise (ISO 4217 : XAF, EUR, USD)."""
    code: str = Field(..., min_length=1, max_length=3, description="Code ISO 4217 (ex. XAF, EUR, USD)")
    libelle: str = Field(..., min_length=1, max_length=50)
    symbole: str | None = Field(None, max_length=10)
    decimales: int = Field(default=0, ge=0, le=6)
    actif: bool = True


class DeviseUpdate(BaseModel):
    """Schéma de mise à jour partielle d'une devise."""
    libelle: str | None = Field(None, min_length=1, max_length=50)
    symbole: str | None = Field(None, max_length=10)
    decimales: int | None = Field(None, ge=0, le=6)
    actif: bool | None = None


class DeviseResponse(BaseModel):
    """Schéma de réponse pour une devise."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str
    symbole: str | None = None
    decimales: int
    actif: bool


class ListDevisesResponse(BaseModel):
    """Réponse paginée de la liste des devises."""
    items: list[DeviseResponse] = Field(..., description="Liste des devises")
    total: int = Field(..., description="Nombre total (pour pagination)")


class DeviseStatsResponse(BaseModel):
    """Statistiques globales sur les devises."""
    total: int = Field(..., description="Nombre total de devises")
    actives: int = Field(..., description="Nombre de devises actives")
    inactives: int = Field(..., description="Nombre de devises inactives")


# --- Taux de change -----------------------------------------------------------

class TauxChangeCreate(BaseModel):
    """Schéma de création d'un taux de change (source : BCEAC, banque centrale, manuel, api)."""
    devise_from_id: int = Field(..., description="ID devise source")
    devise_to_id: int = Field(..., description="ID devise cible")
    taux: Decimal = Field(..., gt=0, decimal_places=6)
    date_effet: date = Field(..., description="Date d'effet du taux")
    source: str | None = Field(None, max_length=30, description="bcceac, banque_centrale, manuel, api")


class TauxChangeUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un taux de change."""
    taux: Decimal | None = Field(None, gt=0)
    source: str | None = Field(None, max_length=30)


class TauxChangeResponse(BaseModel):
    """Schéma de réponse pour un taux de change."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    devise_from_id: int
    devise_to_id: int
    taux: Decimal
    date_effet: date
    source: str | None = None
    created_at: datetime


class ListTauxChangeResponse(BaseModel):
    """Réponse paginée de la liste des taux de change."""
    items: list[TauxChangeResponse] = Field(..., description="Liste des taux")
    total: int = Field(..., description="Nombre total (pour pagination)")


class TauxChangeStatsResponse(BaseModel):
    """Statistiques globales sur les taux de change."""
    total: int = Field(..., description="Nombre total de taux de change")


# --- Entreprise ---------------------------------------------------------------

class EntrepriseCreate(BaseModel):
    """Schéma de création d'une entreprise (conformité CGI/DGI Cameroun, OHADA, ISO pays/devise)."""
    code: str = Field(..., min_length=1, max_length=20)
    raison_sociale: str = Field(..., min_length=1, max_length=255)
    sigle: str | None = Field(None, max_length=50)
    niu: str | None = Field(None, max_length=20, description="NIU DGI – obligatoire pour opérations économiques au Cameroun")
    regime_fiscal: RegimeFiscal = Field(..., description="Régime fiscal (CGI Cameroun)")
    mode_gestion: ModeGestion
    forme_juridique: FormeJuridique | None = Field(None, description="OHADA : SARL, SA, SAS, etc.")
    rccm: str | None = Field(None, max_length=50, description="Registre du Commerce et du Crédit Mobilier")
    cnps: str | None = Field(None, max_length=30, description="Numéro CNPS / sécurité sociale")
    adresse: str | None = None
    code_postal: str | None = Field(None, max_length=20)
    boite_postale: str | None = Field(None, max_length=20, description="Courant en Afrique francophone")
    ville: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    pays: str = Field(default="CMR", max_length=3, description="Code pays ISO 3166-1 alpha-3 (ex. CMR)")
    fuseau_horaire: str | None = Field(None, max_length=50, description="IANA ex. Africa/Douala")
    telephone: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    site_web: str | None = Field(None, max_length=255)
    devise_principale: str = Field(default="XAF", max_length=3, description="Code devise ISO 4217 (XAF = CEMAC)")
    date_creation: date | None = Field(None, description="Date de création juridique de la société")
    capital_social: Decimal | None = Field(None, ge=0, description="Montant en devise principale")
    logo_url: str | None = Field(None, max_length=500)
    actif: bool = True


class EntrepriseUpdate(BaseModel):
    """Schéma de mise à jour partielle d'une entreprise."""
    raison_sociale: str | None = Field(None, min_length=1, max_length=255)
    sigle: str | None = Field(None, max_length=50)
    niu: str | None = Field(None, max_length=20)
    regime_fiscal: RegimeFiscal | None = None
    mode_gestion: ModeGestion | None = None
    forme_juridique: FormeJuridique | None = None
    rccm: str | None = Field(None, max_length=50)
    cnps: str | None = Field(None, max_length=30)
    adresse: str | None = None
    code_postal: str | None = Field(None, max_length=20)
    boite_postale: str | None = Field(None, max_length=20)
    ville: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    pays: str | None = Field(None, max_length=3)
    fuseau_horaire: str | None = Field(None, max_length=50)
    telephone: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    site_web: str | None = Field(None, max_length=255)
    devise_principale: str | None = Field(None, max_length=3)
    date_creation: date | None = None
    capital_social: Decimal | None = Field(None, ge=0)
    logo_url: str | None = Field(None, max_length=500)
    actif: bool | None = None


class EntrepriseResponse(BaseModel):
    """Schéma de réponse pour une entreprise."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    raison_sociale: str
    sigle: str | None = None
    niu: str | None = None
    regime_fiscal: str
    mode_gestion: str
    forme_juridique: str | None = None
    rccm: str | None = None
    cnps: str | None = None
    ville: str | None = None
    region: str | None = None
    pays: str
    fuseau_horaire: str | None = None
    devise_principale: str
    date_creation: date | None = None
    capital_social: Decimal | None = None
    actif: bool
    created_at: datetime
    updated_at: datetime


class ListEntreprisesResponse(BaseModel):
    """Réponse paginée de la liste des entreprises."""
    items: list[EntrepriseResponse] = Field(..., description="Liste des entreprises")
    total: int = Field(..., description="Nombre total d'entreprises (pour pagination)")


class EntrepriseStatsResponse(BaseModel):
    """Statistiques globales sur les entreprises (pour tableau de bord paramétrage)."""
    total: int = Field(..., description="Nombre total d'entreprises (hors supprimées)")
    actives: int = Field(..., description="Nombre d'entreprises actives")
    inactives: int = Field(..., description="Nombre d'entreprises inactives")
    par_regime_fiscal: dict[str, int] = Field(default_factory=dict, description="Effectif par régime fiscal")
    par_pays: dict[str, int] = Field(default_factory=dict, description="Effectif par pays (code ISO)")


# --- Point de vente ----------------------------------------------------------

class PointDeVenteCreate(BaseModel):
    """Schéma de création d'un point de vente (magasin, dépôt, agence)."""
    entreprise_id: int
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=100)
    type: TypePointDeVente
    adresse: str | None = None
    code_postal: str | None = Field(None, max_length=20)
    ville: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    latitude: Decimal | None = Field(None, ge=Decimal("-90"), le=Decimal("90"), description="Latitude WGS84 (-90 à 90)")
    longitude: Decimal | None = Field(None, ge=Decimal("-180"), le=Decimal("180"), description="Longitude WGS84 (-180 à 180)")
    fuseau_horaire: str | None = Field(None, max_length=50, description="Si vide, hérite de l'entreprise")
    est_depot: bool = False
    actif: bool = True


class PointDeVenteUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un point de vente."""
    code: str | None = Field(None, min_length=1, max_length=20)
    libelle: str | None = Field(None, min_length=1, max_length=100)
    type: TypePointDeVente | None = None
    adresse: str | None = None
    code_postal: str | None = Field(None, max_length=20)
    ville: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    latitude: Decimal | None = Field(None, ge=Decimal("-90"), le=Decimal("90"))
    longitude: Decimal | None = Field(None, ge=Decimal("-180"), le=Decimal("180"))
    fuseau_horaire: str | None = Field(None, max_length=50)
    est_depot: bool | None = None
    actif: bool | None = None


class PointDeVenteResponse(BaseModel):
    """Schéma de réponse pour un point de vente (avec coordonnées pour carte)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    type: str
    adresse: str | None = None
    ville: str | None = None
    code_postal: str | None = None
    telephone: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    fuseau_horaire: str | None = None
    est_depot: bool
    actif: bool
    created_at: datetime
    updated_at: datetime


class ListPointsVenteResponse(BaseModel):
    """Réponse paginée de la liste des points de vente d'une entreprise."""
    items: list[PointDeVenteResponse] = Field(..., description="Liste des points de vente")
    total: int = Field(..., description="Nombre total (pour pagination)")


class PointVenteStatsResponse(BaseModel):
    """Statistiques des points de vente d'une entreprise."""
    total: int = Field(..., description="Nombre total de points de vente")
    actifs: int = Field(..., description="Nombre de points actifs")
    inactifs: int = Field(..., description="Nombre de points inactifs")
    par_type: dict[str, int] = Field(default_factory=dict, description="Effectif par type (principal, secondaire, depot)")


# --- Rôle --------------------------------------------------------------------

class RoleCreate(BaseModel):
    """Schéma de création d'un rôle."""
    entreprise_id: int | None = None  # NULL = rôle système
    code: str = Field(..., min_length=1, max_length=50)
    libelle: str = Field(..., min_length=1, max_length=100)


class RoleUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un rôle."""
    code: str | None = Field(None, min_length=1, max_length=50)
    libelle: str | None = Field(None, min_length=1, max_length=100)


class RoleResponse(BaseModel):
    """Schéma de réponse pour un rôle."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int | None = None
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


class RoleMinimal(BaseModel):
    """Rôle minimal (id, code, libellé) pour affichage dans une permission."""
    id: int
    code: str
    libelle: str = ""


class PermissionWithRolesResponse(PermissionResponse):
    """Permission avec la liste des rôles auxquels elle est affectée."""
    roles: list[RoleMinimal] = []


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
    point_de_vente_id: int | None = None
    role_id: int
    login: str = Field(..., min_length=1, max_length=80)
    mot_de_passe: str = Field(..., min_length=8, max_length=128)
    email: EmailStr | None = None
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    actif: bool = True


class UtilisateurUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un utilisateur."""
    point_de_vente_id: int | None = None
    role_id: int | None = None
    email: EmailStr | None = None
    nom: str | None = Field(None, min_length=1, max_length=100)
    prenom: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    actif: bool | None = None
    mot_de_passe: str | None = Field(None, min_length=8, max_length=128)


class UtilisateurResponse(BaseModel):
    """Schéma de réponse pour un utilisateur (sans mot de passe)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    point_de_vente_id: int | None = None
    role_id: int
    login: str
    email: str | None = None
    nom: str
    prenom: str | None = None
    telephone: str | None = None
    actif: bool
    derniere_connexion_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UtilisateurChangePassword(BaseModel):
    """Schéma pour le changement de mot de passe (par l'utilisateur ou un admin)."""
    ancien_mot_de_passe: str | None = Field(None, min_length=1, description="Requis si on change son propre mot de passe.")
    nouveau_mot_de_passe: str = Field(..., min_length=8, max_length=128)


# --- Session -----------------------------------------------------------------

class SessionResponse(BaseModel):
    """Schéma de réponse pour une session (lecture seule)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    utilisateur_id: int
    token: str
    identifiant_appareil: str | None = None
    expire_at: datetime
    last_activity_at: datetime | None = None
    created_at: datetime
    closed_at: datetime | None = None


# --- Affectation utilisateur / PDV -------------------------------------------

class AffectationUtilisateurPdvCreate(BaseModel):
    """Schéma de création d'une affectation utilisateur <-> PDV."""
    utilisateur_id: int
    point_de_vente_id: int
    est_principal: bool = False


class AffectationUtilisateurPdvUpdate(BaseModel):
    """Schéma de mise à jour (principalement est_principal)."""
    est_principal: bool | None = None


class AffectationUtilisateurPdvResponse(BaseModel):
    """Schéma de réponse pour une affectation."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    utilisateur_id: int
    point_de_vente_id: int
    est_principal: bool

