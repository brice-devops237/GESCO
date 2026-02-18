# app/modules/systeme/services/audit.py
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.systeme.models import JournalAudit
from app.modules.systeme.repositories import JournalAuditRepository
from app.modules.systeme.schemas import JournalAuditCreate
from app.modules.systeme.services.base import BaseSystemeService
from app.modules.systeme.services.messages import Messages


class AuditService(BaseSystemeService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = JournalAuditRepository(db)

    async def get_by_id(self, id: int) -> JournalAudit | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> JournalAudit:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.JOURNAL_AUDIT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        utilisateur_id: int | None = None,
        action: str | None = None,
        module: str | None = None,
        date_debut: datetime | None = None,
        date_fin: datetime | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[JournalAudit], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            utilisateur_id=utilisateur_id,
            action=action,
            module=module,
            date_debut=date_debut,
            date_fin=date_fin,
            skip=skip,
            limit=limit,
        )

    async def log(
        self,
        action: str,
        *,
        entreprise_id: int | None = None,
        utilisateur_id: int | None = None,
        module: str | None = None,
        entite_type: str | None = None,
        entite_id: int | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> JournalAudit:
        ent = JournalAudit(
            entreprise_id=entreprise_id,
            utilisateur_id=utilisateur_id,
            action=action.strip(),
            module=module.strip() if module else None,
            entite_type=entite_type.strip() if entite_type else None,
            entite_id=entite_id,
            details=details,
            ip_address=ip_address.strip() if ip_address else None,
            user_agent=user_agent[:500] if user_agent else None,
        )
        return await self._repo.add(ent)

    async def create(self, data: JournalAuditCreate) -> JournalAudit:
        ent = JournalAudit(
            entreprise_id=data.entreprise_id,
            utilisateur_id=data.utilisateur_id,
            action=data.action.strip(),
            module=data.module.strip() if data.module else None,
            entite_type=data.entite_type.strip() if data.entite_type else None,
            entite_id=data.entite_id,
            details=data.details,
            ip_address=data.ip_address.strip() if data.ip_address else None,
            user_agent=(data.user_agent or "")[:500] or None,
        )
        return await self._repo.add(ent)

