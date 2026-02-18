# app/modules/parametrage/services/permission.py
# -----------------------------------------------------------------------------
# Use Case Permission (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Permission, PermissionRole
from app.modules.parametrage.repositories import PermissionRepository, RoleRepository
from app.modules.parametrage.schemas import PermissionCreate, PermissionRoleCreate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class PermissionService(BaseParametrageService):
    """Service de gestion des permissions et affectations permission-rôle."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = PermissionRepository(db)
        self._role_repo = RoleRepository(db)

    async def get_by_id(self, permission_id: int) -> Permission | None:
        return await self._repo.find_by_id(permission_id)

    async def get_or_404(self, permission_id: int) -> Permission:
        p = await self._repo.find_by_id(permission_id)
        if p is None:
            self._raise_not_found(Messages.PERMISSION_NOT_FOUND)
        return p

    async def get_permissions(
        self,
        *,
        skip: int = 0,
        limit: int = 200,
        module: str | None = None,
    ) -> list[Permission]:
        return await self._repo.find_all(
            skip=skip,
            limit=limit,
            module=module,
        )

    async def create(self, data: PermissionCreate) -> Permission:
        module = (data.module or "").strip()
        action = (data.action or "").strip()
        if not module or not action:
            self._raise_bad_request(Messages.DONNEES_INVALIDES)
        if await self._repo.exists_by_module_action(module, action):
            self._raise_conflict(
                Messages.PERMISSION_MODULE_ACTION_EXISTS.format(
                    module=module,
                    action=action,
                ),
            )
        p = Permission(module=module, action=action, libelle=data.libelle)
        return await self._repo.add(p)

    async def add_permission_to_role(self, data: PermissionRoleCreate) -> PermissionRole:
        if await self._role_repo.find_by_id(data.role_id) is None:
            self._raise_not_found(Messages.ROLE_NOT_FOUND)
        await self.get_or_404(data.permission_id)
        if await self._repo.find_permission_role(data.role_id, data.permission_id):
            self._raise_conflict(Messages.PERMISSION_ROLE_ALREADY)
        pr = PermissionRole(role_id=data.role_id, permission_id=data.permission_id)
        return await self._repo.add_permission_role(pr)

    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> None:
        pr = await self._repo.find_permission_role(role_id, permission_id)
        if pr is None:
            self._raise_not_found(Messages.PERMISSION_ROLE_NOT_FOUND)
        await self._repo.delete(pr)

