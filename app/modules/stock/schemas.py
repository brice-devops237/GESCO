# app/modules/stock/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module Stock : stocks, mouvements, alertes.
# -----------------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- Stock ---
class QuantiteStockResponse(BaseModel):
    """Quantité en stock pour un dépôt × produit × variante (optionnelle)."""
    depot_id: int
    produit_id: int
    variante_id: int | None = None
    quantite: Decimal


class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    depot_id: int
    produit_id: int
    variante_id: int | None = None
    quantite: Decimal
    unite_id: int
    updated_at: datetime


class StockUpdate(BaseModel):
    """Ajustement manuel de quantité (préférer les mouvements pour la traçabilité)."""
    quantite: Decimal = Field(..., ge=0)


# --- Mouvement ---
class MouvementStockCreate(BaseModel):
    type_mouvement: str = Field(..., max_length=20)  # entree, sortie, transfert, inventaire
    depot_id: int = Field(..., description="Dépôt origine (ou unique pour entree/sortie/inventaire)")
    depot_dest_id: int | None = Field(None, description="Dépôt destination (obligatoire pour transfert)")
    produit_id: int = Field(...)
    variante_id: int | None = None
    quantite: Decimal = Field(..., gt=0)
    reference_type: str = Field(..., max_length=30)  # reception, bon_livraison, manuel, inventaire, transfert
    reference_id: int | None = None
    notes: str | None = Field(None, max_length=2000)


class MouvementStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type_mouvement: str
    depot_id: int
    depot_dest_id: int | None = None
    produit_id: int
    variante_id: int | None = None
    quantite: Decimal
    date_mouvement: datetime
    reference_type: str
    reference_id: int | None = None
    notes: str | None = None
    created_by_id: int | None = None
    created_at: datetime


# --- Alertes (lecture seule) ---
class AlerteStockResponse(BaseModel):
    """Une alerte : produit/dépôt/variante avec quantité hors seuils."""
    produit_id: int
    produit_code: str | None = None
    produit_libelle: str | None = None
    depot_id: int
    depot_libelle: str | None = None
    variante_id: int | None = None
    variante_libelle: str | None = None
    quantite: Decimal
    seuil_alerte_min: Decimal
    seuil_alerte_max: Decimal | None = None
    type_alerte: str  # sous_seuil | au_dessus_max
