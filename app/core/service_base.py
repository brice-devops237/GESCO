# app/core/service_base.py
# -----------------------------------------------------------------------------
# Classe de base partagée pour les services (Clean Architecture : Application).
# Centralise la session DB et les levées d'exceptions HTTP.
# -----------------------------------------------------------------------------

from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError


class BaseService:
    """
    Base des services métier. Chaque service reçoit la session DB en
    construction et utilise _raise_* pour des erreurs HTTP cohérentes.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @staticmethod
    def _raise_not_found(message: str) -> None:
        """Lève NotFoundError (404) avec le message fourni."""
        raise NotFoundError(detail=message)

    @staticmethod
    def _raise_conflict(message: str) -> None:
        """Lève ConflictError (409) avec le message fourni."""
        raise ConflictError(detail=message)

    @staticmethod
    def _raise_bad_request(message: str) -> None:
        """Lève BadRequestError (400) avec le message fourni."""
        raise BadRequestError(detail=message)

    @staticmethod
    def _validate_enum(value: str, enum_class: type[Enum], message_template: str) -> None:
        """Vérifie que value est une valeur valide de l'enum. Sinon lève 400 (clé : valeur)."""
        if value is None:
            return
        valid = [e.value for e in enum_class]
        if value not in valid:
            raise BadRequestError(detail=message_template.format(valeur=value))
