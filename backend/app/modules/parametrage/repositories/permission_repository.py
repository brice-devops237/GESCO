# app/modules/parametrage/repositories/permission_repository.py
# -----------------------------------------------------------------------------
# Repository Permission et PermissionRole (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Permission, PermissionRole, Role


class PermissionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, permission_id: int) -> Permission | None:
        r = await self._db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 200,
        module: str | None = None,
    ) -> list[Permission]:
        q = select(Permission)
        if module:
            q = q.where(Permission.module == module)
        q = q.order_by(Permission.module, Permission.action).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def exists_by_module_action(self, module: str, action: str) -> bool:
        r = await self._db.execute(
            select(Permission.id).where(
                Permission.module == module,
                Permission.action == action,
            ).limit(1)
        )
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Permission) -> Permission:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def add_permission_role(self, entity: PermissionRole) -> PermissionRole:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def find_permission_role(
        self,
        role_id: int,
        permission_id: int,
    ) -> PermissionRole | None:
        r = await self._db.execute(
            select(PermissionRole).where(
                PermissionRole.role_id == role_id,
                PermissionRole.permission_id == permission_id,
            )
        )
        return r.scalar_one_or_none()

    async def find_roles_by_permission_ids(
        self, permission_ids: list[int]
    ) -> dict[int, list[Role]]:
        """Pour chaque permission_id, retourne la liste des rôles auxquels elle est affectée."""
        if not permission_ids:
            return {}
        q = (
            select(PermissionRole.permission_id, Role)
            .join(Role, Role.id == PermissionRole.role_id)
            .where(PermissionRole.permission_id.in_(permission_ids))
        )
        r = await self._db.execute(q)
        out: dict[int, list[Role]] = {pid: [] for pid in permission_ids}
        for permission_id, role in r.all():
            out.setdefault(permission_id, []).append(role)
        return out

    async def find_permissions_by_role_id(self, role_id: int) -> set[tuple[str, str]]:
        """Retourne l'ensemble des (module, action) associés au rôle (pour vérification d'autorisation)."""
        q = (
            select(Permission.module, Permission.action)
            .select_from(PermissionRole)
            .join(Permission, Permission.id == PermissionRole.permission_id)
            .where(PermissionRole.role_id == role_id)
        )
        r = await self._db.execute(q)
        return {(row[0], row[1]) for row in r.all()}

    async def delete(self, entity: PermissionRole) -> None:
        await self._db.delete(entity)
        await self._db.flush()

