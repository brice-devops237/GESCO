# app/modules/commercial/services/etat_document.py
# app/modules/commercial/services/etat_document.py
# -----------------------------------------------------------------------------
# Service métier : états de document (devis, commande, facture, BL).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commercial.models import EtatDocument
from app.modules.commercial.repositories import EtatDocumentRepository
from app.modules.commercial.schemas import EtatDocumentCreate, EtatDocumentUpdate
from app.modules.commercial.services.base import BaseCommercialService
from app.modules.commercial.services.messages import Messages


class EtatDocumentService(BaseCommercialService):
    """Service de gestion des états de document (référentiel)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = EtatDocumentRepository(db)

    async def get_by_id(self, id: int) -> EtatDocument | None:
        """Retourne un état document par id ou None."""
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> EtatDocument:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.ETAT_DOCUMENT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        type_document: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EtatDocument]:
        return await self._repo.find_all(type_document=type_document, skip=skip, limit=limit)

    async def create(self, data: EtatDocumentCreate) -> EtatDocument:
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.ETAT_DOCUMENT_CODE_VIDE)
        if await self._repo.find_by_type_and_code(data.type_document, code):
            self._raise_conflict(
                Messages.ETAT_DOCUMENT_TYPE_CODE_EXISTS.format(
                    type_document=data.type_document, code=code
                )
            )
        ent = EtatDocument(
            type_document=data.type_document,
            code=code,
            libelle=data.libelle,
            ordre=data.ordre,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: EtatDocumentUpdate) -> EtatDocument:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            code = (update_data["code"] or "").strip()
            if not code:
                self._raise_bad_request(Messages.ETAT_DOCUMENT_CODE_VIDE)
            existing = await self._repo.find_by_type_and_code(ent.type_document, code)
            if existing and existing.id != id:
                self._raise_conflict(
                    Messages.ETAT_DOCUMENT_TYPE_CODE_EXISTS.format(
                        type_document=ent.type_document, code=code
                    )
                )
            update_data["code"] = code
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
