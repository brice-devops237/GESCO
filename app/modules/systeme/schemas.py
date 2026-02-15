# app/modules/systeme/schemas.py
# -----------------------------------------------------------------------------
# Schémas Pydantic pour le module Système.
# -----------------------------------------------------------------------------

import re
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Paramètre système ---
class ParametreSystemeCreate(BaseModel):
    entreprise_id: int = Field(...)
    categorie: str = Field(..., max_length=50)
    cle: str = Field(..., max_length=80)
    valeur: Optional[str] = Field(None)
    description: Optional[str] = Field(None, max_length=255)


class ParametreSystemeUpdate(BaseModel):
    valeur: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)


class ParametreSystemeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    categorie: str
    cle: str
    valeur: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


# --- Journal d'audit ---
class JournalAuditCreate(BaseModel):
    entreprise_id: Optional[int] = None
    utilisateur_id: Optional[int] = None
    action: str = Field(..., max_length=30)
    module: Optional[str] = Field(None, max_length=50)
    entite_type: Optional[str] = Field(None, max_length=80)
    entite_id: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)


class JournalAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: Optional[int] = None
    utilisateur_id: Optional[int] = None
    action: str
    module: Optional[str] = None
    entite_type: Optional[str] = None
    entite_id: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


# --- Notification ---
class NotificationCreate(BaseModel):
    utilisateur_id: int = Field(...)
    titre: str = Field(..., max_length=150)
    message: Optional[str] = Field(None)
    entite_type: Optional[str] = Field(None, max_length=80)
    entite_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    lue: Optional[bool] = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    utilisateur_id: int
    titre: str
    message: Optional[str] = None
    lue: bool
    entite_type: Optional[str] = None
    entite_id: Optional[int] = None
    created_at: datetime


# --- Licence logicielle ---
# Format de la clé : XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (5 blocs de 5 caractères, lettres et chiffres majuscules)
FORMAT_CLE_LICENCE = re.compile(r"^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$")
EXEMPLE_CLE_LICENCE = "A1B2C-D3E4F-G5H6I-J7K8L-M9N0P"


class LicenceLogicielleCreate(BaseModel):
    entreprise_id: int = Field(...)
    cle_licence: str = Field(
        ...,
        max_length=35,
        description="Clé au format XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (5 blocs de 5 caractères, lettres et chiffres majuscules)",
        examples=[EXEMPLE_CLE_LICENCE],
    )
    type_licence: str = Field(
        default="standard",
        max_length=30,
        description="trial (2 mois), standard (6 mois), premium (12 mois). La durée est fixée automatiquement.",
    )
    date_debut: date = Field(..., description="Début de validité")

    @field_validator("type_licence", mode="after")
    @classmethod
    def type_licence_valide(cls, v: str) -> str:
        if v and v.strip().lower() in ("trial", "standard", "premium"):
            return v.strip().lower()
        raise ValueError("type_licence doit être : trial, standard ou premium")

    @field_validator("cle_licence", mode="after")
    @classmethod
    def cle_licence_format(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La clé de licence ne peut pas être vide.")
        cle = v.strip().upper()
        if not FORMAT_CLE_LICENCE.match(cle):
            raise ValueError(
                "Format invalide. Attendu : XXXXX-XXXXX-XXXXX-XXXXX-XXXXX "
                "(5 blocs de 5 caractères, lettres et chiffres majuscules A-Z, 0-9). Ex. : A1B2C-D3E4F-G5H6I-J7K8L-M9N0P"
            )
        return cle


class LicenceLogicielleUpdate(BaseModel):
    type_licence: Optional[str] = Field(None, max_length=30)
    date_fin: Optional[date] = None
    actif: Optional[bool] = None


class LicenceLogicielleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entreprise_id: int
    cle_licence: str
    type_licence: str
    date_debut: date
    date_fin: date
    actif: bool
    nombre_prolongations: int = 0
    date_activation: Optional[datetime] = None
    created_at: datetime


class LicenceProlongationsInfo(BaseModel):
    """Info sur les prolongations (trial/standard : max 3, premium : illimité)."""
    type_licence: str
    nombre_prolongations: int
    prolongations_restantes: Optional[int] = None  # None = illimité (premium)
    duree_ajoutee_mois: int  # durée ajoutée à chaque prolongation


class LicenceValideResponse(BaseModel):
    """Réponse pour la vérification de validité d'une licence."""
    valide: bool
    message: str
    date_fin: Optional[date] = None
