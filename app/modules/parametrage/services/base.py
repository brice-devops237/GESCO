# app/modules/parametrage/services/base.py
# -----------------------------------------------------------------------------
# Classe de base pour tous les services du module Paramétrage. Hérite de
# BaseService (core) et ajoute les helpers de requête (_get_one, _exists, etc.).
# -----------------------------------------------------------------------------

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from app.core.service_base import BaseService


class BaseParametrageService(BaseService):
    """
    Base des services métier Paramétrage. Hérite de BaseService pour
    _raise_* ; ajoute _get_one, _exists, _get_one_or_404 pour les requêtes.
    """

    async def _get_one(self, statement: Executable) -> Any | None:
        """
        Exécute un select et retourne un seul résultat ou None.
        Réutilisable pour éviter de répéter execute/scalar_one_or_none.
        """
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def _exists(self, statement: Executable) -> bool:
        """Retourne True si la requête retourne au moins une ligne."""
        return (await self._get_one(statement)) is not None

    async def _get_one_or_404(self, statement: Executable, not_found_message: str) -> Any:
        """
        Exécute un select ; si aucun résultat, lève NotFoundError avec le message.
        Sinon retourne l'entité.
        """
        entity = await self._get_one(statement)
        if entity is None:
            self._raise_not_found(not_found_message)
        return entity
