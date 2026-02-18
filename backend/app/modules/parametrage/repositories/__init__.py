# app/modules/parametrage/repositories
# -----------------------------------------------------------------------------
# Couche Infrastructure (Clean Architecture) : implémentations d'accès aux données.
# Chaque repository encapsule les requêtes SQLAlchemy pour un agrégat.
# Les services (couche Application) dépendent de ces repositories.
# -----------------------------------------------------------------------------

from app.modules.parametrage.repositories.affectation_pdv_repository import AffectationPdvRepository
from app.modules.parametrage.repositories.devise_repository import DeviseRepository
from app.modules.parametrage.repositories.entreprise_repository import EntrepriseRepository
from app.modules.parametrage.repositories.permission_repository import PermissionRepository
from app.modules.parametrage.repositories.point_vente_repository import PointVenteRepository
from app.modules.parametrage.repositories.role_repository import RoleRepository
from app.modules.parametrage.repositories.taux_change_repository import TauxChangeRepository
from app.modules.parametrage.repositories.utilisateur_repository import UtilisateurRepository

__all__ = [
    "AffectationPdvRepository",
    "DeviseRepository",
    "EntrepriseRepository",
    "PermissionRepository",
    "PointVenteRepository",
    "RoleRepository",
    "TauxChangeRepository",
    "UtilisateurRepository",
]

