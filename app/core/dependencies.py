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

# Alias pour annotations : db: DbSession = Depends(get_db)
DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
