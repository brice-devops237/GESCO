# app/modules/parametrage/services/role.py
# -----------------------------------------------------------------------------
# Use Case Rôle (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Role
from app.modules.parametrage.repositories import EntrepriseRepository, RoleRepository
from app.modules.parametrage.schemas import RoleCreate, RoleUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class RoleService(BaseParametrageService):
    """Use cases pour l'agrégat Rôle."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = RoleRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_roles(
        self,
        entreprise_id: int | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Role]:
        """Liste des rôles (optionnellement filtrée par entreprise)."""
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            skip=skip,
            limit=limit,
        )

    async def get_or_404(self, role_id: int) -> Role:
        role = await self._repo.find_by_id(role_id)
        if role is None:
            self._raise_not_found(Messages.ROLE_NOT_FOUND)
        return role

    async def create(self, data: RoleCreate) -> Role:
        code = (data.code or "").strip()
        libelle = (data.libelle or "").strip()
        if not code or not libelle:
            self._raise_bad_request(Messages.DONNEES_INVALIDES)
        if data.entreprise_id is not None:
            if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
                self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.ROLE_CODE_EXISTS.format(code=code))
        entity = Role(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=libelle,
        )
        return await self._repo.add(entity)

    async def update(self, role_id: int, data: RoleUpdate) -> Role:
        role = await self.get_or_404(role_id)
        if data.code is not None:
            code = data.code.strip()
            if not code:
                self._raise_bad_request(Messages.DONNEES_INVALIDES)
            if await self._repo.exists_by_entreprise_and_code(
                role.entreprise_id, code, exclude_id=role_id
            ):
                self._raise_conflict(Messages.ROLE_CODE_EXISTS.format(code=code))
            role.code = code
        if data.libelle is not None:
            role.libelle = data.libelle.strip() or role.libelle
        return await self._repo.update(role)
