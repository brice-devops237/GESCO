# app/modules/stock/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module Stock : stocks, mouvements, alertes.
# -----------------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Stock ---
class QuantiteStockResponse(BaseModel):
    """Quantité en stock pour un dépôt × produit × variante (optionnelle)."""
    depot_id: int
    produit_id: int
    variante_id: Optional[int] = None
    quantite: Decimal


class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    depot_id: int
    produit_id: int
    variante_id: Optional[int] = None
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
    depot_dest_id: Optional[int] = Field(None, description="Dépôt destination (obligatoire pour transfert)")
    produit_id: int = Field(...)
    variante_id: Optional[int] = None
    quantite: Decimal = Field(..., gt=0)
    reference_type: str = Field(..., max_length=30)  # reception, bon_livraison, manuel, inventaire, transfert
    reference_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=2000)


class MouvementStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type_mouvement: str
    depot_id: int
    depot_dest_id: Optional[int] = None
    produit_id: int
    variante_id: Optional[int] = None
    quantite: Decimal
    date_mouvement: datetime
    reference_type: str
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: datetime


# --- Alertes (lecture seule) ---
class AlerteStockResponse(BaseModel):
    """Une alerte : produit/dépôt/variante avec quantité hors seuils."""
    produit_id: int
    produit_code: Optional[str] = None
    produit_libelle: Optional[str] = None
    depot_id: int
    depot_libelle: Optional[str] = None
    variante_id: Optional[int] = None
    variante_libelle: Optional[str] = None
    quantite: Decimal
    seuil_alerte_min: Decimal
    seuil_alerte_max: Optional[Decimal] = None
    type_alerte: str  # sous_seuil | au_dessus_max
