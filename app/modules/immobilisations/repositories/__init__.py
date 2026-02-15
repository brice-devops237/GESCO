# app/modules/immobilisations/repositories
from app.modules.immobilisations.repositories.categorie_immobilisation_repository import (
    CategorieImmobilisationRepository,
)
from app.modules.immobilisations.repositories.immobilisation_repository import (
    ImmobilisationRepository,
)
from app.modules.immobilisations.repositories.ligne_amortissement_repository import (
    LigneAmortissementRepository,
)

__all__ = ["CategorieImmobilisationRepository", "ImmobilisationRepository", "LigneAmortissementRepository"]
