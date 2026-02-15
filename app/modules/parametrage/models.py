# app/modules/parametrage/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Paramétrage : entreprises, devises, taux de change,
# points de vente, rôles, permissions, utilisateurs, affectations PDV.
# Conformité CGI/DGI Cameroun, ISO pays/devise.
# -----------------------------------------------------------------------------

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
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


class RegimeFiscal(str, PyEnum):
    informel = "informel"
    liberatoire = "liberatoire"
    forfait = "forfait"
    reel_simplifie = "reel_simplifie"
    reel_normal = "reel_normal"


class ModeGestion(str, PyEnum):
    standard = "standard"
    simplifie = "simplifie"


class TypePointDeVente(str, PyEnum):
    principal = "principal"
    secondaire = "secondaire"
    depot = "depot"


class Devise(Base):
    __tablename__ = "devises"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True, index=True)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    symbole: Mapped[str | None] = mapped_column(String(10), nullable=True)
    decimales: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class TauxChange(Base):
    __tablename__ = "taux_change"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    devise_from_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    devise_to_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    taux: Mapped[float] = mapped_column(nullable=False)
    date_effet: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Entreprise(Base):
    __tablename__ = "entreprises"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    raison_sociale: Mapped[str] = mapped_column(String(255), nullable=False)
    sigle: Mapped[str | None] = mapped_column(String(50), nullable=True)
    niu: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    regime_fiscal: Mapped[str] = mapped_column(String(30), nullable=False)
    mode_gestion: Mapped[str] = mapped_column(String(30), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pays: Mapped[str] = mapped_column(String(3), nullable=False, default="CMR")
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    site_web: Mapped[str | None] = mapped_column(String(255), nullable=True)
    devise_principale: Mapped[str] = mapped_column(String(3), nullable=False, default="XAF")
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PointDeVente(Base):
    __tablename__ = "points_de_vente"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    est_depot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_points_de_vente_entreprise_code"),)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    __table_args__ = (UniqueConstraint("module", "action", name="uq_permissions_module_action"),)


class PermissionRole(Base):
    __tablename__ = "permissions_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id"), nullable=False)
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_permissions_roles_role_permission"),)


class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    login: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    derniere_connexion_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint("entreprise_id", "login", name="uq_utilisateurs_entreprise_login"),)


class AffectationUtilisateurPdv(Base):
    __tablename__ = "affectations_utilisateur_pdv"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    est_principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    __table_args__ = (UniqueConstraint("utilisateur_id", "point_de_vente_id", name="uq_affectations_utilisateur_pdv"),)
