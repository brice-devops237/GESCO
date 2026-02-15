# app/modules/paie/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Paie. Préfixe /paie.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.paie import schemas
from app.modules.paie.services import PeriodePaieService, TypeElementPaieService, BulletinPaieService

router = APIRouter(prefix="/paie", tags=["Paie"])


# --- Périodes de paie ---
@router.get("/periodes", response_model=list[schemas.PeriodePaieResponse])
async def list_periodes_paie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    cloturee: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=60),
):
    items, _ = await PeriodePaieService(db).get_all(
        entreprise_id=entreprise_id, cloturee=cloturee, skip=skip, limit=limit
    )
    return items


@router.get("/periodes/{id}", response_model=schemas.PeriodePaieResponse)
async def get_periode_paie(db: DbSession, current_user: CurrentUser, id: int):
    return await PeriodePaieService(db).get_or_404(id)


@router.post("/periodes", response_model=schemas.PeriodePaieResponse, status_code=201)
async def create_periode_paie(db: DbSession, current_user: CurrentUser, data: schemas.PeriodePaieCreate):
    return await PeriodePaieService(db).create(data)


@router.patch("/periodes/{id}", response_model=schemas.PeriodePaieResponse)
async def update_periode_paie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.PeriodePaieUpdate):
    return await PeriodePaieService(db).update(id, data)


# --- Types d'éléments de paie ---
@router.get("/types-element", response_model=list[schemas.TypeElementPaieResponse])
async def list_types_element_paie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    actif_only: bool = False,
    type_filter: str | None = Query(None, description="gain ou retenue"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    items, _ = await TypeElementPaieService(db).get_all(
        entreprise_id=entreprise_id,
        actif_only=actif_only,
        type_filter=type_filter,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/types-element/{id}", response_model=schemas.TypeElementPaieResponse)
async def get_type_element_paie(db: DbSession, current_user: CurrentUser, id: int):
    return await TypeElementPaieService(db).get_or_404(id)


@router.post("/types-element", response_model=schemas.TypeElementPaieResponse, status_code=201)
async def create_type_element_paie(db: DbSession, current_user: CurrentUser, data: schemas.TypeElementPaieCreate):
    return await TypeElementPaieService(db).create(data)


@router.patch("/types-element/{id}", response_model=schemas.TypeElementPaieResponse)
async def update_type_element_paie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.TypeElementPaieUpdate):
    return await TypeElementPaieService(db).update(id, data)


# --- Bulletins de paie ---
@router.get("/bulletins", response_model=list[schemas.BulletinPaieResponse])
async def list_bulletins_paie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    employe_id: int | None = None,
    periode_paie_id: int | None = None,
    statut: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await BulletinPaieService(db).get_all(
        entreprise_id=entreprise_id,
        employe_id=employe_id,
        periode_paie_id=periode_paie_id,
        statut=statut,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/bulletins/{id}", response_model=schemas.BulletinPaieResponse)
async def get_bulletin_paie(db: DbSession, current_user: CurrentUser, id: int):
    return await BulletinPaieService(db).get_or_404(id)


@router.get("/bulletins/{id}/detail", response_model=schemas.BulletinPaieDetailResponse)
async def get_bulletin_paie_detail(db: DbSession, current_user: CurrentUser, id: int):
    ent = await BulletinPaieService(db).get_by_id_with_lignes(id)
    if ent is None:
        from app.modules.paie.services.messages import Messages
        from app.core.exceptions import NotFoundError
        raise NotFoundError(detail=Messages.BULLETIN_PAIE_NOT_FOUND)
    return schemas.BulletinPaieDetailResponse(
        **schemas.BulletinPaieResponse.model_validate(ent).model_dump(),
        lignes=[schemas.LigneBulletinPaieResponse.model_validate(l) for l in ent.lignes],
    )


@router.post("/bulletins", response_model=schemas.BulletinPaieResponse, status_code=201)
async def create_bulletin_paie(db: DbSession, current_user: CurrentUser, data: schemas.BulletinPaieCreate):
    return await BulletinPaieService(db).create(data)


@router.patch("/bulletins/{id}", response_model=schemas.BulletinPaieResponse)
async def update_bulletin_paie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.BulletinPaieUpdate):
    return await BulletinPaieService(db).update(id, data)
