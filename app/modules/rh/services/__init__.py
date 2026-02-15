# app/modules/rh/services
# -----------------------------------------------------------------------------
# Services métier du module RH.
# -----------------------------------------------------------------------------
from app.modules.rh.services.avance import AvanceService
from app.modules.rh.services.commission import CommissionService
from app.modules.rh.services.demande_conge import DemandeCongeService
from app.modules.rh.services.departement import DepartementService
from app.modules.rh.services.employe import EmployeService
from app.modules.rh.services.objectif import ObjectifService
from app.modules.rh.services.poste import PosteService
from app.modules.rh.services.solde_conge import SoldeCongeService
from app.modules.rh.services.taux_commission import TauxCommissionService
from app.modules.rh.services.type_conge import TypeCongeService
from app.modules.rh.services.type_contrat import TypeContratService

__all__ = [
    "DepartementService",
    "PosteService",
    "TypeContratService",
    "EmployeService",
    "TypeCongeService",
    "DemandeCongeService",
    "SoldeCongeService",
    "ObjectifService",
    "TauxCommissionService",
    "CommissionService",
    "AvanceService",
]
