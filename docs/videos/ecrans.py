# -*- coding: utf-8 -*-
"""Les écrans d'Odoo 18 Community, rejoués en HTML pour la vidéo.

Aucune capture d'écran dans la vidéo : chaque écran est reconstruit avec les
couleurs d'Odoo 18 Community (violet ``$o-community-color`` #71639e,
``web/static/src/scss/primary_variables.scss``) et les libellés exacts que
l'application affiche (vues des modules AITE, captures du guide). Les
captures de ``docs/guide/captures`` n'ont servi que de modèle visuel.

Chaque fonction rend une chaîne HTML. Les identifiants servent de cibles au
curseur et aux gestes : uniques dans la vidéo (préfixer par la fenêtre).
"""

from html import escape as _e


def e(texte):
    return _e(str(texte), quote=True)


def _id(identifiant):
    return ' id="%s"' % identifiant if identifiant else ''


ICONES = {
    'grille': '<svg viewBox="0 0 24 24" fill="#fff"><rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9.5" y="2" width="5" height="5" rx="1"/><rect x="17" y="2" width="5" height="5" rx="1"/><rect x="2" y="9.5" width="5" height="5" rx="1"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><rect x="17" y="9.5" width="5" height="5" rx="1"/><rect x="2" y="17" width="5" height="5" rx="1"/><rect x="9.5" y="17" width="5" height="5" rx="1"/><rect x="17" y="17" width="5" height="5" rx="1"/></svg>',
    'bulle': '<svg viewBox="0 0 24 24" fill="#fff"><path d="M3 5h18v11H9l-5 4v-4H3z"/></svg>',
    'horloge': '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2.5"/></svg>',
    'loupe': '<svg viewBox="0 0 24 24" fill="none" stroke="#495057" stroke-width="2.4"><circle cx="10.5" cy="10.5" r="7"/><path d="M16 16l5 5"/></svg>',
    'filtre': '<svg viewBox="0 0 24 24" fill="#fff"><path d="M3 4h18l-7 8v7l-4 2v-9z"/></svg>',
    'engrenage': '<svg viewBox="0 0 24 24" fill="#495057"><path d="M12 8.5a3.5 3.5 0 100 7 3.5 3.5 0 000-7zm8.6 4.9l2-1.5-2-3.5-2.4.8a8 8 0 00-1.7-1L16 5.6h-4l-.5 2.6a8 8 0 00-1.7 1l-2.4-.8-2 3.5 2 1.5a8 8 0 000 2l-2 1.5 2 3.5 2.4-.8a8 8 0 001.7 1l.5 2.6h4l.5-2.6a8 8 0 001.7-1l2.4.8 2-3.5-2-1.5a8 8 0 000-2z"/></svg>',
    'fleche_bas': '<svg viewBox="0 0 24 24" fill="#495057"><path d="M6 9l6 6 6-6z"/></svg>',
    'precedent': '<svg viewBox="0 0 24 24" fill="none" stroke="#495057" stroke-width="2.4" stroke-linecap="round"><path d="M15 5l-7 7 7 7"/></svg>',
    'suivant': '<svg viewBox="0 0 24 24" fill="none" stroke="#495057" stroke-width="2.4" stroke-linecap="round"><path d="M9 5l7 7-7 7"/></svg>',
    'rafraichir': '<svg viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2.4" stroke-linecap="round"><path d="M20 11a8 8 0 10-2.3 5.7M20 4v7h-7"/></svg>',
    'imprimer': '<svg viewBox="0 0 24 24" fill="#374151"><path d="M6 2h12v6H6zM3 9h18v8h-3v5H6v-5H3zm5 6v5h8v-5z"/></svg>',
    'export': '<svg viewBox="0 0 24 24" fill="#374151"><path d="M11 3h2v9l3-3 1.5 1.5L12 16l-5.5-5.5L8 9l3 3zM4 18h16v3H4z"/></svg>',
    'livre': '<svg viewBox="0 0 24 24" fill="#71639E"><path d="M4 3h11a3 3 0 013 3v15H7a3 3 0 01-3-3zm3 15h9v-2H7z"/></svg>',
    'liste': '<svg viewBox="0 0 24 24" fill="#495057"><path d="M3 5h18v2.6H3zm0 5.7h18v2.6H3zm0 5.7h18V19H3z"/></svg>',
    'dollar': '<svg viewBox="0 0 24 24" fill="#495057"><path d="M11 2h2v2.1c2.3.3 4 1.7 4 3.9h-2.5c0-1-.9-1.7-2.5-1.7s-2.5.6-2.5 1.6c0 1 1 1.4 3 1.9 2.8.6 4.7 1.6 4.7 4.2 0 2.1-1.7 3.5-4.2 3.8V22h-2v-2.2c-2.6-.3-4.4-1.9-4.4-4.2h2.5c.1 1.2 1.1 2 2.9 2 1.7 0 2.7-.7 2.7-1.7 0-1.1-.9-1.5-3.1-2-2.6-.6-4.6-1.5-4.6-4 0-2 1.6-3.4 4-3.7z"/></svg>',
    'coche': '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
}


def icone(nom, classe='ico'):
    return '<span class="%s">%s</span>' % (classe, ICONES[nom])


def curseur_svg():
    return ('<svg id="curseur-fleche" viewBox="0 0 32 32"><path d="M5 3l20 12-9 2.2L20.5 27l-4.2 2-4.4-9.6L5 25z" '
            'fill="#fff" stroke="#1C1620" stroke-width="2" stroke-linejoin="round"/></svg>')


# ---------------------------------------------------------- la fenêtre --

MENUS = ['Tableau de bord', 'Clients', 'Fournisseurs', 'Comptabilité', 'Analyse', 'Configuration']


def fenetre(ident, vues, calques='', app='Facturation', menus=MENUS, societe='Bar-Hôtel Démo AITE', classe='',
            deroulants=None):
    """La fenêtre d'Odoo 18 : barre violette, menus de l'application, contenu.

    Les menus portent l'identifiant ``<ident>-m<n>`` (n à partir de 0) ;
    ``deroulants`` : {n: html du menu déroulant}, ancré sous le menu n."""
    deroulants = deroulants or {}
    items = ''.join('<span class="nav-menu" id="%s-m%d"><span class="nm-t">%s</span>%s</span>'
                    % (ident, i, e(m), deroulants.get(i, '')) for i, m in enumerate(menus))
    return ('<div class="app %s" id="%s"><div class="o-nav">%s<span class="nav-app">%s</span>%s'
            '<span class="nav-droite">%s<span class="nav-badge">3</span>%s<span class="nav-societe">%s</span>'
            '<span class="nav-avatar">A</span></span></div><div class="o-contenu">%s</div>%s</div>'
            % (classe, ident, icone('grille', 'nav-grille'), e(app), items, icone('bulle', 'nav-ico'),
               icone('horloge', 'nav-ico'), e(societe), ''.join(vues), calques))


def vue(ident, contenu, initiale=False, groupe=None):
    """Une vue de la fenêtre ; le geste ``vue`` passe de l'une à l'autre."""
    return '<div class="vue%s" id="%s"%s>%s</div>' % (
        ' initiale' if initiale else '', ident, ' data-groupe="%s"' % groupe if groupe else '', contenu)


# --------------------------------------------------- panneau de contrôle --

def bouton(ident, libelle, style='primaire', ico=None):
    return '<span class="btn %s"%s>%s%s</span>' % (style, _id(ident), icone(ico) if ico else '', e(libelle))


def recherche(facettes=(), ph='Rechercher...', ident=None, large=None):
    f = ''.join('<span class="facette">%s<span class="f-nom">%s</span><span class="f-val">%s</span>'
                '<span class="f-x">×</span></span>'
                % (icone('filtre', 'f-ico') if n is None else '', e(n) if n else '', e(v)) for n, v in facettes)
    return ('<div class="recherche"%s%s>%s%s<span class="ph">%s</span><span class="r-fleche">%s</span></div>'
            % (_id(ident), ' style="width:%dpx"' % large if large else '', icone('loupe', 'r-loupe'), f, e(ph),
               ICONES['fleche_bas']))


def pager(texte):
    return ('<span class="pager"><span class="p-t">%s</span><span class="p-b">%s</span><span class="p-b">%s</span></span>'
            % (e(texte), ICONES['precedent'], ICONES['suivant']))


def cp_liste(titre, facettes=(), pager_txt='', nouveau=True, ident=None, large=None, extra=''):
    return ('<div class="cp">%s<span class="cp-titre">%s %s</span>%s%s%s</div>'
            % (bouton(None, 'Nouveau') if nouveau else '', e(titre), icone('engrenage', 'cp-gear'),
               recherche(facettes, ident=ident, large=large), extra, pager(pager_txt) if pager_txt else ''))


def cp_fiche(parent, titre, pager_txt='1 / 1', smart=''):
    fil = ('<span class="fil"><span class="fil-parent">%s</span><span class="fil-titre">%s %s</span></span>'
           % (e(parent), e(titre), icone('engrenage', 'cp-gear')) if parent else
           '<span class="fil seul"><span class="fil-titre">%s %s</span></span>' % (e(titre), icone('engrenage', 'cp-gear')))
    return ('<div class="cp">%s%s<span class="smart">%s</span>%s</div>'
            % (bouton(None, 'Nouveau', 'contour'), fil, smart, pager(pager_txt)))


def cp_simple(titre, pager_txt='1 / 1'):
    return '<div class="cp"><span class="cp-titre seul">%s</span>%s</div>' % (e(titre), pager(pager_txt))


def bouton_smart(ident, ico, haut, bas=None, masque=False):
    return ('<span class="sb%s"%s>%s<span class="sb-t"><span>%s</span>%s</span></span>'
            % (' masque' if masque else '', _id(ident), icone(ico, 'sb-ico'), e(haut),
               '<span class="sb-n">%s</span>' % e(bas) if bas else ''))


# ------------------------------------------------------------------ liste --

def liste(ident, colonnes, lignes, case=True, classe=''):
    """Une vue liste. ``colonnes`` : (libellé, largeur CSS, alignement 'g'|'d') ;
    ``lignes`` : dict id, cellules (texte ou (html,)), classe."""
    gabarit = ('44px ' if case else '') + ' '.join(c[1] for c in colonnes)
    def cell(c, al):
        if isinstance(c, tuple):
            return '<span class="c %s">%s</span>' % (al, c[0])
        return '<span class="c %s ell">%s</span>' % (al, e(c))
    tete = ''.join('<span class="c %s ell">%s</span>' % ('d' if c[2] == 'd' else 'g', e(c[0])) for c in colonnes)
    corps = []
    for l in lignes:
        cells = ''.join(cell(c, 'd' if colonnes[i][2] == 'd' else 'g') for i, c in enumerate(l['cellules']))
        corps.append('<div class="l-ligne%s" id="%s" style="grid-template-columns:%s">%s%s</div>'
                     % (' ' + l['classe'] if l.get('classe') else '', l['id'], gabarit,
                        '<span class="case"></span>' if case else '', cells))
    return ('<div class="liste %s"%s><div class="l-tete" style="grid-template-columns:%s">%s%s</div>%s</div>'
            % (classe, _id(ident), gabarit, '<span class="case"></span>' if case else '', tete, ''.join(corps)))


def pastille(texte, genre='gris', ident=None):
    return '<span class="pastille %s"%s>%s</span>' % (genre, _id(ident), e(texte))


def interrupteur(actif):
    return '<span class="inter%s"><i></i></span>' % (' on' if actif else '')


def tag(texte, ident=None):
    return '<span class="tag"%s>%s</span>' % (_id(ident), e(texte))


# ------------------------------------------------------------------ fiche --

def statut(ident, etats, actif):
    return '<div class="statut"%s>%s</div>' % (_id(ident), ''.join(
        '<span class="st%s" id="%s-%d">%s</span>' % (' actif' if i == actif else '', ident, i, e(s))
        for i, s in enumerate(etats)))


def barre(ident, groupes, statut_html):
    """La barre d'actions d'une fiche : un ou plusieurs groupes de boutons
    (``<ident>-g0``, ``-g1``… ; les suivants masqués), et la barre d'état."""
    g = ''.join('<div class="b-groupe%s" id="%s-g%d">%s</div>' % ('' if i == 0 else ' masque', ident, i, ''.join(b))
                for i, b in enumerate(groupes))
    return '<div class="barre" id="%s">%s%s</div>' % (ident, g, statut_html)


def feuille(contenu, ruban=None, ident=None):
    r = '<div class="ruban"><span>%s</span></div>' % e(ruban) if ruban else ''
    return ('<div class="feuille"%s data-layout-allow-overflow data-layout-allow-occlusion>%s%s</div>'
            % (_id(ident), r, contenu))


def champs(gauche, droite, larg_g=170, larg_d=250, ident=None):
    """Deux colonnes de champs : (libellé, valeur[, identifiant[, gras]]) ;
    une valeur (html,) est posée telle quelle (adresse sur plusieurs lignes)."""
    def col(items, larg):
        return ''.join('<div class="ch"%s style="grid-template-columns:%dpx 1fr"><span class="ch-l">%s</span>'
                       '<span class="ch-v%s">%s</span></div>'
                       % (_id(i[2] if len(i) > 2 else None), larg, e(i[0]), ' gras' if len(i) > 3 and i[3] else '',
                          i[1][0] if isinstance(i[1], tuple) else e(i[1]))
                       for i in items)
    return '<div class="champs"><div class="col"%s>%s</div><div class="col"%s>%s</div></div>' % (
        _id(ident and ident + '-g'), col(gauche, larg_g), _id(ident and ident + '-d'), col(droite, larg_d))


def onglets(ident, noms, actif=0):
    return '<div class="onglets"%s>%s</div>' % (_id(ident), ''.join(
        '<span class="og%s" id="%s-%d">%s</span>' % (' actif' if i == actif else '', ident, i, e(n))
        for i, n in enumerate(noms)))


def tableau(ident, colonnes, lignes, classe=''):
    """Un tableau de lignes de fiche (lignes de facture, écritures, lignes de
    déclaration). ``colonnes`` : (libellé, largeur, 'g'|'d') ; ``lignes`` :
    (id, cellules, classe)."""
    gabarit = ' '.join(c[1] for c in colonnes)
    tete = ''.join('<span class="c %s ell">%s</span>' % (c[2], e(c[0])) for c in colonnes)
    corps = []
    for ident_l, cells, cl in lignes:
        corps.append('<div class="t-ligne %s"%s style="grid-template-columns:%s">%s</div>' % (
            cl, _id(ident_l), gabarit, ''.join(
                '<span class="c %s%s">%s</span>' % (colonnes[i][2], '' if isinstance(c, tuple) else ' ell',
                                                    c[0] if isinstance(c, tuple) else e(c))
                for i, c in enumerate(cells))))
    return '<div class="tableau %s"%s><div class="t-tete" style="grid-template-columns:%s">%s</div>%s</div>' % (
        classe, _id(ident), gabarit, tete, ''.join(corps))


def totaux(lignes, ident=None):
    """Le pied d'une facture : (libellé, valeur, classe, identifiant)."""
    return '<div class="totaux"%s>%s</div>' % (_id(ident), ''.join(
        '<div class="tx %s"%s><span class="tx-l">%s</span><span class="tx-v">%s</span></div>'
        % (c, _id(i), e(l), e(v)) for l, v, c, i in lignes))


# --------------------------------------------------------------- MIS Builder --

def mis(ident, titre, groupes, colonnes, lignes):
    """Un état MIS Builder dans son widget : recherche, Rafraîchir / Imprimer /
    Export, en-têtes « Exercice N » et « Exercice N-1 », lignes (libellé,
    valeurs, gras) ; chaque montant suivi du petit triangle des annotations."""
    nb = len(colonnes)
    gabarit = '1fr ' + ' '.join(['%dpx' % (172 if nb > 2 else 230)] * nb)
    tete_g = ''.join('<span class="m-g" style="grid-column:span %d">%s</span>' % (n, e(g)) for g, n in groupes)
    tete_c = ''.join('<span class="m-c">%s</span>' % e(c) for c in colonnes) if any(colonnes) else ''
    corps = ''.join(
        '<div class="m-ligne%s" id="%s-r%d" style="grid-template-columns:%s"><span class="m-lib ell">%s</span>%s</div>'
        % (' gras' if gras else '', ident, i, gabarit, e(lib),
           ''.join('<span class="m-v">%s<i class="m-t"></i></span>' % e(v) for v in vals))
        for i, (lib, vals, gras) in enumerate(lignes))
    outils = ('<div class="m-outils"><span id="%s-rafr">%sRafraîchir</span><span id="%s-impr">%sImprimer</span>'
              '<span id="%s-exp">%sExport</span></div>'
              % (ident, icone('rafraichir'), ident, icone('imprimer'), ident, icone('export')))
    return (cp_simple(titre) +
            '<div class="mis" id="%s"><div class="m-haut">%s%s</div>'
            '<div class="m-tete" style="grid-template-columns:%s"><span></span>%s</div>%s%s</div>'
            % (ident, recherche(large=1180), outils, gabarit, tete_g,
               '<div class="m-tete2" style="grid-template-columns:%s"><span></span>%s</div>' % (gabarit, tete_c)
               if tete_c else '', corps))


# ---------------------------------------------------------- menus, notification --

def deroulant(ident, sections):
    """Le menu déroulant d'un menu de la barre : sections (titre ou None, éléments).
    Chaque élément a l'identifiant ``<ident>-<n>`` (n dans l'ordre d'affichage)."""
    corps, n = [], 0
    for titre, items in sections:
        if titre:
            corps.append('<div class="dd-sec">%s</div>' % e(titre))
        for it in items:
            corps.append('<div class="dd-it%s" id="%s-%d">%s</div>' % (' seul' if not titre else '', ident, n, e(it)))
            n += 1
    return ('<div class="deroulant masque" id="%s" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
            % (ident, ''.join(corps)))


def notification(ident, titre, texte, genre='succes'):
    return ('<div class="notif masque %s" id="%s" data-layout-allow-overlap data-layout-allow-occlusion>'
            '<b>%s</b><span>%s</span></div>' % (genre, ident, e(titre), e(texte)))


# ------------------------------------------------------------------- Apps --

def apps(cartes, ident):
    """L'écran Apps filtré sur « SYSCOHADA » : une carte par module (icône,
    nom, résumé, bouton)."""
    c = ''.join('<div class="app-carte"%s><img src="assets/logos/%s.png" alt=""><div class="ac-t">%s</div>'
                '<div class="ac-d">%s</div><div class="ac-b">%s</div></div>'
                % (_id(i), icone_mod, e(nom), e(resume),
                   bouton(None, 'Activer') + bouton(None, 'En savoir plus', 'clair') if activer else
                   bouton(None, 'En savoir plus', 'clair'))
                for i, icone_mod, nom, resume, activer in cartes)
    return ('<div class="cp"><span class="cp-titre">Apps %s</span>%s%s</div><div class="apps"%s>%s</div>'
            % (icone('engrenage', 'cp-gear'), recherche([('Module', 'SYSCOHADA')], large=440), pager('1-8 / 8'),
               _id(ident), c))


# --------------------------------------------------------- tableau de bord --

def tableau_de_bord(cartes):
    out = []
    for titre, boutons, a, b, graphe in cartes:
        bts = ''.join(bouton(None, l, s) for l, s in boutons)
        if isinstance(a, tuple):
            chiffres = ('<div class="tb-ch"><span>%s</span><span>%s</span></div>'
                        '<div class="tb-ch lien"><span>%s</span><span>%s</span></div>' % (e(a[0]), e(a[1]), e(b[0]), e(b[1])))
        else:
            chiffres = '<div class="tb-ch"><span class="lien">%s</span><span>%s</span></div>' % (e(a), e(b))
        if graphe == 'barres':
            g = ('<div class="tb-barres">%s</div>' % ''.join(
                '<span><i style="height:%dpx"></i><b>%s</b></span>' % (h, e(l)) for h, l in
                [(0, 'Dû'), (0, '28 sept. - 4 oct.'), (104, 'Cette semaine'), (0, '12 - 18 oct.'),
                 (0, '19 - 25 oct.'), (0, 'Pas dû')]))
        else:
            g = ('<svg class="tb-ligne" viewBox="0 0 600 110" preserveAspectRatio="none"><path d="M0,20 L120,95 '
                 'L240,105 L360,62 L480,70 L600,10 L600,110 L0,110Z" fill="#F1F1F3"/><path d="M0,20 L120,95 L240,105 '
                 'L360,62 L480,70 L600,10" fill="none" stroke="#D9D9DE" stroke-width="2"/></svg>')
        out.append('<div class="tb-carte"><div class="tb-t">%s</div><div class="tb-haut"><div>%s</div>'
                   '<div class="tb-chiffres">%s</div></div>%s</div>' % (e(titre), bts, chiffres, g))
    return '<div class="tb">%s</div>' % ''.join(out)


# --------------------------------------------------------- document imprimé --

def papier(ident, logo, adresse, titre, periode, section, lignes):
    corps = ''.join('<div class="pp-l%s"><span>%s</span><span>%s</span><span>%s</span></div>'
                    % (' sec' if sec else '', e(l), e(b), e(t)) for l, b, t, sec in lignes)
    return ('<div class="papier masque" id="%s" data-layout-allow-overlap data-layout-allow-occlusion>'
            '<img class="pp-logo" src="assets/logos/%s.png" alt=""><div class="pp-adr">%s</div>'
            '<div class="pp-titre">%s</div><div class="pp-per">%s</div><div class="pp-sec">%s</div>'
            '<div class="pp-l tete"><span>Ligne</span><span>Base</span><span>Taxe</span></div>%s</div>'
            % (ident, logo, '<br>'.join(e(a) for a in adresse), e(titre), e(periode), e(section), corps))
