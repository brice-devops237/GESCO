# app/shared/schemas/common.py
# -----------------------------------------------------------------------------
# Schémas Pydantic partagés (pagination, réponses génériques).
# Aucun import depuis app.modules pour rester réutilisable partout.
#
# Stratégie de pagination : les listes actuelles renvoient souvent list[Schema]
# (items + total en tuple côté service). Pour des routes paginées avec métadonnées
# (page, page_size, total_pages), utiliser PaginatedResponse et
# build_paginated_response().
# -----------------------------------------------------------------------------

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Paramètres de pagination pour les listes (query params).
    Utilisé par les routes GET ...?page=1&page_size=20&sort=...
    """

    page: int = Field(default=1, ge=1, description="Numéro de page (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Nombre d'éléments par page")
    sort_by: str | None = Field(default=None, description="Champ de tri (ex: raison_sociale)")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Ordre de tri (asc ou desc)")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Réponse paginée générique : liste d'éléments + métadonnées (total, page, etc.).
    """

    items: list[T] = Field(default_factory=list, description="Liste des éléments de la page")
    total: int = Field(ge=0, description="Nombre total d'éléments (toutes pages)")
    page: int = Field(ge=1, description="Numéro de page actuelle")
    page_size: int = Field(ge=1, description="Taille de la page")
    total_pages: int = Field(ge=0, description="Nombre total de pages")


def build_paginated_response(
    items: list[T],
    total: int,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[T]:
    """Construit une PaginatedResponse à partir des éléments et du total."""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
