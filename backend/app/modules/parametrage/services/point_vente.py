# app/modules/parametrage/services/point_vente.py
# -----------------------------------------------------------------------------
# Use Case PointDeVente (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import PointDeVente
from app.modules.parametrage.repositories import EntrepriseRepository, PointVenteRepository
from app.modules.parametrage.schemas import PointDeVenteCreate, PointDeVenteUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class PointVenteService(BaseParametrageService):
    """Service de gestion des points de vente (par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = PointVenteRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, point_vente_id: int) -> PointDeVente | None:
        return await self._repo.find_by_id(point_vente_id)

    async def get_or_404(self, point_vente_id: int) -> PointDeVente:
        pv = await self._repo.find_by_id(point_vente_id)
        if pv is None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        return pv

    async def get_points_vente(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        inactif_only: bool = False,
        search: str | None = None,
        type_filter: str | None = None,
    ) -> tuple[list[PointDeVente], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_by_entreprise(
            entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            inactif_only=inactif_only,
            search=search,
            type_filter=type_filter,
        )

    async def get_stats(self, entreprise_id: int) -> dict:
        """Statistiques des points de vente d'une entreprise."""
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.get_stats(entreprise_id)

    async def create(self, data: PointDeVenteCreate) -> PointDeVente:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.POINT_VENTE_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(
                Messages.POINT_VENTE_CODE_EXISTS.format(code=code),
            )
        pv = PointDeVente(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle,
            type=data.type,
            adresse=data.adresse,
            code_postal=data.code_postal,
            ville=data.ville,
            telephone=data.telephone,
            latitude=data.latitude,
            longitude=data.longitude,
            fuseau_horaire=data.fuseau_horaire,
            est_depot=data.est_depot,
            actif=data.actif,
        )
        return await self._repo.add(pv)

    async def update(self, point_vente_id: int, data: PointDeVenteUpdate) -> PointDeVente:
        pv = await self.get_or_404(point_vente_id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            new_code = (update_data["code"] or "").strip()
            if not new_code:
                self._raise_bad_request(Messages.POINT_VENTE_CODE_VIDE)
            if await self._repo.exists_by_entreprise_and_code(
                pv.entreprise_id,
                new_code,
                exclude_id=point_vente_id,
            ):
                self._raise_conflict(Messages.POINT_VENTE_CODE_ALREADY_USED)
        for key, value in update_data.items():
            setattr(pv, key, value)
        return await self._repo.update(pv)

    async def delete_soft(self, point_vente_id: int) -> None:
        pv = await self.get_or_404(point_vente_id)
        if pv.deleted_at is not None:
            self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        await self._repo.soft_delete(pv)

