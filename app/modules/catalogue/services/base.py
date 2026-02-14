# app/modules/catalogue/services/base.py
# -----------------------------------------------------------------------------
# Classe de base pour tous les services du module Catalogue. Hérite de
# BaseService (core) pour session DB et levées d'exceptions.
# -----------------------------------------------------------------------------

from app.core.service_base import BaseService


class BaseCatalogueService(BaseService):
    """
    Base des services métier Catalogue. Hérite de BaseService pour
    _raise_* et _db ; pas de helpers SQL supplémentaires (usage des repos).
    """
    pass
