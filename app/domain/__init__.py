# app/domain
# -----------------------------------------------------------------------------
# Couche Domain (Clean Architecture) : entités métier et exceptions domaine.
# Aucune dépendance vers l'infrastructure (DB, HTTP) ou la présentation.
# -----------------------------------------------------------------------------

from app.domain.exceptions import (
    DomainConflictError,
    DomainNotFoundError,
    DomainValidationError,
)

__all__ = [
    "DomainConflictError",
    "DomainNotFoundError",
    "DomainValidationError",
]
