# app/modules/parametrage/services/__init__.py
# -----------------------------------------------------------------------------
# Export des classes de service du module Paramétrage. Les routes instancient
# ces classes avec la session DB (ex: EntrepriseService(db)).
# -----------------------------------------------------------------------------

from app.modules.parametrage.services.affectation_utilisateur_pdv import (
    AffectationUtilisateurPdvService,
)
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.devise import DeviseService
from app.modules.parametrage.services.entreprise import EntrepriseService
from app.modules.parametrage.services.permission import PermissionService
from app.modules.parametrage.services.point_vente import PointVenteService
from app.modules.parametrage.services.role import RoleService
from app.modules.parametrage.services.taux_change import TauxChangeService
from app.modules.parametrage.services.utilisateur import UtilisateurService

__all__ = [
    "AffectationUtilisateurPdvService",
    "BaseParametrageService",
    "DeviseService",
    "EntrepriseService",
    "PermissionService",
    "PointVenteService",
    "RoleService",
    "TauxChangeService",
    "UtilisateurService",
]
