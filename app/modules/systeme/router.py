# app/modules/systeme/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Système. Préfixe /systeme.
# -----------------------------------------------------------------------------

from datetime import datetime
from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.systeme import schemas
from app.modules.systeme.services import (
    ParametreSystemeService,
    AuditService,
    NotificationService,
    LicenceLogicielleService,
)

router = APIRouter(prefix="/systeme", tags=["Système"])


# --- Paramètres système ---
@router.get("/parametres", response_model=list[schemas.ParametreSystemeResponse])
async def list_parametres_systeme(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    categorie: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
):
    items, _ = await ParametreSystemeService(db).get_all(
        entreprise_id=entreprise_id,
        categorie=categorie,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/parametres/{id}", response_model=schemas.ParametreSystemeResponse)
async def get_parametre_systeme(db: DbSession, current_user: CurrentUser, id: int):
    return await ParametreSystemeService(db).get_or_404(id)


@router.post("/parametres", response_model=schemas.ParametreSystemeResponse, status_code=201)
async def create_parametre_systeme(db: DbSession, current_user: CurrentUser, data: schemas.ParametreSystemeCreate):
    return await ParametreSystemeService(db).create(data)


@router.patch("/parametres/{id}", response_model=schemas.ParametreSystemeResponse)
async def update_parametre_systeme(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ParametreSystemeUpdate):
    return await ParametreSystemeService(db).update(id, data)


# --- Journal d'audit ---
@router.get("/audit", response_model=list[schemas.JournalAuditResponse])
async def list_journal_audit(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int | None = Query(None, description="Filtrer par entreprise"),
    utilisateur_id: int | None = Query(None, description="Filtrer par utilisateur"),
    action: str | None = Query(None, description="Filtrer par action"),
    module: str | None = Query(None, description="Filtrer par module"),
    date_debut: datetime | None = Query(None, description="Début de période"),
    date_fin: datetime | None = Query(None, description="Fin de période"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await AuditService(db).get_all(
        entreprise_id=entreprise_id,
        utilisateur_id=utilisateur_id,
        action=action,
        module=module,
        date_debut=date_debut,
        date_fin=date_fin,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/audit/{id}", response_model=schemas.JournalAuditResponse)
async def get_journal_audit(db: DbSession, current_user: CurrentUser, id: int):
    return await AuditService(db).get_or_404(id)


@router.post("/audit", response_model=schemas.JournalAuditResponse, status_code=201)
async def create_entree_audit(db: DbSession, current_user: CurrentUser, data: schemas.JournalAuditCreate):
    return await AuditService(db).create(data)


# --- Notifications ---
@router.get("/notifications", response_model=list[schemas.NotificationResponse])
async def list_notifications(
    db: DbSession,
    current_user: CurrentUser,
    lue: bool | None = Query(None, description="Filtrer par statut lu/non lu"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await NotificationService(db).get_all(
        utilisateur_id=current_user.id,
        lue=lue,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/notifications/{id}", response_model=schemas.NotificationResponse)
async def get_notification(db: DbSession, current_user: CurrentUser, id: int):
    return await NotificationService(db).get_or_404_for_user(id, current_user.id)


@router.post("/notifications", response_model=schemas.NotificationResponse, status_code=201)
async def create_notification(db: DbSession, current_user: CurrentUser, data: schemas.NotificationCreate):
    return await NotificationService(db).create(data)


@router.patch("/notifications/{id}", response_model=schemas.NotificationResponse)
async def update_notification(db: DbSession, current_user: CurrentUser, id: int, data: schemas.NotificationUpdate):
    await NotificationService(db).get_or_404_for_user(id, current_user.id)
    return await NotificationService(db).update(id, data)


@router.post("/notifications/{id}/marquer-lue", response_model=schemas.NotificationResponse)
async def marquer_notification_lue(db: DbSession, current_user: CurrentUser, id: int):
    return await NotificationService(db).marquer_lue(id, current_user.id)


# --- Licences logicielles (validité 1 an) ---
@router.get("/licences", response_model=list[schemas.LicenceLogicielleResponse])
async def list_licences(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int | None = Query(None, description="Filtrer par entreprise"),
    actif_only: bool = False,
    valide_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await LicenceLogicielleService(db).get_all(
        entreprise_id=entreprise_id,
        actif_only=actif_only,
        valide_only=valide_only,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/licences/verifier", response_model=schemas.LicenceValideResponse)
async def verifier_licence(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
):
    """Vérifie si l'entreprise dispose d'une licence valide (active et non expirée)."""
    valide, message, date_fin = await LicenceLogicielleService(db).verifier_validite(entreprise_id)
    return schemas.LicenceValideResponse(valide=valide, message=message, date_fin=date_fin)


@router.get("/licences/{id}", response_model=schemas.LicenceLogicielleResponse)
async def get_licence(db: DbSession, current_user: CurrentUser, id: int):
    return await LicenceLogicielleService(db).get_or_404(id)


@router.post("/licences", response_model=schemas.LicenceLogicielleResponse, status_code=201)
async def create_licence(db: DbSession, current_user: CurrentUser, data: schemas.LicenceLogicielleCreate):
    """Crée une licence. Durée selon type : trial 2 mois, standard 6 mois, premium 12 mois."""
    return await LicenceLogicielleService(db).create(data)


@router.patch("/licences/{id}", response_model=schemas.LicenceLogicielleResponse)
async def update_licence(db: DbSession, current_user: CurrentUser, id: int, data: schemas.LicenceLogicielleUpdate):
    return await LicenceLogicielleService(db).update(id, data)


@router.post("/licences/{id}/activer", response_model=schemas.LicenceLogicielleResponse)
async def activer_licence(db: DbSession, current_user: CurrentUser, id: int):
    """Enregistre la date d'activation de la licence (première utilisation)."""
    return await LicenceLogicielleService(db).activer(id)


@router.post("/licences/{id}/prolonger", response_model=schemas.LicenceLogicielleResponse)
async def prolonger_licence(db: DbSession, current_user: CurrentUser, id: int):
    """
    Prolonge la licence : ajoute la durée du type à la date de fin actuelle.
    Trial et standard : maximum 3 prolongations. Premium : illimité.
    """
    return await LicenceLogicielleService(db).prolonger(id)


@router.get("/licences/{id}/info-prolongations", response_model=schemas.LicenceProlongationsInfo)
async def info_prolongations_licence(db: DbSession, current_user: CurrentUser, id: int):
    """Retourne le nombre de prolongations utilisées et restantes (trial/standard : max 3, premium : illimité)."""
    ent = await LicenceLogicielleService(db).get_or_404(id)
    info = LicenceLogicielleService(db).get_info_prolongations(ent.type_licence, ent.nombre_prolongations or 0)
    return schemas.LicenceProlongationsInfo(**info)
