# app/modules/systeme/repositories/notification_repository.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.systeme.models import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> Notification | None:
        r = await self._db.execute(select(Notification).where(Notification.id == id))
        return r.scalar_one_or_none()

    async def find_all(
        self,
        utilisateur_id: int,
        *,
        lue: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        q = select(Notification).where(Notification.utilisateur_id == utilisateur_id)
        if lue is not None:
            q = q.where(Notification.lue.is_(lue))
        count_q = select(func.count()).select_from(Notification).where(
            Notification.utilisateur_id == utilisateur_id
        )
        if lue is not None:
            count_q = count_q.where(Notification.lue.is_(lue))
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: Notification) -> Notification:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: Notification) -> Notification:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity
