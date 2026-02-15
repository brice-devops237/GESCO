# app/modules/catalogue/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic du module Catalogue : validation entrées (Create/Update)
# et sérialisation sorties (Response). Conformité : TVA CGI Cameroun, unités courantes.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.catalogue.models import TypeProduit, TypeUniteMesure

# --- UniteMesure -----------------------------------------------------------------

class UniteMesureCreate(BaseModel):
    """Schéma de création d'une unité de mesure."""
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=50)
    symbole: str | None = Field(None, max_length=10)
    type: TypeUniteMesure
    actif: bool = True


class UniteMesureUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    libelle: str | None = Field(None, min_length=1, max_length=50)
    symbole: str | None = Field(None, max_length=10)
    type: TypeUniteMesure | None = None
    actif: bool | None = None


class UniteMesureResponse(BaseModel):
    """Schéma de réponse pour une unité de mesure."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str
    symbole: str | None = None
    type: str
    actif: bool


# --- TauxTva --------------------------------------------------------------------

class TauxTvaCreate(BaseModel):
    """Schéma de création d'un taux de TVA (CGI Cameroun : 0, 9.75, 10, 19.25 %, etc.)."""
    code: str = Field(..., min_length=1, max_length=20)
    taux: Decimal = Field(..., ge=0, le=100, decimal_places=2)
    libelle: str = Field(..., min_length=1, max_length=80)
    actif: bool = True


class TauxTvaUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    taux: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)
    libelle: str | None = Field(None, min_length=1, max_length=80)
    actif: bool | None = None


class TauxTvaResponse(BaseModel):
    """Schéma de réponse pour un taux de TVA."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    taux: Decimal
    libelle: str
    actif: bool


# --- FamilleProduit -------------------------------------------------------------

class FamilleProduitCreate(BaseModel):
    """Schéma de création d'une famille de produits."""
    entreprise_id: int
    parent_id: int | None = None
    code: str = Field(..., min_length=1, max_length=30)
    libelle: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    niveau: int = Field(default=1, ge=1)
    ordre_affichage: int = 0
    actif: bool = True


class FamilleProduitUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    parent_id: int | None = None
    code: str | None = Field(None, min_length=1, max_length=30)
    libelle: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = None
    niveau: int | None = Field(None, ge=1)
    ordre_affichage: int | None = None
    actif: bool | None = None


class FamilleProduitResponse(BaseModel):
    """Schéma de réponse pour une famille de produits."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    parent_id: int | None = None
    code: str
    libelle: str
    description: str | None = None
    niveau: int
    ordre_affichage: int
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Conditionnement -----------------------------------------------------------

class ConditionnementCreate(BaseModel):
    """Schéma de création d'un conditionnement."""
    entreprise_id: int
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=80)
    quantite_unites: Decimal = Field(..., gt=0, decimal_places=3)
    unite_id: int
    actif: bool = True


class ConditionnementUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    code: str | None = Field(None, min_length=1, max_length=20)
    libelle: str | None = Field(None, min_length=1, max_length=80)
    quantite_unites: Decimal | None = Field(None, gt=0, decimal_places=3)
    unite_id: int | None = None
    actif: bool | None = None


class ConditionnementResponse(BaseModel):
    """Schéma de réponse pour un conditionnement."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    quantite_unites: Decimal
    unite_id: int
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- Produit --------------------------------------------------------------------

class ProduitCreate(BaseModel):
    """Schéma de création d'un produit."""
    entreprise_id: int
    famille_id: int | None = None
    code: str = Field(..., min_length=1, max_length=50)
    code_barre: str | None = Field(None, max_length=50)
    libelle: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: TypeProduit = TypeProduit.produit
    unite_vente_id: int
    unite_achat_id: int | None = None
    coefficient_achat_vente: Decimal = Field(default=Decimal("1"), ge=0, decimal_places=4)
    prix_achat_ht: Decimal | None = Field(None, ge=0, decimal_places=2)
    prix_vente_ttc: Decimal = Field(..., ge=0, decimal_places=2)
    taux_tva_id: int | None = None
    seuil_alerte_min: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=3)
    seuil_alerte_max: Decimal | None = Field(None, ge=0, decimal_places=3)
    gerer_stock: bool = True
    actif: bool = True


class ProduitUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    famille_id: int | None = None
    code: str | None = Field(None, min_length=1, max_length=50)
    code_barre: str | None = Field(None, max_length=50)
    libelle: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    type: TypeProduit | None = None
    unite_vente_id: int | None = None
    unite_achat_id: int | None = None
    coefficient_achat_vente: Decimal | None = Field(None, ge=0, decimal_places=4)
    prix_achat_ht: Decimal | None = Field(None, ge=0, decimal_places=2)
    prix_vente_ttc: Decimal | None = Field(None, ge=0, decimal_places=2)
    taux_tva_id: int | None = None
    seuil_alerte_min: Decimal | None = Field(None, ge=0, decimal_places=3)
    seuil_alerte_max: Decimal | None = Field(None, ge=0, decimal_places=3)
    gerer_stock: bool | None = None
    actif: bool | None = None


class ProduitResponse(BaseModel):
    """Schéma de réponse pour un produit."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    famille_id: int | None = None
    code: str
    code_barre: str | None = None
    libelle: str
    description: str | None = None
    type: str
    unite_vente_id: int
    unite_achat_id: int | None = None
    coefficient_achat_vente: Decimal
    prix_achat_ht: Decimal | None = None
    prix_vente_ttc: Decimal
    taux_tva_id: int | None = None
    seuil_alerte_min: Decimal
    seuil_alerte_max: Decimal | None = None
    gerer_stock: bool
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- ProduitConditionnement -----------------------------------------------------

class ProduitConditionnementCreate(BaseModel):
    """Schéma de création d'une liaison produit-conditionnement."""
    produit_id: int
    conditionnement_id: int
    quantite_unites: Decimal = Field(..., gt=0, decimal_places=3)
    prix_vente_ttc: Decimal | None = Field(None, ge=0, decimal_places=2)


class ProduitConditionnementUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    quantite_unites: Decimal | None = Field(None, gt=0, decimal_places=3)
    prix_vente_ttc: Decimal | None = Field(None, ge=0, decimal_places=2)


class ProduitConditionnementResponse(BaseModel):
    """Schéma de réponse pour une liaison produit-conditionnement."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    produit_id: int
    conditionnement_id: int
    quantite_unites: Decimal
    prix_vente_ttc: Decimal | None = None


# --- CanalVente -----------------------------------------------------------------

class CanalVenteCreate(BaseModel):
    """Schéma de création d'un canal de vente."""
    entreprise_id: int
    code: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=80)
    ordre: int = 0
    actif: bool = True


class CanalVenteUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    code: str | None = Field(None, min_length=1, max_length=20)
    libelle: str | None = Field(None, min_length=1, max_length=80)
    ordre: int | None = None
    actif: bool | None = None


class CanalVenteResponse(BaseModel):
    """Schéma de réponse pour un canal de vente."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    code: str
    libelle: str
    ordre: int
    actif: bool
    created_at: datetime
    updated_at: datetime


# --- PrixProduit ----------------------------------------------------------------

class PrixProduitCreate(BaseModel):
    """Schéma de création d'un prix produit (canal/PDV)."""
    produit_id: int
    canal_vente_id: int | None = None
    point_de_vente_id: int | None = None
    prix_ttc: Decimal = Field(..., ge=0, decimal_places=2)
    prix_ht: Decimal | None = Field(None, ge=0, decimal_places=2)
    date_debut: date
    date_fin: date | None = None


class PrixProduitUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    canal_vente_id: int | None = None
    point_de_vente_id: int | None = None
    prix_ttc: Decimal | None = Field(None, ge=0, decimal_places=2)
    prix_ht: Decimal | None = Field(None, ge=0, decimal_places=2)
    date_debut: date | None = None
    date_fin: date | None = None


class PrixProduitResponse(BaseModel):
    """Schéma de réponse pour un prix produit."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    produit_id: int
    canal_vente_id: int | None = None
    point_de_vente_id: int | None = None
    prix_ttc: Decimal
    prix_ht: Decimal | None = None
    date_debut: date
    date_fin: date | None = None
    created_at: datetime
    updated_at: datetime


# --- VarianteProduit ------------------------------------------------------------

class VarianteProduitCreate(BaseModel):
    """Schéma de création d'une variante de produit."""
    produit_id: int
    code: str = Field(..., min_length=1, max_length=50)
    libelle: str = Field(..., min_length=1, max_length=150)
    prix_ttc_supplement: Decimal = Field(default=Decimal("0"), decimal_places=2)
    stock_separe: bool = False
    actif: bool = True


class VarianteProduitUpdate(BaseModel):
    """Schéma de mise à jour partielle."""
    code: str | None = Field(None, min_length=1, max_length=50)
    libelle: str | None = Field(None, min_length=1, max_length=150)
    prix_ttc_supplement: Decimal | None = Field(None, decimal_places=2)
    stock_separe: bool | None = None
    actif: bool | None = None


class VarianteProduitResponse(BaseModel):
    """Schéma de réponse pour une variante de produit."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    produit_id: int
    code: str
    libelle: str
    prix_ttc_supplement: Decimal
    stock_separe: bool
    actif: bool
    created_at: datetime
    updated_at: datetime
