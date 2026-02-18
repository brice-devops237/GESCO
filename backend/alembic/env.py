import sys
from pathlib import Path

# Racine projet (parent de alembic)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig

from sqlalchemy import pool

from alembic import context

# URL depuis la config Gesco (DATABASE_URL_SYNC pour migrations synchrones)
from app.config import get_settings
settings = get_settings()
db_url = settings.DATABASE_URL_SYNC

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées de tous les modèles (import pour enregistrer les tables)
from app.core.database import Base
from app.modules.parametrage import models as _parametrage_models
from app.modules.catalogue import models as _catalogue_models
from app.modules.partenaires import models as _partenaires_models
from app.modules.commercial import models as _commercial_models
from app.modules.achats import models as _achats_models
from app.modules.stock import models as _stock_models
from app.modules.tresorerie import models as _tresorerie_models
from app.modules.comptabilite import models as _comptabilite_models
from app.modules.rh import models as _rh_models
from app.modules.paie import models as _paie_models
from app.modules.immobilisations import models as _immobilisations_models
from app.modules.systeme import models as _systeme_models

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (URL depuis app.config)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (Engine depuis app.config)."""
    from sqlalchemy import create_engine
    connectable = create_engine(db_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
