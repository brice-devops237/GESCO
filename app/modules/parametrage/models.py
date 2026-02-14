# app/modules/parametrage/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module Paramétrage (A.1) : entreprises, devises, taux_change,
# points_de_vente, utilisateurs, roles, permissions, sessions, affectations.
# Conformité : Cameroun (CGI, DGI, NIU), CEMAC (XAF), ISO 3166 (pays), ISO 4217 (devises).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    pass  # Pour les type hints des relations (évite imports circulaires)


# --- Enums (alignés sur la spécification) ------------------------------------

class RegimeFiscal(str, PyEnum):
    """
    Régime fiscal entreprise (Cameroun – CGI).
    - informel : secteur informel
    - liberatoire : impôt libératoire (CA ≤ 10 M FCFA)
    - forfait : régime forfaitaire
    - reel_simplifie : régime simplifié d'imposition – RSI (CA 10–50 M FCFA)
    - reel_normal : régime du réel (CA > 50 M FCFA)
    """
    informel = "informel"
    liberatoire = "liberatoire"
    forfait = "forfait"
    reel_simplifie = "reel_simplifie"
    reel_normal = "reel_normal"


class ModeGestion(str, PyEnum):
    """Mode de gestion (informel / formel)."""
    informel = "informel"
    formel = "formel"


class TypePointDeVente(str, PyEnum):
    """Type de point de vente (siège, boutique, dépôt, marché, stand, mobile)."""
    siege = "siege"
    boutique = "boutique"
    depot = "depot"
    marche = "marche"
    stand = "stand"
    mobile = "mobile"


# --- Tables sans FK vers d'autres tables du module ---------------------------

class Devise(Base):
    """
    Référentiel des devises (ISO 4217 : XAF, EUR, USD). Utilisé pour les montants
    et les taux de change. CEMAC : devise légale XAF. Table : devises.
    """
    __tablename__ = "devises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False, index=True)  # ISO 4217
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    symbole: Mapped[str | None] = mapped_column(String(10), nullable=True)  # FCFA, €, $
    decimales: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relations vers tables qui référencent devises (lecture seule depuis ce module)
    # taux_change_from = relationship("TauxChange", foreign_keys="TauxChange.devise_from_id", ...)


class Permission(Base):
    """
    Référentiel des actions autorisables par module (lire, créer, modifier, ...).
    Affectation à un rôle via permissions_roles. Table : permissions.
    """
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)

    __table_args__ = (UniqueConstraint("module", "action", name="uq_permissions_module_action"),)

    # Many-to-many avec Role via permissions_roles
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="permissions_roles",
        back_populates="permissions",
    )


# --- Entreprise (racine multi-tenant) -----------------------------------------
# created_by_id / updated_by_id -> utilisateurs ; on utilise FK sans relationship
# pour éviter cycle Entreprise <-> Utilisateur au chargement.

class Entreprise(Base):
    """
    Entité racine : entreprise avec infos légales et fiscales (Cameroun / international).
    NIU : Numéro d'Identification Unique DGI, obligatoire pour opérations économiques (CGI).
    Pays : ISO 3166-1 alpha-3 (CMR par défaut). Devise : ISO 4217 (XAF par défaut, CEMAC).
    Table : entreprises.
    """
    __tablename__ = "entreprises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    raison_sociale: Mapped[str] = mapped_column(String(255), nullable=False)
    sigle: Mapped[str | None] = mapped_column(String(50), nullable=True)
    niu: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, index=True)  # DGI Cameroun
    regime_fiscal: Mapped[str] = mapped_column(
        Enum(RegimeFiscal),
        nullable=False,
    )
    mode_gestion: Mapped[str] = mapped_column(Enum(ModeGestion), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pays: Mapped[str] = mapped_column(String(3), nullable=False, default="CMR")  # ISO 3166-1 alpha-3
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    site_web: Mapped[str | None] = mapped_column(String(255), nullable=True)
    devise_principale: Mapped[str] = mapped_column(String(3), nullable=False, default="XAF")  # CEMAC
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relations (noms en chaîne pour éviter forward reference)
    points_de_vente: Mapped[list["PointDeVente"]] = relationship("PointDeVente", back_populates="entreprise")
    roles: Mapped[list["Role"]] = relationship("Role", back_populates="entreprise")
    utilisateurs: Mapped[list["Utilisateur"]] = relationship("Utilisateur", back_populates="entreprise")


class Role(Base):
    """
    Profil de droits (admin, vendeur, caissier). Les permissions sont définies
    via permissions_roles. Table : roles.
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=True)  # NULL = rôle système
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_roles_entreprise_code"),)

    entreprise: Mapped["Entreprise | None"] = relationship("Entreprise", back_populates="roles")
    utilisateurs: Mapped[list["Utilisateur"]] = relationship("Utilisateur", back_populates="role")
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="permissions_roles",
        back_populates="roles",
    )


class PointDeVente(Base):
    """
    Lieu de vente ou d'activité (siège, boutique, dépôt, marché, stand, mobile).
    Table : points_de_vente.
    """
    __tablename__ = "points_de_vente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(Enum(TypePointDeVente), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    est_depot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "code", name="uq_points_de_vente_entreprise_code"),)

    entreprise: Mapped["Entreprise"] = relationship("Entreprise", back_populates="points_de_vente")


class Utilisateur(Base):
    """
    Compte utilisateur (login, mot de passe, rôle) pour accéder au système.
    Lié à une entreprise, un point de vente par défaut et un rôle ; peut être
    affecté à plusieurs PDV via affectations_utilisateur_point_de_vente.
    Table : utilisateurs.
    """
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    point_de_vente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    login: Mapped[str] = mapped_column(String(80), nullable=False)
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
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint("entreprise_id", "login", name="uq_utilisateurs_entreprise_login"),)

    entreprise: Mapped["Entreprise"] = relationship("Entreprise", back_populates="utilisateurs")
    point_de_vente: Mapped["PointDeVente | None"] = relationship("PointDeVente", backref="utilisateurs_par_defaut")
    role: Mapped["Role"] = relationship("Role", back_populates="utilisateurs")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="utilisateur")
    affectations_pdv: Mapped[list["AffectationUtilisateurPdv"]] = relationship(
        "AffectationUtilisateurPdv",
        back_populates="utilisateur",
    )


# --- Taux de change (après Devise) --------------------------------------------

class TauxChange(Base):
    """
    Taux de change entre deux devises à une date donnée (ex. 1 EUR = 655,957 XAF).
    Table : taux_change.
    """
    __tablename__ = "taux_change"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    devise_from_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    devise_to_id: Mapped[int] = mapped_column(Integer, ForeignKey("devises.id"), nullable=False)
    taux: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    date_effet: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Table de liaison many-to-many : permissions_roles ------------------------

class PermissionRole(Base):
    """
    Liaison many-to-many entre rôles et permissions : quelles actions
    sont accordées à quel rôle. Table : permissions_roles.
    """
    __tablename__ = "permissions_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id"), nullable=False)

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_permissions_roles_role_permission"),)


# --- Session (authentification, reprise) -------------------------------------

class Session(Base):
    """
    Session d'authentification d'un utilisateur (token, expiration).
    Enrichie pour reprise de travail : identifiant appareil, dernière activité.
    Table : sessions.
    """
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    identifiant_appareil: Mapped[str | None] = mapped_column(String(100), nullable=True)
    appareil_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur", back_populates="sessions")


# --- Affectation utilisateur <-> point de vente -------------------------------

class AffectationUtilisateurPdv(Base):
    """
    Affectation d'un utilisateur à un ou plusieurs points de vente.
    Un PDV peut être marqué comme principal. Table : affectations_utilisateur_point_de_vente.
    """
    __tablename__ = "affectations_utilisateur_point_de_vente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    point_de_vente_id: Mapped[int] = mapped_column(Integer, ForeignKey("points_de_vente.id"), nullable=False)
    est_principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("utilisateur_id", "point_de_vente_id", name="uq_affectations_utilisateur_pdv"),
    )

    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur", back_populates="affectations_pdv")
    point_de_vente: Mapped["PointDeVente"] = relationship("PointDeVente", backref="affectations_utilisateurs")
