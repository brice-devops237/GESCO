# app/modules/commercial/repositories/etat_document_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import EtatDocument


class EtatDocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_id(self, id: int) -> EtatDocument | None:
        r = await self._db.execute(select(EtatDocument).where(EtatDocument.id == id))
        return r.scalar_one_or_none()

    async def find_by_type_and_code(self, type_document: str, code: str) -> EtatDocument | None:
        r = await self._db.execute(
            select(EtatDocument).where(
                EtatDocument.type_document == type_document,
                EtatDocument.code == code,
            )
        )
        return r.scalar_one_or_none()

    async def find_all(
        self,
        *,
        type_document: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EtatDocument]:
        q = select(EtatDocument)
        if type_document:
            q = q.where(EtatDocument.type_document == type_document)
        q = q.order_by(EtatDocument.type_document, EtatDocument.ordre, EtatDocument.code).offset(skip).limit(limit)
        r = await self._db.execute(q)
        return list(r.scalars().all())

    async def add(self, entity: EtatDocument) -> EtatDocument:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def update(self, entity: EtatDocument) -> EtatDocument:
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

