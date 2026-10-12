# -*- coding: utf-8 -*-
"""Les données montrées dans la vidéo de présentation.

Une seule source : la société de démonstration « Bar-Hôtel Démo AITE »
(module ``aite_syscohada_demo``, société et personnes fictives), telle que
l'affiche la base de formation du guide. Chaque valeur est relevée sur une
capture du guide (``docs/guide/captures``, légendes dans ``docs/guide/guide.md``)
ou calculée par les modules sur une copie de cette base (écriture de
liquidation de septembre 2026) : rien n'est inventé. Aucune donnée d'une
base de recette d'un client n'apparaît à l'écran.
"""

SOCIETE = 'Bar-Hôtel Démo AITE'
SERVICES = 'Services Informatiques Démo AITE'

# ---------------------------------------------------------------- les modules --
# Nom et résumé des manifestes (addons/*/__manifest__.py) ; icône de chaque module.
MODULES = {
    'community': ('aite_syscohada_community', 'SYSCOHADA révisé – adaptation Odoo Community (Cameroun)',
                  "États SYSCOHADA en un clic (MIS Builder, exercices N et N-1), déclaration mensuelle I/TVA-IR "
                  "complète (TVA, retenues, acomptes, IRCM, salaires) et écritures de liquidation, sans Odoo Enterprise."),
    'base': ('aite_syscohada_base', 'SYSCOHADA révisé – socle AITE (Cameroun)',
             "Rubriques des états SYSCOHADA, moteur de calcul indépendant de l'édition, corrections du plan "
             "comptable, taxes camerounaises complémentaires et contrôles."),
    'mis': ('aite_syscohada_mis', 'SYSCOHADA révisé – états MIS Builder (Community)',
            "Bilan, compte de résultat et tableau des flux SYSCOHADA en modèles MIS Builder, générés depuis le "
            "référentiel des rubriques AITE."),
    'reports': ('aite_syscohada_reports', 'SYSCOHADA révisé – rapports Enterprise',
                "Bilan, compte de résultat et tableau des flux SYSCOHADA dans le moteur de rapports d'Odoo "
                "Enterprise, générés depuis le référentiel des rubriques AITE."),
    'demo': ('aite_syscohada_demo', 'SYSCOHADA révisé – données de démonstration (bar-hôtel, Cameroun)',
             "Société « Bar-Hôtel Démo AITE » avec 21 mois d'opérations (janvier 2025 à septembre 2026) : ventes, "
             "nuitées, achats, retenues, paie, immobilisations, emprunt, déclarations I/TVA-IR liquidées et états "
             "SYSCOHADA prêts à consulter. Pour les bases de test et de formation."),
    'services': ('aite_syscohada_demo_services',
                 'SYSCOHADA révisé – données de démonstration (services informatiques, Cameroun)',
                 "Société « Services Informatiques Démo AITE » avec 21 mois d'opérations (janvier 2025 à septembre "
                 "2026) : infogérance, régie, projets, formations, revente de matériel, services en nuage étrangers, "
                 "sous-traitance, retenues subies et opérées, déclarations I/TVA-IR liquidées et états SYSCOHADA. "
                 "Pour les bases de test et de formation."),
}

# --------------------------------------------------------- tableau de bord --
# Capture 02-tableau-de-bord.
TABLEAU_DE_BORD = [
    ('Factures clients', [('Nouveau', 'primaire')], '2 Non payé', '1 955 700 FCFA', 'barres'),
    ('Factures fournisseurs', [('Charger', 'primaire'), ('Nouveau', 'clair')], '2 À payer', '2 028 400 FCFA', 'barres'),
    ('Banque', [('Configuration de la banque', 'primaire'), ('Transactions', 'primaire')],
     ('Solde', '-28 575 698 FCFA'), ('Opérations diverses', '47 204 984 FCFA'), 'ligne'),
    ('MTN Mobile Money', [('Configuration de la banque', 'primaire'), ('Transactions', 'primaire')],
     ('Solde', '13 429 935 FCFA'), ('Opérations diverses', '-12 785 985 FCFA'), 'ligne'),
]

# ------------------------------------------------------------------ menus --
# Captures 03-menu-syscohada et 22-configuration.
MENU_ANALYSE = [
    ('Syscohada', ['États et contrôles (AITE)', 'Bilan actif', 'Bilan passif', 'Compte de résultat',
                   'Tableau des flux de trésorerie', 'Déclarations de TVA (Cameroun)']),
    ('Gestion', ['Analyse des factures', 'Rapport Analytique']),
    ('MIS Reporting', ['MIS Reports', 'Derniers rapports générés']),
]
MENU_CONFIGURATION = [
    (None, ['Paramètres']),
    ('Facturation', ['Conditions de paiement']),
    ('Banques', ['Ajouter un compte bancaire', 'Modèles de rapprochement']),
    ('Comptabilité', ['Plan comptable', 'Taxes', 'Journaux', 'Devises', 'Positions fiscales',
                      'Multinormes comptables']),
    ('Paiements en ligne', ['Fournisseurs de paiement', 'Modes de paiement']),
    ('Gestion', ['Catégories de produits']),
    ('MIS Reporting', ['Modèles MIS Report', 'Styles MIS Report']),
    ('SYSCOHADA', ['Rubriques des états', 'Appliquer le paramétrage']),
]

# --------------------------------------------------------- plan comptable --
# Capture 20-plan-comptable : filtre « 447 », 21 comptes ; seize sous-comptes
# créés par le paramétrage (res_company.py, SUB_ACCOUNTS).
COMPTES_447 = [
    ('447100', "État, impôt général sur le revenu retenu à la source", False),
    ('447110', 'État, IRCM retenu à la source', True),
    ('447120', 'État, taxe spéciale sur le revenu retenue (TSR)', True),
    ('447130', 'État, précomptes retenus sur loyers', True),
    ('447140', 'État, retenues sur rémunérations et honoraires', True),
    ('447150', 'État, IRNC retenu à la source', True),
    ('447160', 'État, TVA retenue à la source', True),
    ('447161', 'État, TVA autoliquidée sur prestations étrangères', True),
    ('447170', "État, acomptes sur chiffre d'affaires retenus à la source", True),
    ('447180', 'État, précomptes sur achats retenus', True),
    ('447200', 'État, impôts sur salaires retenus à la source', False),
    ('447210', 'État, IRPP retenu sur salaires', True),
    ('447215', 'État, centimes additionnels communaux sur IRPP', True),
    ('447220', 'État, Crédit foncier du Cameroun, part salariale', True),
    ('447230', 'État, Crédit foncier du Cameroun, part patronale', True),
    ('447240', "État, Fonds national de l'emploi", True),
    ('447250', 'État, redevance audiovisuelle', True),
    ('447260', 'État, taxe de développement local', True),
    ('447300', 'Contribution nationale', False),
]

# ------------------------------------------------------------------ taxes --
# Capture 21-taxes : filtre « valider ». (nom, description, type, actif dans la démonstration)
TAXES = [
    ('Précompte sur achats (taux à valider)',
     "Précompte sur achats facturé par le fournisseur, avance sur l'impôt sur le revenu", 'Achats', True),
    ('Précompte sur loyers retenu (taux à valider)', 'Précompte sur loyers retenu (taux à valider)', 'Achats', True),
    ('Retenue sur honoraires (taux à valider)', 'Retenue sur honoraires (taux à valider)', 'Achats', True),
    ("TSR sur rémunérations versées à l'étranger (taux à valider)",
     "TSR sur rémunérations versées à l'étranger (taux à valider)", 'Achats', True),
    ('TVA retenue à la source, entreprise habilitée (taux à valider)',
     'TVA retenue à la source, entreprise habilitée (taux à valider)', 'Achats', False),
    ('Acompte sur CA retenu à la source (taux à valider)', 'Acompte sur CA retenu à la source (taux à valider)',
     'Achats', False),
    ('Acompte sur CA retenu par le client (taux à valider)', 'Acompte sur CA retenu par le client (taux à valider)',
     'Ventes', True),
    ('Précompte sur loyers retenu par le locataire (taux à valider)',
     'Précompte sur loyers retenu par le locataire (taux à valider)', 'Ventes', False),
    ('Retenue sur honoraires subie (taux à valider)', 'Retenue sur honoraires subie (taux à valider)', 'Ventes', False),
    ('TVA 19,25 % autoliquidée, services étrangers (à valider)', '', 'Achats', True),
]

# ---------------------------------------------------------------- factures --
# Capture 16-facture-nuitees.
NUITEES = {
    'fil': 'FAC/2026/00022 (HEB-2026-09)', 'type': 'Facture client', 'numero': 'FAC/2026/00022',
    'partenaire': ('Client', 'Clients hébergement (passage)', ['Douala', 'Cameroun']),
    'dates': [('Date de facturation', '30/09/2026'), ("Date d'échéance", '07/10/2026')],
    'ligne': ('Nuitées du mois 09/2026', '706100 Services vendus dans la région', '1,00', '2 200 000,00',
              '19,25 % S (encaissement)', '2 200 000 FCFA'),
    'totaux': [('Montant hors taxes:', '2 200 000 FCFA'), ('T.V.A. 19.25%:', '423 500 FCFA')],
    'total': '2 623 500 FCFA', 'paye': ('Payé le 30/09/2026', '2 098 800 FCFA'), 'du': '524 700 FCFA',
    'ruban': 'PARTIEL',
}
# Capture 17-facture-loyer.
LOYER = {
    'fil': 'FACTU/2026/09/0001 (LOY-2026-09)', 'type': 'Facture fournisseur', 'numero': 'FACTU/2026/09/0001',
    'partenaire': ('Fournisseur', 'SCI Akwa Démo', ['Douala', 'Cameroun']), 'reference': 'LOY-2026-09',
    'dates': [('Date de facturation', '01/09/2026'), ('Date comptable', '01/09/2026'),
              ("Date d'échéance", '07/10/2026')],
    'ligne': ('Loyer du mois 09/2026', "622200 Location d'immeubles", '1,00', '600 000,00',
              'Précompte sur loyers retenu (taux à valider)', '600 000 FCFA'),
    'totaux': [('Montant hors taxes:', '600 000 FCFA'), ('Retenues, précomptes et autres taxes:', '-90 000 FCFA')],
    'total': '510 000 FCFA', 'paye': ('Payé le 05/09/2026', '510 000 FCFA'), 'ruban': 'PAYÉ',
}
# Capture 18-logiciel-etranger, onglet « Écritures comptables ».
LOGICIEL = {
    'fil': 'FACTU/2026/07/0006 (LOG-2026-07)', 'type': 'Facture fournisseur', 'numero': 'FACTU/2026/07/0006',
    'partenaire': ('Fournisseur', 'Hospitality Software Demo Ltd', ['Londres', 'Royaume-Uni']),
    'reference': 'LOG-2026-07',
    'dates': [('Date de facturation', '15/07/2026'), ('Date comptable', '15/07/2026'),
              ("Date d'échéance", '07/10/2026')],
    'ecritures': [
        ('634300 Redevances de logiciels', 'Licence du logiciel de gestion hôtelière, trimestre', '300 000 FCFA', '0 FCFA', ''),
        ('447120 État, taxe spéciale sur le revenu retenue (TSR)',
         "TSR sur rémunérations versées à l'étranger (taux à valider)", '0 FCFA', '45 000 FCFA', ''),
        ('445400 État, TVA récupérable sur services extérieurs et autres charges',
         'TVA 19,25 % autoliquidée, services étrangers (à valider)', '57 750 FCFA', '0 FCFA', '+CM_21'),
        ('447161 État, TVA autoliquidée sur prestations étrangères',
         'TVA 19,25 % autoliquidée, services étrangers (à valider)', '0 FCFA', '57 750 FCFA', ''),
        ('401100 Fournisseurs', 'LOG-2026-07', '0 FCFA', '255 000 FCFA', ''),
    ],
    'total': ('357 750 FCFA', '357 750 FCFA'), 'ruban': 'PAYÉ',
}

# ---------------------------------------------------- états et contrôles --
# Capture 04-etats-controles : exercice 2025 du bar-hôtel.
CONTROLES = [
    ('RATTACHEMENT', 'Rattachement des comptes', 'Tous les comptes sont rattachés une seule fois.'),
    ('BROUILLONS', 'Pièces non validées sur la période', 'Aucune pièce en brouillon.'),
    ('EQUILIBRE', 'Total actif = total passif (BZ = DZ)', 'BZ 37 621 918 ; DZ 37 621 918 ; écart 0'),
    ('RESULTAT', 'Résultat net : XI = CJ hors résultats antérieurs non affectés',
     'XI 1 253 472 ; CJ 1 253 472 ; résultats antérieurs non affectés 0'),
    ('ATTENTE', "Comptes d'attente et de virements internes soldés", 'Tous soldés.'),
    ('CAISSE', 'Aucune caisse créditrice', 'Aucune caisse créditrice.'),
    ('TFT', 'Trésorerie de clôture du TFT (ZH) = BT − DT', 'ZH 21 148 110 ; BT − DT 21 148 110 ; écart 0'),
    ('ESPECES', 'Paiements fournisseurs en espèces > 100 000 FCFA',
     'Aucun : la TVA des factures réglées reste déductible.'),
    ('BASCULES', 'Comptes reclassés selon le sens du solde', 'Aucun.'),
]

# -------------------------------------------------------- états MIS Builder --
# Captures 06-bilan-actif, 08-compte-de-resultat, 09-flux-de-tresorerie :
# exercice N = 2026 (jusqu'au 30 septembre), N-1 = 2025. (libellé, valeurs, gras)
BILAN_ACTIF = [
    ('AD – Immobilisations incorporelles', ['', '', '', '', '', ''], True),
    ('AE – Frais de développement et de prospection', ['', '', '', '', '', ''], False),
    ('AF – Brevets, licences, logiciels et droits similaires', ['', '', '', '', '', ''], False),
    ('AG – Fonds commercial et droit au bail', ['', '', '', '', '', ''], False),
    ('AH – Autres immobilisations incorporelles', ['', '', '', '', '', ''], False),
    ('AI – Immobilisations corporelles',
     ['19 200 000', '3 640 000', '15 560 000', '13 200 000', '1 680 000', '11 520 000'], True),
    ('AJ – Terrains', ['', '', '', '', '', ''], False),
    ('AK – Bâtiments', ['', '', '', '', '', ''], False),
    ('AL – Aménagements, agencements et installations',
     ['9 600 000', '1 680 000', '7 920 000', '9 600 000', '960 000', '8 640 000'], False),
    ('AM – Matériel, mobilier et actifs biologiques',
     ['9 600 000', '1 960 000', '7 640 000', '3 600 000', '720 000', '2 880 000'], False),
    ('AN – Matériel de transport', ['', '', '', '', '', ''], False),
    ('AP – Avances et acomptes versés sur immobilisations', ['', '', '', '', '', ''], False),
    ('AQ – Immobilisations financières', ['', '', '', '', '', ''], True),
]
COMPTE_RESULTAT = [
    ('TA – Ventes de marchandises', ['33 480 000', '41 600 000'], False),
    ('RA – Achats de marchandises', ['-16 070 400', '-19 668 000'], False),
    ('RB – Variation de stocks de marchandises', ['400 000', '2 400 000'], False),
    ('XA – MARGE COMMERCIALE', ['17 809 600', '24 332 000'], True),
    ('TB – Ventes de produits fabriqués', ['', ''], False),
    ('TC – Travaux, services vendus', ['26 060 000', '30 200 000'], False),
    ('TD – Produits accessoires', ['', ''], False),
    ("XB – CHIFFRE D'AFFAIRES", ['59 540 000', '71 800 000'], True),
    ('TE – Production stockée (ou déstockage)', ['', ''], False),
    ('TF – Production immobilisée', ['', ''], False),
    ("TG – Subventions d'exploitation", ['', ''], False),
    ('TH – Autres produits', ['', ''], False),
    ("TI – Transferts de charges d'exploitation", ['', ''], False),
]
FLUX = [
    ('ZA – Trésorerie nette au 1er janvier', ['21 148 110', ''], False),
    ("FA – Capacité d'autofinancement globale (CAFG)", ['4 009 350', '2 933 472'], False),
    ('FB – Actif circulant HAO', ['0', '0'], False),
    ('FC – Variation des stocks', ['-400 000', '-2 400 000'], False),
    ('FD – Variation des créances', ['-1 105 268', '-2 553 808'], False),
    ('FE – Variation du passif circulant', ['-2 109 906', '6 368 446'], False),
    ('ZB – Flux de trésorerie provenant des activités opérationnelles', ['394 176', '4 348 110'], True),
    ("FF – Décaissements liés aux acquisitions d'immobilisations incorporelles", ['', ''], False),
    ("FG – Décaissements liés aux acquisitions d'immobilisations corporelles", ['-6 000 000', '-13 200 000'], False),
    ("FH – Décaissements liés aux acquisitions d'immobilisations financières", ['', ''], False),
    ("FI – Encaissements liés aux cessions d'immobilisations incorporelles et corporelles", ['', ''], False),
    ("ZC – Flux de trésorerie provenant des activités d'investissement", ['-6 000 000', '-13 200 000'], True),
    ('FK – Augmentations de capital par apports nouveaux', ['0', '30 000 000'], False),
]

# ------------------------------------------------------------ déclarations --
# Capture 10-declarations (12 premières lignes) : (nom, société, L28, L29, L32,
# L35, total, date limite, écriture, état).
DECLARATIONS = [
    ('TVA 2026-09-01 – 2026-09-30', SERVICES, '2 128 280 FCFA', '605 220 FCFA', '1 523 060 FCFA', '0 FCFA',
     '2 357 068 FCFA', '15/10/2026', '', 'Brouillon'),
    ('TVA 2026-09-01 – 2026-09-30', SOCIETE, '1 133 440 FCFA', '520 520 FCFA', '612 920 FCFA', '0 FCFA',
     '1 068 786 FCFA', '15/10/2026', '', 'Brouillon'),
    ('TVA 2026-08-01 – 2026-08-31', SERVICES, '1 118 040 FCFA', '374 220 FCFA', '743 820 FCFA', '0 FCFA',
     '1 474 820 FCFA', '15/09/2026', 'OD/2026/08/0002 (TVA 2026-08-01 – 2026-08-31)', 'Validée'),
    ('TVA 2026-08-01 – 2026-08-31', SOCIETE, '1 339 800 FCFA', '510 048 FCFA', '829 752 FCFA', '0 FCFA',
     '1 284 018 FCFA', '15/09/2026', 'OD/2026/08/0002 (TVA 2026-08-01 – 2026-08-31)', 'Validée'),
    ('TVA 2026-07-01 – 2026-07-31', SERVICES, '1 330 560 FCFA', '431 970 FCFA', '898 590 FCFA', '0 FCFA',
     '2 501 404 FCFA', '15/08/2026', 'OD/2026/07/0002 (TVA 2026-07-01 – 2026-07-31)', 'Validée'),
    ('TVA 2026-07-01 – 2026-07-31', SOCIETE, '1 562 330 FCFA', '567 798 FCFA', '994 532 FCFA', '0 FCFA',
     '1 679 280 FCFA', '15/08/2026', 'OD/2026/07/0002 (TVA 2026-07-01 – 2026-07-31)', 'Validée'),
    ('TVA 2026-06-01 – 2026-06-30', SERVICES, '2 553 320 FCFA', '547 470 FCFA', '2 005 850 FCFA', '0 FCFA',
     '2 878 066 FCFA', '15/07/2026', 'OD/2026/06/0003 (TVA 2026-06-01 – 2026-06-30)', 'Validée'),
    ('TVA 2026-06-01 – 2026-06-30', SOCIETE, '1 219 680 FCFA', '553 784 FCFA', '665 896 FCFA', '0 FCFA',
     '1 129 026 FCFA', '15/07/2026', 'OD/2026/06/0003 (TVA 2026-06-01 – 2026-06-30)', 'Validée'),
    ('TVA 2026-05-01 – 2026-05-31', SERVICES, '1 552 320 FCFA', '669 130 FCFA', '883 190 FCFA', '0 FCFA',
     '1 674 190 FCFA', '15/06/2026', 'OD/2026/05/0002 (TVA 2026-05-01 – 2026-05-31)', 'Validée'),
    ('TVA 2026-05-01 – 2026-05-31', SOCIETE, '1 501 500 FCFA', '443 520 FCFA', '1 057 980 FCFA', '0 FCFA',
     '1 495 910 FCFA', '15/06/2026', 'OD/2026/05/0002 (TVA 2026-05-01 – 2026-05-31)', 'Validée'),
    ('TVA 2026-04-01 – 2026-04-30', SERVICES, '1 407 560 FCFA', '1 529 220 FCFA', '0 FCFA', '121 660 FCFA',
     '887 864 FCFA', '15/05/2026', 'OD/2026/04/0002 (TVA 2026-04-01 – 2026-04-30)', 'Validée'),
    ('TVA 2026-04-01 – 2026-04-30', SOCIETE, '1 347 500 FCFA', '1 068 760 FCFA', '278 740 FCFA', '0 FCFA',
     '841 820 FCFA', '15/05/2026', 'OD/2026/04/0002 (TVA 2026-04-01 – 2026-04-30)', 'Validée'),
]

# Capture 11-declaration-tva : déclaration de septembre 2026 du bar-hôtel.
DECLARATION = {
    'nom': 'TVA 2026-09-01 – 2026-09-30',
    'gauche': [('Société', SOCIETE), ('Du', '01/09/2026'), ('Au', '30/09/2026')],
    'droite': [('L28 – TVA collectée', '1 133 440 FCFA'), ('L29 – TVA déductible', '520 520 FCFA'),
               ('L32 – TVA à payer', '612 920 FCFA'), ('L33 – Crédit de TVA', '0 FCFA'),
               ('L35 – Crédit à reporter', '0 FCFA'), ('L54 – Acompte à payer', '103 616 FCFA'),
               ('Total à payer', '1 068 786 FCFA'), ('Date limite de dépôt et de paiement', '15/10/2026')],
    # Onglet « Déclaration I/TVA-IR » (capture 11 et document imprimé, capture 14) : (ligne, base, taxe, section)
    'tva': [
        ("2-Chiffre d'affaires réalisé", '', '', True),
        ('10. Opérations taxables au taux normal', '5 888 000 FCFA', '1 133 440 FCFA', False),
        ("11. Montant du Droit d'Accises", '0 FCFA', '0 FCFA', False),
        ('12. Autres opérations taxables', '0 FCFA', '0 FCFA', False),
        ('13. Exportations', '0 FCFA', '', False),
        ("14. Chiffre d'affaires exonéré", '0 FCFA', '', False),
        ('15. CA global hors taxes', '5 888 000 FCFA', '1 133 440 FCFA', False),
        ('3-TVA déductible', '', '', True),
        ('17. Report du crédit antérieur', '', '0 FCFA', False),
        ('18. TVA déductible sur achats locaux', '', '417 340 FCFA', False),
        ('19. TVA déductible sur services locaux', '', '103 180 FCFA', False),
    ],
}
# Capture 13 : onglet « Retenues, acomptes, IRCM, salaires », lignes L36 à L55,
# libellés et sections de itvair.py (LINES, SECTIONS). (section, ligne, libellé,
# taux, base, principal, CAC, total, classe : '' normale, 'gras' total, 'attenue' grisée)
_TVA, _REV, _DED, _LIQ = ('TVA à payer', 'Acomptes et précomptes à reverser', 'Acomptes et précomptes à déduire',
                          "Liquidation des acomptes d'impôt sur le revenu")
RETENUES = [
    (_TVA, 'L36', 'TVA à payer (L32)', '0,0000', '0 FCFA', '612 920 FCFA', '0 FCFA', '612 920 FCFA', ''),
    (_TVA, 'L37', 'TVA retenue à la source (entreprise habilitée)', '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', 'attenue'),
    (_TVA, 'L38', "TVA retenue sur rémunérations versées à l'étranger", '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', 'attenue'),
    (_TVA, 'L39', 'Montant de TVA à payer (L36 + L37 + L38)', '0,0000', '0 FCFA', '612 920 FCFA', '0 FCFA', '612 920 FCFA', 'gras'),
    (_REV, 'L40', "Acompte sur chiffre d'affaires retenu à la source", '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', 'attenue'),
    (_REV, 'L41', 'Précomptes sur achats retenus', '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', 'attenue'),
    (_REV, 'L42', 'Précomptes sur loyers (15 %)', '0,0000', '600 000 FCFA', '90 000 FCFA', '0 FCFA', '90 000 FCFA', ''),
    (_REV, 'L43', 'Précomptes sur rémunérations et honoraires (5 %)', '0,0000', '400 000 FCFA', '20 000 FCFA', '0 FCFA',
     '20 000 FCFA', ''),
    (_REV, 'L44', 'Total des acomptes et précomptes à reverser', '0,0000', '0 FCFA', '110 000 FCFA', '0 FCFA',
     '110 000 FCFA', 'gras'),
    (_DED, 'L45', "Acompte sur chiffre d'affaires retenu à la source (subi)", '0,0000', '0 FCFA', '0 FCFA', '0 FCFA',
     '0 FCFA', 'attenue'),
    (_DED, 'L46', 'Précomptes sur achats (subis)', '0,0000', '1 296 000 FCFA', '25 920 FCFA', '0 FCFA', '25 920 FCFA', ''),
    (_DED, 'L47', 'Précomptes de 15 % sur loyers (subis)', '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', 'attenue'),
    (_DED, 'L48', 'Précomptes sur rémunérations et honoraires (subis)', '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA',
     'attenue'),
    (_DED, 'L49', 'Total des acomptes et précomptes à déduire', '0,0000', '0 FCFA', '25 920 FCFA', '0 FCFA',
     '25 920 FCFA', 'gras'),
    (_LIQ, 'L50', "Acompte sur chiffre d'affaires déclaré", '0,0000', '5 888 000 FCFA', '117 760 FCFA', '11 776 FCFA',
     '129 536 FCFA', ''),
    (_LIQ, 'L51', 'Acompte de 15 % sur loyers perçus', '15,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', ''),
    (_LIQ, 'L52', 'Déductions à opérer (L49)', '0,0000', '0 FCFA', '25 920 FCFA', '0 FCFA', '25 920 FCFA', 'gras'),
    (_LIQ, 'L53', 'Crédit antérieur (L55 de la déclaration précédente)', '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', ''),
    (_LIQ, 'L54', 'Acompte à payer', '0,0000', '0 FCFA', '103 616 FCFA', '0 FCFA', '103 616 FCFA', 'gras'),
    (_LIQ, 'L55', "Crédit d'impôt à reporter", '0,0000', '0 FCFA', '0 FCFA', '0 FCFA', '0 FCFA', ''),
]
# Écriture de liquidation de septembre 2026, calculée par le module (« Passer
# l'écriture de liquidation ») sur une copie de la base de formation, puis
# annulée : mêmes comptes que la capture 15 (août), montants de septembre.
LIQUIDATION = {
    'nom': 'OD/2026/09/0003', 'reference': 'TVA 2026-09-01 – 2026-09-30', 'date': '30/09/2026',
    'journal': 'Opérations diverses',
    'lignes': [
        ('443100 État, TVA facturée sur ventes', 'Liquidation de la TVA', '693 000 FCFA', '0 FCFA'),
        ('443200 État, TVA facturée sur prestations de services', 'Liquidation de la TVA', '440 440 FCFA', '0 FCFA'),
        ('445200 État, TVA récupérable sur achats', 'Liquidation de la TVA', '0 FCFA', '417 340 FCFA'),
        ('445400 État, TVA récupérable sur services extérieurs et autres charges', 'Liquidation de la TVA',
         '0 FCFA', '103 180 FCFA'),
        ('444100 État, TVA due', 'L32 – TVA à payer', '0 FCFA', '612 920 FCFA'),
        ("449250 État, acomptes d'impôt sur le résultat versés", "L54 – Acompte d'impôt sur le résultat",
         '103 616 FCFA', '0 FCFA'),
        ("441100 État, acomptes d'impôt sur le résultat à payer",
         "L54 – Acompte d'impôt sur le résultat à payer", '0 FCFA', '103 616 FCFA'),
    ],
    'total': '1 237 056 FCFA',
}
# Capture 14-declaration-imprimee (en-tête du document de travail).
IMPRIME = {
    'adresse': [SOCIETE, 'Rue de la Joie, Akwa', 'Douala', 'Cameroun', 'Tax ID: M000000000000D'],
    'titre': "Déclaration des taxes sur le chiffre d'affaires et des impôts sur le revenu (I/TVA-IR)",
    'periode': 'Période du 01/09/2026 au 30/09/2026 · NIU : M000000000000D · Date limite de dépôt et de paiement : '
               '15/10/2026 · État : Brouillon',
    'section': 'Sections 2 à 5 : TVA (lignes L10 à L35)',
}
