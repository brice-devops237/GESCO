# app/modules/rh/services/employe.py
# -----------------------------------------------------------------------------
# Service métier : employés (CNPS, NIU, salaire, poste, département, etc.).
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import DeviseRepository, EntrepriseRepository
from app.modules.rh.models import Employe
from app.modules.rh.repositories import EmployeRepository
from app.modules.rh.schemas import EmployeCreate, EmployeUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages


class EmployeService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = EmployeRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._devise_repo = DeviseRepository(db)

    async def get_by_id(self, id: int) -> Employe | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Employe:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        departement_id: int | None = None,
        poste_id: int | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[Employe], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            departement_id=departement_id,
            poste_id=poste_id,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: EmployeCreate) -> Employe:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if data.devise_id and await self._devise_repo.find_by_id(data.devise_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        matricule = (data.matricule or "").strip()
        if not matricule:
            self._raise_bad_request(Messages.EMPLOYE_MATRICULE_VIDE)
        if await self._repo.exists_by_entreprise_and_matricule(data.entreprise_id, matricule):
            self._raise_conflict(Messages.EMPLOYE_MATRICULE_EXISTS.format(matricule=matricule))
        ent = Employe(
            entreprise_id=data.entreprise_id,
            utilisateur_id=data.utilisateur_id,
            departement_id=data.departement_id,
            poste_id=data.poste_id,
            type_contrat_id=data.type_contrat_id,
            matricule=matricule,
            nom=data.nom.strip(),
            prenom=data.prenom.strip(),
            date_naissance=data.date_naissance,
            lieu_naissance=data.lieu_naissance.strip() if data.lieu_naissance else None,
            genre=data.genre.strip() if data.genre else None,
            nationalite=data.nationalite.strip() if data.nationalite else None,
            situation_familiale=data.situation_familiale.strip() if data.situation_familiale else None,
            niu=data.niu.strip() if data.niu else None,
            numero_cnps=data.numero_cnps.strip() if data.numero_cnps else None,
            email=data.email.strip() if data.email else None,
            telephone=data.telephone.strip() if data.telephone else None,
            adresse=data.adresse.strip() if data.adresse else None,
            date_embauche=data.date_embauche,
            salaire_base=data.salaire_base,
            devise_id=data.devise_id,
            compte_bancaire=data.compte_bancaire.strip() if data.compte_bancaire else None,
            banque=data.banque.strip() if data.banque else None,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: EmployeUpdate) -> Employe:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "devise_id" in update_data and update_data["devise_id"] is not None:
            if await self._devise_repo.find_by_id(update_data["devise_id"]) is None:
                self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        if "matricule" in update_data and update_data["matricule"] is not None:
            update_data["matricule"] = update_data["matricule"].strip()
            if not update_data["matricule"]:
                self._raise_bad_request(Messages.EMPLOYE_MATRICULE_VIDE)
            if await self._repo.exists_by_entreprise_and_matricule(ent.entreprise_id, update_data["matricule"], exclude_id=id):
                self._raise_conflict(Messages.EMPLOYE_MATRICULE_EXISTS.format(matricule=update_data["matricule"]))
        for key, value in update_data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)

