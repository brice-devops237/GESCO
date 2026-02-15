# scripts/seed_data.py
# -----------------------------------------------------------------------------
# Seed cohérent pour toutes les tables Gesco. Données Cameroun (XAF, NIU, DGI,
# Douala/Yaoundé, Mobile Money, régime fiscal CGI). Exécuter après migrations :
#   python -m scripts.seed_data
# Nécessite .env avec DATABASE_URL (async), DATABASE_URL_SYNC, SECRET_KEY.
#
# Tables seedées (62 au total, tous modules sauf auth qui n'a pas de table) :
#   Paramétrage (9)   : devises, taux_change, entreprises, points_de_vente,
#                      roles, permissions, permissions_roles, utilisateurs,
#                      affectations_utilisateur_pdv
#   Catalogue (9)     : unites_mesure, taux_tva, familles_produits,
#                      conditionnements, produits, produits_conditionnements,
#                      canaux_vente, prix_produits, variantes_produits
#   Partenaires (3)  : types_tiers, tiers, contacts
#   Commercial (5)    : etats_document, devis, commandes, factures, bons_livraison
#   Achats (4)       : depots, commandes_fournisseurs, receptions,
#                      factures_fournisseurs
#   Stock (2)        : stocks, mouvements_stock
#   Trésorerie (3)   : modes_paiement, comptes_tresorerie, reglements
#   Comptabilité (5) : comptes_comptables, journaux_comptables,
#                      periodes_comptables, ecritures_comptables, lignes_ecritures
#   RH (11)          : departements, postes, types_contrat, employes,
#                      types_conge, demandes_conge, soldes_conge, objectifs,
#                      taux_commissions, commissions, avances
#   Paie (4)         : periodes_paie, types_element_paie, bulletins_paie,
#                      lignes_bulletin_paie
#   Immobilisations (3): categories_immobilisation, immobilisations,
#                        lignes_amortissement
#   Système (4)      : parametres_systeme, journaux_audit, notifications,
#                      licences_logicielles
# -----------------------------------------------------------------------------

from __future__ import annotations

import asyncio
import os
import sys
from datetime import date
from decimal import Decimal

# Charger .env avant app
if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# Racine projet = répertoire parent de scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Import de tous les modèles pour enregistrement métadonnées
from app.config import get_settings
from app.core.security import hash_password

# Paramétrage
from app.modules.parametrage.models import (
    Devise,
    TauxChange,
    Entreprise,
    PointDeVente,
    Role,
    Permission,
    PermissionRole,
    Utilisateur,
    AffectationUtilisateurPdv,
)
# Catalogue
from app.modules.catalogue.models import (
    UniteMesure,
    TauxTva,
    FamilleProduit,
    Conditionnement,
    Produit,
    ProduitConditionnement,
    CanalVente,
    PrixProduit,
    VarianteProduit,
)
# Partenaires
from app.modules.partenaires.models import TypeTiers, Tiers, Contact
# Commercial
from app.modules.commercial.models import EtatDocument, Devis, Commande, Facture, BonLivraison
# Achats
from app.modules.achats.models import Depot, CommandeFournisseur, Reception, FactureFournisseur
# Stock
from app.modules.stock.models import Stock, MouvementStock
# Trésorerie
from app.modules.tresorerie.models import ModePaiement, CompteTresorerie, Reglement
# Comptabilité
from app.modules.comptabilite.models import (
    CompteComptable,
    JournalComptable,
    PeriodeComptable,
    EcritureComptable,
    LigneEcriture,
)
# RH
from app.modules.rh.models import (
    Departement,
    Poste,
    TypeContrat,
    Employe,
    TypeConge,
    DemandeConge,
    SoldeConge,
    Objectif,
    TauxCommission,
    Commission,
    Avance,
)
# Paie
from app.modules.paie.models import PeriodePaie, TypeElementPaie, BulletinPaie, LigneBulletinPaie
# Immobilisations
from app.modules.immobilisations.models import CategorieImmobilisation, Immobilisation, LigneAmortissement
# Système
from app.modules.systeme.models import ParametreSysteme, JournalAudit, Notification, LicenceLogicielle


async def run_seed(session: AsyncSession) -> None:
    """Insère les données dans l'ordre des dépendances (FK)."""

    # ----- 1. Référentiels globaux (sans FK entreprise) -----
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
        UniteMesure(code="M", libelle="Mètre", symbole="m", type="longueur", actif=True),
    ]
    for u in unites:
        session.add(u)
    await session.flush()

    taux_tva = [
        TauxTva(code="TVA0", taux=Decimal("0"), libelle="Taux 0% (exonéré)", actif=True),
        TauxTva(code="TVA19", taux=Decimal("19.25"), libelle="TVA 19,25% (CGI Cameroun)", actif=True),
    ]
    for t in taux_tva:
        session.add(t)
    await session.flush()

    # Taux de change (XAF référence)
    xaf_id = next(d.id for d in devises if d.code == "XAF")
    eur_id = next(d.id for d in devises if d.code == "EUR")
    session.add(TauxChange(devise_from_id=eur_id, devise_to_id=xaf_id, taux=655.957, date_effet=date(2025, 1, 1)))
    await session.flush()

    # ----- 2. Entreprise (Cameroun) -----
    ent = Entreprise(
        code="GESCO-CM",
        raison_sociale="Gesco Cameroun SA",
        sigle="GESCO",
        niu="M123456789A",
        regime_fiscal="reel_simplifie",
        mode_gestion="standard",
        adresse="Boulevard de la Liberté, Akwa",
        ville="Douala",
        region="Littoral",
        pays="CMR",
        telephone="+237 233 40 00 00",
        email="contact@gesco-cm.com",
        site_web="https://www.gesco-cm.com",
        devise_principale="XAF",
        actif=True,
    )
    session.add(ent)
    await session.flush()
    ent_id = ent.id

    # ----- 3. Points de vente -----
    pdv_principal = PointDeVente(
        entreprise_id=ent_id,
        code="PDV-DLA-01",
        libelle="Siège Douala - Vente",
        type="principal",
        adresse="Bd de la Liberté, Akwa",
        ville="Douala",
        telephone="+237 233 40 00 01",
        est_depot=False,
        actif=True,
    )
    pdv_depot = PointDeVente(
        entreprise_id=ent_id,
        code="DEP-DLA-01",
        libelle="Entrepôt Bonabéri",
        type="depot",
        ville="Douala",
        telephone="+237 233 41 00 00",
        est_depot=True,
        actif=True,
    )
    session.add(pdv_principal)
    session.add(pdv_depot)
    await session.flush()
    pdv_principal_id = pdv_principal.id
    pdv_depot_id = pdv_depot.id

    # ----- 4. Rôles et permissions -----
    perms_data = [
        ("parametrage", "read", "Paramétrage - Lecture"),
        ("parametrage", "write", "Paramétrage - Écriture"),
        ("catalogue", "read", "Catalogue - Lecture"),
        ("catalogue", "write", "Catalogue - Écriture"),
        ("commercial", "read", "Commercial - Lecture"),
        ("commercial", "write", "Commercial - Écriture"),
        ("achats", "read", "Achats - Lecture"),
        ("achats", "write", "Achats - Écriture"),
        ("comptabilite", "read", "Comptabilité - Lecture"),
        ("comptabilite", "write", "Comptabilité - Écriture"),
        ("rh", "read", "RH - Lecture"),
        ("rh", "write", "RH - Écriture"),
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
    session.add(role_admin)
    session.add(role_compta)
    session.add(role_commercial)
    await session.flush()

    for p in permissions:
        session.add(PermissionRole(role_id=role_admin.id, permission_id=p.id))
    for p in permissions:
        if p.module in ("comptabilite", "parametrage") and p.action == "read":
            session.add(PermissionRole(role_id=role_compta.id, permission_id=p.id))
    await session.flush()

    # ----- 5. Utilisateurs -----
    pwd_hash = hash_password("Gesco2025!")
    user_admin = Utilisateur(
        entreprise_id=ent_id,
        point_de_vente_id=pdv_principal_id,
        role_id=role_admin.id,
        login="admin",
        mot_de_passe_hash=pwd_hash,
        email="admin@gesco-cm.com",
        nom="Fotso",
        prenom="Jean",
        telephone="+237 6 90 00 00 01",
        actif=True,
    )
    user_compta = Utilisateur(
        entreprise_id=ent_id,
        point_de_vente_id=pdv_principal_id,
        role_id=role_compta.id,
        login="compta",
        mot_de_passe_hash=pwd_hash,
        email="compta@gesco-cm.com",
        nom="Mbarga",
        prenom="Marie",
        actif=True,
    )
    session.add(user_admin)
    session.add(user_compta)
    await session.flush()

    session.add(AffectationUtilisateurPdv(utilisateur_id=user_admin.id, point_de_vente_id=pdv_principal_id, est_principal=True))
    session.add(AffectationUtilisateurPdv(utilisateur_id=user_compta.id, point_de_vente_id=pdv_principal_id, est_principal=True))
    await session.flush()

    # ----- 6. Catalogue : familles, conditionnements, canaux -----
    fam_alim = FamilleProduit(entreprise_id=ent_id, parent_id=None, code="ALIM", libelle="Alimentaire", niveau=1, ordre_affichage=1, actif=True)
    fam_boisson = FamilleProduit(entreprise_id=ent_id, parent_id=None, code="BOIS", libelle="Boissons", niveau=1, ordre_affichage=2, actif=True)
    session.add(fam_alim)
    session.add(fam_boisson)
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

    # Produits (unite_vente = PCE, taux_tva 19.25%)
    tva19_id = next(t.id for t in taux_tva if t.code == "TVA19")
    produits = [
        Produit(
            entreprise_id=ent_id,
            famille_id=fam_alim.id,
            code="RIZ-1KG",
            code_barre="6131234567890",
            libelle="Riz parfumé 1 kg",
            type="produit",
            unite_vente_id=unites[1].id,
            unite_achat_id=unites[1].id,
            coefficient_achat_vente=Decimal("1"),
            prix_achat_ht=Decimal("450"),
            prix_vente_ttc=Decimal("650"),
            taux_tva_id=tva19_id,
            seuil_alerte_min=Decimal("10"),
            gerer_stock=True,
            actif=True,
        ),
        Produit(
            entreprise_id=ent_id,
            famille_id=fam_boisson.id,
            code="EAU-1.5L",
            libelle="Eau minérale 1,5 L",
            type="produit",
            unite_vente_id=unites[2].id,
            unite_achat_id=unites[2].id,
            coefficient_achat_vente=Decimal("1"),
            prix_achat_ht=Decimal("150"),
            prix_vente_ttc=Decimal("250"),
            taux_tva_id=tva19_id,
            seuil_alerte_min=Decimal("20"),
            gerer_stock=True,
            actif=True,
        ),
        Produit(
            entreprise_id=ent_id,
            famille_id=fam_boisson.id,
            code="JUS-ORANGE",
            libelle="Jus d'orange 1 L",
            type="produit",
            unite_vente_id=unites[2].id,
            prix_achat_ht=Decimal("400"),
            prix_vente_ttc=Decimal("650"),
            taux_tva_id=tva19_id,
            gerer_stock=True,
            actif=True,
        ),
    ]
    for pr in produits:
        session.add(pr)
    await session.flush()

    session.add(ProduitConditionnement(produit_id=produits[1].id, conditionnement_id=cond_caisse.id, quantite_unites=Decimal("12"), prix_vente_ttc=Decimal("2800")))
    await session.flush()

    date_debut_prix = date(2025, 1, 1)
    for pr in produits:
        session.add(PrixProduit(produit_id=pr.id, canal_vente_id=canal_det.id, prix_ttc=pr.prix_vente_ttc, date_debut=date_debut_prix))
    await session.flush()

    var_1 = VarianteProduit(produit_id=produits[2].id, code="JUS-OR-NAT", libelle="Nature", prix_ttc_supplement=Decimal("0"), stock_separe=False, actif=True)
    session.add(var_1)
    await session.flush()

    # ----- 7. Partenaires : types, tiers (clients/fournisseurs), contacts -----
    type_client = TypeTiers(code="CLI", libelle="Client")
    type_fourn = TypeTiers(code="FOU", libelle="Fournisseur")
    session.add(type_client)
    session.add(type_fourn)
    await session.flush()

    clients = [
        Tiers(
            entreprise_id=ent_id,
            type_tiers_id=type_client.id,
            code="CLI-001",
            raison_sociale="Super Marché Bonanjo",
            niu="M987654321B",
            adresse="Avenue Général de Gaulle",
            ville="Douala",
            region="Littoral",
            pays="CMR",
            telephone="+237 233 42 00 00",
            email="contact@bonanjo.cm",
            canal_vente_id=canal_gros.id,
            limite_credit=Decimal("5000000"),
            delai_paiement_jours=30,
            mobile_money_numero="670000001",
            mobile_money_operateur="MTN",
            actif=True,
        ),
        Tiers(
            entreprise_id=ent_id,
            type_tiers_id=type_client.id,
            code="CLI-002",
            raison_sociale="Boutique Essos",
            ville="Yaoundé",
            region="Centre",
            pays="CMR",
            telephone="+237 222 21 00 00",
            mobile_money_operateur="Orange",
            actif=True,
        ),
    ]
    fournisseurs = [
        Tiers(
            entreprise_id=ent_id,
            type_tiers_id=type_fourn.id,
            code="FOU-001",
            raison_sociale="SIC Céréales Cameroun",
            niu="M111222333C",
            ville="Douala",
            region="Littoral",
            pays="CMR",
            telephone="+237 233 43 00 00",
            delai_paiement_jours=45,
            actif=True,
        ),
    ]
    for t in clients + fournisseurs:
        session.add(t)
    await session.flush()
    client1_id = clients[0].id
    client2_id = clients[1].id
    fourn1_id = fournisseurs[0].id

    session.add(Contact(tiers_id=client1_id, nom="Mbida", prenom="Paul", fonction="Acheteur", telephone="+237 6 70 00 00 02", est_principal=True, actif=True))
    session.add(Contact(tiers_id=fourn1_id, nom="Nkoulou", prenom="André", fonction="Commercial", telephone="+237 6 99 00 00 03", est_principal=True, actif=True))
    await session.flush()

    # ----- 8. États document (devis, commande, facture, bl) -----
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

    # ----- 9. Commercial : devis, commande, facture, BL -----
    devis = Devis(
        entreprise_id=ent_id,
        point_de_vente_id=pdv_principal_id,
        client_id=client1_id,
        numero="DEV-2025-001",
        date_devis=date(2025, 1, 15),
        date_validite=date(2025, 2, 15),
        etat_id=etat_devis_valide,
        montant_ht=Decimal("15000"),
        montant_tva=Decimal("2887.50"),
        montant_ttc=Decimal("17887.50"),
        devise_id=xaf_id,
        taux_change=Decimal("1"),
    )
    session.add(devis)
    await session.flush()

    commande = Commande(
        entreprise_id=ent_id,
        point_de_vente_id=pdv_principal_id,
        client_id=client1_id,
        devis_id=devis.id,
        numero="CDE-2025-001",
        date_commande=date(2025, 1, 18),
        date_livraison_prevue=date(2025, 1, 25),
        etat_id=etat_cde_valide,
        montant_ht=Decimal("15000"),
        montant_tva=Decimal("2887.50"),
        montant_ttc=Decimal("17887.50"),
        devise_id=xaf_id,
        adresse_livraison="Avenue Général de Gaulle, Douala",
    )
    session.add(commande)
    await session.flush()

    facture = Facture(
        entreprise_id=ent_id,
        point_de_vente_id=pdv_principal_id,
        client_id=client1_id,
        commande_id=commande.id,
        numero="FAC-2025-001",
        date_facture=date(2025, 1, 22),
        date_echeance=date(2025, 2, 22),
        etat_id=etat_fact_valide,
        type_facture="facture",
        montant_ht=Decimal("15000"),
        montant_tva=Decimal("2887.50"),
        montant_ttc=Decimal("17887.50"),
        montant_restant_du=Decimal("17887.50"),
        devise_id=xaf_id,
    )
    session.add(facture)
    await session.flush()

    bl = BonLivraison(
        entreprise_id=ent_id,
        point_de_vente_id=pdv_principal_id,
        client_id=client1_id,
        commande_id=commande.id,
        facture_id=facture.id,
        numero="BL-2025-001",
        date_livraison=date(2025, 1, 23),
        adresse_livraison="Avenue Général de Gaulle, Douala",
        etat_id=etat_bl_valide,
    )
    session.add(bl)
    await session.flush()

    # ----- 10. Achats : dépôt, commande fournisseur, réception, facture fournisseur -----
    depot = Depot(entreprise_id=ent_id, code="DEP-DLA", libelle="Entrepôt Douala", point_de_vente_id=pdv_depot_id)
    session.add(depot)
    await session.flush()

    etat_cde_fou = next(e.id for e in etats if e.type_document == "commande" and e.code == "VALIDE")
    cde_fou = CommandeFournisseur(
        entreprise_id=ent_id,
        fournisseur_id=fourn1_id,
        depot_id=depot.id,
        numero="CF-2025-001",
        numero_fournisseur="CF-SIC-001",
        date_commande=date(2025, 1, 10),
        date_livraison_prevue=date(2025, 1, 20),
        etat_id=etat_cde_fou,
        montant_ht=Decimal("80000"),
        montant_tva=Decimal("15400"),
        montant_ttc=Decimal("95400"),
        devise_id=xaf_id,
    )
    session.add(cde_fou)
    await session.flush()

    recept = Reception(
        commande_fournisseur_id=cde_fou.id,
        depot_id=depot.id,
        numero="REC-2025-001",
        date_reception=date(2025, 1, 19),
        etat="validee",
    )
    session.add(recept)
    await session.flush()

    fact_fou = FactureFournisseur(
        entreprise_id=ent_id,
        fournisseur_id=fourn1_id,
        commande_fournisseur_id=cde_fou.id,
        numero_fournisseur="FAC-SIC-2025-001",
        date_facture=date(2025, 1, 25),
        date_echeance=date(2025, 3, 10),
        montant_ht=Decimal("80000"),
        montant_tva=Decimal("15400"),
        montant_ttc=Decimal("95400"),
        montant_restant_du=Decimal("95400"),
        devise_id=xaf_id,
        statut_paiement="non_paye",
    )
    session.add(fact_fou)
    await session.flush()

    # ----- 11. Stock et mouvements -----
    for pr in produits:
        session.add(Stock(depot_id=depot.id, produit_id=pr.id, variante_id=None, quantite=Decimal("100"), unite_id=pr.unite_vente_id))
    await session.flush()

    session.add(
        MouvementStock(
            type_mouvement="entree",
            depot_id=depot.id,
            produit_id=produits[0].id,
            variante_id=None,
            quantite=Decimal("50"),
            reference_type="reception",
            reference_id=recept.id,
            notes="Réception CF-2025-001",
            created_by_id=user_admin.id,
        )
    )
    await session.flush()

    # ----- 12. Trésorerie : modes de paiement, comptes, règlement -----
    mode_esp = ModePaiement(entreprise_id=ent_id, code="ESP", libelle="Espèces", actif=True)
    mode_momo = ModePaiement(entreprise_id=ent_id, code="MOMO", libelle="Mobile Money (MTN/Orange)", actif=True)
    mode_vir = ModePaiement(entreprise_id=ent_id, code="VIR", libelle="Virement bancaire", actif=True)
    mode_cheque = ModePaiement(entreprise_id=ent_id, code="CHQ", libelle="Chèque", actif=True)
    for m in (mode_esp, mode_momo, mode_vir, mode_cheque):
        session.add(m)
    await session.flush()

    cpte_caisse = CompteTresorerie(entreprise_id=ent_id, type_compte="caisse", libelle="Caisse principale XAF", devise_id=xaf_id, actif=True)
    cpte_banque = CompteTresorerie(entreprise_id=ent_id, type_compte="bancaire", libelle="Compte BICEC", devise_id=xaf_id, actif=True)
    session.add(cpte_caisse)
    session.add(cpte_banque)
    await session.flush()

    regl = Reglement(
        entreprise_id=ent_id,
        type_reglement="client",
        facture_id=facture.id,
        tiers_id=client1_id,
        montant=Decimal("10000"),
        date_reglement=date(2025, 1, 28),
        mode_paiement_id=mode_momo.id,
        compte_tresorerie_id=cpte_caisse.id,
        reference="MTN 670000001",
        created_by_id=user_admin.id,
    )
    session.add(regl)
    await session.flush()

    # ----- 13. Comptabilité : plan comptable OHADA/CEMAC, journaux, période, écriture -----
    comptes = [
        CompteComptable(entreprise_id=ent_id, numero="411", libelle="Clients", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="401", libelle="Fournisseurs", sens_normal="credit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="512", libelle="Banque", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="53", libelle="Caisse", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="611", libelle="Achats stockés", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="711", libelle="Ventes marchandises", sens_normal="credit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="2250", libelle="Matériel informatique (OHADA)", sens_normal="debit", actif=True),
        CompteComptable(entreprise_id=ent_id, numero="2820", libelle="Amortissement matériel informatique", sens_normal="credit", actif=True),
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
    j_vt = next(j.id for j in journaux if j.code == "VT")
    j_ca = next(j.id for j in journaux if j.code == "CA")

    periode_compta = PeriodeComptable(
        entreprise_id=ent_id,
        date_debut=date(2025, 1, 1),
        date_fin=date(2025, 12, 31),
        libelle="Exercice 2025",
        cloturee=False,
    )
    session.add(periode_compta)
    await session.flush()

    ecriture = EcritureComptable(
        entreprise_id=ent_id,
        journal_id=j_ca,
        periode_id=periode_compta.id,
        date_ecriture=date(2025, 1, 28),
        numero_piece="ENC-001",
        libelle="Encaissement client Super Marché Bonanjo",
        created_by_id=user_admin.id,
    )
    session.add(ecriture)
    await session.flush()

    session.add(LigneEcriture(ecriture_id=ecriture.id, compte_id=cpt_53, libelle_ligne="Caisse", debit=Decimal("10000"), credit=Decimal("0")))
    session.add(LigneEcriture(ecriture_id=ecriture.id, compte_id=cpt_411, libelle_ligne="Client", debit=Decimal("0"), credit=Decimal("10000")))
    await session.flush()

    # ----- 14. RH : départements, postes, types contrat, employés, congés, objectifs, commissions, avances -----
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

    type_cdi = TypeContrat(entreprise_id=ent_id, code="CDI", libelle="Contrat à durée indéterminée", actif=True)
    type_cdd = TypeContrat(entreprise_id=ent_id, code="CDD", libelle="Contrat à durée déterminée", actif=True)
    session.add(type_cdi)
    session.add(type_cdd)
    await session.flush()

    emp1 = Employe(
        entreprise_id=ent_id,
        utilisateur_id=user_admin.id,
        departement_id=dept_compta.id,
        poste_id=poste_compta.id,
        type_contrat_id=type_cdi.id,
        matricule="EMP001",
        nom="Fotso",
        prenom="Jean",
        date_naissance=date(1990, 5, 15),
        lieu_naissance="Douala",
        genre="M",
        nationalite="Camerounaise",
        niu="N123456789D",
        numero_cnps="CNPS123456",
        email="jean.fotso@gesco-cm.com",
        telephone="+237 6 90 00 00 01",
        adresse="Akwa, Douala",
        date_embauche=date(2022, 3, 1),
        salaire_base=Decimal("250000"),
        devise_id=xaf_id,
        actif=True,
    )
    emp2 = Employe(
        entreprise_id=ent_id,
        departement_id=dept_com.id,
        poste_id=poste_com.id,
        type_contrat_id=type_cdi.id,
        matricule="EMP002",
        nom="Ngo",
        prenom="Sandra",
        genre="F",
        nationalite="Camerounaise",
        date_embauche=date(2023, 6, 1),
        salaire_base=Decimal("180000"),
        devise_id=xaf_id,
        actif=True,
    )
    session.add(emp1)
    session.add(emp2)
    await session.flush()

    type_conge_annuel = TypeConge(entreprise_id=ent_id, code="ANN", libelle="Congé annuel", paye=True, actif=True)
    type_conge_maladie = TypeConge(entreprise_id=ent_id, code="MAL", libelle="Congé maladie", paye=True, actif=True)
    session.add(type_conge_annuel)
    session.add(type_conge_maladie)
    await session.flush()

    session.add(
        DemandeConge(
            entreprise_id=ent_id,
            employe_id=emp2.id,
            type_conge_id=type_conge_annuel.id,
            date_debut=date(2025, 7, 1),
            date_fin=date(2025, 7, 14),
            nombre_jours=10,
            statut="approuve",
            created_by_id=user_admin.id,
        )
    )
    session.add(SoldeConge(entreprise_id=ent_id, employe_id=emp2.id, type_conge_id=type_conge_annuel.id, annee=2025, droits_acquis=22, jours_pris=0))
    await session.flush()

    session.add(Objectif(entreprise_id=ent_id, employe_id=emp2.id, libelle="CA trimestre 1", date_debut=date(2025, 1, 1), date_fin=date(2025, 3, 31), montant_cible=Decimal("15000000"), atteint=False))
    await session.flush()

    taux_comm = TauxCommission(entreprise_id=ent_id, code="VENTE", libelle="Commission vente", taux_pct=Decimal("5"), actif=True)
    session.add(taux_comm)
    await session.flush()
    session.add(
        Commission(
            entreprise_id=ent_id,
            employe_id=emp2.id,
            taux_commission_id=taux_comm.id,
            date_debut=date(2025, 1, 1),
            date_fin=date(2025, 1, 31),
            montant=Decimal("7500"),
            libelle="Commission janvier 2025",
            payee=False,
        )
    )
    session.add(Avance(entreprise_id=ent_id, employe_id=emp2.id, date_avance=date(2025, 1, 15), montant=Decimal("50000"), motif="Frais médicaux", rembourse=False, created_by_id=user_admin.id))
    await session.flush()

    # ----- 15. Paie : période, types élément, bulletins, lignes -----
    periode_paie = PeriodePaie(
        entreprise_id=ent_id,
        annee=2025,
        mois=1,
        date_debut=date(2025, 1, 1),
        date_fin=date(2025, 1, 31),
        cloturee=False,
    )
    session.add(periode_paie)
    await session.flush()

    type_salaire = TypeElementPaie(entreprise_id=ent_id, code="SAL_BASE", libelle="Salaire de base", type="gain", ordre_affichage=1, actif=True)
    type_cnps_sal = TypeElementPaie(entreprise_id=ent_id, code="CNPS_SAL", libelle="CNPS salarié 2,8%", type="retenue", ordre_affichage=10, actif=True)
    type_cnps_pat = TypeElementPaie(entreprise_id=ent_id, code="CNPS_PAT", libelle="CNPS patronal 4,2%", type="gain", ordre_affichage=2, actif=True)
    type_ir = TypeElementPaie(entreprise_id=ent_id, code="IR", libelle="Impôt sur le revenu", type="retenue", ordre_affichage=11, actif=True)
    for t in (type_salaire, type_cnps_sal, type_cnps_pat, type_ir):
        session.add(t)
    await session.flush()

    bulletin_emp1 = BulletinPaie(
        entreprise_id=ent_id,
        employe_id=emp1.id,
        periode_paie_id=periode_paie.id,
        salaire_brut=Decimal("250000"),
        total_gains=Decimal("260500"),
        total_retenues=Decimal("19500"),
        net_a_payer=Decimal("241000"),
        statut="valide",
        date_paiement=date(2025, 2, 5),
    )
    session.add(bulletin_emp1)
    await session.flush()
    session.add(LigneBulletinPaie(bulletin_paie_id=bulletin_emp1.id, type_element_paie_id=type_salaire.id, libelle="Salaire de base", type="gain", montant=Decimal("250000"), ordre=1))
    session.add(LigneBulletinPaie(bulletin_paie_id=bulletin_emp1.id, type_element_paie_id=type_cnps_pat.id, libelle="CNPS patronal", type="gain", montant=Decimal("10500"), ordre=2))
    session.add(LigneBulletinPaie(bulletin_paie_id=bulletin_emp1.id, type_element_paie_id=type_cnps_sal.id, libelle="CNPS salarié", type="retenue", montant=Decimal("7000"), ordre=10))
    session.add(LigneBulletinPaie(bulletin_paie_id=bulletin_emp1.id, type_element_paie_id=type_ir.id, libelle="IR", type="retenue", montant=Decimal("12500"), ordre=11))
    await session.flush()

    # ----- 16. Immobilisations -----
    cat_info = CategorieImmobilisation(entreprise_id=ent_id, code="INFO", libelle="Matériel informatique", duree_amortissement_annees=3, taux_amortissement=Decimal("33.33"))
    cat_vehic = CategorieImmobilisation(entreprise_id=ent_id, code="VEH", libelle="Véhicules", duree_amortissement_annees=5, taux_amortissement=Decimal("20"))
    session.add(cat_info)
    session.add(cat_vehic)
    await session.flush()

    immo = Immobilisation(
        entreprise_id=ent_id,
        categorie_id=cat_info.id,
        compte_comptable_id=cpt_2250,
        compte_amortissement_id=cpt_2820,
        code="IMMO-PC-001",
        designation="Ordinateur portable Dell Latitude",
        date_acquisition=date(2024, 6, 1),
        valeur_acquisition=Decimal("450000"),
        duree_amortissement_annees=3,
        date_mise_en_service=date(2024, 6, 15),
        notes="Siège Douala",
        actif=True,
    )
    session.add(immo)
    await session.flush()
    session.add(
        LigneAmortissement(
            immobilisation_id=immo.id,
            annee=2024,
            mois=12,
            montant_dotation=Decimal("12500"),
            cumul_amortissement=Decimal("12500"),
            valeur_nette=Decimal("437500"),
        )
    )
    await session.flush()

    # ----- 17. Système : paramètres, audit, notification, licence -----
    session.add(ParametreSysteme(entreprise_id=ent_id, categorie="general", cle="langue", valeur="fr", description="Langue interface"))
    session.add(ParametreSysteme(entreprise_id=ent_id, categorie="general", cle="devise_affichage", valeur="XAF", description="Devise affichage"))
    session.add(ParametreSysteme(entreprise_id=ent_id, categorie="compta", cle="plan_comptable", valeur="OHADA", description="Plan comptable CEMAC"))
    await session.flush()

    session.add(
        JournalAudit(
            entreprise_id=ent_id,
            utilisateur_id=user_admin.id,
            action="login",
            module="auth",
            entite_type="utilisateur",
            entite_id=user_admin.id,
            ip_address="127.0.0.1",
        )
    )
    session.add(Notification(utilisateur_id=user_admin.id, titre="Bienvenue", message="Seed données Gesco chargées.", lue=False))
    await session.flush()

    session.add(
        LicenceLogicielle(
            entreprise_id=ent_id,
            cle_licence="GESCO-XXXXX-XXXXX-XXXXX-XXXXX",
            type_licence="standard",
            date_debut=date(2025, 1, 1),
            date_fin=date(2025, 12, 31),
            actif=True,
            nombre_prolongations=0,
        )
    )
    await session.commit()
    print("Seed terminé : toutes les tables ont été remplies (données cohérentes Cameroun).")


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    async with session_factory() as session:
        try:
            await run_seed(session)
        except Exception as e:
            await session.rollback()
            print(f"Erreur seed: {e}")
            raise
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
