# app/modules/tresorerie/services/mode_paiement.py
# -----------------------------------------------------------------------------
# Service métier : modes de paiement (CRUD).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tresorerie.models import ModePaiement
from app.modules.tresorerie.repositories import ModePaiementRepository
from app.modules.tresorerie.schemas import ModePaiementCreate, ModePaiementUpdate
from app.modules.tresorerie.services.base import BaseTresorerieService
from app.modules.tresorerie.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class ModePaiementService(BaseTresorerieService):
    """Service de gestion des modes de paiement."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ModePaiementRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> ModePaiement | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> ModePaiement:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.MODE_PAIEMENT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[ModePaiement], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: ModePaiementCreate) -> ModePaiement:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.MODE_PAIEMENT_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.MODE_PAIEMENT_CODE_EXISTS.format(code=code))
        ent = ModePaiement(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle.strip(),
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ModePaiementUpdate) -> ModePaiement:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].strip()
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
