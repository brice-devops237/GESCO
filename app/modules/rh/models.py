# app/modules/rh/models.py
# -----------------------------------------------------------------------------
# Modèles ORM du module RH : structure (départements, postes, types de contrat),
# employés (CNPS, NIU, salaire, devise), congés, avances, objectifs et commissions.
# Conforme aux réalités camerounaises (Code du travail, CNPS, SMIG, XAF) et bonnes
# pratiques internationales (ISO dates, champs optionnels).
# Dépend de Paramétrage (entreprises, utilisateurs, devises).
# -----------------------------------------------------------------------------

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    ...


# --- Département (service) ----------------------------------------------------
class Departement(Base):
    """
    Département ou service de l'entreprise (ex. Commercial, Comptabilité, RH).
    Table : departements.
    """
    __tablename__ = "departements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_departements_entreprise_code"),
    )


# --- Poste (fonction) ---------------------------------------------------------
class Poste(Base):
    """
    Poste ou fonction (ex. Commercial, Comptable, Responsable RH).
    Peut être rattaché à un département.
    Table : postes.
    """
    __tablename__ = "postes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    departement_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("departements.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_postes_entreprise_code"),
    )


# --- Type de contrat (CDI, CDD, Stage, etc.) ----------------------------------
class TypeContrat(Base):
    """
    Type de contrat (CDI, CDD, Stage, Convention de stage, etc.).
    Référentiel par entreprise, aligné Code du travail camerounais.
    Table : types_contrat.
    """
    __tablename__ = "types_contrat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_types_contrat_entreprise_code"),
    )


# --- Employé ------------------------------------------------------------------
class Employe(Base):
    """
    Employé de l'entreprise. Données d'état civil, CNPS/NIU (Cameroun),
    poste, département, type de contrat, rémunération (XAF ou autre devise).
    Peut être lié à un utilisateur (connexion).
    Table : employes.
    """
    __tablename__ = "employes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    utilisateur_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    departement_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("departements.id"), nullable=True)
    poste_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("postes.id"), nullable=True)
    type_contrat_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("types_contrat.id"), nullable=True)

    matricule: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(80), nullable=False)
    prenom: Mapped[str] = mapped_column(String(80), nullable=False)
    date_naissance: Mapped[date | None] = mapped_column(Date, nullable=True)
    lieu_naissance: Mapped[str | None] = mapped_column(String(100), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(1), nullable=True)  # M / F
    nationalite: Mapped[str | None] = mapped_column(String(50), nullable=True)
    niu: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)  # NIF au Cameroun
    numero_cnps: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)  # CNPS
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    adresse: Mapped[str | None] = mapped_column(String(255), nullable=True)

    date_embauche: Mapped[date] = mapped_column(Date, nullable=False)
    salaire_base: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    devise_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("devises.id"), nullable=True)
    compte_bancaire: Mapped[str | None] = mapped_column(String(50), nullable=True)
    banque: Mapped[str | None] = mapped_column(String(80), nullable=True)

    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "matricule", name="uq_employes_entreprise_matricule"),
    )


# --- Type de congé -------------------------------------------------------------
class TypeConge(Base):
    """
    Type de congé (annuel, maladie, maternité, sans solde, etc.).
    Référentiel par entreprise.
    Table : types_conge.
    """
    __tablename__ = "types_conge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    paye: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_types_conge_entreprise_code"),
    )


# --- Demande de congé ---------------------------------------------------------
class DemandeConge(Base):
    """
    Demande de congé d'un employé (dates, type, statut, approbation).
    Table : demandes_conge.
    """
    __tablename__ = "demandes_conge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    employe_id: Mapped[int] = mapped_column(Integer, ForeignKey("employes.id"), nullable=False)
    type_conge_id: Mapped[int] = mapped_column(Integer, ForeignKey("types_conge.id"), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    nombre_jours: Mapped[int] = mapped_column(Integer, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="en_attente")  # brouillon, en_attente, approuve, refuse
    motif: Mapped[str | None] = mapped_column(String(255), nullable=True)
    commentaire_refus: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approuve_par_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    date_decision: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Solde de congé (optionnel, par employé / type / année) -------------------
class SoldeConge(Base):
    """
    Solde de congés (droits acquis, pris, restants) par employé, type et année.
    Table : soldes_conge.
    """
    __tablename__ = "soldes_conge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    employe_id: Mapped[int] = mapped_column(Integer, ForeignKey("employes.id"), nullable=False)
    type_conge_id: Mapped[int] = mapped_column(Integer, ForeignKey("types_conge.id"), nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    droits_acquis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jours_pris: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "employe_id", "type_conge_id", "annee", name="uq_soldes_conge_emp_type_annee"),
    )


# --- Objectif (commercial / performance) --------------------------------------
class Objectif(Base):
    """
    Objectif assigné à un employé (ex. CA, quantités) sur une période.
    Table : objectifs.
    """
    __tablename__ = "objectifs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    employe_id: Mapped[int] = mapped_column(Integer, ForeignKey("employes.id"), nullable=False)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    montant_cible: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    atteint: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = ()


# --- Taux de commission -------------------------------------------------------
class TauxCommission(Base):
    """
    Taux de commission par catégorie (ex. vente, marge). Utilisé pour calcul des commissions.
    Table : taux_commissions.
    """
    __tablename__ = "taux_commissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(80), nullable=False)
    taux_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entreprise_id", "code", name="uq_taux_commissions_entreprise_code"),
    )


# --- Commission (calculée / enregistrée) --------------------------------------
class Commission(Base):
    """
    Commission versée ou à verser à un employé (période, montant, lien optionnel à un taux).
    Table : commissions.
    """
    __tablename__ = "commissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    employe_id: Mapped[int] = mapped_column(Integer, ForeignKey("employes.id"), nullable=False)
    taux_commission_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("taux_commissions.id"), nullable=True)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    libelle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payee: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# --- Avance sur salaire -------------------------------------------------------
class Avance(Base):
    """
    Avance sur salaire accordée à un employé. Remboursement déductible de la paie.
    Table : avances.
    """
    __tablename__ = "avances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entreprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("entreprises.id"), nullable=False)
    employe_id: Mapped[int] = mapped_column(Integer, ForeignKey("employes.id"), nullable=False)
    date_avance: Mapped[date] = mapped_column(Date, nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    motif: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rembourse: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
