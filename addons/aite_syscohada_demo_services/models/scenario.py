# -*- coding: utf-8 -*-
"""Paramètres du scénario de démonstration : une société de services informatiques de Douala, de janvier 2025 à
septembre 2026.

Ce fichier ne contient que des données. Le générateur (``generator.py``, sur le moteur commun
``aite_syscohada_demo_common``) les lit pour créer les pièces ; les tests (``tests/test_demo_services.py``)
recalculent à la main les montants attendus.

Tous les montants sont en FCFA (XAF, sans décimale). Les montants hors taxes soumis à la TVA de 19,25 % sont des
multiples de 400 : la TVA de chaque ligne tombe juste, sans arrondi.

ACTIVITÉ
    Infogérance (maintenance du parc et des serveurs) d'une banque, conseil en régie facturé au jour pour un
    industriel, projets de développement au forfait pour un assureur, formations, contrat de support annuel d'un
    opérateur télécom, revente de matériel informatique aux PME. Charges : salaires, loyer des bureaux, services
    d'informatique en nuage d'un éditeur étranger, sous-traitance d'un développeur indépendant, internet,
    électricité, frais bancaires. Investissements : ordinateurs et serveurs (2442), progiciel de gestion (2131).

RYTHME MENSUEL (chaque mois, de janvier 2025 à septembre 2026)
    1er   infogérance de la banque : TVA sur encaissement, acompte de 2 % retenu par la banque ; réglée le 25
    1er   loyer des bureaux, précompte de 15 % retenu ; réglé le 5
    5     services en nuage de l'éditeur étranger : TVA autoliquidée et TSR de 15 % ; réglés le 15
    10    matériel acheté au distributeur (75 % des ventes de matériel du mois) ; réglé le 10 du mois suivant
    12    électricité, réglée le 20 ; 14 : internet, réglé le 22
    15    paiement de la déclaration I/TVA-IR et des cotisations CNPS du mois précédent
    20    matériel revendu aux PME, réglé le dernier jour du mois
    dernier jour
          conseil en régie (jours × taux journalier), réglé le 20 du mois suivant ; frais bancaires ; paie et
          salaires nets ; dotations aux amortissements ; déclaration mensuelle calculée, liquidée et validée
          (celle de septembre 2026 reste en brouillon).
    Projets au forfait le 15 (février, mai, août, novembre 2025 ; février, mai, août 2026) : 4 000 000, retenue
    de 5 % sur honoraires par l'assureur, réglés le 15 du mois suivant. Formations le 25 (mars, juin, octobre
    2025 ; mars, juin 2026) : 1 200 000, réglées le jour même. Sous-traitance le 28 (avril, mai, septembre,
    octobre 2025 ; avril, mai, septembre 2026) : 1 200 000 sans TVA (prestataire non assujetti), retenue de 5 %
    sur honoraires, réglée le 10 du mois suivant.

OPÉRATIONS PONCTUELLES
    02/01/2025 apport en capital de 25 000 000 ; 15/01/2025 ordinateurs portables et serveur de développement
    (10 800 000, réglés le 31) ; 28/02 patente ; 10/03/2025 progiciel de gestion (7 200 000, réglé le 31) ;
    01/10/2025 contrat de support annuel d'octobre 2025 à septembre 2026 (6 000 000, réglé le 20 octobre) ;
    31/12/2025 stock de matériel de 1 800 000, produits constatés d'avance (9 mois de support restant à courir :
    4 500 000), impôt sur le résultat ; 01/01/2026 résultat 2025 en instance d'affectation, reprise du stock et
    des produits constatés d'avance ; 15/03/2026 impôt 2025 : acomptes imputés, solde payé ; 10/04/2026 serveurs
    de virtualisation (5 400 000, réglés le 30) ; 30/06/2026 affectation du résultat 2025 ; 20/07/2026
    dividendes, IRCM retenu (ligne L57 de juillet) ; 30/09/2026 stock de matériel de 2 100 000.

SIMPLIFICATIONS ASSUMÉES (démonstration, pas conseil fiscal)
    Paie globale illustrative ; impôt sur le résultat illustratif (27,5 % du résultat comptable, au minimum les
    acomptes et précomptes, sans passage au résultat fiscal) ; dotations dès le mois d'acquisition ; taxes de
    retenue « taux à valider » activées dans la seule société de démonstration ; retenue de 5 % sur le projet
    de l'assureur et sur le développeur indépendant à confirmer selon le statut de chaque prestataire.
"""
from datetime import date

# ------------------------------------------------------------------ période
START = (2025, 1)
END = (2026, 9)

# ------------------------------------------------------------------ société (coordonnées fictives)
COMPANY = {
    "name": "Services Informatiques Démo AITE",
    "street": "Rue Njo-Njo, Bonapriso",
    "city": "Douala",
    "phone": "+237 600 000 001",
    "email": "demo-services@example.com",
    "company_registry": "RC/DLA/2025/B/0001 (fictif)",
}
NIU = "M000000000001S"  # numéro d'identifiant unique fictif

# ------------------------------------------------------------------ montants par exercice
YEARS = {
    2025: {"maintenance": 3_000_000, "taux_jour": 160_000,
           "jours": [10, 10, 12, 12, 12, 10, 8, 6, 12, 12, 12, 10],
           "materiel": [1_200_000, 1_200_000, 1_600_000, 1_600_000, 1_600_000, 2_000_000,
                        1_200_000, 800_000, 2_400_000, 1_600_000, 1_600_000, 2_800_000],
           "loyer": 600_000, "cloud": 500_000, "internet": 200_000, "electricite": 200_000, "patente": 600_000},
    2026: {"maintenance": 3_200_000, "taux_jour": 176_000,
           "jours": [10, 12, 12, 14, 14, 12, 8, 6, 14],
           "materiel": [1_600_000, 1_600_000, 2_000_000, 2_000_000, 2_400_000, 2_400_000,
                        1_600_000, 1_200_000, 2_800_000],
           "loyer": 600_000, "cloud": 600_000, "internet": 200_000, "electricite": 220_000, "patente": 650_000},
}
# Paie globale du mois (illustrative) : retenues salariales et charges patronales
PAIE = {
    2025: {"brut": 3_000_000, "cnps_salariale": 126_000, "irpp": 240_000, "cac": 24_000, "cfc_salariale": 30_000,
           "rav": 13_000, "tdl": 10_000, "cnps_pf": 210_000, "cnps_at": 52_500, "cnps_pension": 126_000,
           "cfc_patronale": 45_000, "fne": 30_000},
    2026: {"brut": 3_300_000, "cnps_salariale": 138_600, "irpp": 270_000, "cac": 27_000, "cfc_salariale": 33_000,
           "rav": 13_000, "tdl": 10_000, "cnps_pf": 231_000, "cnps_at": 57_750, "cnps_pension": 138_600,
           "cfc_patronale": 49_500, "fne": 33_000},
}

FRAIS_BANCAIRES = 24_000
ACHAT_MATERIEL = 75  # pourcentage des ventes de matériel du mois
PROJET = 4_000_000
PROJET_MOIS = {2025: (2, 5, 8, 11), 2026: (2, 5, 8)}
FORMATION = 1_200_000
FORMATION_MOIS = {2025: (3, 6, 10), 2026: (3, 6)}
SOUS_TRAITANCE = 1_200_000
SOUS_TRAITANCE_MOIS = {2025: (4, 5, 9, 10), 2026: (4, 5, 9)}
# Contrat de support annuel facturé d'avance ; produits constatés d'avance au 31/12/2025 (9 mois sur 12),
# repris le 01/01/2026
SUPPORT = {"date": date(2025, 10, 1), "montant": 6_000_000, "reglement": date(2025, 10, 20),
           "pca": date(2025, 12, 31), "pca_montant": 4_500_000, "reprise": date(2026, 1, 1)}

CAPITAL = (date(2025, 1, 2), 25_000_000)
# Immobilisations : clé, libellé, compte, compte d'amortissement, montant HT, (année, mois) de mise en service,
# durée en mois (dotation mensuelle = montant // durée, dès le mois de mise en service)
IMMOBILISATIONS = [
    ("postes", "Ordinateurs portables et serveur de développement", "2442", "2844", 10_800_000, (2025, 1), 36),
    ("erp", "Progiciel de gestion intégré, licence perpétuelle", "2131", "2813", 7_200_000, (2025, 3), 36),
    ("serveurs", "Serveurs de virtualisation", "2442", "2844", 5_400_000, (2026, 4), 36),
]
# Factures d'immobilisations : date, fournisseur, immobilisations, règlements [(date, % du TTC ou None = solde)]
INVESTISSEMENTS = [
    (date(2025, 1, 15), "integrateur", ("postes",), [(date(2025, 1, 31), None)]),
    (date(2025, 3, 10), "editeur", ("erp",), [(date(2025, 3, 31), None)]),
    (date(2026, 4, 10), "integrateur", ("serveurs",), [(date(2026, 4, 30), None)]),
]
INVENTAIRES = {date(2025, 12, 31): 1_800_000, date(2026, 9, 30): 2_100_000}
# Impôt illustratif : 25 % (chiffre d'affaires d'au plus 3 milliards) + 10 % de CAC = 27,5 % (fiche IS de la DGI,
# skill fiscalite-cameroun), appliqué au résultat comptable ; l'impôt réel, sur le résultat fiscal, est à établir par
# l'expert-comptable
TAUX_IS_ILLUSTRATIF = 0.275
# Acomptes imputés sur l'impôt 2025, solde payé. Date de démonstration : l'échéance de la DSF et du solde de l'IS
# dépend du centre des impôts de rattachement (15 mars DGE, 15 avril CIME, 15 mai CDI)
IMPUTATION_IS = date(2026, 3, 15)
AFFECTATION = date(2026, 6, 30)      # assemblée générale ordinaire
DIVIDENDES = date(2026, 7, 20)       # versement, IRCM déclaré en ligne L57 de la déclaration de juillet 2026

# ------------------------------------------------------------------ partenaires (fictifs)
PARTNERS = {
    "banque_cliente": {"name": "Banque Démo Cameroun SA", "is_company": True},
    "industrie": {"name": "Société Industrielle Démo SA", "is_company": True},
    "assurances": {"name": "Assurances Démo SA", "is_company": True},
    "patronat": {"name": "Groupement Patronal Démo", "is_company": True},
    "operateur": {"name": "Opérateur Télécom Démo SA", "is_company": True},
    "pme": {"name": "Clients matériel (PME)"},
    "distributeur": {"name": "Distributeur Informatique Démo SARL", "is_company": True},
    "bailleur": {"name": "SCI Bonapriso Démo", "is_company": True},
    "cloud": {"name": "Cloud Software Demo Inc.", "is_company": True, "country": "base.us", "city": "Seattle"},
    "freelance": {"name": "Développeur indépendant Démo"},
    "fai": {"name": "Fournisseur d'accès Internet Démo SA", "is_company": True},
    "energie": {"name": "Énergie Démo SA", "is_company": True},
    "banque": {"name": "Banque Commerciale Démo SA", "is_company": True},
    "integrateur": {"name": "Intégrateur Matériel Démo SA", "is_company": True, "investissement": True},
    # progiciel : immobilisation incorporelle, fournisseur en 4811 (4812 pour les immobilisations corporelles)
    "editeur": {"name": "Éditeur Logiciel Démo SARL", "is_company": True, "investissement": True, "compte": "4811"},
}

# Taxes activées dans la société de démonstration (créées inactives par le socle, taux « à valider »)
TAXES_ACTIVEES = ("retenue_loyers", "retenue_honoraires", "retenue_tsr", "autoliquidation_services",
                  "subie_acompte_ca", "subie_honoraires")
