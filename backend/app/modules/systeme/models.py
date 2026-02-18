# app/modules/systeme/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Système : paramètres applicatifs, journal d'audit,
# notifications, licences. Dépend de Paramétrage (entreprises, utilisateurs).
# Extension monde réel : isolation multi-tenant, toutes structures, tous secteurs.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    ...


# --- Paramètre système -------------------------------------------------------
class ParametreSysteme(Base):
    """
    Paramètre applicatif par entreprise (clé/valeur ou catégorie).
    Ex. : langue par défaut, devise affichage, délai session, options module.
    Table : parametres_systeme.
    """
    __tablename__ = "parametres_systeme"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ex. "general", "compta", "rh"
    cle: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    valeur: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "categorie", "cle", name="uq_parametres_systeme_ent_cat_cle"),
    )


# --- Journal d'audit ----------------------------------------------------------
class JournalAudit(Base):
    """
    Trace des actions utilisateur (création, modification, suppression, connexion).
    Table : journaux_audit.
    """
    __tablename__ = "journaux_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=True)
    utilisateur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # create, update, delete, login, logout
    module: Mapped[str] = mapped_column(String(50), nullable=True, index=True)  # comptabilite, rh, etc.
    entite_type: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    entite_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Notification -------------------------------------------------------------
class Notification(Base):
    """
    Notification à l'attention d'un utilisateur (in-app).
    Table : notifications.
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    titre: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    lue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    entite_type: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    entite_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Licence logicielle -------------------------------------------------------
class LicenceLogicielle(Base):
    """
    Licence logicielle par entreprise, validité 1 an (ou autre durée).
    Table : licences_logicielles.
    """
    __tablename__ = "licences_logicielles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    cle_licence: Mapped[str] = mapped_column(String(35), nullable=False, index=True)  # Format: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
    type_licence: Mapped[str] = mapped_column(String(30), nullable=False, default="standard")  # standard, premium, trial
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    nombre_prolongations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # trial/standard max 3, premium illimité
    date_activation: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "cle_licence", name="uq_licences_logicielles_entreprise_cle"),
    )

