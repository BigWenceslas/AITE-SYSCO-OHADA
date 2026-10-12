# -*- coding: utf-8 -*-
"""Vidéo de présentation complète d'AITE Fiscalité OHADA (SYSCOHADA révisé pour Odoo 18).

Le parcours suit celui du guide (``docs/guide/guide.md``) et de la recette de
la base de formation : constat, solution, installation, paramétrage, saisie,
états financiers, déclaration mensuelle, clôture et DSF, qualité. Chaque
libellé à l'écran vient des vues des modules ou d'une capture du guide ;
chaque montant, d'une capture ou du calcul des modules (``demo.py``) ; chaque
règle dite par la voix, du guide, du lisez-moi ou du document de travail.

La voix est écrite comme elle se dit : « Aïté » pour AITE, « Ohada »,
« I T V A I R », « D G I » (voir ``README.md``, prononciation).
"""

import demo
from ecrans import (apps, barre, bouton, bouton_smart, champs, cp_fiche, cp_liste, deroulant, e, fenetre, feuille,
                    interrupteur, liste, mis, notification, onglets, papier, pastille, statut, tableau,
                    tableau_de_bord, tag, totaux, vue)
from moteur import (anneau, apparaitre, cacher, choisir_menu, clic, classe, defiler, menu, montrer, notifier, pause,
                    survol, vue as aller)

# ------------------------------------------------------------------ outils --

def _items(sections):
    """La position de chaque élément d'un menu déroulant, dans l'ordre d'affichage."""
    return [it for _titre, items in sections for it in items]


ANALYSE = _items(demo.MENU_ANALYSE)
CONFIGURATION = _items(demo.MENU_CONFIGURATION)


def assistant_etats(p, calcule):
    """L'assistant « États et contrôles » (capture 04), exercice 2025 du bar-hôtel ;
    ``calcule`` : onglets et contrôles déjà affichés (sinon masqués, révélés par Calculer)."""
    lignes = [('%s-ctl-%d' % (p, k), [code, lib, 'Conforme', detail], 'vert')
              for k, (code, lib, detail) in enumerate(demo.CONTROLES)]
    resultats = ('<div id="%s-res"%s>%s%s</div>' % (
        p, '' if calcule else ' class="masque"',
        onglets(p + '-og', ['Contrôles', 'Bilan actif', 'Bilan passif', 'Compte de résultat', 'Flux de trésorerie']),
        tableau(p + '-ctl', [('Contrôle', '200px', 'g'), ('Libellé', '590px', 'g'), ('Résultat', '120px', 'g'),
                             ('Détail', '1fr', 'g')], lignes, classe='controles')))
    contenu = (champs([('Société', demo.SOCIETE), ('Exercice N-1', ('<span class="case-cochee"></span>',))],
                      [('Du', '01/01/2025'), ('Au', '31/12/2025')], larg_g=170, larg_d=80, ident=p + '-ch')
               + resultats)
    return (cp_fiche('États et contrôles', 'États et contrôles')
            + barre(p + '-barre', [[bouton(p + '-calc', 'Calculer')]], '')
            + feuille(contenu))


def fiche_facture(p, f, onglet=0, lignes_html=''):
    """Une facture comptabilisée (captures 16, 17, 18)."""
    nom, adresse = f['partenaire'][1], f['partenaire'][2]
    gauche = [(f['partenaire'][0], ('<span class="lien">%s</span><br>%s' % (e(nom), '<br>'.join(e(a) for a in adresse)),))]
    if f.get('reference'):
        gauche.append(('Référence facture', f['reference']))
    droite = list(f['dates']) + [('Journal', ('%s <span class="gris-o">&nbsp;&nbsp;dans&nbsp;&nbsp;</span>'
                                              '<span class="lien">XAF</span>' % e('Factures clients' if f['type'] == 'Facture client'
                                                                                   else 'Factures fournisseurs'),))]
    if f['type'] == 'Facture client':
        boutons = [bouton(None, 'Envoyer'), bouton(None, 'Imprimer'), bouton(None, 'Payer'), bouton(None, 'Aperçu', 'clair'),
                   bouton(None, 'Avoir', 'clair'), bouton(None, 'Remettre en brouillon', 'clair')]
        smart = bouton_smart(None, 'liste', 'Paiements', '1') + bouton_smart(None, 'dollar', 'Pièces comptables de trésorerie')
    else:
        boutons = [bouton(None, 'Imprimer'), bouton(None, 'Avoir', 'clair'), bouton(None, 'Remettre en brouillon', 'clair')]
        smart = bouton_smart(None, 'liste', 'Paiements', '1')
    corps = ('<div class="f-type">%s</div><div class="f-num">%s</div>' % (e(f['type']), e(f['numero']))
             + champs(gauche, droite, larg_g=180, larg_d=190)
             + onglets(p + '-og', ['Lignes de facture', 'Écritures comptables', 'Autres informations'], onglet)
             + lignes_html)
    return (cp_fiche(None, f['fil'], smart=smart)
            + barre(p + '-barre', [boutons], statut(p + '-st', ['Brouillon', 'Comptabilisé'], 1))
            + feuille(corps, ruban=f['ruban']))


def ligne_facture(p, f, totaux_html):
    produit, compte, qte, prix, taxe, montant = f['ligne']
    t = tableau(p + '-lignes', [('Produit', '330px', 'g'), ('Compte', '1fr', 'g'), ('Quantité', '110px', 'd'),
                                ('Prix', '150px', 'd'), ('Taxes', '330px', 'g'), ('Montant', '170px', 'd')],
                [(p + '-l1', [produit, compte, qte, prix, (tag(taxe, p + '-taxe'),), montant], 'italique')])
    return t + totaux_html


# ===================================================================== écrans

# --- ouverture : l'assistant calculé, en vitrine
ECRAN_OUVERTURE = fenetre('w0', [vue('w0-wiz', assistant_etats('w0', True), initiale=True)])

# --- installation : Apps filtré sur « SYSCOHADA » (capture 01)
M = demo.MODULES
CARTES_APPS = [
    (None, M['community'][0], M['community'][1], M['community'][2], False),
    (None, M['base'][0], M['base'][1], M['base'][2], False),
    (None, M['demo'][0], M['demo'][1], M['demo'][2], False),
    (None, 'aite_syscohada_demo_common', 'SYSCOHADA révisé – moteur des données de démonstration',
     'Moteur commun des sociétés de démonstration (bar-hôtel, services informatiques) : création de la société et de '
     'ses pièces par lots, paie, amortissements, déclarations I/TVA-IR, clôture. Ne crée rien à lui seul.', False),
    (None, M['services'][0], M['services'][1], M['services'][2], False),
    (None, M['mis'][0], M['mis'][1], M['mis'][2], False),
    (None, M['reports'][0], M['reports'][1], M['reports'][2], True),
    (None, 'l10n_syscohada', 'OHADA - Comptabilité', '', False),
]
ECRAN_APPS = fenetre('w5', [vue('w5-apps', apps(CARTES_APPS, 'w5-grille'), initiale=True)], app='Apps', menus=['Apps'])

# --- paramétrage (captures 22, 20, 21)
W1_DD = deroulant('w1-dd', demo.MENU_CONFIGURATION)
TB1 = vue('w1-tb', cp_liste('Tableau de bord', [(None, 'Favoris')], '1-7 / 7', nouveau=False)
          + tableau_de_bord(demo.TABLEAU_DE_BORD), initiale=True)
PLAN = vue('w1-plan', cp_liste('Plan comptable', [(None, 'Compte actif'), ('Compte', '447')], '1-21 / 21', large=520)
           + '<div class="panneau-g"><b>Tous</b><div style="margin-top:8px">▸ 4</div></div>'
           + '<div class="defil-liste" id="w1-plan-defil">%s</div>' % liste('w1-plan-l', [
               ('Code', '110px', 'g'), ('Nom du compte', '1fr', 'g'), ('Type', '220px', 'g'),
               ('Autoriser le lettrage', '200px', 'g'), ('Devise du compte', '170px', 'g'), ('Sociétés', '230px', 'g')],
               [{'id': 'w1-c-%s' % code, 'classe': 'nouveau' if nouveau else '',
                 'cellules': [code, nom, 'Dettes à court terme', (interrupteur(False),), '', (tag(demo.SOCIETE),)]}
                for code, nom, nouveau in demo.COMPTES_447]))
TAXES = vue('w1-taxes', cp_liste('Taxes', [(None, 'Ventes ou Achats'), ('Nom', 'valider')], '1-10 / 10', large=540)
            + liste('w1-tx-l', [('Nom de la taxe', '560px', 'g'), ('Description', '1fr', 'g'), ('Type de taxe', '140px', 'g'),
                                ('Portée de la taxe', '150px', 'g'), ('Libellé sur les factures', '170px', 'g'),
                                ('Société', '170px', 'g'), ('Actif', '70px', 'g')],
                    [{'id': 'w1-tx-%d' % k, 'classe': '' if actif else 'attenue',
                      'cellules': [nom, desc, typ, '', '', demo.SOCIETE, (interrupteur(actif),)]}
                     for k, (nom, desc, typ, actif) in enumerate(demo.TAXES)]))
ECRAN_PARAM = fenetre('w1', [TB1, PLAN, TAXES], deroulants={5: W1_DD},
                      calques=notification('w1-notif', 'SYSCOHADA', 'Paramétrage appliqué.'))
I_APPLIQUER, I_PLAN, I_TAXES = (CONFIGURATION.index(x) for x in ('Appliquer le paramétrage', 'Plan comptable', 'Taxes'))

# --- saisie (captures 16, 17, 18)
N, L, G = demo.NUITEES, demo.LOYER, demo.LOGICIEL
TOT_NUIT = totaux([(l, v, '', None) for l, v in N['totaux']] + [('Total:', N['total'], 'total', None),
                   (N['paye'][0], N['paye'][1], 'paye', 'w2-n-paye'), ('Montant dû:', N['du'], 'du', 'w2-n-du')])
TOT_LOYER = totaux([(N_l, v, '', 'w2-l-ret' if v.startswith('-') else None) for N_l, v in L['totaux']]
                   + [('Total:', L['total'], 'total', 'w2-l-total'), (L['paye'][0], L['paye'][1], 'paye', None)])
ECRITURES_LOG = tableau('w2-g', [('Compte', '600px', 'g'), ('Libellé', '1fr', 'g'), ('Débit', '160px', 'd'),
                                 ('Crédit', '160px', 'd'), ('Grilles de taxes', '170px', 'g')],
                        [('w2-g-%d' % k, [c, lib, d, cr, (tag(g),) if g else ''], '')
                         for k, (c, lib, d, cr, g) in enumerate(G['ecritures'])]
                        + [(None, ['', '', G['total'][0], G['total'][1], ''], 'total')])
ECRAN_SAISIE = fenetre('w2', [
    vue('w2-nuit', fiche_facture('w2-n', N, 0, ligne_facture('w2-n', N, TOT_NUIT)), initiale=True),
    vue('w2-loyer', fiche_facture('w2-l', L, 0, ligne_facture('w2-l', L, TOT_LOYER))),
    vue('w2-log', fiche_facture('w2-g', G, 1, ECRITURES_LOG)),
])

# --- états financiers (captures 02, 03, 04, 06, 08, 09)
W3_DD = deroulant('w3-dd', demo.MENU_ANALYSE)
ECRAN_ETATS = fenetre('w3', [
    vue('w3-tb', cp_liste('Tableau de bord', [(None, 'Favoris')], '1-7 / 7', nouveau=False)
        + tableau_de_bord(demo.TABLEAU_DE_BORD), initiale=True),
    vue('w3-wiz', assistant_etats('w3', False)),
    vue('w3-actif', mis('w3-ma', 'SYSCOHADA – Bilan actif', [('Exercice N', 3), ('Exercice N-1', 3)],
                        ['Brut', 'Amort. et dépréc.', 'Net'] * 2, demo.BILAN_ACTIF)),
    vue('w3-cr', mis('w3-mr', 'SYSCOHADA – Compte de résultat', [('Exercice N', 1), ('Exercice N-1', 1)], ['', ''],
                     demo.COMPTE_RESULTAT)),
    vue('w3-tft', mis('w3-mf', 'SYSCOHADA – Tableau des flux de trésorerie', [('Exercice N', 1), ('Exercice N-1', 1)],
                      ['', ''], demo.FLUX)),
], deroulants={4: W3_DD})
I_ETATS, I_ACTIF, I_CR, I_TFT = (ANALYSE.index(x) for x in ('États et contrôles (AITE)', 'Bilan actif', 'Compte de résultat',
                                                            'Tableau des flux de trésorerie'))

# --- déclaration mensuelle (captures 10, 11, 13, 14 ; liquidation calculée)
D = demo.DECLARATION
LISTE_DECL = liste('w4-l', [('Déclaration', '250px', 'g'), ('Société', '235px', 'g'), ('L28 – TVA collectée', '145px', 'd'),
                            ('L29 – TVA déductible', '145px', 'd'), ('L32 – TVA à payer', '145px', 'd'),
                            ('L35 – Crédit à reporter', '115px', 'd'), ('Total à payer', '145px', 'd'),
                            ('Date limite de dépôt et de paiement', '120px', 'g'), ('Écriture de liquidation', '1fr', 'g'),
                            ('État', '105px', 'g')],
                   [{'id': 'w4-r%d' % k, 'cellules': list(r[:9]) + [(pastille(r[9], 'gris' if r[9] == 'Brouillon' else 'vert'),)]}
                    for k, r in enumerate(demo.DECLARATIONS)], classe='serree')
TVA = tableau('w4-tva', [('Ligne', '1fr', 'g'), ('Base', '220px', 'd'), ('Taxe', '220px', 'd')],
              [(None, [l, b, t], 'sec' if sec else '') for l, b, t, sec in D['tva']])
RET = tableau('w4-ret', [('Section', '175px', 'g'), ('Ligne', '52px', 'g'), ('Libellé', '1fr', 'g'), ('Base saisie', '100px', 'd'),
                         ('Taux ou tarif', '100px', 'd'), ('Montant saisi', '110px', 'd'), ('Pénalités', '90px', 'd'),
                         ('Base', '140px', 'd'), ('Principal', '130px', 'd'), ('CAC', '105px', 'd'), ('Total', '130px', 'd')],
              [('w4-%s' % code, [sec, code, lib, '0 FCFA', taux, '0 FCFA', '0 FCFA', base, princ, cac, tot], cl)
               for sec, code, lib, taux, base, princ, cac, tot, cl in demo.RETENUES], classe='serree')
FORM_DECL = (cp_fiche('Déclarations de TVA (Cameroun)', D['nom'], smart=bouton_smart('w4-sb', 'livre', 'Écriture', masque=True))
             + barre('w4-barre', [[bouton('w4-calc', 'Calculer'), bouton('w4-liq', "Passer l'écriture de liquidation", 'clair'),
                                   bouton('w4-val', 'Valider', 'clair')],
                                  [bouton('w4-calc2', 'Calculer'), bouton('w4-val2', 'Valider', 'clair')],
                                  [bouton('w4-brou', 'Remettre en brouillon', 'clair')]],
                     statut('w4-st', ['Brouillon', 'Validée'], 0))
             + feuille('<div class="defil-fiche" id="w4-defil"><div class="f-num">%s</div>%s%s'
                       '<div class="panneaux"><div id="w4-p0">%s</div><div id="w4-p1" class="masque">%s</div></div></div>'
                       % (e(D['nom']), champs(D['gauche'], [(l, v, 'w4-%s' % ('total' if l == 'Total à payer' else
                                                                              'date' if l.startswith('Date') else 'v%d' % k),
                                                             l == 'Total à payer')
                                                            for k, (l, v) in enumerate(D['droite'])],
                                              larg_g=120, larg_d=280, ident='w4-ch'),
                          onglets('w4-og', ['Déclaration I/TVA-IR', 'Retenues, acomptes, IRCM, salaires',
                                            'Saisies du déclarant']), TVA, RET)))
Q = demo.LIQUIDATION
FORM_MOVE = (cp_fiche(D['nom'], '%s (%s)' % (Q['nom'], Q['reference']))
             + barre('w4-mb', [[bouton(None, "Écriture d'extourne", 'clair'), bouton(None, 'Remettre en brouillon', 'clair')]],
                     statut('w4-mst', ['Brouillon', 'Comptabilisé'], 1))
             + feuille('<div class="f-num">%s</div>%s%s%s' % (
                 e(Q['nom']), champs([('Référence', Q['reference'])], [('Date comptable', Q['date']), ('Journal', Q['journal'])],
                                     larg_g=140, larg_d=190),
                 onglets('w4-mog', ['Écritures comptables', 'Autres informations']),
                 tableau('w4-m', [('Compte', '1fr', 'g'), ('Partenaire', '130px', 'g'), ('Libellé', '520px', 'g'),
                                  ('Débit', '170px', 'd'), ('Crédit', '170px', 'd'), ('Grilles de taxes', '150px', 'g')],
                         [('w4-m-%d' % k, [c, '', lib, d, cr, ''], '') for k, (c, lib, d, cr) in enumerate(Q['lignes'])]
                         + [(None, ['', '', '', Q['total'], Q['total'], ''], 'total')]))))
I = demo.IMPRIME
PAPIER = papier('w4-papier', 'aite_syscohada_demo', I['adresse'], I['titre'], I['periode'], I['section'],
                [(l, b, t, sec) for l, b, t, sec in D['tva']])
ECRAN_DECL = fenetre('w4', [
    vue('w4-liste', cp_liste('Déclarations de TVA (Cameroun)', [], '1-42 / 42') + LISTE_DECL, initiale=True),
    vue('w4-form', FORM_DECL),
    vue('w4-move', FORM_MOVE),
], calques=PAPIER)


# =================================================================== scénario

SCENARIO = {
    'slug': 'aite-fiscalite-ohada-presentation',
    'titre': 'AITE Fiscalité OHADA — présentation de la solution',
    'scenes': [
        {'type': 'signature', 'id': 'sig', 'marque': 'AITE Fiscalité OHADA', 'sous': 'SYSCOHADA révisé · Odoo 18'},

        {'type': 'vitrine', 'id': 'ouv', 'grand': True, 'fenetre': 'w0', 'ecran': ECRAN_OUVERTURE,
         'kicker': 'AITE Consulting · Transformation digitale', 'titre': 'AITE Fiscalité OHADA',
         'texte': "Le SYSCOHADA révisé et la fiscalité camerounaise, au cœur d'Odoo 18 Community.",
         'voix': "Aïté Fiscalité Ohada rend Odoo dix-huit conforme au SYSCOHADA révisé et à la fiscalité "
                 "camerounaise : des états financiers à la déclaration mensuelle, sans quitter Odoo."},

        {'type': 'cartes', 'id': 'constat', 'kicker': 'Le constat',
         'titre': 'Odoo 18 livre le plan comptable, pas les obligations.',
         'cartes': [
             ('Odoo 18', 'Le plan SYSCOHADA : oui',
              'Plan révisé de 1 134 comptes et TVA à 19,25 %, livrés par la localisation camerounaise.'),
             ('Édition Community', 'Les états financiers : non',
              'Ni bilan, ni compte de résultat, ni tableau des flux au format SYSCOHADA.'),
             ('Déclaration DGI', 'La déclaration mensuelle : non',
              'Les lignes L10 à L35 sont définies, sans écran ; rien pour les retenues, les acomptes et les impôts sur salaires.'),
         ],
         'voix': "Odoo dix-huit livre le plan SYSCOHADA révisé et la TVA à dix-neuf virgule vingt-cinq pour cent. "
                 "Mais en édition Community, il n'y a ni bilan, ni compte de résultat, ni tableau des flux au format "
                 "SYSCOHADA. Et pour la déclaration mensuelle, aucun écran : ni pour la TVA, ni pour les retenues et "
                 "les acomptes."},

        {'type': 'chiffres', 'id': 'solution', 'kicker': 'La solution',
         'titre': "AITE Fiscalité OHADA comble l'écart, dans Odoo 18 Community.",
         'chiffres': [
             {'affiche': '124', 'compte': 124, 'libelle': '<b>rubriques</b> des états : une seule source pour tous les calculs'},
             {'affiche': '4', 'compte': 4, 'libelle': '<b>états</b> : bilan actif, bilan passif, compte de résultat, tableau des flux'},
             {'affiche': '9', 'compte': 9, 'libelle': '<b>contrôles</b> de cohérence, du rattachement des comptes aux bascules'},
             {'affiche': 'L0 → L80', 'libelle': 'toute la <b>déclaration I/TVA-IR</b> : TVA, retenues, acomptes, IRCM, salaires'},
             {'affiche': '112', 'compte': 112, 'libelle': '<b>tests automatiques</b>, montants attendus calculés à la main'},
             {'affiche': '0', 'libelle': '<b>dépendance</b> à Odoo Enterprise'},
         ],
         'voix': "Un référentiel unique de cent vingt-quatre rubriques alimente les quatre états financiers. Neuf "
                 "contrôles vérifient leur cohérence. La déclaration mensuelle couvre tout le formulaire, de la ligne "
                 "zéro à la ligne quatre-vingts. Et cent douze tests automatiques vérifient le tout, sans aucune "
                 "dépendance à Odoo Enterprise."},

        {'type': 'cartes', 'id': 'modules', 'kicker': 'Architecture', 'titre': 'Trois modules, un seul à installer.',
         'cartes': [
             ('Le socle', 'Référentiel et contrôles',
              '<code>aite_syscohada_base</code> : 124 rubriques, moteur de calcul, paramétrage du plan et des taxes, '
              '9 contrôles, assistant « États et contrôles (AITE) ».'),
             ('Les états', 'MIS Builder',
              '<code>aite_syscohada_mis</code> : les quatre états en modèles MIS Builder, générés depuis le référentiel.'),
             ("L'adaptation Community", 'Menus et déclaration',
              '<code>aite_syscohada_community</code> : menus Syscohada en un clic, déclaration I/TVA-IR complète, '
              'écriture de liquidation, impression.'),
         ],
         'note': "<b>Sur Odoo Enterprise</b>, le module facultatif aite_syscohada_reports rend les mêmes états dans le "
                 "moteur de rapports natif. <b>Pour la formation</b>, deux sociétés de démonstration.",
         'voix': "La solution tient en trois modules. Le socle porte le référentiel, le moteur de calcul, le paramétrage "
                 "et les contrôles. Les états prennent forme dans M I S Bildeur. L'adaptation Community ajoute les menus "
                 "et la déclaration mensuelle. Sur Enterprise, un module facultatif rend les mêmes états dans le moteur "
                 "de rapports natif."},

        {'type': 'vitrine', 'id': 'install', 'fenetre': 'w5', 'ecran': ECRAN_APPS,
         'kicker': 'Installation', 'titre': 'Prêt en quelques minutes',
         'puces': ['Un seul paquet zip : modules AITE et OCA dans un même dossier addons/',
                   'Dans Apps, installer « SYSCOHADA révisé – adaptation Odoo Community (Cameroun) »',
                   'Le paramétrage s\'applique tout seul aux sociétés au plan « cm »'],
         'voix': "Tout est livré dans un seul paquet. Dans Apps, on installe l'adaptation Community : le socle et les "
                 "états suivent, et le paramétrage s'applique tout seul aux sociétés au plan camerounais."},

        # ------------------------------------------------------- paramétrage
        {'type': 'chapitre', 'id': 'ch1', 'numero': '01', 'titre': 'Le paramétrage',
         'sous': 'Plan « cm », sous-comptes et taxes camerounaises', 'voix': 'Premier temps : le paramétrage.'},
        {'type': 'ecran', 'id': 'param', 'fenetre': 'w1', 'ecran': ECRAN_PARAM, 'vue_initiale': 'w1-tb', 'etapes': [
            {'titre': 'Appliquer le paramétrage',
             'texte': "Facturation > Configuration > SYSCOHADA. Sans risque : rien de ce qui porte des écritures n'est modifié.",
             'voix': "Le menu Appliquer le paramétrage corrige les libellés et les types de comptes, crée les sous-comptes "
                     "et les taxes qui manquent. On peut le relancer sans risque : rien de ce qui porte déjà des écritures "
                     "n'est modifié.",
             'gestes': [*menu('w1', 5, 'w1-dd'), pause(0.6), *choisir_menu('w1', 5, 'w1-dd', I_APPLIQUER),
                        notifier('w1-notif', duree=4.2), anneau('#w1-notif', d=1.8, decale=0.3)]},
            {'titre': 'Un compte par retenue',
             'texte': 'Seize sous-comptes du 447 : chaque retenue et chaque impôt sur salaire de la déclaration a le sien.',
             'voix': "Chaque retenue et chaque impôt sur salaire reçoit son propre compte : seize sous-comptes du 447, "
                     "de l'impôt sur les revenus des capitaux mobiliers à la taxe de développement local.",
             'gestes': [*menu('w1', 5, 'w1-dd'), *choisir_menu('w1', 5, 'w1-dd', I_PLAN), aller('w1-plan', 'w1'),
                        pause(0.4), classe('#w1-plan .nouveau', ajouter=['surligne']), pause(1.2),
                        defiler('#w1-plan-defil', -240, d=1.2), anneau('#w1-c-447210', d=1.4)]},
            {'titre': 'Des taux à valider',
             'texte': "Retenues et précomptes « (taux à valider) » : inactifs tant que l'expert-comptable n'a pas confirmé le taux.",
             'voix': "Les retenues à la source sont livrées marquées taux à valider. Dans une société réelle, elles restent "
                     "inactives tant que l'expert-comptable n'a pas confirmé leur taux ; la démonstration en active six.",
             'gestes': [*menu('w1', 5, 'w1-dd'), *choisir_menu('w1', 5, 'w1-dd', I_TAXES), aller('w1-taxes', 'w1'),
                        pause(0.5), anneau('#w1-tx-1', d=1.6), anneau('#w1-tx-4', d=1.6)]},
        ]},

        # ------------------------------------------------------------ saisie
        {'type': 'chapitre', 'id': 'ch2', 'numero': '02', 'titre': 'La saisie quotidienne',
         'sous': 'La TVA au bon moment, chaque retenue sur son compte', 'voix': 'Deuxième temps : la saisie quotidienne.'},
        {'type': 'ecran', 'id': 'saisie', 'fenetre': 'w2', 'ecran': ECRAN_SAISIE, 'vue_initiale': 'w2-nuit', 'etapes': [
            {'titre': 'TVA sur encaissement',
             'texte': 'Taxe « 19,25 % S (encaissement) » : seule la TVA des sommes encaissées entre dans la déclaration du mois.',
             'voix': "Une facture de nuitées porte la TVA sur encaissement. Huit dixièmes sont encaissés le trente "
                     "septembre : seule la TVA de cette part entre dans la déclaration du mois.",
             'gestes': [pause(0.4), anneau('#w2-n-taxe', d=1.8), anneau('#w2-n-paye', d=1.6), anneau('#w2-n-du', d=1.5)]},
            {'titre': 'Précompte sur loyer',
             'texte': "90 000 retenus sur 600 000, reversés à l'État en ligne L42 ; 510 000 payés au bailleur.",
             'voix': "Sur un loyer, le précompte de quinze pour cent est retenu dès la facture : quatre-vingt-dix mille "
                     "francs, reversés à l'État en ligne L quarante-deux.",
             'gestes': [aller('w2-loyer', 'w2'), pause(0.4), anneau('#w2-l-taxe', d=1.6), anneau('#w2-l-ret', d=1.6),
                        anneau('#w2-l-total', d=1.4)]},
            {'titre': 'Fournisseur étranger',
             'texte': 'TVA autoliquidée de 57 750 (445400 et 447161), TSR de 15 % retenue sur 447120.',
             'voix': "Un logiciel facturé depuis Londres : la TVA est autoliquidée, au débit et au crédit, et la taxe "
                     "spéciale sur le revenu est retenue sur son compte dédié.",
             'gestes': [aller('w2-log', 'w2'), pause(0.4), anneau('#w2-g-2', d=1.4), anneau('#w2-g-3', d=1.4),
                        anneau('#w2-g-1', d=1.6)]},
        ]},

        # ------------------------------------------------------------- états
        {'type': 'chapitre', 'id': 'ch3', 'numero': '03', 'titre': 'Les états financiers',
         'sous': 'Bilan, compte de résultat, tableau des flux : en un clic', 'voix': 'Troisième temps : les états financiers.'},
        {'type': 'ecran', 'id': 'etats', 'fenetre': 'w3', 'ecran': ECRAN_ETATS, 'vue_initiale': 'w3-tb', 'etapes': [
            {'titre': 'Le menu Syscohada',
             'texte': 'Facturation > Analyse > Syscohada : assistant, quatre états MIS Builder, déclarations de TVA.',
             'voix': "Le menu Analyse regroupe la section Syscohada : l'assistant États et contrôles, les quatre états, "
                     "et les déclarations de TVA.",
             'gestes': [*menu('w3', 4, 'w3-dd'), pause(1.4), *choisir_menu('w3', 4, 'w3-dd', I_ETATS),
                        aller('w3-wiz', 'w3')]},
            {'titre': 'Neuf contrôles',
             'texte': 'Exercice 2025 du bar-hôtel : actif = passif, résultat, trésorerie… tout est conforme.',
             'voix': "On choisit la période, puis on clique sur Calculer. Neuf contrôles s'affichent : équilibre du bilan, "
                     "résultat, trésorerie, comptes d'attente, caisses. Ici, tout est conforme : le total de l'actif égale "
                     "celui du passif.",
             'gestes': [anneau('#w3-ch-d', d=1.2), clic('#w3-calc'), montrer('#w3-res', y=0, d=0.3),
                        apparaitre('#w3-res .t-ligne', 9, d=0.35, decalage=0.12, avec=True),
                        pause(0.6), anneau('#w3-ctl-2', d=2.0)]},
            {'titre': 'Le bilan actif',
             'texte': 'Exercices N et N-1 ; brut, amortissements et dépréciations, net ; un clic sur un montant ouvre ses écritures.',
             'voix': "Les états s'ouvrent dans M I S Bildeur : exercice N et exercice N moins un côte à côte, brut, "
                     "amortissements et net. Un clic sur un montant ouvre ses écritures.",
             'gestes': [*menu('w3', 4, 'w3-dd'), *choisir_menu('w3', 4, 'w3-dd', I_ACTIF), aller('w3-actif', 'w3'),
                        pause(0.5), anneau('#w3-ma-r5', d=2.0)]},
            {'titre': 'Imprimer, exporter',
             'texte': 'Compte de résultat : « Imprimer » donne le PDF, « Export » le fichier Excel.',
             'voix': "Le compte de résultat suit le même modèle. Chaque état s'imprime en PDF ou s'exporte vers Excel.",
             'gestes': [*menu('w3', 4, 'w3-dd'), *choisir_menu('w3', 4, 'w3-dd', I_CR), aller('w3-cr', 'w3'),
                        pause(0.4), anneau('#w3-mr-r7', d=1.4), anneau('#w3-mr-impr', d=1.0), anneau('#w3-mr-exp', d=1.0)]},
            {'titre': 'Le tableau des flux',
             'texte': "Trésorerie nette au 1er janvier 2026 (ZA) : 21 148 110, la clôture 2025 de l'assistant.",
             'voix': "Dans le tableau des flux, la trésorerie d'ouverture égale la trésorerie de clôture calculée par "
                     "l'assistant pour l'exercice précédent.",
             'gestes': [*menu('w3', 4, 'w3-dd'), *choisir_menu('w3', 4, 'w3-dd', I_TFT), aller('w3-tft', 'w3'),
                        pause(0.4), anneau('#w3-mf-r0', d=2.0)]},
        ]},

        # ------------------------------------------------------- déclaration
        {'type': 'chapitre', 'id': 'ch4', 'numero': '04', 'titre': 'La déclaration mensuelle I/TVA-IR',
         'sous': 'Calculée, liquidée, imprimée, validée',
         'voix': 'Quatrième temps : la déclaration mensuelle I T V A I R.'},
        {'type': 'ecran', 'id': 'decl', 'fenetre': 'w4', 'ecran': ECRAN_DECL, 'vue_initiale': 'w4-liste', 'etapes': [
            {'titre': 'Une déclaration par mois',
             'texte': 'Une par société : septembre 2026 est encore en brouillon.',
             'voix': "Chaque mois, une déclaration par société, liquidée puis validée. Celle de septembre est encore en "
                     "brouillon : ouvrons-la.",
             'gestes': [pause(0.3), anneau('#w4-r3', d=1.3), survol('#w4-r1', decale=0.2), clic('#w4-r1', fx=0.1),
                        aller('w4-form', 'w4')]},
            {'titre': 'Calculer',
             'texte': 'TVA collectée, déductible, à payer, acompte : 1 068 786 FCFA à payer avant le 15/10/2026.',
             'voix': "Calculer lit les écritures du mois : TVA collectée, TVA déductible, TVA à payer et acompte d'impôt. "
                     "Le total à payer s'affiche avec sa date limite, le quinze octobre.",
             'gestes': [clic('#w4-calc'), anneau('#w4-ch-d', d=1.8), anneau('#w4-total', d=1.3), anneau('#w4-date', d=1.2)]},
            {'titre': 'Retenues, acomptes, IRCM, salaires',
             'texte': "Le reste du formulaire : précomptes à reverser (L42), précomptes subis (L46), acompte de 2 % (L50, L54).",
             'voix': "Le second onglet couvre le reste du formulaire : précomptes sur loyers et sur honoraires à reverser, "
                     "précomptes subis, et l'acompte sur le chiffre d'affaires, diminué des précomptes subis.",
             'gestes': [clic('#w4-og-1'), classe('#w4-og-0', retirer=['actif'], avec=True),
                        classe('#w4-og-1', ajouter=['actif'], avec=True), cacher('#w4-p0', d=0.2, avec=True),
                        montrer('#w4-p1', y=0, d=0.3), defiler('#w4-defil', -440, d=1.2),
                        anneau('#w4-L42', d=1.2), anneau('#w4-L46', d=1.2), defiler('#w4-defil', -720, d=1.0),
                        anneau('#w4-L50', d=1.2), anneau('#w4-L54', d=1.4)]},
            {'titre': "L'écriture de liquidation",
             'texte': 'Comptes 443 et 445 soldés vers la TVA due (444100) ; acompte en 449250 contre 441100.',
             'voix': "Passer l'écriture de liquidation solde les comptes de TVA du mois vers la TVA due, et constate "
                     "l'acompte à payer. Le compte d'attente des prestations non encaissées n'est pas touché.",
             'gestes': [defiler('#w4-defil', 0, d=0.9), clic('#w4-liq'), cacher('#w4-barre-g0', d=0.2),
                        montrer('#w4-barre-g1', y=0, d=0.25, avec=True), montrer('#w4-sb', y=0, d=0.3, avec=True),
                        pause(0.3), clic('#w4-sb'), aller('w4-move', 'w4'), pause(0.4),
                        anneau('#w4-m-4', d=1.5), anneau('#w4-m-5', d=1.4)]},
            {'titre': 'Imprimer, puis valider',
             'texte': "Document de travail pour le portail de la DGI ; validée, la déclaration fonde les reports du mois suivant.",
             'voix': "Le document de travail s'imprime, tableau par tableau, pour la saisie sur le portail de la D G I. "
                     "Puis Valider fige la déclaration : c'est d'elle que partiront les reports de crédit du mois suivant.",
             'gestes': [aller('w4-form', 'w4'), pause(0.3), montrer('#w4-papier', y=40, d=0.5), pause(3.2),
                        cacher('#w4-papier', d=0.35), clic('#w4-val2'), cacher('#w4-barre-g1', d=0.2),
                        montrer('#w4-barre-g2', y=0, d=0.25, avec=True), classe('#w4-st-0', retirer=['actif'], avec=True),
                        classe('#w4-st-1', ajouter=['actif'], avec=True), anneau('#w4-st', d=1.4)]},
        ]},

        # --------------------------------------------------------- DSF, qualité
        {'type': 'cartes', 'id': 'dsf', 'kicker': 'Clôture et DSF', 'titre': 'Prêt pour la DSF, et la suite déjà tracée.',
         'cartes': [
             ('Clôture', 'Les quatre états en N et N-1', 'Les valeurs à reporter dans les onglets du classeur DSF de la DGI.'),
             ('DSF', 'Chaque rubrique connaît sa cellule',
              'Onglet, cellule N, cellule N-1 et signe : la correspondance est déjà dans le référentiel.'),
             ('Feuille de route', 'La suite',
              'Notes annexes, remplissage du classeur DSF, paie camerounaise, dépôt par API, facture électronique.'),
         ],
         'voix': "À la clôture, l'assistant fournit les quatre états en exercice N et N moins un : ce sont les valeurs à "
                 "reporter dans le classeur de la DSF, et chaque rubrique connaît déjà sa cellule. La suite est tracée : "
                 "notes annexes, remplissage du classeur, paie camerounaise, dépôt par l'API de la D G I et facture "
                 "électronique."},

        {'type': 'chiffres', 'id': 'qualite', 'kicker': 'Qualité', 'titre': 'Vérifié, démontré, documenté.',
         'chiffres': [
             {'affiche': '112', 'compte': 112, 'libelle': '<b>tests automatiques</b> à chaque version, 0 échec'},
             {'affiche': '2', 'compte': 2, 'libelle': '<b>sociétés de démonstration</b> : un bar-hôtel, une société de services informatiques'},
             {'affiche': '21', 'compte': 21, 'libelle': "<b>mois d'activité</b> rejoués : pièces, paie, déclarations, clôture"},
             {'affiche': '34', 'compte': 34, 'libelle': '<b>tests</b> des données de démonstration'},
             {'affiche': '27', 'compte': 27, 'libelle': '<b>captures</b> dans le guide illustré'},
             {'affiche': '1', 'compte': 1, 'libelle': '<b>paquet</b> unique : modules AITE et OCA, guide, lisez-moi'},
         ],
         'voix': "Cent douze tests automatiques vérifient chaque montant, calculé à la main, à chaque version. Deux "
                 "sociétés de démonstration, un bar-hôtel et une société de services informatiques, rejouent vingt et "
                 "un mois d'activité. Et un guide illustré accompagne chaque écran."},

        {'type': 'fin', 'id': 'fin', 'titre': '<span class="ac">AITE</span> Fiscalité OHADA',
         'sous': "Le SYSCOHADA révisé et la fiscalité camerounaise, au cœur d'Odoo 18",
         'contact': '<b>AITE Consulting</b> · Makepe, Bloc F — Douala, Cameroun<br>'
                    'www.aite-consulting.com · info@aite-consulting.com · (+237) 656 80 10 98',
         'pied': 'AITE Consulting · Transformation digitale',
         'voix': "Aïté Fiscalité Ohada : vos obligations SYSCOHADA, au cœur d'Odoo. Aïté Consulting, à Douala."},
    ],
    'vignette': {'scene': 'decl', 'etape': 2, 'apres': 3.0},
}
