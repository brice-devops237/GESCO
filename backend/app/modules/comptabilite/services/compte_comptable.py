# app/modules/comptabilite/services/compte_comptable.py
# -----------------------------------------------------------------------------
# Service métier : comptes comptables (plan comptable).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comptabilite.models import CompteComptable, SensCompte
from app.modules.comptabilite.repositories import CompteComptableRepository
from app.modules.comptabilite.schemas import CompteComptableCreate, CompteComptableUpdate
from app.modules.comptabilite.services.base import BaseComptabiliteService
from app.modules.comptabilite.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class CompteComptableService(BaseComptabiliteService):
    """Service de gestion des comptes comptables (plan comptable)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CompteComptableRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    def _validate_sens(self, value: str) -> None:
        valid = [e.value for e in SensCompte]
        if value not in valid:
            self._raise_bad_request(Messages.SENS_COMPTE_INVALIDE.format(valeur=value))

    async def get_by_id(self, id: int) -> CompteComptable | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> CompteComptable:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.COMPTE_COMPTABLE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[CompteComptable], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: CompteComptableCreate) -> CompteComptable:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        numero = (data.numero or "").strip()
        if not numero:
            self._raise_bad_request(Messages.COMPTE_NUMERO_VIDE)
        self._validate_sens(data.sens_normal)
        if await self._repo.exists_by_entreprise_and_numero(data.entreprise_id, numero):
            self._raise_conflict(Messages.COMPTE_NUMERO_EXISTS.format(numero=numero))
        ent = CompteComptable(
            entreprise_id=data.entreprise_id,
            numero=numero,
            libelle=data.libelle.strip(),
            type_compte=data.type_compte,
            sens_normal=data.sens_normal,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CompteComptableUpdate) -> CompteComptable:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "numero" in update_data and update_data["numero"] is not None:
            update_data["numero"] = update_data["numero"].strip()
            if await self._repo.exists_by_entreprise_and_numero(ent.entreprise_id, update_data["numero"], exclude_id=id):
                self._raise_conflict(Messages.COMPTE_NUMERO_EXISTS.format(numero=update_data["numero"]))
        if "sens_normal" in update_data and update_data["sens_normal"] is not None:
            self._validate_sens(update_data["sens_normal"])
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

