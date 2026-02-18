# scripts/seed_data.py
# -----------------------------------------------------------------------------
# Seed Gesco : entreprise type BAZARD (commerce de détail varié), données Faker.
# Période : 3 ans = (aujourd'hui - 2 ans) → aujourd'hui.
# Modes : LIGHT (~50k), FULL (~400k), STRESS (~2M) pour montée en charge.
#
# Exécution : python -m scripts.seed_data [LIGHT|FULL|STRESS]
# Prérequis : migrations appliquées, .env (DATABASE_URL, DATABASE_URL_SYNC, SECRET_KEY).
# -----------------------------------------------------------------------------

from __future__ import annotations

import asyncio
import os
import random
import sys
from datetime import date, timedelta
from decimal import Decimal

# Période : 3 ans = maintenant - 2 ans → maintenant
_TODAY = date.today()
DATE_FIN = _TODAY
DATE_DEBUT = date(_TODAY.year - 2, 1, 1) if _TODAY.month == 1 and _TODAY.day == 1 else date(_TODAY.year - 2, _TODAY.month, _TODAY.day)
ANNEE_DEBUT = DATE_DEBUT.year
ANNEE_FIN = DATE_FIN.year

# Mode seed : LIGHT (rapide) | FULL (volume moyen) | STRESS (~2M enregistrements)
SEED_MODE = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SEED_MODE", "LIGHT")).upper()
if SEED_MODE not in ("LIGHT", "FULL", "STRESS"):
    SEED_MODE = "LIGHT"

# Volumes par mode (bazard : nombreux clients, factures, mouvements)
if SEED_MODE == "LIGHT":
    N_CLIENTS, N_FOURNISSEURS, N_PRODUITS = 150, 40, 180
    N_DEVIS_PAR_AN, N_COMMANDES_PAR_AN, N_FACTURES_PAR_AN = 450, 420, 420
    N_EMPLOYES, N_CF_FOURNISSEUR_PAR_AN = 28, 90
    BATCH_FLUSH = 500
elif SEED_MODE == "FULL":
    N_CLIENTS, N_FOURNISSEURS, N_PRODUITS = 1200, 120, 800
    N_DEVIS_PAR_AN, N_COMMANDES_PAR_AN, N_FACTURES_PAR_AN = 4000, 3800, 3800
    N_EMPLOYES, N_CF_FOURNISSEUR_PAR_AN = 45, 400
    BATCH_FLUSH = 2000
else:  # STRESS ~2M
    N_CLIENTS, N_FOURNISSEURS, N_PRODUITS = 6000, 300, 2500
    N_DEVIS_PAR_AN, N_COMMANDES_PAR_AN, N_FACTURES_PAR_AN = 22000, 20000, 20000
    N_EMPLOYES, N_CF_FOURNISSEUR_PAR_AN = 60, 2500
    BATCH_FLUSH = 5000

N_ANNEES = ANNEE_FIN - ANNEE_DEBUT + 1
N_PERIODES_PAIE = N_ANNEES * 12

# Charger .env avant app
if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# Racine projet = parent de scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker

# Faker : français + seed pour reproductibilité
FAKER = Faker("fr_FR")
FAKER.seed_instance(42)
random.seed(42)

# Référentiels géo Cameroun (bazard = ventes nationales)
VILLES_REGIONS_CMR = [
    ("Douala", "Littoral"), ("Yaoundé", "Centre"), ("Garoua", "Nord"),
    ("Bamenda", "Nord-Ouest"), ("Bafoussam", "Ouest"), ("Maroua", "Extrême-Nord"),
    ("Nkongsamba", "Littoral"), ("Kribi", "Sud"), ("Limbe", "Sud-Ouest"),
    ("Ebolowa", "Sud"), ("Dschang", "Ouest"), ("Bonabéri", "Littoral"),
    ("Ngaoundéré", "Adamaoua"), ("Bertoua", "Est"), ("Édea", "Littoral"),
    ("Foumban", "Ouest"), ("Kousséri", "Extrême-Nord"), ("Mbalmayo", "Centre"),
    ("Sangmélima", "Sud"), ("Buea", "Sud-Ouest"), ("Melong", "Littoral"),
    ("Tiko", "Sud-Ouest"), ("Kumba", "Sud-Ouest"), ("Mbouda", "Ouest"),
    ("Bafang", "Ouest"), ("Manjo", "Littoral"), ("Loum", "Littoral"),
    ("Obala", "Centre"), ("Mbandjock", "Centre"), ("Nkoteng", "Centre"),
    ("Batouri", "Est"), ("Abong-Mbang", "Est"), ("Yokadouma", "Est"),
]
# Paiement : Cash, ou Mobile (MTN / Orange), ou Cash + Mobile avec montants par méthode
OPERATEURS_MOMO = ["MTN", "Orange"]

# Libellés produits type bazard (alimentation, boissons, hygiène, quincaillerie)
LIBELLES_BAZARD = [
    "Riz parfumé 1 kg", "Huile végétale 1 L", "Sucre 1 kg", "Farine 1 kg",
    "Sardines boîte 125 g", "Lait concentré sucré", "Café 250 g", "Thé 100 sachets",
    "Savon lessive 1 kg", "Biscuit chocolat", "Pâte alimentaire 500 g",
    "Tomate concentrée 400 g", "Sauce piment", "Chocolat tablette", "Confiture",
    "Soda orange 1,5 L", "Eau minérale 1,5 L", "Jus d'orange 1 L", "Yaourt nature",
    "Oeufs plateau 30", "Poulet congelé 1 kg", "Huile palme 1 L", "Sel 1 kg",
    "Bouillon cube", "Sauce soja", "Mayonnaise", "Ketchup", "Miel 500 g",
    "Savon de toilette", "Dentifrice", "Shampoing", "Papier hygiénique",
    "Batterie cuisine", "Lampe torche", "Bougie", "Allumettes",
    "Riz local 25 kg", "Maïs grain 1 kg", "Haricot rouge 1 kg", "Lentilles 500 g",
    "Spaghetti 500 g", "Vermicelle 400 g", "Lait en poudre 400 g", "Cacao 500 g",
    "Margarine 250 g", "Confiture mangue 450 g", "Sardines à l'huile 1 kg",
    "Thon boîte 170 g", "Pilchards boîte", "Corned beef boîte", "Choucroute boîte",
    "Jus mangue 1 L", "Limonade 33 cl", "Bière bouteille 65 cl", "Vin rouge 75 cl",
    "Eau gazeuse 1 L", "Lait caillé 500 ml", "Fromage portion", "Beurre 200 g",
    "Déodorant spray", "Rasoir jetable", "Serviettes hygiéniques", "Couches bébé",
    "Lessive liquide 1 L", "Eau de javel 1 L", "Éponge vaisselle", "Film alimentaire",
    "Sachets congélation", "Assiettes jetables", "Gobelets plastique", "Briquet",
    "Piles AA 4", "Ampoule LED", "Câble USB", "Savon noir 1 kg", "Crème corps",
    "Lait bébé 400 g", "Biberon", "Céréales petit-déjeuner", "Biscuit salé",
    "Cacahuètes 200 g", "Bonbon menthe", "Chocolat chaud sachet", "Infusion camomille",
]


def _date_alea(debut: date, fin: date) -> date:
    delta = (fin - debut).days
    return debut + timedelta(days=random.randint(0, max(0, delta))) if delta > 0 else debut


def _niu_cameroun() -> str:
    """NIU format DGI Cameroun : M + 9 chiffres + lettre."""
    return "M{:09d}{}".format(random.randint(1, 999999999), random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ"))


def _phone_cmr() -> str:
    """Téléphone Cameroun : +237 2/6 XX XX XX XX."""
    prefix = "2" if random.random() > 0.5 else "6"
    return "+237 {} {:02d} {:02d} {:02d} {:02d}".format(
        prefix, random.randint(20, 99), random.randint(10, 99),
        random.randint(10, 99), random.randint(10, 99)
    )


def _raison_sociale_client_bazard() -> str:
    templates = [
        "Boutique {}", "Épicerie {}", "Mini-market {}", "Supérette {}",
        "Commerce {}", "Dépôt {}", "Supermarché {}", "Grossiste {}",
    ]
    return FAKER.company() if random.random() > 0.5 else random.choice(templates).format(FAKER.last_name())


def _raison_sociale_fournisseur() -> str:
    return FAKER.company() + " " + random.choice(["Cameroun", "SA", "SARL", "Distribution"])


def _libelle_produit_bazard() -> str:
    base = random.choice(LIBELLES_BAZARD)
    if N_PRODUITS > 200:
        return "{} ({})".format(base, FAKER.ean8() if random.random() > 0.7 else FAKER.word())
    return base


# Imports SQLAlchemy et app
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings
from app.core.security import hash_password

from app.modules.parametrage.models import (
    Devise, TauxChange, Entreprise, PointDeVente, Role, Permission,
    PermissionRole, Utilisateur, AffectationUtilisateurPdv,
)
from app.modules.catalogue.models import (
    UniteMesure, TauxTva, FamilleProduit, Conditionnement, Produit,
    ProduitConditionnement, CanalVente, PrixProduit, VarianteProduit,
)
from app.modules.partenaires.models import TypeTiers, Tiers, Contact
from app.modules.commercial.models import EtatDocument, Devis, Commande, Facture, BonLivraison
from app.modules.achats.models import Depot, CommandeFournisseur, Reception, FactureFournisseur
from app.modules.stock.models import Stock, MouvementStock
from app.modules.tresorerie.models import ModePaiement, CompteTresorerie, Reglement
from app.modules.comptabilite.models import (
    CompteComptable, JournalComptable, PeriodeComptable, EcritureComptable, LigneEcriture,
)
from app.modules.rh.models import (
    Departement, Poste, TypeContrat, Employe, TypeConge, DemandeConge, SoldeConge,
    Objectif, TauxCommission, Commission, Avance,
)
from app.modules.paie.models import PeriodePaie, TypeElementPaie, BulletinPaie, LigneBulletinPaie
from app.modules.immobilisations.models import CategorieImmobilisation, Immobilisation, LigneAmortissement
from app.modules.systeme.models import ParametreSysteme, JournalAudit, Notification, LicenceLogicielle


async def run_seed(session: AsyncSession) -> None:
    """Seed complet : entreprise Bazard, Faker, période 3 ans, volume selon SEED_MODE."""
    # Base déjà seedée ? (évite doublon si on relance par erreur)
    existing = await session.execute(select(Devise).where(Devise.code == "XAF").limit(1))
    if existing.scalar_one_or_none() is not None:
        print("Base deja seedee (devise XAF presente). Pour repartir de zero : fermez l'app, supprimez app/db/gesco.db, relancez 'alembic upgrade head' puis ce script.")
        return
    # ----- 1. Référentiels globaux -----
    devises = [
        Devise(code="XAF", libelle="Franc CFA (CEMAC)", symbole="FCFA", decimales=0, actif=True),
        Devise(code="EUR", libelle="Euro", symbole="€", decimales=2, actif=True),
        Devise(code="USD", libelle="Dollar US", symbole="$", decimales=2, actif=True),
    ]
    for d in devises:
        session.add(d)
    await session.flush()

    unites = [
        UniteMesure(code="PCE", libelle="Pièce", symbole="pce", type="unite", actif=True),
        UniteMesure(code="KG", libelle="Kilogramme", symbole="kg", type="poids", actif=True),
        UniteMesure(code="L", libelle="Litre", symbole="L", type="volume", actif=True),
        UniteMesure(code="CARTON", libelle="Carton", symbole="ct", type="unite", actif=True),
    ]
    for u in unites:
        session.add(u)
    await session.flush()

    taux_tva = [
        TauxTva(code="TVA0", taux=Decimal("0"), libelle="Exonéré", actif=True),
        TauxTva(code="TVA19", taux=Decimal("19.25"), libelle="TVA 19,25% CGI", actif=True),
    ]
    for t in taux_tva:
        session.add(t)
    await session.flush()

    xaf_id = next(d.id for d in devises if d.code == "XAF")
    eur_id = next(d.id for d in devises if d.code == "EUR")
    for an in range(ANNEE_DEBUT, ANNEE_FIN + 1):
        session.add(TauxChange(devise_from_id=eur_id, devise_to_id=xaf_id, taux=655.957 + (an - ANNEE_DEBUT) * 2, date_effet=date(an, 1, 1)))
    await session.flush()

    # ----- 2. Entreprise : Bazard (commerce détail varié) -----
    ent = Entreprise(
        code="BAZARD-BON",
        raison_sociale="Bazard du Marché Bonabéri",
        sigle="BAZARD BONABÉRI",
        niu=_niu_cameroun(),
        regime_fiscal="reel_simplifie",
        mode_gestion="standard",
        adresse="Marché Bonabéri, face gare routière",
        ville="Douala",
        region="Littoral",
        pays="CMR",
        telephone="+237 233 41 12 34",
        email="contact@bazard-bonaberi.cm",
        site_web="https://www.bazard-bonaberi.cm",
        devise_principale="XAF",
        actif=True,
    )
    session.add(ent)
    await session.flush()
    ent_id = ent.id

    # ----- 3. Points de vente (coordonnées WGS84 : Bonabéri / Douala) -----
    pdv_principal = PointDeVente(
        entreprise_id=ent_id, code="PDV-01", libelle="Siège Marché Bonabéri",
        type="principal", adresse="Marché Bonabéri", ville="Douala",
        telephone="+237 233 41 12 35",
        latitude=Decimal("4.084400"), longitude=Decimal("9.667800"),
        est_depot=False, actif=True,
    )
    pdv_depot = PointDeVente(
        entreprise_id=ent_id, code="DEP-01", libelle="Entrepôt Bonabéri",
        type="depot", ville="Douala", telephone="+237 233 41 12 36",
        latitude=Decimal("4.081200"), longitude=Decimal("9.672100"),
        est_depot=True, actif=True,
    )
    session.add(pdv_principal)
    session.add(pdv_depot)
    await session.flush()
    pdv_principal_id = pdv_principal.id
    pdv_depot_id = pdv_depot.id

    # ----- 4. Rôles et permissions -----
    perms_data = [
        ("parametrage", "read", "Paramétrage - Lecture"), ("parametrage", "write", "Paramétrage - Écriture"),
        ("catalogue", "read", "Catalogue - Lecture"), ("catalogue", "write", "Catalogue - Écriture"),
        ("commercial", "read", "Commercial - Lecture"), ("commercial", "write", "Commercial - Écriture"),
        ("achats", "read", "Achats - Lecture"), ("achats", "write", "Achats - Écriture"),
        ("comptabilite", "read", "Comptabilité - Lecture"), ("comptabilite", "write", "Comptabilité - Écriture"),
        ("rh", "read", "RH - Lecture"), ("rh", "write", "RH - Écriture"),
    ]
    permissions = []
    for mod, act, lib in perms_data:
        p = Permission(module=mod, action=act, libelle=lib)
        session.add(p)
        permissions.append(p)
    await session.flush()

    role_admin = Role(entreprise_id=ent_id, code="ADMIN", libelle="Administrateur")
    role_compta = Role(entreprise_id=ent_id, code="COMPTA", libelle="Comptable")
    role_commercial = Role(entreprise_id=ent_id, code="COMMERCIAL", libelle="Commercial")
    for r in (role_admin, role_compta, role_commercial):
        session.add(r)
    await session.flush()
    for p in permissions:
        session.add(PermissionRole(role_id=role_admin.id, permission_id=p.id))
    for p in permissions:
        if p.module in ("comptabilite", "parametrage") and p.action == "read":
            session.add(PermissionRole(role_id=role_compta.id, permission_id=p.id))
    await session.flush()

    # ----- 5. Utilisateurs -----
    pwd_hash = hash_password("gesco@1234")
    user_admin = Utilisateur(
        entreprise_id=ent_id, point_de_vente_id=pdv_principal_id, role_id=role_admin.id,
        login="admin", mot_de_passe_hash=pwd_hash, email="admin@bazard-bonaberi.cm",
        nom=FAKER.last_name(), prenom=FAKER.first_name(), telephone=_phone_cmr(), actif=True,
    )
    user_compta = Utilisateur(
        entreprise_id=ent_id, point_de_vente_id=pdv_principal_id, role_id=role_compta.id,
        login="compta", mot_de_passe_hash=pwd_hash, email="compta@bazard-bonaberi.cm",
        nom=FAKER.last_name(), prenom=FAKER.first_name(), actif=True,
    )
    session.add(user_admin)
    session.add(user_compta)
    await session.flush()
    session.add(AffectationUtilisateurPdv(utilisateur_id=user_admin.id, point_de_vente_id=pdv_principal_id, est_principal=True))
    session.add(AffectationUtilisateurPdv(utilisateur_id=user_compta.id, point_de_vente_id=pdv_principal_id, est_principal=True))
    await session.flush()

    # ----- 6. Catalogue : familles (bazard), conditionnements, canaux, produits -----
    familles_data = [
        ("ALIM", "Alimentaire", 1), ("BOIS", "Boissons", 2), ("HYG", "Hygiène", 3),
        ("CONS", "Conserves", 4), ("LAIT", "Laitiers", 5), ("EPIC", "Epicerie", 6), ("QUIN", "Quincaillerie", 7),
    ]
    familles = []
    for code, lib, ord in familles_data:
        f = FamilleProduit(entreprise_id=ent_id, parent_id=None, code=code, libelle=lib, niveau=1, ordre_affichage=ord, actif=True)
        session.add(f)
        familles.append(f)
    await session.flush()

    cond_caisse = Conditionnement(entreprise_id=ent_id, code="CAISSE12", libelle="Caisse de 12", quantite_unites=Decimal("12"), unite_id=unites[0].id, actif=True)
    cond_carton = Conditionnement(entreprise_id=ent_id, code="CARTON24", libelle="Carton 24", quantite_unites=Decimal("24"), unite_id=unites[3].id, actif=True)
    session.add(cond_caisse)
    session.add(cond_carton)
    await session.flush()

    canal_det = CanalVente(entreprise_id=ent_id, code="DET", libelle="Détail", ordre=1, actif=True)
    canal_gros = CanalVente(entreprise_id=ent_id, code="GROS", libelle="Gros", ordre=2, actif=True)
    session.add(canal_det)
    session.add(canal_gros)
    await session.flush()

    tva19_id = next(t.id for t in taux_tva if t.code == "TVA19")
    tva0_id = next(t.id for t in taux_tva if t.code == "TVA0")
    produits = []
    for i in range(1, N_PRODUITS + 1):
        lib = _libelle_produit_bazard()
        famille = random.choice(familles)
        unite = random.choice(unites)
        prix_achat = Decimal(str(random.randint(100, 12000)))
        marge = Decimal(str(random.uniform(1.12, 1.40)))
        prix_vente = (prix_achat * marge).quantize(Decimal("1"))
        pr = Produit(
            entreprise_id=ent_id, famille_id=famille.id, code="PROD-{:05d}".format(i),
            code_barre="613{:010d}".format(i) if i % 2 == 0 else None,
            libelle=lib[:255], type="produit", unite_vente_id=unite.id, unite_achat_id=unite.id,
            coefficient_achat_vente=Decimal("1"), prix_achat_ht=prix_achat, prix_vente_ttc=prix_vente,
            taux_tva_id=tva19_id if i % 5 != 0 else tva0_id,
            seuil_alerte_min=Decimal(str(random.randint(5, 50))), gerer_stock=True, actif=True,
        )
        session.add(pr)
        produits.append(pr)
        if (i % BATCH_FLUSH) == 0:
            await session.flush()
    await session.flush()

    for pr in produits[: min(25, len(produits))]:
        session.add(ProduitConditionnement(produit_id=pr.id, conditionnement_id=cond_caisse.id, quantite_unites=Decimal("12"), prix_vente_ttc=(pr.prix_vente_ttc * 12 * Decimal("0.95")).quantize(Decimal("1"))))
    await session.flush()

    date_debut_prix = DATE_DEBUT
    for pr in produits:
        session.add(PrixProduit(produit_id=pr.id, canal_vente_id=canal_det.id, prix_ttc=pr.prix_vente_ttc, date_debut=date_debut_prix))
        if pr.id % BATCH_FLUSH == 0:
            await session.flush()
    await session.flush()

    for pr in produits[2: min(15, len(produits))]:
        session.add(VarianteProduit(produit_id=pr.id, code="VAR-{}-1".format(pr.code), libelle="Nature", prix_ttc_supplement=Decimal("0"), stock_separe=False, actif=True))
    await session.flush()

    # ----- 7. Partenaires : clients et fournisseurs (Faker) -----
    type_client = TypeTiers(code="CLI", libelle="Client")
    type_fourn = TypeTiers(code="FOU", libelle="Fournisseur")
    session.add(type_client)
    session.add(type_fourn)
    await session.flush()

    clients = []
    for i in range(1, N_CLIENTS + 1):
        ville, region = random.choice(VILLES_REGIONS_CMR)
        t = Tiers(
            entreprise_id=ent_id, type_tiers_id=type_client.id, code="CLI-{:05d}".format(i),
            raison_sociale=_raison_sociale_client_bazard()[:255],
            niu=_niu_cameroun() if i % 3 != 0 else None,
            adresse=FAKER.street_address()[:200] if i % 2 == 0 else None,
            ville=ville, region=region, pays="CMR", telephone=_phone_cmr(),
            email=FAKER.company_email() if i % 4 != 0 else None,
            canal_vente_id=canal_gros.id if i % 3 == 0 else canal_det.id,
            limite_credit=Decimal(str(random.choice([0, 500000, 1000000, 5000000]))),
            delai_paiement_jours=random.choice([0, 7, 15, 30, 45, 60]),
            mobile_money_numero="6{:08d}".format(random.randint(70000000, 79999999)) if i % 2 == 0 else None,
            mobile_money_operateur=random.choice(OPERATEURS_MOMO) if i % 2 == 0 else None,
            actif=True,
        )
        session.add(t)
        clients.append(t)
        if (i % BATCH_FLUSH) == 0:
            await session.flush()
    await session.flush()

    fournisseurs = []
    for i in range(1, N_FOURNISSEURS + 1):
        ville, region = random.choice(VILLES_REGIONS_CMR)
        t = Tiers(
            entreprise_id=ent_id, type_tiers_id=type_fourn.id, code="FOU-{:05d}".format(i),
            raison_sociale=_raison_sociale_fournisseur()[:255],
            niu=_niu_cameroun(), ville=ville, region=region, pays="CMR",
            telephone=_phone_cmr(), delai_paiement_jours=random.choice([30, 45, 60]), actif=True,
        )
        session.add(t)
        fournisseurs.append(t)
    await session.flush()
    client1_id = clients[0].id
    fourn1_id = fournisseurs[0].id

    n_contacts_cli = min(60, len(clients))
    for i in range(n_contacts_cli):
        c = clients[i]
        session.add(Contact(tiers_id=c.id, nom=FAKER.last_name(), prenom=FAKER.first_name(), fonction=random.choice(["Acheteur", "Directeur", "Gérant", "Responsable"]), telephone=_phone_cmr(), est_principal=(i == 0), actif=True))
    for i, f in enumerate(fournisseurs[: min(25, len(fournisseurs))]):
        session.add(Contact(tiers_id=f.id, nom=FAKER.last_name(), prenom=FAKER.first_name(), fonction="Commercial", telephone=_phone_cmr(), est_principal=True, actif=True))
    await session.flush()

    # ----- 8. États document -----
    etats = [
        EtatDocument(type_document="devis", code="BROUILLON", libelle="Brouillon", ordre=0),
        EtatDocument(type_document="devis", code="VALIDE", libelle="Validé", ordre=1),
        EtatDocument(type_document="commande", code="BROUILLON", libelle="Brouillon", ordre=0),
        EtatDocument(type_document="commande", code="VALIDE", libelle="Validé", ordre=1),
        EtatDocument(type_document="facture", code="VALIDE", libelle="Validé", ordre=1),
        EtatDocument(type_document="bon_livraison", code="VALIDE", libelle="Validé", ordre=1),
    ]
    for e in etats:
        session.add(e)
    await session.flush()
    etat_devis_valide = next(e.id for e in etats if e.type_document == "devis" and e.code == "VALIDE")
    etat_cde_valide = next(e.id for e in etats if e.type_document == "commande" and e.code == "VALIDE")
    etat_fact_valide = next(e.id for e in etats if e.type_document == "facture" and e.code == "VALIDE")
    etat_bl_valide = next(e.id for e in etats if e.type_document == "bon_livraison" and e.code == "VALIDE")

    # ----- 9. Commercial : devis, commandes, factures, BL (3 ans, batch) -----
    devis_list, commande_list, facture_list, bl_list = [], [], [], []
    seq_devis, seq_cde, seq_fac, seq_bl = 0, 0, 0, 0
    for an in range(ANNEE_DEBUT, ANNEE_FIN + 1):
        debut_an = date(an, 1, 1)
        fin_an = date(an, 12, 31)
        n_devis = N_DEVIS_PAR_AN
        n_cde = N_COMMANDES_PAR_AN
        n_fac = N_FACTURES_PAR_AN

        for _ in range(n_devis):
            seq_devis += 1
            dt = _date_alea(debut_an, fin_an)
            client = random.choice(clients)
            mt_ht = Decimal(str(random.randint(8000, 3500000)))
            mt_tva = (mt_ht * Decimal("0.1925")).quantize(Decimal("0.01"))
            mt_ttc = mt_ht + mt_tva
            dev = Devis(entreprise_id=ent_id, point_de_vente_id=pdv_principal_id, client_id=client.id, numero="DEV-{}-{:05d}".format(an, seq_devis), date_devis=dt, date_validite=dt + timedelta(days=30), etat_id=etat_devis_valide, montant_ht=mt_ht, montant_tva=mt_tva, montant_ttc=mt_ttc, devise_id=xaf_id, taux_change=Decimal("1"))
            session.add(dev)
            devis_list.append(dev)
            if len(devis_list) % BATCH_FLUSH == 0:
                await session.flush()
        await session.flush()

        for _ in range(n_cde):
            seq_cde += 1
            dt = _date_alea(debut_an, fin_an)
            client = random.choice(clients)
            dev_ref = random.choice(devis_list) if devis_list and random.random() > 0.3 else None
            mt_ht = Decimal(str(random.randint(10000, 3000000)))
            mt_tva = (mt_ht * Decimal("0.1925")).quantize(Decimal("0.01"))
            mt_ttc = mt_ht + mt_tva
            cmd = Commande(entreprise_id=ent_id, point_de_vente_id=pdv_principal_id, client_id=client.id, devis_id=dev_ref.id if dev_ref else None, numero="CDE-{}-{:05d}".format(an, seq_cde), date_commande=dt, date_livraison_prevue=dt + timedelta(days=random.randint(3, 14)), etat_id=etat_cde_valide, montant_ht=mt_ht, montant_tva=mt_tva, montant_ttc=mt_ttc, devise_id=xaf_id, adresse_livraison="{}, CMR".format(random.choice(VILLES_REGIONS_CMR)[0]))
            session.add(cmd)
            commande_list.append(cmd)
            if len(commande_list) % BATCH_FLUSH == 0:
                await session.flush()
        await session.flush()

        for _ in range(n_fac):
            seq_fac += 1
            dt = _date_alea(debut_an, fin_an)
            client = random.choice(clients)
            cmd_ref = random.choice(commande_list) if commande_list and random.random() > 0.2 else None
            mt_ht = Decimal(str(random.randint(12000, 2800000)))
            mt_tva = (mt_ht * Decimal("0.1925")).quantize(Decimal("0.01"))
            mt_ttc = mt_ht + mt_tva
            restant = mt_ttc if random.random() > 0.4 else Decimal("0")
            fac = Facture(entreprise_id=ent_id, point_de_vente_id=pdv_principal_id, client_id=client.id, commande_id=cmd_ref.id if cmd_ref else None, numero="FAC-{}-{:05d}".format(an, seq_fac), date_facture=dt, date_echeance=dt + timedelta(days=random.choice([30, 45, 60])), etat_id=etat_fact_valide, type_facture="facture", montant_ht=mt_ht, montant_tva=mt_tva, montant_ttc=mt_ttc, montant_restant_du=restant, devise_id=xaf_id)
            session.add(fac)
            facture_list.append(fac)
            if len(facture_list) % BATCH_FLUSH == 0:
                await session.flush()
        await session.flush()

        for fac in facture_list[-n_fac:]:
            seq_bl += 1
            bl = BonLivraison(entreprise_id=ent_id, point_de_vente_id=pdv_principal_id, client_id=fac.client_id, commande_id=fac.commande_id, facture_id=fac.id, numero="BL-{}-{:05d}".format(an, seq_bl), date_livraison=fac.date_facture + timedelta(days=random.randint(0, 3)), adresse_livraison="Livraison client", etat_id=etat_bl_valide)
            session.add(bl)
            bl_list.append(bl)
        await session.flush()

    devis = devis_list[0]
    commande = commande_list[0]
    facture = facture_list[0]

    # ----- 10. Achats : dépôt, commandes fournisseurs, réceptions, factures fournisseurs -----
    depot = Depot(entreprise_id=ent_id, code="DEP-01", libelle="Entrepôt Bonabéri", point_de_vente_id=pdv_depot_id)
    session.add(depot)
    await session.flush()
    etat_cde_fou = next(e.id for e in etats if e.type_document == "commande" and e.code == "VALIDE")
    cf_list, recept_list, fact_fou_list = [], [], []
    seq_cf, seq_rec, seq_ff = 0, 0, 0
    for an in range(ANNEE_DEBUT, ANNEE_FIN + 1):
        debut_an, fin_an = date(an, 1, 1), date(an, 12, 31)
        for _ in range(N_CF_FOURNISSEUR_PAR_AN):
            seq_cf += 1
            fourn = random.choice(fournisseurs)
            dt = _date_alea(debut_an, fin_an)
            mt_ht = Decimal(str(random.randint(50000, 4000000)))
            mt_tva = (mt_ht * Decimal("0.1925")).quantize(Decimal("0.01"))
            mt_ttc = mt_ht + mt_tva
            cde_fou = CommandeFournisseur(entreprise_id=ent_id, fournisseur_id=fourn.id, depot_id=depot.id, numero="CF-{}-{:05d}".format(an, seq_cf), numero_fournisseur="CF-EXT-{}-{}".format(an, seq_cf), date_commande=dt, date_livraison_prevue=dt + timedelta(days=random.randint(5, 20)), etat_id=etat_cde_fou, montant_ht=mt_ht, montant_tva=mt_tva, montant_ttc=mt_ttc, devise_id=xaf_id)
            session.add(cde_fou)
            cf_list.append(cde_fou)
        await session.flush()
        for cde_fou in cf_list[-N_CF_FOURNISSEUR_PAR_AN:]:
            seq_rec += 1
            recept = Reception(commande_fournisseur_id=cde_fou.id, depot_id=depot.id, numero="REC-{}-{:05d}".format(an, seq_rec), date_reception=cde_fou.date_commande + timedelta(days=random.randint(2, 10)), etat="validee")
            session.add(recept)
            recept_list.append(recept)
        await session.flush()
        for cde_fou in cf_list[-N_CF_FOURNISSEUR_PAR_AN:]:
            seq_ff += 1
            statut = random.choice(["non_paye", "non_paye", "partiel", "paye"])
            restant = cde_fou.montant_ttc if statut != "paye" else Decimal("0")
            if statut == "partiel":
                restant = (cde_fou.montant_ttc * Decimal("0.4")).quantize(Decimal("0.01"))
            fact_fou = FactureFournisseur(entreprise_id=ent_id, fournisseur_id=cde_fou.fournisseur_id, commande_fournisseur_id=cde_fou.id, numero_fournisseur="FAC-{}-{:05d}".format(an, seq_ff), date_facture=cde_fou.date_commande + timedelta(days=random.randint(5, 15)), date_echeance=cde_fou.date_commande + timedelta(days=random.randint(45, 90)), montant_ht=cde_fou.montant_ht, montant_tva=cde_fou.montant_tva, montant_ttc=cde_fou.montant_ttc, montant_restant_du=restant, devise_id=xaf_id, statut_paiement=statut)
            session.add(fact_fou)
            fact_fou_list.append(fact_fou)
        await session.flush()

    # ----- 11. Stock et mouvements -----
    for pr in produits:
        qte = Decimal(str(random.randint(30, 1500)))
        session.add(Stock(depot_id=depot.id, produit_id=pr.id, variante_id=None, quantite=qte, unite_id=pr.unite_vente_id))
        if pr.id % BATCH_FLUSH == 0:
            await session.flush()
    await session.flush()

    n_mvt = min(300, len(recept_list)) if SEED_MODE == "LIGHT" else min(1500, len(recept_list))
    for recept in recept_list[:n_mvt]:
        for _ in range(random.randint(1, 4)):
            pr = random.choice(produits)
            session.add(MouvementStock(type_mouvement="entree", depot_id=depot.id, produit_id=pr.id, variante_id=None, quantite=Decimal(str(random.randint(10, 200))), reference_type="reception", reference_id=recept.id, notes="Réception fournisseur", created_by_id=user_admin.id))
    await session.flush()

    # ----- 12. Trésorerie : Cash, Mobile (MTN / Orange), ou Cash + Mobile (montants par méthode) -----
    mode_esp = ModePaiement(entreprise_id=ent_id, code="ESP", libelle="Espèces (cash)", actif=True)
    mode_mtn = ModePaiement(entreprise_id=ent_id, code="MTN", libelle="Mobile Money MTN", code_operateur="MTN", actif=True)
    mode_orange = ModePaiement(entreprise_id=ent_id, code="ORANGE", libelle="Mobile Money Orange", code_operateur="Orange", actif=True)
    mode_vir = ModePaiement(entreprise_id=ent_id, code="VIR", libelle="Virement bancaire", actif=True)
    for m in (mode_esp, mode_mtn, mode_orange, mode_vir):
        session.add(m)
    await session.flush()
    cpte_caisse = CompteTresorerie(entreprise_id=ent_id, type_compte="caisse", libelle="Caisse principale XAF", devise_id=xaf_id, actif=True)
    cpte_banque = CompteTresorerie(entreprise_id=ent_id, type_compte="bancaire", libelle="Compte BICEC", devise_id=xaf_id, actif=True)
    session.add(cpte_caisse)
    session.add(cpte_banque)
    await session.flush()

    def _add_reglement_client(fac, montant_total, date_regl):
        """Enregistre un ou deux règlements : cash seul, mobile seul (MTN ou Orange), ou cash + mobile avec montants."""
        if montant_total <= 0:
            return
        choix = random.choice(["cash", "mobile_mtn", "mobile_orange", "cash_et_mobile"])
        if choix == "cash":
            session.add(Reglement(entreprise_id=ent_id, type_reglement="client", facture_id=fac.id, tiers_id=fac.client_id, montant=montant_total, date_reglement=date_regl, mode_paiement_id=mode_esp.id, compte_tresorerie_id=cpte_caisse.id, reference=None, created_by_id=user_admin.id))
        elif choix == "mobile_mtn":
            session.add(Reglement(entreprise_id=ent_id, type_reglement="client", facture_id=fac.id, tiers_id=fac.client_id, montant=montant_total, date_reglement=date_regl, mode_paiement_id=mode_mtn.id, compte_tresorerie_id=cpte_caisse.id, reference="MTN 6{:08d}".format(random.randint(70000000, 79999999)), created_by_id=user_admin.id))
        elif choix == "mobile_orange":
            session.add(Reglement(entreprise_id=ent_id, type_reglement="client", facture_id=fac.id, tiers_id=fac.client_id, montant=montant_total, date_reglement=date_regl, mode_paiement_id=mode_orange.id, compte_tresorerie_id=cpte_caisse.id, reference="OM 6{:08d}".format(random.randint(69000000, 69999999)), created_by_id=user_admin.id))
        else:
            # Cash + Mobile : répartition des montants (ex. 40% cash, 60% mobile)
            part_cash = (montant_total * Decimal(str(random.uniform(0.2, 0.8)))).quantize(Decimal("0.01"))
            part_mobile = montant_total - part_cash
            if part_cash > 0:
                session.add(Reglement(entreprise_id=ent_id, type_reglement="client", facture_id=fac.id, tiers_id=fac.client_id, montant=part_cash, date_reglement=date_regl, mode_paiement_id=mode_esp.id, compte_tresorerie_id=cpte_caisse.id, reference="Espèces", created_by_id=user_admin.id))
            if part_mobile > 0:
                op = random.choice(["MTN", "Orange"])
                ref = "MTN 6{:08d}".format(random.randint(70000000, 79999999)) if op == "MTN" else "OM 6{:08d}".format(random.randint(69000000, 69999999))
                session.add(Reglement(entreprise_id=ent_id, type_reglement="client", facture_id=fac.id, tiers_id=fac.client_id, montant=part_mobile, date_reglement=date_regl, mode_paiement_id=mode_mtn.id if op == "MTN" else mode_orange.id, compte_tresorerie_id=cpte_caisse.id, reference=ref, created_by_id=user_admin.id))

    session.add(Reglement(entreprise_id=ent_id, type_reglement="client", facture_id=facture.id, tiers_id=client1_id, montant=Decimal("10000"), date_reglement=facture.date_facture + timedelta(days=5), mode_paiement_id=mode_mtn.id, compte_tresorerie_id=cpte_caisse.id, reference="MTN 670000001", created_by_id=user_admin.id))
    n_regl = min(600, len(facture_list)) if SEED_MODE == "LIGHT" else min(5000, len(facture_list))
    for fac in facture_list[1:n_regl]:
        if random.random() > 0.5:
            montant = fac.montant_ttc if random.random() > 0.3 else (fac.montant_ttc * Decimal(str(random.uniform(0.3, 0.9)))).quantize(Decimal("0.01"))
            date_regl = fac.date_facture + timedelta(days=random.randint(1, 60))
            _add_reglement_client(fac, montant, date_regl)
    await session.flush()

    # ----- 13. Comptabilité -----
    comptes = [
        CompteComptable(entreprise_id=ent_id, numero="411", libelle="Clients", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="401", libelle="Fournisseurs", sens_normal="credit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="512", libelle="Banque", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="53", libelle="Caisse", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="611", libelle="Achats stockés", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="711", libelle="Ventes marchandises", sens_normal="credit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="2250", libelle="Matériel informatique", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="2820", libelle="Amortissement matériel", sens_normal="credit", actif=True),
    ]
    for c in comptes:
        session.add(c)
    await session.flush()
    cpt_411 = next(c.id for c in comptes if c.numero == "411")
    cpt_53 = next(c.id for c in comptes if c.numero == "53")
    cpt_2250 = next(c.id for c in comptes if c.numero == "2250")
    cpt_2820 = next(c.id for c in comptes if c.numero == "2820")
    journaux = [
        JournalComptable(entreprise_id=ent_id, code="VT", libelle="Ventes", actif=True),
        JournalComptable(entreprise_id=ent_id, code="AC", libelle="Achats", actif=True),
        JournalComptable(entreprise_id=ent_id, code="BQ", libelle="Banque", actif=True),
        JournalComptable(entreprise_id=ent_id, code="CA", libelle="Caisse", actif=True),
        JournalComptable(entreprise_id=ent_id, code="OD", libelle="Opérations diverses", actif=True),
    ]
    for j in journaux:
        session.add(j)
    await session.flush()
    j_vt_id = next(j.id for j in journaux if j.code == "VT")
    j_ca_id = next(j.id for j in journaux if j.code == "CA")

    periodes_compta = []
    for an in range(ANNEE_DEBUT, ANNEE_FIN + 1):
        p = PeriodeComptable(entreprise_id=ent_id, date_debut=date(an, 1, 1), date_fin=date(an, 12, 31), libelle="Exercice {}".format(an), cloturee=(an < ANNEE_FIN))
        session.add(p)
        periodes_compta.append(p)
    await session.flush()
    periode_compta = periodes_compta[0]

    ecriture = EcritureComptable(entreprise_id=ent_id, journal_id=j_ca_id, periode_id=periode_compta.id, date_ecriture=DATE_DEBUT + timedelta(days=28), numero_piece="ENC-001", libelle="Encaissement client", created_by_id=user_admin.id)
    session.add(ecriture)
    await session.flush()
    session.add(LigneEcriture(ecriture_id=ecriture.id, compte_id=cpt_53, libelle_ligne="Caisse", debit=Decimal("10000"), credit=Decimal("0")))
    session.add(LigneEcriture(ecriture_id=ecriture.id, compte_id=cpt_411, libelle_ligne="Client", debit=Decimal("0"), credit=Decimal("10000")))
    n_ecr = min(400, len(facture_list)) if SEED_MODE == "LIGHT" else min(3000, len(facture_list))
    for idx, fac in enumerate(facture_list[:n_ecr]):
        per = periodes_compta[(fac.date_facture.year - ANNEE_DEBUT) % len(periodes_compta)]
        e = EcritureComptable(entreprise_id=ent_id, journal_id=j_vt_id, periode_id=per.id, date_ecriture=fac.date_facture, numero_piece=fac.numero, libelle="Vente " + fac.numero, created_by_id=user_admin.id)
        session.add(e)
        await session.flush()
        session.add(LigneEcriture(ecriture_id=e.id, compte_id=cpt_411, libelle_ligne="Client", debit=fac.montant_ttc, credit=Decimal("0")))
        session.add(LigneEcriture(ecriture_id=e.id, compte_id=next(c.id for c in comptes if c.numero == "711"), libelle_ligne="Ventes", debit=Decimal("0"), credit=fac.montant_ttc))
        if n_ecr > 500 and (idx + 1) % BATCH_FLUSH == 0:
            await session.flush()
    await session.flush()

    # ----- 14. RH : départements, postes, employés, congés, objectifs, commissions, avances -----
    dept_com = Departement(entreprise_id=ent_id, code="COM", libelle="Commercial", actif=True)
    dept_compta = Departement(entreprise_id=ent_id, code="COMPTA", libelle="Comptabilité", actif=True)
    dept_rh = Departement(entreprise_id=ent_id, code="RH", libelle="Ressources humaines", actif=True)
    for d in (dept_com, dept_compta, dept_rh):
        session.add(d)
    await session.flush()
    poste_com = Poste(entreprise_id=ent_id, departement_id=dept_com.id, code="COMM", libelle="Commercial", actif=True)
    poste_compta = Poste(entreprise_id=ent_id, departement_id=dept_compta.id, code="COMPTA", libelle="Comptable", actif=True)
    poste_rh = Poste(entreprise_id=ent_id, departement_id=dept_rh.id, code="RESP-RH", libelle="Responsable RH", actif=True)
    for p in (poste_com, poste_compta, poste_rh):
        session.add(p)
    await session.flush()
    type_cdi = TypeContrat(entreprise_id=ent_id, code="CDI", libelle="CDI", actif=True)
    type_cdd = TypeContrat(entreprise_id=ent_id, code="CDD", libelle="CDD", actif=True)
    session.add(type_cdi)
    session.add(type_cdd)
    await session.flush()

    employes = []
    emp1 = Employe(entreprise_id=ent_id, utilisateur_id=user_admin.id, departement_id=dept_compta.id, poste_id=poste_compta.id, type_contrat_id=type_cdi.id, matricule="EMP001", nom=FAKER.last_name(), prenom=FAKER.first_name(), date_naissance=FAKER.date_of_birth(minimum_age=25, maximum_age=55), lieu_naissance="Douala", genre="M", nationalite="Camerounaise", niu=_niu_cameroun(), numero_cnps="CNPS123456", email="jean@bazard-bonaberi.cm", telephone=_phone_cmr(), adresse="Bonabéri, Douala", date_embauche=date(ANNEE_DEBUT, 3, 1), salaire_base=Decimal("280000"), devise_id=xaf_id, actif=True)
    session.add(emp1)
    employes.append(emp1)
    await session.flush()
    for i in range(2, N_EMPLOYES + 1):
        dept = random.choice([dept_com, dept_compta, dept_rh])
        poste = poste_com if dept == dept_com else (poste_compta if dept == dept_compta else poste_rh)
        emp = Employe(entreprise_id=ent_id, utilisateur_id=None, departement_id=dept.id, poste_id=poste.id, type_contrat_id=type_cdi.id if random.random() > 0.2 else type_cdd.id, matricule="EMP{:05d}".format(i), nom=FAKER.last_name(), prenom=FAKER.first_name(), date_naissance=FAKER.date_of_birth(minimum_age=22, maximum_age=50), lieu_naissance=random.choice(VILLES_REGIONS_CMR)[0], genre="F" if i % 3 == 0 else "M", nationalite="Camerounaise", niu=_niu_cameroun(), numero_cnps="CNPS{:06d}".format(100000 + i), email="emp{}@bazard-bonaberi.cm".format(i), telephone=_phone_cmr(), adresse=FAKER.address()[:200], date_embauche=_date_alea(DATE_DEBUT, DATE_FIN - timedelta(days=365)), salaire_base=Decimal(str(random.randint(120000, 380000))), devise_id=xaf_id, actif=True)
        session.add(emp)
        employes.append(emp)
    await session.flush()

    type_conge_annuel = TypeConge(entreprise_id=ent_id, code="ANN", libelle="Congé annuel", paye=True, actif=True)
    type_conge_maladie = TypeConge(entreprise_id=ent_id, code="MAL", libelle="Congé maladie", paye=True, actif=True)
    session.add(type_conge_annuel)
    session.add(type_conge_maladie)
    await session.flush()
    for emp in employes[: min(18, len(employes))]:
        an = random.randint(ANNEE_DEBUT, ANNEE_FIN)
        session.add(DemandeConge(entreprise_id=ent_id, employe_id=emp.id, type_conge_id=type_conge_annuel.id, date_debut=date(an, random.randint(6, 8), 1), date_fin=date(an, random.randint(6, 8), 14), nombre_jours=10, statut=random.choice(["approuve", "approuve", "refuse"]), created_by_id=user_admin.id))
        session.add(SoldeConge(entreprise_id=ent_id, employe_id=emp.id, type_conge_id=type_conge_annuel.id, annee=an, droits_acquis=22, jours_pris=random.randint(0, 15)))
    for emp in employes[1: min(14, len(employes))]:
        an = random.randint(ANNEE_DEBUT, ANNEE_FIN)
        session.add(Objectif(entreprise_id=ent_id, employe_id=emp.id, libelle="CA trimestre", date_debut=date(an, 1, 1), date_fin=date(an, 3, 31), montant_cible=Decimal(str(random.randint(5000000, 20000000))), atteint=random.random() > 0.6))
    taux_comm = TauxCommission(entreprise_id=ent_id, code="VENTE", libelle="Commission vente", taux_pct=Decimal("5"), actif=True)
    session.add(taux_comm)
    await session.flush()
    for emp in employes[1: min(18, len(employes))]:
        for an in range(ANNEE_DEBUT, ANNEE_FIN + 1):
            for mois in range(1, 13):
                session.add(Commission(entreprise_id=ent_id, employe_id=emp.id, taux_commission_id=taux_comm.id, date_debut=date(an, mois, 1), date_fin=date(an, mois, 28), montant=Decimal(str(random.randint(5000, 45000))), libelle="Commission {}/{}".format(mois, an), payee=random.random() > 0.3))
    for emp in employes[2: min(22, len(employes))]:
        session.add(Avance(entreprise_id=ent_id, employe_id=emp.id, date_avance=_date_alea(DATE_DEBUT, DATE_FIN), montant=Decimal(str(random.randint(20000, 120000))), motif="Avance traitement", rembourse=random.random() > 0.5, created_by_id=user_admin.id))
    await session.flush()

    # ----- 15. Paie : périodes, types élément, bulletins -----
    periodes_paie_list = []
    for an in range(ANNEE_DEBUT, ANNEE_FIN + 1):
        for mois in range(1, 13):
            d_debut = date(an, mois, 1)
            d_fin = date(an, 12, 31) if mois == 12 else date(an, mois + 1, 1) - timedelta(days=1)
            pp = PeriodePaie(entreprise_id=ent_id, annee=an, mois=mois, date_debut=d_debut, date_fin=d_fin, cloturee=True)
            session.add(pp)
            periodes_paie_list.append(pp)
    await session.flush()
    type_salaire = TypeElementPaie(entreprise_id=ent_id, code="SAL_BASE", libelle="Salaire de base", type="gain", ordre_affichage=1, actif=True)
    type_cnps_sal = TypeElementPaie(entreprise_id=ent_id, code="CNPS_SAL", libelle="CNPS salarié 2,8%", type="retenue", ordre_affichage=10, actif=True)
    type_cnps_pat = TypeElementPaie(entreprise_id=ent_id, code="CNPS_PAT", libelle="CNPS patronal 4,2%", type="gain", ordre_affichage=2, actif=True)
    type_ir = TypeElementPaie(entreprise_id=ent_id, code="IR", libelle="Impôt sur le revenu", type="retenue", ordre_affichage=11, actif=True)
    for t in (type_salaire, type_cnps_pat, type_cnps_sal, type_ir):
        session.add(t)
    await session.flush()

    for emp in employes:
        salaire = emp.salaire_base
        for pp in periodes_paie_list:
            cnps_pat = (salaire * Decimal("0.042")).quantize(Decimal("0.01"))
            cnps_sal = (salaire * Decimal("0.028")).quantize(Decimal("0.01"))
            ir = (salaire * Decimal("0.05")).quantize(Decimal("0.01"))
            total_gains = salaire + cnps_pat
            total_retenues = cnps_sal + ir
            net = total_gains - total_retenues
            bull = BulletinPaie(entreprise_id=ent_id, employe_id=emp.id, periode_paie_id=pp.id, salaire_brut=salaire, total_gains=total_gains, total_retenues=total_retenues, net_a_payer=net, statut=random.choice(["valide", "valide", "paye"]), date_paiement=date(pp.annee, pp.mois, min(5, 28)))
            session.add(bull)
            await session.flush()
            session.add(LigneBulletinPaie(bulletin_paie_id=bull.id, type_element_paie_id=type_salaire.id, libelle="Salaire de base", type="gain", montant=salaire, ordre=1))
            session.add(LigneBulletinPaie(bulletin_paie_id=bull.id, type_element_paie_id=type_cnps_pat.id, libelle="CNPS patronal", type="gain", montant=cnps_pat, ordre=2))
            session.add(LigneBulletinPaie(bulletin_paie_id=bull.id, type_element_paie_id=type_cnps_sal.id, libelle="CNPS salarié", type="retenue", montant=cnps_sal, ordre=10))
            session.add(LigneBulletinPaie(bulletin_paie_id=bull.id, type_element_paie_id=type_ir.id, libelle="IR", type="retenue", montant=ir, ordre=11))
    await session.flush()

    # ----- 16. Immobilisations -----
    cat_info = CategorieImmobilisation(entreprise_id=ent_id, code="INFO", libelle="Matériel informatique", duree_amortissement_annees=3, taux_amortissement=Decimal("33.33"))
    cat_vehic = CategorieImmobilisation(entreprise_id=ent_id, code="VEH", libelle="Véhicules", duree_amortissement_annees=5, taux_amortissement=Decimal("20"))
    session.add(cat_info)
    session.add(cat_vehic)
    await session.flush()
    for i in range(1, 12):
        an_acq = random.randint(ANNEE_DEBUT, ANNEE_FIN - 1)
        cat = cat_info if i % 3 != 0 else cat_vehic
        val = Decimal(str(random.randint(300000, 6000000)))
        duree = 3 if cat == cat_info else 5
        immo = Immobilisation(entreprise_id=ent_id, categorie_id=cat.id, compte_comptable_id=cpt_2250, compte_amortissement_id=cpt_2820, code="IMMO-{:05d}".format(i), designation="Matériel informatique" if cat == cat_info else "Véhicule livraison", date_acquisition=date(an_acq, random.randint(1, 12), 1), valeur_acquisition=val, duree_amortissement_annees=duree, date_mise_en_service=date(an_acq, random.randint(1, 12), 15), notes="Siège", actif=True)
        session.add(immo)
        await session.flush()
        dot = (val / (duree * 12)).quantize(Decimal("0.01"))
        session.add(LigneAmortissement(immobilisation_id=immo.id, annee=an_acq, mois=12, montant_dotation=dot, cumul_amortissement=dot, valeur_nette=val - dot))
    await session.flush()

    # ----- 17. Système -----
    session.add(ParametreSysteme(entreprise_id=ent_id, categorie="general", cle="langue", valeur="fr", description="Langue interface"))
    session.add(ParametreSysteme(entreprise_id=ent_id, categorie="general", cle="devise_affichage", valeur="XAF", description="Devise affichage"))
    session.add(ParametreSysteme(entreprise_id=ent_id, categorie="compta", cle="plan_comptable", valeur="OHADA", description="Plan comptable CEMAC"))
    session.add(JournalAudit(entreprise_id=ent_id, utilisateur_id=user_admin.id, action="login", module="auth", entite_type="utilisateur", entite_id=user_admin.id, ip_address="127.0.0.1"))
    session.add(Notification(utilisateur_id=user_admin.id, titre="Bienvenue", message="Seed Bazard Bonabéri chargé.", lue=False))
    session.add(LicenceLogicielle(entreprise_id=ent_id, cle_licence="GESCO-XXXXX-XXXXX-XXXXX-XXXXX", type_licence="standard", date_debut=DATE_DEBUT, date_fin=DATE_FIN, actif=True, nombre_prolongations=0))
    for i in range(200):
        session.add(JournalAudit(entreprise_id=ent_id, utilisateur_id=user_admin.id, action=random.choice(["login", "read", "create", "update"]), module=random.choice(["commercial", "catalogue", "parametrage"]), entite_type="document", entite_id=random.randint(1, 500), ip_address="192.168.1.{}".format(random.randint(1, 254))))
    for u_id in [user_admin.id, user_compta.id]:
        for i in range(50):
            session.add(Notification(utilisateur_id=u_id, titre="Notification {}".format(i), message="Message test.", lue=random.random() > 0.5))
    await session.flush()

    await session.commit()
    total_approx = (
        N_CLIENTS + N_FOURNISSEURS + N_PRODUITS + len(devis_list) + len(commande_list) + len(facture_list) + len(bl_list)
        + len(cf_list) + len(recept_list) + len(fact_fou_list) + len(produits) + N_EMPLOYES * (1 + len(periodes_paie_list) * 5)
    )
    print("Seed termine : Bazard du Marche Bonaberi | Periode {} -> {} ({} ans) | Mode {} | ~{} enregistrements".format(DATE_DEBUT, DATE_FIN, N_ANNEES, SEED_MODE, total_approx))
    print("Comptes : admin / gesco@1234  |  compta / gesco@1234")


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    async with session_factory() as session:
        try:
            await run_seed(session)
        except Exception as e:
            await session.rollback()
            print("Erreur seed:", e)
            raise
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
