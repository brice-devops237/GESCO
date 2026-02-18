# app/domain/exceptions.py
# -----------------------------------------------------------------------------
# Exceptions du domaine métier. Indépendantes du transport (HTTP).
# La couche présentation (API) les mappe vers des réponses HTTP (404, 409, 400).
# -----------------------------------------------------------------------------


class DomainError(Exception):
    """Base des erreurs métier. Possède un message et un code pour le client."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class DomainNotFoundError(DomainError):
    """Ressource non trouvée (ex: entreprise, utilisateur)."""

    def __init__(self, message: str, code: str = "NOT_FOUND") -> None:
        super().__init__(message, code)


class DomainConflictError(DomainError):
    """Conflit métier (ex: unicité violée)."""

    def __init__(self, message: str, code: str = "CONFLICT") -> None:
        super().__init__(message, code)


class DomainValidationError(DomainError):
    """Données invalides (validation métier)."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code)

