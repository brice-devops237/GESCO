# app/modules/partenaires/services/base.py
# -----------------------------------------------------------------------------
# Classe de base pour tous les services du module Partenaires. Hérite de
# BaseService (core) pour session DB et levées d'exceptions.
# -----------------------------------------------------------------------------

from app.core.service_base import BaseService


class BasePartenairesService(BaseService):
    """
    Base des services métier Partenaires. Hérite de BaseService pour
    _raise_* et _db.
    """
    pass

