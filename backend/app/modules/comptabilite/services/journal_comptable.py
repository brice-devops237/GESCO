# app/modules/comptabilite/services/journal_comptable.py
# -----------------------------------------------------------------------------
# Service métier : journaux comptables.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comptabilite.models import JournalComptable
from app.modules.comptabilite.repositories import JournalComptableRepository
from app.modules.comptabilite.schemas import JournalComptableCreate, JournalComptableUpdate
from app.modules.comptabilite.services.base import BaseComptabiliteService
from app.modules.comptabilite.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class JournalComptableService(BaseComptabiliteService):
    """Service de gestion des journaux comptables."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = JournalComptableRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> JournalComptable | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> JournalComptable:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.JOURNAL_COMPTABLE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[JournalComptable], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: JournalComptableCreate) -> JournalComptable:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.JOURNAL_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.JOURNAL_CODE_EXISTS.format(code=code))
        ent = JournalComptable(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle.strip(),
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: JournalComptableUpdate) -> JournalComptable:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] is not None:
            update_data["code"] = update_data["code"].strip()
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, update_data["code"], exclude_id=id):
                self._raise_conflict(Messages.JOURNAL_CODE_EXISTS.format(code=update_data["code"]))
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

