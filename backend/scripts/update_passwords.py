# scripts/update_passwords.py
# -----------------------------------------------------------------------------
# Met à jour le mot de passe de tous les utilisateurs en base.
# Usage : python -m scripts.update_passwords
# Mot de passe appliqué : gesco@1234
# -----------------------------------------------------------------------------

import asyncio
import os
import sys

if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings
from app.core.security import hash_password
from app.modules.parametrage.models import Utilisateur


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    new_hash = hash_password("gesco@1234")

    async with session_factory() as session:
        result = await session.execute(select(Utilisateur))
        users = result.scalars().all()
        for u in users:
            u.mot_de_passe_hash = new_hash
        await session.commit()
        print("Mot de passe mis a jour pour {} utilisateur(s) : gesco@1234".format(len(users)))
        for u in users:
            print("  - {} (login: {})".format(u.email or u.login, u.login))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
