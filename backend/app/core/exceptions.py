# app/core/exceptions.py
# -----------------------------------------------------------------------------
# Exceptions HTTP (présentation). Utilisées par les routes et les services.
# Cohérentes avec FastAPI (héritent de HTTPException) pour une réponse JSON
# uniforme. Optionnellement mappent les exceptions domaine vers HTTP.
# -----------------------------------------------------------------------------

from fastapi import HTTPException


class AppHTTPException(HTTPException):
    """Base des exceptions HTTP métier avec champ code pour le client."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code or "ERROR"


class NotFoundError(AppHTTPException):
    """Ressource non trouvée (404)."""

    def __init__(self, detail: str = "Ressource non trouvée", code: str = "NOT_FOUND") -> None:
        super().__init__(status_code=404, detail=detail, code=code)


class ConflictError(AppHTTPException):
    """Conflit métier (ex: unicité violée) (409)."""

    def __init__(self, detail: str = "Conflit", code: str = "CONFLICT") -> None:
        super().__init__(status_code=409, detail=detail, code=code)


class ForbiddenError(AppHTTPException):
    """Accès refusé (droits insuffisants) (403)."""

    def __init__(self, detail: str = "Accès refusé", code: str = "FORBIDDEN") -> None:
        super().__init__(status_code=403, detail=detail, code=code)


class UnauthorizedError(AppHTTPException):
    """Non authentifié ou token invalide (401)."""

    def __init__(
        self,
        detail: str = "Authentification requise",
        code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(status_code=401, detail=detail, code=code)


class BadRequestError(AppHTTPException):
    """Requête invalide (400)."""

    def __init__(
        self,
        detail: str = "Requête invalide",
        code: str = "BAD_REQUEST",
    ) -> None:
        super().__init__(status_code=400, detail=detail, code=code)

