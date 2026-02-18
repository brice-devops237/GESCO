# app/modules/achats/services/depot.py
# -----------------------------------------------------------------------------
# Service métier : dépôts (entrepôts). CRUD par entreprise, unicité du code.
# Adapté à toute structure : mono-site (un dépôt ou aucun), multi-sites (plusieurs dépôts).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achats.models import Depot
from app.modules.achats.repositories import DepotRepository
from app.modules.achats.schemas import DepotCreate, DepotUpdate
from app.modules.achats.services.base import BaseAchatsService
from app.modules.achats.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.shared.regulations import is_pays_code_valide


class DepotService(BaseAchatsService):
    """Service de gestion des dépôts (CRUD, validations, unicité code par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = DepotRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> Depot | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Depot:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.DEPOT_NOT_FOUND)
        return ent

    async def get_all(
        self, *, entreprise_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Depot], int]:
        return await self._repo.find_all(entreprise_id=entreprise_id, skip=skip, limit=limit)

    async def create(self, data: DepotCreate) -> Depot:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.DEPOT_CODE_VIDE)
        if data.pays is not None and data.pays.strip() and not is_pays_code_valide(data.pays.strip()):
            self._raise_bad_request(Messages.DEPOT_PAYS_INVALIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.DEPOT_CODE_EXISTS.format(code=code))
        ent = Depot(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle.strip(),
            adresse=data.adresse.strip() if data.adresse else None,
            ville=data.ville.strip() if data.ville else None,
            code_postal=data.code_postal.strip() if data.code_postal else None,
            pays=data.pays.strip().upper() if data.pays and data.pays.strip() else None,
            point_de_vente_id=data.point_de_vente_id,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: DepotUpdate) -> Depot:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] is not None:
            update_data["code"] = update_data["code"].strip()
            if not update_data["code"]:
                self._raise_bad_request(Messages.DEPOT_CODE_VIDE)
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, update_data["code"], exclude_id=id):
                self._raise_conflict(Messages.DEPOT_CODE_EXISTS.format(code=update_data["code"]))
        if "pays" in update_data and update_data["pays"] is not None and str(update_data["pays"]).strip():
            if not is_pays_code_valide(str(update_data["pays"]).strip()):
                self._raise_bad_request(Messages.DEPOT_PAYS_INVALIDE)
            update_data["pays"] = str(update_data["pays"]).strip().upper()
        for key, value in update_data.items():
            if isinstance(value, str) and key not in ("code", "pays"):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)

