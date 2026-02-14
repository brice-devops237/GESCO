# app/core/database.py
# -----------------------------------------------------------------------------
# Connexion et session SQLAlchemy asynchrone pour Gesco.
# Base déclarative partagée par tous les modèles ORM.
# Aucun import depuis app.modules pour éviter les imports circulaires.
# -----------------------------------------------------------------------------

from collections.abc import AsyncGenerator
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr

# Import différé de get_settings pour éviter chargement circulaire au démarrage
# (config peut être chargé avant que l'app soit complète)


def _get_database_url() -> str:
    """Lit l'URL de la base depuis la config (import local pour éviter cycle)."""
    from app.config import get_settings
    return get_settings().DATABASE_URL


def _get_engine_kwargs() -> dict:
    """Options du moteur (pool, echo)."""
    from app.config import get_settings
    s = get_settings()
    return {
        "pool_size": s.DATABASE_POOL_SIZE,
        "max_overflow": s.DATABASE_MAX_OVERFLOW,
        "echo": s.DATABASE_ECHO,
    }


class Base(DeclarativeBase):
    """
    Base déclarative SQLAlchemy. Tous les modèles du projet héritent de Base.
    __tablename__ est dérivé automatiquement du nom de la classe (snake_case).
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Génère le nom de table en snake_case à partir du nom de la classe."""
        name = cls.__name__
        # Conversion CamelCase -> snake_case (ex: PointDeVente -> point_de_vente)
        result = [name[0].lower()]
        for c in name[1:]:
            result.append(c.lower() if not c.isupper() else f"_{c.lower()}")
        return "".join(result).replace("__", "_")


# Moteur asynchrone (créé au premier accès)
_engine = None


def get_engine():
    """Retourne le moteur asynchrone (création paresseuse)."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _get_database_url(),
            **_get_engine_kwargs(),
        )
    return _engine


# Factory de sessions (créée à la première utilisation pour retarder l'accès à get_engine)
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Retourne le sessionmaker asynchrone (création paresseuse)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Générateur de session asynchrone pour l'injection FastAPI.
    Garantit la fermeture de la session après la requête (finally).
    Usage : db: AsyncSession = Depends(get_db)
    """
    async with _get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type raccourci pour l'annotation des dépendances
DbSession = Annotated[AsyncSession, "Injection de la session SQLAlchemy asynchrone"]
