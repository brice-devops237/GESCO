# app/core/dependencies.py
# -----------------------------------------------------------------------------
# Dépendances FastAPI partagées (injection de la session DB, config).
# Ne contient pas get_current_user : celle-ci est dans parametrage.dependencies
# pour éviter que core dépende des modules métier (évite imports circulaires).
# -----------------------------------------------------------------------------

from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.core.database import AsyncSession, get_db

# Alias canonique pour l'injection de session dans les routes : db: DbSession
DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

