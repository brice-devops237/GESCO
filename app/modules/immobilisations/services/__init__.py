# app/modules/immobilisations/services
from app.modules.immobilisations.services.categorie_immobilisation import (
    CategorieImmobilisationService,
)
from app.modules.immobilisations.services.immobilisation import ImmobilisationService

__all__ = ["CategorieImmobilisationService", "ImmobilisationService"]
