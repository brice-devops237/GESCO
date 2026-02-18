# app/modules/comptabilite/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Comptabilité. Isolation multi-tenant : listes par
# ValidatedEntrepriseId ; GET/PATCH/POST vérifient que la ressource appartient
# à l'entreprise de l'utilisateur. Adapté toute structure, tout secteur (OHADA/CEMAC).
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.core.exceptions import ForbiddenError
from app.modules.comptabilite import schemas
from app.modules.comptabilite.services import (
    CompteComptableService,
    EcritureComptableService,
    JournalComptableService,
    PeriodeComptableService,
)
from app.modules.parametrage.dependencies import CurrentUser, ValidatedEntrepriseId

router = APIRouter(prefix="/comptabilite")

TAG_COMPTES_COMPTABLES = "Comptabilité - Comptes comptables"
TAG_JOURNAUX_COMPTABLES = "Comptabilité - Journaux comptables"
TAG_PERIODES_COMPTABLES = "Comptabilité - Périodes comptables"
TAG_ECRITURES_COMPTABLES = "Comptabilité - Écritures comptables"


# --- Comptes comptables (plan comptable) ---
@router.get("/comptes", response_model=list[schemas.CompteComptableResponse], tags=[TAG_COMPTES_COMPTABLES])
async def list_comptes_comptables(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
):
    items, _ = await CompteComptableService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/comptes/{id}", response_model=schemas.CompteComptableResponse, tags=[TAG_COMPTES_COMPTABLES])
async def get_compte_comptable(db: DbSession, current_user: CurrentUser, id: int):
    ent = await CompteComptableService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/comptes", response_model=schemas.CompteComptableResponse, status_code=201, tags=[TAG_COMPTES_COMPTABLES])
async def create_compte_comptable(db: DbSession, current_user: CurrentUser, data: schemas.CompteComptableCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CompteComptableService(db).create(data)


@router.patch("/comptes/{id}", response_model=schemas.CompteComptableResponse, tags=[TAG_COMPTES_COMPTABLES])
async def update_compte_comptable(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CompteComptableUpdate):
    ent = await CompteComptableService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await CompteComptableService(db).update(id, data)


# --- Journaux comptables ---
@router.get("/journaux", response_model=list[schemas.JournalComptableResponse], tags=[TAG_JOURNAUX_COMPTABLES])
async def list_journaux_comptables(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await JournalComptableService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/journaux/{id}", response_model=schemas.JournalComptableResponse, tags=[TAG_JOURNAUX_COMPTABLES])
async def get_journal_comptable(db: DbSession, current_user: CurrentUser, id: int):
    ent = await JournalComptableService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/journaux", response_model=schemas.JournalComptableResponse, status_code=201, tags=[TAG_JOURNAUX_COMPTABLES])
async def create_journal_comptable(db: DbSession, current_user: CurrentUser, data: schemas.JournalComptableCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await JournalComptableService(db).create(data)


@router.patch("/journaux/{id}", response_model=schemas.JournalComptableResponse, tags=[TAG_JOURNAUX_COMPTABLES])
async def update_journal_comptable(db: DbSession, current_user: CurrentUser, id: int, data: schemas.JournalComptableUpdate):
    ent = await JournalComptableService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await JournalComptableService(db).update(id, data)


# --- Périodes comptables ---
@router.get("/periodes", response_model=list[schemas.PeriodeComptableResponse], tags=[TAG_PERIODES_COMPTABLES])
async def list_periodes_comptables(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    items, _ = await PeriodeComptableService(db).get_all(
        entreprise_id=entreprise_id, skip=skip, limit=limit
    )
    return items


@router.get("/periodes/{id}", response_model=schemas.PeriodeComptableResponse, tags=[TAG_PERIODES_COMPTABLES])
async def get_periode_comptable(db: DbSession, current_user: CurrentUser, id: int):
    ent = await PeriodeComptableService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/periodes", response_model=schemas.PeriodeComptableResponse, status_code=201, tags=[TAG_PERIODES_COMPTABLES])
async def create_periode_comptable(db: DbSession, current_user: CurrentUser, data: schemas.PeriodeComptableCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PeriodeComptableService(db).create(data)


@router.patch("/periodes/{id}", response_model=schemas.PeriodeComptableResponse, tags=[TAG_PERIODES_COMPTABLES])
async def update_periode_comptable(db: DbSession, current_user: CurrentUser, id: int, data: schemas.PeriodeComptableUpdate):
    ent = await PeriodeComptableService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PeriodeComptableService(db).update(id, data)


# --- Écritures comptables ---
@router.get("/ecritures", response_model=list[schemas.EcritureComptableResponse], tags=[TAG_ECRITURES_COMPTABLES])
async def list_ecritures_comptables(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    journal_id: int | None = None,
    periode_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await EcritureComptableService(db).get_all(
        entreprise_id=entreprise_id,
        journal_id=journal_id,
        periode_id=periode_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/ecritures/{id}", response_model=schemas.EcritureComptableDetailResponse, tags=[TAG_ECRITURES_COMPTABLES])
async def get_ecriture_comptable(db: DbSession, current_user: CurrentUser, id: int):
    ent, lignes = await EcritureComptableService(db).get_with_lignes(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return schemas.EcritureComptableDetailResponse(
        **schemas.EcritureComptableResponse.model_validate(ent).model_dump(),
        lignes=[schemas.LigneEcritureResponse.model_validate(ligne) for ligne in lignes],
    )


@router.post("/ecritures", response_model=schemas.EcritureComptableResponse, status_code=201, tags=[TAG_ECRITURES_COMPTABLES])
async def create_ecriture_comptable(db: DbSession, current_user: CurrentUser, data: schemas.EcritureComptableCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await EcritureComptableService(db).create(data, created_by_id=getattr(current_user, "id", None))

