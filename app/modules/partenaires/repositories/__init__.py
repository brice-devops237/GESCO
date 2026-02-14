# app/modules/partenaires/repositories
# -----------------------------------------------------------------------------
# Couche Infrastructure : repositories du module Partenaires.
# -----------------------------------------------------------------------------

from app.modules.partenaires.repositories.contact_repository import ContactRepository
from app.modules.partenaires.repositories.tiers_repository import TiersRepository
from app.modules.partenaires.repositories.type_tiers_repository import TypeTiersRepository

__all__ = [
    "ContactRepository",
    "TiersRepository",
    "TypeTiersRepository",
]
