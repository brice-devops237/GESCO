# app/modules/catalogue/services
# -----------------------------------------------------------------------------
# Couche Application : use cases du module Catalogue.
# -----------------------------------------------------------------------------

from app.modules.catalogue.services.canal_vente import CanalVenteService
from app.modules.catalogue.services.conditionnement import ConditionnementService
from app.modules.catalogue.services.famille_produit import FamilleProduitService
from app.modules.catalogue.services.prix import PrixProduitService
from app.modules.catalogue.services.produit import ProduitService
from app.modules.catalogue.services.produit_conditionnement import ProduitConditionnementService
from app.modules.catalogue.services.taux_tva import TauxTvaService
from app.modules.catalogue.services.unite_mesure import UniteMesureService
from app.modules.catalogue.services.variante import VarianteProduitService

__all__ = [
    "CanalVenteService",
    "ConditionnementService",
    "FamilleProduitService",
    "PrixProduitService",
    "ProduitService",
    "ProduitConditionnementService",
    "TauxTvaService",
    "UniteMesureService",
    "VarianteProduitService",
]

