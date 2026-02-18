# app/modules/parametrage/services/entreprise.py
# -----------------------------------------------------------------------------
# Use Case Entreprise (Clean Architecture : couche Application). Dépend du
# repository (Infrastructure) et des schémas ; pas de SQLAlchemy direct.
# -----------------------------------------------------------------------------

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Entreprise
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.parametrage.schemas import EntrepriseCreate, EntrepriseUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages
from app.shared.regulations import is_devise_code_valide, is_pays_code_valide


class EntrepriseService(BaseParametrageService):
    """Use cases pour l'agrégat Entreprise."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = EntrepriseRepository(db)

    async def get_by_id(self, entreprise_id: int) -> Entreprise | None:
        return await self._repo.find_by_id(entreprise_id)

    async def get_or_404(self, entreprise_id: int) -> Entreprise:
        ent = await self._repo.find_by_id(entreprise_id)
        if ent is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return ent

    async def get_entreprises(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Entreprise], int]:
        """Liste globale des entreprises (sans filtre entreprise_id).
        Convention : les autres modules utilisent get_all(entreprise_id, ...) pour une liste scopée."""
        return await self._repo.find_all(
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def create(self, data: EntrepriseCreate) -> Entreprise:
        if not is_pays_code_valide(data.pays):
            self._raise_bad_request(Messages.ENTREPRISE_PAYS_INVALIDE)
        if not is_devise_code_valide(data.devise_principale):
            self._raise_bad_request(Messages.ENTREPRISE_DEVISE_INVALIDE)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.ENTREPRISE_CODE_INVALID)
        if await self._repo.exists_by_code(code):
            self._raise_conflict(Messages.ENTREPRISE_CODE_EXISTS.format(code=code))
        if data.niu and await self._repo.exists_by_niu(data.niu):
            self._raise_conflict(Messages.ENTREPRISE_NIU_EXISTS.format(niu=data.niu))
        ent = Entreprise(
            code=code,
            raison_sociale=data.raison_sociale,
            sigle=data.sigle,
            niu=data.niu,
            regime_fiscal=data.regime_fiscal,
            mode_gestion=data.mode_gestion,
            forme_juridique=data.forme_juridique.value if data.forme_juridique else None,
            rccm=data.rccm,
            cnps=data.cnps,
            adresse=data.adresse,
            code_postal=data.code_postal,
            boite_postale=data.boite_postale,
            ville=data.ville,
            region=data.region,
            pays=data.pays,
            fuseau_horaire=data.fuseau_horaire,
            telephone=data.telephone,
            email=data.email,
            site_web=data.site_web,
            devise_principale=data.devise_principale,
            date_creation=data.date_creation,
            capital_social=data.capital_social,
            logo_url=data.logo_url,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, entreprise_id: int, data: EntrepriseUpdate) -> Entreprise:
        ent = await self.get_or_404(entreprise_id)
        update_data = data.model_dump(exclude_unset=True)
        if "pays" in update_data and update_data["pays"] and not is_pays_code_valide(update_data["pays"]):
            self._raise_bad_request(Messages.ENTREPRISE_PAYS_INVALIDE)
        if "devise_principale" in update_data and update_data["devise_principale"] and not is_devise_code_valide(update_data["devise_principale"]):
            self._raise_bad_request(Messages.ENTREPRISE_DEVISE_INVALIDE)
        if "niu" in update_data and update_data["niu"]:
            if await self._repo.exists_by_niu(
                update_data["niu"],
                exclude_id=entreprise_id,
            ):
                self._raise_conflict(
                    Messages.ENTREPRISE_NIU_ALREADY_USED.format(
                        niu=update_data["niu"],
                    )
                )
        for key, value in update_data.items():
            if key == "forme_juridique" and value is not None and hasattr(value, "value"):
                value = value.value
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete_soft(self, entreprise_id: int) -> None:
        ent = await self.get_or_404(entreprise_id)
        ent.deleted_at = datetime.now(UTC)
        await self._repo.update(ent)

