# tests/conftest.py
# -----------------------------------------------------------------------------
# Fixtures pytest : base SQLite en mémoire, création des tables, seed minimal,
# client HTTP async pour les tests d'API.
# -----------------------------------------------------------------------------

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Définir l'environnement AVANT tout import de app (pour que get_settings lise ces valeurs)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///:memory:"
os.environ.setdefault("SECRET_KEY", "0123456789abcdef0123456789abcdef")

from app.core.database import Base, get_engine
from app.core.security import hash_password
from app.modules.commercial.models import EtatDocument
from app.modules.partenaires.models import TypeTiers, Tiers
from app.modules.parametrage.models import (
    AffectationUtilisateurPdv,
    Devise,
    Entreprise,
    PointDeVente,
    Role,
    Utilisateur,
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """Boucle d'événements partagée pour la session (pytest-asyncio)."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


async def _seed_minimal(session: AsyncSession) -> None:
    """Insère le minimum pour login et un test facture (devise, entreprise, PDV, rôle, user, état, type tiers, tiers)."""
    r = await session.execute(select(Devise).where(Devise.code == "XAF"))
    devise = r.scalar_one_or_none()
    if devise is None:
        devise = Devise(code="XAF", libelle="Franc CFA", symbole="FCFA", decimales=0, actif=True)
        session.add(devise)
        await session.flush()
    r = await session.execute(select(Entreprise).limit(1))
    ent = r.scalar_one_or_none()
    if not ent:
        ent = Entreprise(
            code="ENT1",
            raison_sociale="Entreprise Test",
            sigle="ENT1",
            pays="CMR",
            devise_principale_id=devise.id,
            actif=True,
        )
        session.add(ent)
        await session.flush()
    r = await session.execute(select(PointDeVente).where(PointDeVente.entreprise_id == ent.id).limit(1))
    pdv = r.scalar_one_or_none()
    if not pdv:
        pdv = PointDeVente(
            entreprise_id=ent.id,
            code="PDV1",
            libelle="Point Test",
            type="vente",
            actif=True,
        )
        session.add(pdv)
        await session.flush()
    r = await session.execute(select(Role).where(Role.entreprise_id == ent.id).limit(1))
    role = r.scalar_one_or_none()
    if not role:
        role = Role(entreprise_id=ent.id, code="ADMIN", libelle="Administrateur")
        session.add(role)
        await session.flush()
    r = await session.execute(
        select(Utilisateur).where(
            Utilisateur.entreprise_id == ent.id,
            Utilisateur.login == "test",
        ).limit(1)
    )
    if r.scalar_one_or_none() is None:
        user = Utilisateur(
            entreprise_id=ent.id,
            point_de_vente_id=pdv.id,
            role_id=role.id,
            login="test",
            mot_de_passe_hash=hash_password("password"),
            email="test@test.local",
            nom="Test",
            prenom="User",
            actif=True,
        )
        session.add(user)
        await session.flush()
        session.add(AffectationUtilisateurPdv(utilisateur_id=user.id, point_de_vente_id=pdv.id, est_principal=True))
    r = await session.execute(select(EtatDocument).where(EtatDocument.type_document == "facture").limit(1))
    if r.scalar_one_or_none() is None:
        session.add(EtatDocument(type_document="facture", code="BROUILLON", libelle="Brouillon", ordre=0))
        await session.flush()
    r = await session.execute(select(TypeTiers).limit(1))
    tt = r.scalar_one_or_none()
    if not tt:
        tt = TypeTiers(libelle="Client", code="CLI")
        session.add(tt)
        await session.flush()
    r = await session.execute(select(Tiers).where(Tiers.entreprise_id == ent.id).limit(1))
    if r.scalar_one_or_none() is None:
        session.add(Tiers(entreprise_id=ent.id, type_tiers_id=tt.id, code="CLI001", libelle="Client Test", actif=True))
    await session.commit()


@pytest.fixture(scope="session")
async def _engine_and_tables():
    """Crée le moteur, les tables et insère les données de test (une fois par session)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        await _seed_minimal(session)
    return engine


@pytest.fixture
async def client(_engine_and_tables):
    """Client HTTP async pour appeler l'API (tables et seed déjà en place)."""
    await _engine_and_tables
    from app.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

