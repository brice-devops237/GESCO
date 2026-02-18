# app/modules/paie/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Paie. Isolation multi-tenant : listes par
# ValidatedEntrepriseId ; GET/PATCH/POST vérifient entreprise. Extension monde réel.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.core.exceptions import ForbiddenError
from app.modules.paie import schemas
from app.modules.paie.services import (
    BulletinPaieService,
    PeriodePaieService,
    TypeElementPaieService,
)
from app.modules.parametrage.dependencies import CurrentUser, ValidatedEntrepriseId

router = APIRouter(prefix="/paie")

TAG_PERIODES_PAIE = "Paie - Périodes de paie"
TAG_TYPES_ELEMENT_PAIE = "Paie - Types d'éléments de paie"
TAG_BULLETINS_PAIE = "Paie - Bulletins de paie"


# --- Périodes de paie ---
@router.get("/periodes", response_model=list[schemas.PeriodePaieResponse], tags=[TAG_PERIODES_PAIE])
async def list_periodes_paie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    cloturee: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=60),
):
    items, _ = await PeriodePaieService(db).get_all(
        entreprise_id=entreprise_id, cloturee=cloturee, skip=skip, limit=limit
    )
    return items


@router.get("/periodes/{id}", response_model=schemas.PeriodePaieResponse, tags=[TAG_PERIODES_PAIE])
async def get_periode_paie(db: DbSession, current_user: CurrentUser, id: int):
    ent = await PeriodePaieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/periodes", response_model=schemas.PeriodePaieResponse, status_code=201, tags=[TAG_PERIODES_PAIE])
async def create_periode_paie(db: DbSession, current_user: CurrentUser, data: schemas.PeriodePaieCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PeriodePaieService(db).create(data)


@router.patch("/periodes/{id}", response_model=schemas.PeriodePaieResponse, tags=[TAG_PERIODES_PAIE])
async def update_periode_paie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.PeriodePaieUpdate):
    ent = await PeriodePaieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PeriodePaieService(db).update(id, data)


# --- Types d'éléments de paie ---
@router.get("/types-element", response_model=list[schemas.TypeElementPaieResponse], tags=[TAG_TYPES_ELEMENT_PAIE])
async def list_types_element_paie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
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


@router.get("/types-element/{id}", response_model=schemas.TypeElementPaieResponse, tags=[TAG_TYPES_ELEMENT_PAIE])
async def get_type_element_paie(db: DbSession, current_user: CurrentUser, id: int):
    ent = await TypeElementPaieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/types-element", response_model=schemas.TypeElementPaieResponse, status_code=201, tags=[TAG_TYPES_ELEMENT_PAIE])
async def create_type_element_paie(db: DbSession, current_user: CurrentUser, data: schemas.TypeElementPaieCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await TypeElementPaieService(db).create(data)


@router.patch("/types-element/{id}", response_model=schemas.TypeElementPaieResponse, tags=[TAG_TYPES_ELEMENT_PAIE])
async def update_type_element_paie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.TypeElementPaieUpdate):
    ent = await TypeElementPaieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await TypeElementPaieService(db).update(id, data)


# --- Bulletins de paie ---
@router.get("/bulletins", response_model=list[schemas.BulletinPaieResponse], tags=[TAG_BULLETINS_PAIE])
async def list_bulletins_paie(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
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


@router.get("/bulletins/{id}", response_model=schemas.BulletinPaieResponse, tags=[TAG_BULLETINS_PAIE])
async def get_bulletin_paie(db: DbSession, current_user: CurrentUser, id: int):
    ent = await BulletinPaieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.get("/bulletins/{id}/detail", response_model=schemas.BulletinPaieDetailResponse, tags=[TAG_BULLETINS_PAIE])
async def get_bulletin_paie_detail(db: DbSession, current_user: CurrentUser, id: int):
    """Détail d'un bulletin de paie avec ses lignes (éléments de paie)."""
    ent = await BulletinPaieService(db).get_by_id_with_lignes_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return schemas.BulletinPaieDetailResponse(
        **schemas.BulletinPaieResponse.model_validate(ent).model_dump(),
        lignes=[schemas.LigneBulletinPaieResponse.model_validate(ligne) for ligne in ent.lignes],
    )


@router.post("/bulletins", response_model=schemas.BulletinPaieResponse, status_code=201, tags=[TAG_BULLETINS_PAIE])
async def create_bulletin_paie(db: DbSession, current_user: CurrentUser, data: schemas.BulletinPaieCreate):
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await BulletinPaieService(db).create(data)


@router.patch("/bulletins/{id}", response_model=schemas.BulletinPaieResponse, tags=[TAG_BULLETINS_PAIE])
async def update_bulletin_paie(db: DbSession, current_user: CurrentUser, id: int, data: schemas.BulletinPaieUpdate):
    ent = await BulletinPaieService(db).get_or_404(id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await BulletinPaieService(db).update(id, data)

