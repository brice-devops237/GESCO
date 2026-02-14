# app/modules/catalogue/repositories
# -----------------------------------------------------------------------------
# Couche Infrastructure : repositories d'accès aux données du module Catalogue.
# -----------------------------------------------------------------------------

from app.modules.catalogue.repositories.canal_vente_repository import CanalVenteRepository
from app.modules.catalogue.repositories.conditionnement_repository import ConditionnementRepository
from app.modules.catalogue.repositories.famille_produit_repository import FamilleProduitRepository
from app.modules.catalogue.repositories.prix_repository import PrixProduitRepository
from app.modules.catalogue.repositories.produit_conditionnement_repository import ProduitConditionnementRepository
from app.modules.catalogue.repositories.produit_repository import ProduitRepository
from app.modules.catalogue.repositories.taux_tva_repository import TauxTvaRepository
from app.modules.catalogue.repositories.unite_mesure_repository import UniteMesureRepository
from app.modules.catalogue.repositories.variante_repository import VarianteProduitRepository

__all__ = [
    "CanalVenteRepository",
    "ConditionnementRepository",
    "FamilleProduitRepository",
    "PrixProduitRepository",
    "ProduitConditionnementRepository",
    "ProduitRepository",
    "TauxTvaRepository",
    "UniteMesureRepository",
    "VarianteProduitRepository",
]
