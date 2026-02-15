# app/modules/systeme/services/notification.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import UtilisateurRepository
from app.modules.systeme.models import Notification
from app.modules.systeme.repositories import NotificationRepository
from app.modules.systeme.schemas import NotificationCreate, NotificationUpdate
from app.modules.systeme.services.base import BaseSystemeService
from app.modules.systeme.services.messages import Messages


class NotificationService(BaseSystemeService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = NotificationRepository(db)
        self._utilisateur_repo = UtilisateurRepository(db)

    async def get_by_id(self, id: int) -> Notification | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Notification:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.NOTIFICATION_NOT_FOUND)
        return ent

    async def get_all(
        self,
        utilisateur_id: int,
        *,
        lue: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        return await self._repo.find_all(
            utilisateur_id=utilisateur_id,
            lue=lue,
            skip=skip,
            limit=limit,
        )

    async def get_or_404_for_user(self, id: int, utilisateur_id: int) -> Notification:
        ent = await self.get_or_404(id)
        if ent.utilisateur_id != utilisateur_id:
            self._raise_bad_request(Messages.NOTIFICATION_UTILISATEUR_FORBIDDEN)
        return ent

    async def create(self, data: NotificationCreate) -> Notification:
        if await self._utilisateur_repo.find_by_id(data.utilisateur_id) is None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        ent = Notification(
            utilisateur_id=data.utilisateur_id,
            titre=data.titre.strip(),
            message=data.message.strip() if data.message else None,
            entite_type=data.entite_type.strip() if data.entite_type else None,
            entite_id=data.entite_id,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: NotificationUpdate) -> Notification:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def marquer_lue(self, id: int, utilisateur_id: int) -> Notification:
        ent = await self.get_or_404_for_user(id, utilisateur_id)
        ent.lue = True
        return await self._repo.update(ent)
