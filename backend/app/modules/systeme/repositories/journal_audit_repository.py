# app/modules/systeme/repositories/journal_audit_repository.py
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.systeme.models import JournalAudit


class JournalAuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> JournalAudit | None:
        r = await self._db.execute(select(JournalAudit).where(JournalAudit.id == id))
        return r.scalar_one_or_none()

    async def find_all(
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
        q = select(JournalAudit)
        if entreprise_id is not None:
            q = q.where(JournalAudit.entreprise_id == entreprise_id)
        if utilisateur_id is not None:
            q = q.where(JournalAudit.utilisateur_id == utilisateur_id)
        if action is not None:
            q = q.where(JournalAudit.action == action)
        if module is not None:
            q = q.where(JournalAudit.module == module)
        if date_debut is not None:
            q = q.where(JournalAudit.created_at >= date_debut)
        if date_fin is not None:
            q = q.where(JournalAudit.created_at <= date_fin)
        count_q = select(func.count()).select_from(JournalAudit)
        if entreprise_id is not None:
            count_q = count_q.where(JournalAudit.entreprise_id == entreprise_id)
        if utilisateur_id is not None:
            count_q = count_q.where(JournalAudit.utilisateur_id == utilisateur_id)
        if action is not None:
            count_q = count_q.where(JournalAudit.action == action)
        if module is not None:
            count_q = count_q.where(JournalAudit.module == module)
        if date_debut is not None:
            count_q = count_q.where(JournalAudit.created_at >= date_debut)
        if date_fin is not None:
            count_q = count_q.where(JournalAudit.created_at <= date_fin)
        total = (await self._db.execute(count_q)).scalar_one() or 0
        q = q.order_by(JournalAudit.created_at.desc()).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all()), total

    async def add(self, entity: JournalAudit) -> JournalAudit:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

