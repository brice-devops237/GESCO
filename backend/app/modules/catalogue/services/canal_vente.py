# app/modules/catalogue/services/canal_vente.py
# -----------------------------------------------------------------------------
# Use Case Canal de vente (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import CanalVente
from app.modules.catalogue.repositories import CanalVenteRepository
from app.modules.catalogue.schemas import CanalVenteCreate, CanalVenteUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class CanalVenteService(BaseCatalogueService):
    """Service de gestion des canaux de vente (par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CanalVenteRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def _ensure_entreprise_exists(self, entreprise_id: int) -> None:
        ent = await self._entreprise_repo.find_by_id(entreprise_id)
        if ent is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)

    async def get_by_id(self, id: int) -> CanalVente | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> CanalVente:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.CANAL_VENTE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[CanalVente], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def create(self, data: CanalVenteCreate) -> CanalVente:
        await self._ensure_entreprise_exists(data.entreprise_id)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.CANAL_VENTE_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.CANAL_VENTE_CODE_EXISTS.format(code=code))
        ent = CanalVente(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle,
            ordre=data.ordre,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CanalVenteUpdate) -> CanalVente:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            code = (update_data["code"] or "").strip()
            if not code:
                self._raise_bad_request(Messages.CANAL_VENTE_CODE_VIDE)
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, code, exclude_id=id):
                self._raise_conflict(Messages.CANAL_VENTE_CODE_EXISTS.format(code=code))
            update_data["code"] = code
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete(self, id: int) -> None:
        ent = await self.get_or_404(id)
        await self._repo.delete(ent)

