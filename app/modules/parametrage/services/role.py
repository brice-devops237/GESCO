# app/modules/parametrage/services/role.py
# -----------------------------------------------------------------------------
# Use Case Role (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Role
from app.modules.parametrage.repositories import EntrepriseRepository, RoleRepository
from app.modules.parametrage.schemas import RoleCreate, RoleUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class RoleService(BaseParametrageService):
    """Service de gestion des rôles (par entreprise ou globaux)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = RoleRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self._repo.find_by_id(role_id)

    async def get_or_404(self, role_id: int) -> Role:
        r = await self._repo.find_by_id(role_id)
        if r is None:
            self._raise_not_found(Messages.ROLE_NOT_FOUND)
        return r

    async def get_roles(
        self,
        entreprise_id: int | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Role]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: RoleCreate) -> Role:
        if data.entreprise_id is not None:
            if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
                self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.DONNEES_INVALIDES)
        if await self._repo.exists_by_entreprise_and_code(
            data.entreprise_id,
            code,
        ):
            self._raise_conflict(Messages.ROLE_CODE_EXISTS.format(code=code))
        role = Role(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle,
        )
        return await self._repo.add(role)

    async def update(self, role_id: int, data: RoleUpdate) -> Role:
        role = await self.get_or_404(role_id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            new_code = (update_data["code"] or "").strip()
            if not new_code:
                self._raise_bad_request(Messages.DONNEES_INVALIDES)
            if await self._repo.exists_by_entreprise_and_code(
                role.entreprise_id,
                new_code,
                exclude_id=role_id,
            ):
                self._raise_conflict(Messages.ROLE_CODE_ALREADY_USED)
        for key, value in update_data.items():
            setattr(role, key, value)
        return await self._repo.update(role)
