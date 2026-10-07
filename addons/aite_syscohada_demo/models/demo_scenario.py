# -*- coding: utf-8 -*-
"""Paramètres du scénario de démonstration : un bar-hôtel de Douala, de janvier 2025 à septembre 2026.

Ce fichier ne contient que des données. Le générateur (``demo_generator.py``, sur le moteur commun
``aite_syscohada_demo_common``) les lit pour créer les pièces ;
les tests (``tests/test_demo.py``) recalculent à la main les montants attendus.

Tous les montants sont en FCFA (XAF, sans décimale). Les montants hors taxes soumis à la TVA de 19,25 % sont des
multiples de 400 : la TVA de chaque ligne tombe juste, sans arrondi.

RYTHME MENSUEL (chaque mois, de janvier 2025 à septembre 2026)
    1er   loyer (précompte de 15 % retenu), réglé le 5
    1er   versement en banque des espèces du mois précédent (départ de la caisse le 1er, arrivée en banque le 2,
          par le compte de virements de fonds 585) ; le 3, même chose pour Orange Money et MTN Mobile Money
    5     boissons des brasseries (36 % des ventes du bar du mois), TVA et précompte sur achats de 2 %,
          réglées le 5 du mois suivant
    8     vins et spiritueux (12 % des ventes du bar), réglés le 25
    10    règlement des factures du mois précédent : solde des nuitées, séminaire, honoraires, logiciel
    12    électricité, réglée le 20 ; 14 : internet et téléphone, réglés le 22
    15    paiement de la déclaration I/TVA-IR et des cotisations CNPS du mois précédent ; échéance d'emprunt (2026)
    dernier jour
          ventes du bar (facture de synthèse encaissée à 60 % en espèces, 25 % par Orange Money, 15 % par MTN) ;
          nuitées du mois (encaissées à 80 % par carte bancaire, le solde le 10 du mois suivant) ; frais bancaires ;
          paie et salaires nets virés ; dotations aux amortissements ; déclaration mensuelle calculée, liquidée et
          validée (celle de septembre 2026 reste en brouillon, à liquider par l'utilisateur).
    Trimestriels : logiciel de gestion hôtelière d'un éditeur étranger le 15 (janvier, avril, juillet, octobre :
    TVA autoliquidée et TSR de 15 %), honoraires de l'expert-comptable le 28 (mars, juin, septembre, décembre :
    retenue de 5 %). Séminaires d'une agence le 20 (mars, juin, septembre, novembre 2025 ; mars, juin,
    septembre 2026) et d'une société pétrolière qui retient l'acompte de 2 % (12 octobre 2025, 12 mai 2026).

OPÉRATIONS PONCTUELLES
    02/01/2025 apport en capital de 30 000 000 ; 10/01/2025 aménagements (9 600 000) et mobilier (3 600 000),
    réglés par moitié les 20 janvier et 20 février ; 28/02 patente de l'année ; 31/12/2025 stock final de
    2 400 000, ristourne de 300 000 à obtenir des brasseries, impôt sur le résultat ; 01/01/2026 résultat 2025
    en instance d'affectation et reprise du stock ; 15/01/2026 emprunt de 12 000 000 ; 10/02/2026 avoir de
    ristourne imputé sur la facture des brasseries de février ; 02/03/2026 chambre froide (6 000 000), réglée le
    25 ; 15/03/2026 imputation des acomptes sur l'impôt 2025 ; 30/06/2026 affectation du résultat 2025 ;
    20/07/2026 dividendes versés, IRCM retenu (ligne L57 de la déclaration de juillet) ; 30/09/2026 inventaire
    intermédiaire de 2 800 000 (situation au 30 septembre).

SIMPLIFICATIONS ASSUMÉES (démonstration, pas conseil fiscal)
    Paie globale illustrative (le module de paie camerounaise n'est pas encore livré) ; impôt sur le résultat
    illustratif : maximum de 27,5 % du résultat comptable et des acomptes versés, sans passage au résultat fiscal ;
    dotations dès le mois d'acquisition, sans prorata temporis ; avoir de ristourne hors TVA (la régularisation de
    TVA sur avoir n'est pas illustrée) ; taxes de retenue « taux à valider » activées dans la seule société de
    démonstration.

SAISONNALITÉ : coefficients mensuels en dixièmes, janvier à décembre = 9, 9, 10, 10, 10, 11, 12, 12, 10, 10, 11, 16
    Somme sur douze mois = 130 (13,0) ; somme de janvier à septembre = 93 (9,3).

EXERCICE 2025, CALCUL À LA MAIN
    TA  ventes du bar            3 200 000 × 13,0                                         = 41 600 000
    TC  nuitées 1 800 000 × 13,0 = 23 400 000 + séminaires de l'agence 4 × 1 200 000
        + séminaire pétrolier 2 000 000                                                   = 30 200 000
    XB                           41 600 000 + 30 200 000                                  = 71 800 000
    RA  achats 48 % × 41 600 000 = 19 968 000, moins ristourne 300 000                    = −19 668 000
    RB  stock final 2 400 000 (stock initial nul)                                         = +2 400 000
    RE  électricité 12 × 400 000                                                          = −4 800 000
    RH  téléphone 12 × 120 000 + loyer 12 × 600 000 + honoraires 4 × 400 000
        + logiciel 4 × 300 000 + frais bancaires 12 × 16 000                              = −11 632 000
    RI  patente 350 000 + taxes patronales 12 × 60 000                                    = −1 070 000
    RK  salaires 12 × 2 400 000 + charges patronales 12 × 310 800                         = −32 529 600
    RL  dotations 12 × (80 000 + 60 000)                                                  = −1 680 000
    XG  71 800 000 − 19 668 000 + 2 400 000 − 4 800 000 − 11 632 000 − 1 070 000
        − 32 529 600 − 1 680 000                                                          = 2 820 400
    Acomptes de l'année : 2 % + 10 % de CAC = 2,2 % du chiffre d'affaires déclaré (ligne L15), avant déduction des
        précomptes subis. L15 cumulé = ventes 41 600 000 + nuitées encaissées 23 400 000 − 576 000 (solde de
        décembre, encaissé en janvier 2026) + séminaires 4 800 000 + 2 000 000 = 71 224 000 ; 2,2 % = 1 566 928
    RS  impôt illustratif = maximum (27,5 % × 2 820 400 = 775 610 ; acomptes 1 566 928)   = −1 566 928
    XI  2 820 400 − 1 566 928                                                             = 1 253 472

AFFECTATION DU RÉSULTAT 2025 (assemblée du 30 juin 2026)
    Réserve légale 10 % : 1 253 472 // 10 = 125 347 ; dividendes : la moitié arrondie à la dizaine de mille
    inférieure = 620 000 ; report à nouveau 1 253 472 − 125 347 − 620 000 = 508 125.
    Dividendes versés le 20 juillet 2026 ; IRCM retenu au taux par défaut de la ligne L57 (15 % + 10 % de CAC) :
    93 000 + 9 300 = 102 300 ; net versé 517 700.

EXERCICE 2026, JANVIER À SEPTEMBRE, CALCUL À LA MAIN
    TA  3 600 000 × 9,3                                                                   = 33 480 000
    TC  nuitées 2 200 000 × 9,3 = 20 460 000 + séminaires 3 × 1 200 000 + 2 000 000       = 26 060 000
    RA  achats 48 % × 33 480 000                                                          = −16 070 400
    RB  reprise du stock 2 400 000, stock au 30 septembre 2 800 000                       = +400 000
    RE  9 × 440 000                                                                       = −3 960 000
    RH  9 × 120 000 + 9 × 600 000 + 3 × 400 000 + 3 × 300 000 + 9 × 16 000               = −8 724 000
    RI  patente 380 000 + taxes patronales 9 × 62 500                                     = −942 500
    RK  9 × (2 500 000 + 323 750)                                                         = −25 413 750
    RL  9 × 140 000 + 7 × 100 000 (chambre froide à partir de mars)                      = −1 960 000
    RM  intérêts d'emprunt, février à septembre : 120 000 + 115 000 + … + 85 000         = −820 000
    XG = XI (pas d'impôt constaté en cours d'exercice)                                    = 2 049 350
"""
from datetime import date

# ------------------------------------------------------------------ période et saisonnalité
START = (2025, 1)
END = (2026, 9)
COEF_DIXIEMES = [9, 9, 10, 10, 10, 11, 12, 12, 10, 10, 11, 16]  # janvier à décembre



# ------------------------------------------------------------------ société (coordonnées fictives)
COMPANY = {
    "name": "Bar-Hôtel Démo AITE",
    "street": "Rue de la Joie, Akwa",
    "city": "Douala",
    "phone": "+237 600 000 000",
    "email": "demo@example.com",
    "company_registry": "RC/DLA/2025/B/0000 (fictif)",
}
NIU = "M000000000000D"  # numéro d'identifiant unique fictif, imprimé sur la déclaration

# ------------------------------------------------------------------ montants par exercice
YEARS = {
    2025: {"ventes": 3_200_000, "hebergement": 1_800_000, "electricite": 400_000, "patente": 350_000},
    2026: {"ventes": 3_600_000, "hebergement": 2_200_000, "electricite": 440_000, "patente": 380_000},
}
# Paie globale du mois (illustrative) : retenues salariales et charges patronales
PAIE = {
    2025: {"brut": 2_400_000, "cnps_salariale": 100_800, "irpp": 120_000, "cac": 12_000, "cfc_salariale": 24_000,
           "rav": 9_000, "tdl": 7_500, "cnps_pf": 168_000, "cnps_at": 42_000, "cnps_pension": 100_800,
           "cfc_patronale": 36_000, "fne": 24_000},
    2026: {"brut": 2_500_000, "cnps_salariale": 105_000, "irpp": 125_000, "cac": 12_500, "cfc_salariale": 25_000,
           "rav": 9_750, "tdl": 7_500, "cnps_pf": 175_000, "cnps_at": 43_750, "cnps_pension": 105_000,
           "cfc_patronale": 37_500, "fne": 25_000},
}

# Ventes du bar : lignes de la facture de synthèse (pourcentage des ventes)
VENTES_LIGNES = [("Bières", 60), ("Vins et spiritueux", 25), ("Boissons sans alcool", 15)]
# Encaissement des ventes du bar (pourcentage du TTC) ; les espèces reçoivent le solde
ENCAISSEMENT_ORANGE_MONEY = 25
ENCAISSEMENT_MTN = 15
# Achats en pourcentage des ventes du bar
ACHAT_BRASSERIES = 36
ACHAT_VINS = 12
# Nuitées encaissées dans le mois (pourcentage du TTC), le solde le 10 du mois suivant
HEBERGEMENT_ENCAISSE = 80

LOYER = 600_000
TELEPHONE = 120_000
FRAIS_BANCAIRES = 16_000
HONORAIRES = 400_000
HONORAIRES_MOIS = (3, 6, 9, 12)
LOGICIEL = 300_000
LOGICIEL_MOIS = (1, 4, 7, 10)
SEMINAIRE_AGENCE = 1_200_000
SEMINAIRE_AGENCE_MOIS = {2025: (3, 6, 9, 11), 2026: (3, 6, 9)}
SEMINAIRE_PETROLIER = 2_000_000
SEMINAIRE_PETROLIER_MOIS = ((2025, 10), (2026, 5))

CAPITAL = (date(2025, 1, 2), 30_000_000)
# Immobilisations : clé, libellé, compte, compte d'amortissement, montant HT, (année, mois) de mise en service,
# durée en mois (dotation mensuelle = montant // durée, dès le mois de mise en service)
IMMOBILISATIONS = [
    ("agencements", "Aménagements et agencements des chambres et du bar", "2351", "2835", 9_600_000, (2025, 1), 120),
    ("mobilier", "Mobilier des chambres et de la terrasse", "2444", "2844", 3_600_000, (2025, 1), 60),
    ("chambre_froide", "Chambre froide du bar", "2413", "2841", 6_000_000, (2026, 3), 60),
]
# Factures d'immobilisations : date, fournisseur, immobilisations, règlements [(date, % du TTC ou None = solde)]
INVESTISSEMENTS = [
    (date(2025, 1, 10), "agencement", ("agencements", "mobilier"), [(date(2025, 1, 20), 50), (date(2025, 2, 20), None)]),
    (date(2026, 3, 2), "froid", ("chambre_froide",), [(date(2026, 3, 25), None)]),
]
# Emprunt bancaire : reçu le 15 janvier 2026 ; à partir de février, le 15 de chaque mois, 500 000 de capital
# et 1 % d'intérêts sur le capital restant dû avant l'échéance
EMPRUNT = {"date": date(2026, 1, 15), "montant": 12_000_000, "capital_mensuel": 500_000, "taux_mensuel_pour_cent": 1}

INVENTAIRES = {date(2025, 12, 31): 2_400_000, date(2026, 9, 30): 2_800_000}
RISTOURNE = {"constatee": date(2025, 12, 31), "montant": 300_000, "imputee": date(2026, 2, 10)}
# Impôt illustratif : 25 % (chiffre d'affaires d'au plus 3 milliards) + 10 % de CAC = 27,5 % (fiche IS de la DGI,
# skill fiscalite-cameroun), appliqué au résultat comptable ; l'impôt réel, sur le résultat fiscal, est à établir par
# l'expert-comptable
TAUX_IS_ILLUSTRATIF = 0.275
# Imputation des acomptes sur l'impôt 2025. Date de démonstration : l'échéance de la DSF et du solde de l'IS dépend
# du centre des impôts de rattachement (15 mars DGE, 15 avril CIME, 15 mai CDI)
IMPUTATION_IS = date(2026, 3, 15)
AFFECTATION = date(2026, 6, 30)      # assemblée générale ordinaire
DIVIDENDES = date(2026, 7, 20)       # versement, IRCM déclaré en ligne L57 de la déclaration de juillet 2026

# ------------------------------------------------------------------ partenaires (fictifs)
PARTNERS = {
    "comptoir": {"name": "Client comptoir (ventes du bar)"},
    "hebergement": {"name": "Clients hébergement (passage)"},
    "agence": {"name": "Agence Événements Démo SARL", "is_company": True},
    "petrolier": {"name": "Société Pétrolière Démo SA", "is_company": True},
    "brasseries": {"name": "Brasseries Démo SA", "is_company": True},
    "vins": {"name": "Vins et Spiritueux Démo SARL", "is_company": True},
    "energie": {"name": "Énergie Démo SA", "is_company": True},
    "telecom": {"name": "Télécom Démo SA", "is_company": True},
    "bailleur": {"name": "SCI Akwa Démo", "is_company": True},
    "cabinet": {"name": "Cabinet Comptable Démo SARL", "is_company": True},
    "logiciel": {"name": "Hospitality Software Demo Ltd", "is_company": True, "country": "base.uk", "city": "Londres"},
    "banque": {"name": "Banque Démo SA", "is_company": True},
    "agencement": {"name": "Agencements et Mobilier Démo SARL", "is_company": True, "investissement": True},
    "froid": {"name": "Froid Industriel Démo SA", "is_company": True, "investissement": True},
}

# Taxes activées dans la société de démonstration (créées inactives par le socle, taux « à valider »)
TAXES_ACTIVEES = ("precompte_achats", "retenue_loyers", "retenue_honoraires", "retenue_tsr",
                  "autoliquidation_services", "subie_acompte_ca")

