# app/modules/parametrage/repositories/role_repository.py
# -----------------------------------------------------------------------------
# Repository Role (couche Infrastructure).
# -----------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Role


class RoleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, role_id: int) -> Role | None:
        r = await self._db.execute(select(Role).where(Role.id == role_id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        entreprise_id: int | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Role]:
        q = select(Role)
        if entreprise_id is not None:
            q = q.where(
                (Role.entreprise_id == entreprise_id) | (Role.entreprise_id.is_(None))
            )
        q = q.order_by(Role.entreprise_id.nulls_last(), Role.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def exists_by_entreprise_and_code(
        self,
        entreprise_id: int | None,
        code: str,
        exclude_id: int | None = None,
    ) -> bool:
        q = select(Role.id).where(
            Role.entreprise_id == entreprise_id,
            Role.code == code,
        ).limit(1)
        if exclude_id is not None:
            q = q.where(Role.id != exclude_id)
        r = await self._db.execute(q)
        return r.scalar_one_or_none() is not None

    async def add(self, entity: Role) -> Role:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Role) -> Role:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

