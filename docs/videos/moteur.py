# -*- coding: utf-8 -*-
"""Le moteur de la vidéo de présentation : d'un scénario à une composition HyperFrames.

Un scénario (``scenarios/<nom>.py``) est une suite de scènes, chacune d'un
type : ``signature`` (la marque, sans voix), ``vitrine`` (un titre et un
écran incliné), ``chapitre`` (un aplat violet qui ouvre une partie),
``cartes``, ``chiffres``, ``ecran`` (Odoo rejoué : étapes, gestes, légendes)
et ``fin``. Le moteur pose chaque scène dans un calque minuté, écrit le
*plan* des gestes (``shared/aite-motion.js`` en tire la timeline GSAP) et
cale tout sur la voix : une scène dure le temps de sa phrase, une étape
d'écran le temps de ses gestes ou de sa phrase si elle est plus longue.

Méthode et gestes repris du moteur du skill ``aite-motion-design-1``
(guides vidéo PGest), adaptés à une vidéo de présentation.
"""

import json
from html import escape

import sons
from ecrans import ICONES, curseur_svg, e

LARGEUR, HAUTEUR = 1920, 1080

BASE = {'signature': 3.3, 'vitrine': 7.0, 'chapitre': 4.4, 'cartes': 8.0, 'chiffres': 8.0, 'fin': 6.5}
CLIC_SONORE = 0.02    # le son suit d'un souffle l'appui du curseur
AVANT_VOIX = 0.45     # la voix démarre un peu après l'image
APRES_VOIX = 0.65     # et laisse respirer avant la scène suivante
SORTIE = 0.4          # fondu de sortie de chaque scène
COULEURS = ['violet', 'bleu', 'orange']


# ------------------------------------------------------------- les gestes --
# Chaque fonction rend un geste ; ``jouer`` les pose l'un après l'autre.
# Options communes : avec=True (en même temps que le précédent),
# decale=s (attendre avant), puis=s (respiration après).

def _g(geste, **kw):
    kw['geste'] = geste
    return kw


def curseur(sel, fx=0.5, fy=0.5, d=0.7, **kw):
    return _g('curseur', sel=sel, fx=fx, fy=fy, d=d, **kw)


def clic(sel, fx=0.5, fy=0.5, d=0.7, deplacer=True, **kw):
    """Amène le curseur sur l'élément et clique."""
    return _g('clic', sel=sel, fx=fx, fy=fy, d=d, deplacer=deplacer, **kw)


def saisir(ident, texte, d=None, **kw):
    return _g('saisir', ident=ident, texte=texte, d=d or max(0.5, 0.055 * len(texte)), **kw)


def vue(ident, groupe, **kw):
    """Passe d'une vue à l'autre dans la fenêtre ``groupe``."""
    return _g('vue', ident=ident, groupe=groupe, **kw)


def montrer(sel, d=0.35, y=12, **kw):
    return _g('montrer', sel=sel, d=d, y=y, **kw)


def cacher(sel, d=0.25, **kw):
    return _g('cacher', sel=sel, d=d, **kw)


def classe(sel, ajouter=(), retirer=(), **kw):
    return _g('classe', sel=sel, ajouter=list(ajouter), retirer=list(retirer), **kw)


def texte(sel, apres, **kw):
    return _g('texte', sel=sel, apres=apres, **kw)


def compter(sel, de, a, d=1.0, decimales=0, avant='', apres='', **kw):
    return _g('compter', sel=sel, de=de, a=a, d=d, decimales=decimales, avant=avant, apres=apres, **kw)


def pause(d):
    return _g('pause', d=d)


def defiler(sel, y, d=0.8, **kw):
    """Fait défiler un contenu (y négatif : vers le bas de la page)."""
    return _g('defiler', sel=sel, y=y, d=d, **kw)


def anneau(sel, d=1.2, **kw):
    """Entoure un élément d'un anneau orange, sans cliquer."""
    return _g('anneau', sel=sel, d=d, **kw)


def notifier(ident, duree=2.6, **kw):
    """Affiche une notification puis la retire, sans bloquer."""
    return _g('notifier', ident=ident, duree=duree, **kw)


def apparaitre(sel, nombre, d=0.4, decalage=0.08, y=10, **kw):
    """Fait apparaître ``nombre`` éléments l'un après l'autre (lignes calculées)."""
    return _g('apparaitre', sel=sel, nombre=nombre, d=d, decalage=decalage, y=y, **kw)


def survol(sel, **kw):
    return classe(sel, ajouter=['survol'], **kw)


def menu(fenetre, n, deroulant, **kw):
    """Ouvre le menu ``n`` de la barre : clic, puis le menu déroulant."""
    return [clic('#%s-m%d' % (fenetre, n), **kw), classe('#%s-m%d' % (fenetre, n), ajouter=['ouvert'], avec=True),
            montrer('#' + deroulant, avec=True, decale=0.05)]


def choisir_menu(fenetre, n, deroulant, item, **kw):
    """Survole puis clique un élément du menu déroulant, qui se referme."""
    return [curseur('#%s-%d' % (deroulant, item), fx=0.3, d=0.5), survol('#%s-%d' % (deroulant, item), avec=True, decale=0.3),
            clic('#%s-%d' % (deroulant, item), fx=0.3, deplacer=False, **kw), cacher('#' + deroulant),
            classe('#%s-m%d' % (fenetre, n), retirer=['ouvert'], avec=True),
            classe('#%s-%d' % (deroulant, item), retirer=['survol'], avec=True)]


PUIS = {'curseur': 0.05, 'clic': 0.25, 'saisir': 0.2, 'vue': 0.25, 'montrer': 0.15, 'cacher': 0.05,
        'classe': 0.12, 'texte': 0.1, 'compter': 0.2, 'pause': 0.0, 'defiler': 0.15, 'anneau': 0.1,
        'notifier': 0.3, 'apparaitre': 0.15}


# -------------------------------------------------------------- la vidéo --

class Presentation:
    """La vidéo, construite à partir de son scénario."""

    def __init__(self, scenario, durees_voix=None, fichiers_voix=None, bruitages=None):
        self.s = scenario
        self.id = scenario['slug'].split('-', 1)[-1].replace('_', '-')
        self.durees_voix = durees_voix or {}
        self.fichiers_voix = fichiers_voix or {}
        self.bruitages = bruitages
        self.couches = []
        self.ops = []
        self.cibles = {}
        self.defilements = []
        self.audios = []
        self.sons = []                 # (instant, 'ouverture' | 'passage' | 'clic')
        self.vues = {}
        self.positions = {}
        self.reperes = []              # instants à photographier
        self.alertes = []              # étapes où l'image tourne sans voix
        self.etapes_t = {}             # (scène, n) : (début, durée)
        self.scenes_t = []             # (identifiant, début, durée)
        self.piste = 1

    # -- outils
    def op(self, **kw):
        self.ops.append(kw)

    def cible(self, sel, fx=0.5, fy=0.5):
        cle = '%s@%.2f,%.2f' % (sel, fx, fy)
        self.cibles.setdefault(cle, {'sel': sel, 'fx': fx, 'fy': fy})
        return cle

    def entree(self, sel, t, d=0.6, y=30, x=0, echelle=None, decalage=None):
        de = {'autoAlpha': 0, 'y': y, 'x': x}
        # immediateRender : l'élément prend son état de départ dès la
        # construction, sans apparaître un instant avant son entrée.
        a = {'autoAlpha': 1, 'y': 0, 'x': 0, 'duration': d, 'ease': 'power3.out', 'immediateRender': True}
        if echelle:
            de['scale'] = echelle
            a['scale'] = 1
        if decalage:
            a['stagger'] = decalage
        self.op(op='fromTo', sel=sel, de=de, a=a, t=round(t, 3))

    def sortie(self, sel, t, d=SORTIE):
        self.op(op='fromTo', sel=sel, de={'autoAlpha': 1}, a={'autoAlpha': 0, 'duration': d, 'ease': 'power1.in'},
                t=round(t, 3))

    def duree(self, case, base):
        """La durée d'une scène : sa base, ou plus si la voix off l'exige."""
        dv = self.durees_voix.get(case)
        if dv:
            return round(max(base, AVANT_VOIX + dv + APRES_VOIX), 2)
        return base

    def poser_voix(self, case, t):
        if case in self.fichiers_voix and case in self.durees_voix:
            self.audios.append((case, self.fichiers_voix[case], round(t + AVANT_VOIX, 3), self.durees_voix[case]))

    def clip(self, ident, t, d, contenu, classes='clip scene'):
        self.couches.append('<div id="%s" class="%s" data-start="%.3f" data-duration="%.3f" data-track-index="%d">%s</div>'
                            % (ident, classes, t, d, self.piste, contenu))
        self.piste += 1
        self.scenes_t.append((ident, round(t, 3), round(d, 3)))

    def curseur_visible(self, t, visible, x=1500, y=1000):
        # un conteneur intérieur : le calque minuté, lui, est géré par HyperFrames
        self.op(op='set', sel='#curseur-zone', vars={'autoAlpha': 1 if visible else 0}, t=round(t, 3))
        if visible:
            self.op(op='set', sel='#curseur', vars={'x': x, 'y': y}, t=round(t, 3))

    @staticmethod
    def mots(texte, classe='mot'):
        return ' '.join('<span class="%s">%s</span>' % (classe, e(m)) for m in texte.split())

    # ------------------------------------------------------------ scènes --
    def scene_signature(self, sc, t):
        """La marque : la carte AITE se pose sur le carillon, le trait aux trois
        couleurs se trace, « AITE Fiscalité OHADA » monte lettre par lettre."""
        d = BASE['signature']
        lettres = ''.join('<span class="lettre%s">%s</span>' % (' ac' if i < 4 else '', '&nbsp;' if c == ' ' else e(c))
                          for i, c in enumerate(sc['marque']))
        html = ('<div class="sig" id="sig-in"><div class="sig-logo"><div class="carte-logo" id="sig-logo">'
                '<img src="assets/logos/aite.jpg" alt=""></div></div><div class="sig-trait" id="sig-trait"></div>'
                '<div class="sig-marque" id="sig-marque">%s</div><div class="sig-sous" id="sig-sous">%s</div></div>'
                % (lettres, e(sc['sous'])))
        self.clip('sc-' + sc['id'], t, d, html)
        self.op(op='fromTo', sel='#fond .bande', de={'scaleX': 0},
                a={'scaleX': 1, 'duration': 1.0, 'ease': 'power2.inOut', 'immediateRender': True}, t=round(t + 0.05, 3))
        self.op(op='fromTo', sel='#sig-logo', de={'autoAlpha': 0, 'y': 30, 'scale': 0.82},
                a={'autoAlpha': 1, 'y': 0, 'scale': 1, 'duration': 0.6, 'ease': 'back.out(1.6)', 'immediateRender': True},
                t=round(t + sons.CARILLON - 0.5, 3))
        self.op(op='fromTo', sel='#sig-trait', de={'scaleX': 0},
                a={'scaleX': 1, 'duration': 0.7, 'ease': 'power3.inOut', 'immediateRender': True}, t=round(t + 0.6, 3))
        self.entree('#sig-marque .lettre', t + sons.CARILLON, d=0.5, y=44, decalage=0.035)
        self.entree('#sig-sous', t + 1.55, d=0.5, y=16)
        self.op(op='fromTo', sel='#sig-in', de={'autoAlpha': 1, 'y': 0},
                a={'autoAlpha': 0, 'y': -30, 'duration': 0.45, 'ease': 'power2.in'}, t=round(t + d - 0.45, 3))
        self.sons.append((round(t, 3), 'ouverture'))
        self.reperes.append(round(t + 2.4, 2))
        return t + d

    def scene_vitrine(self, sc, t):
        """Un titre à gauche, un écran d'Odoo incliné à droite, qui se pose puis flotte."""
        i = sc['id']
        d = self.duree(i, BASE['vitrine'])
        puces = ''.join('<div class="vit-puce"><i>%s</i><span>%s</span></div>' % (ICONES['coche'], e(p))
                        for p in sc.get('puces', []))
        html = ('<div id="%s-in"><div class="vit-texte"><div class="kicker" id="%s-k">%s</div>'
                '<div class="titre%s" id="%s-t">%s</div><div class="vit-trait" id="%s-trait"></div>%s%s</div>'
                '<div class="vit-zone" data-layout-allow-overflow data-layout-allow-occlusion data-layout-allow-overlap>%s</div></div>'
                % (i, i, e(sc['kicker']), ' grand' if sc.get('grand') else '', i, self.mots(sc['titre']), i,
                   '<p class="vit-p" id="%s-p">%s</p>' % (i, e(sc['texte'])) if sc.get('texte') else '',
                   '<div class="vit-puces" id="%s-puces">%s</div>' % (i, puces) if puces else '', sc['ecran']))
        self.clip('sc-' + i, t, d, html)
        self.entree('#%s-k' % i, t + 0.1, y=18)
        self.entree('#%s-t .mot' % i, t + 0.25, d=0.65, y=60, decalage=0.07)
        self.op(op='fromTo', sel='#%s-trait' % i, de={'scaleX': 0},
                a={'scaleX': 1, 'duration': 0.6, 'ease': 'power2.out', 'immediateRender': True}, t=round(t + 0.9, 3))
        if sc.get('texte'):
            self.entree('#%s-p' % i, t + 1.1, y=22)
        if puces:
            self.entree('#%s-puces .vit-puce' % i, t + 1.3, d=0.5, y=20, decalage=0.22)
        fen = '#' + sc['fenetre']
        self.op(op='fromTo', sel=fen, de={'autoAlpha': 0, 'rotationY': -38, 'rotationX': 9, 'x': 320, 'z': -260},
                a={'autoAlpha': 1, 'rotationY': -17, 'rotationX': 5, 'x': 0, 'z': 0, 'duration': 1.25,
                   'ease': 'power3.out', 'immediateRender': True}, t=round(t + 0.35, 3))
        self.op(op='fromTo', sel=fen, de={'rotationY': -17, 'y': 0},
                a={'rotationY': -12, 'y': -18, 'duration': max(1.0, d - 2.2), 'ease': 'sine.inOut',
                   'immediateRender': False}, t=round(t + 1.6, 3))
        self.sortie('#%s-in' % i, t + d - SORTIE)
        self.poser_voix(i, t)
        return t + d

    def scene_chapitre(self, sc, t):
        """Un aplat violet balaie l'écran ; le numéro et le titre de la partie entrent."""
        i = sc['id']
        d = self.duree(i, BASE['chapitre'])
        html = ('<div class="chap-fond" id="%s-fond"><i></i></div><div class="chap-bloc" id="%s-bloc">'
                '<div class="chap-num" id="%s-n">%s</div><div class="chap-titre" id="%s-t">%s</div>'
                '<div class="chap-trait" id="%s-trait"></div>%s</div>'
                % (i, i, i, e(sc['numero']), i, self.mots(sc['titre']), i,
                   '<div class="chap-sous" id="%s-s">%s</div>' % (i, e(sc['sous'])) if sc.get('sous') else ''))
        self.clip('sc-' + i, t, d, html)
        self.op(op='fromTo', sel='#%s-fond' % i, de={'scaleX': 0, 'transformOrigin': '0% 50%'},
                a={'scaleX': 1, 'duration': 0.6, 'ease': 'power3.inOut', 'immediateRender': True}, t=round(t, 3))
        self.entree('#%s-n' % i, t + 0.45, y=24)
        self.entree('#%s-t .mot' % i, t + 0.55, d=0.6, y=70, decalage=0.06)
        self.op(op='fromTo', sel='#%s-trait' % i, de={'scaleX': 0},
                a={'scaleX': 1, 'duration': 0.5, 'ease': 'power2.out', 'immediateRender': True}, t=round(t + 1.1, 3))
        if sc.get('sous'):
            self.entree('#%s-s' % i, t + 1.25, y=20)
        self.op(op='fromTo', sel='#%s-bloc' % i, de={'autoAlpha': 1},
                a={'autoAlpha': 0, 'duration': 0.3, 'ease': 'power1.in'}, t=round(t + d - 0.75, 3))
        self.op(op='fromTo', sel='#%s-fond' % i, de={'scaleX': 1, 'transformOrigin': '100% 50%'},
                a={'scaleX': 0, 'duration': 0.5, 'ease': 'power3.inOut'}, t=round(t + d - 0.5, 3))
        self.sons.append((round(t, 3), 'passage'))
        self.poser_voix(i, t)
        return t + d

    def scene_cartes(self, sc, t):
        i = sc['id']
        d = self.duree(i, BASE['cartes'])
        n = len(sc['cartes'])
        cartes = ''.join(
            '<div class="ca-carte"><div class="ca-pastille"><i style="background:var(--%s)"></i>%s</div>'
            '<div class="ca-t">%s</div><div class="ca-x">%s</div></div>'
            % (COULEURS[k % 3], e(eti), e(titre), txt) for k, (eti, titre, txt) in enumerate(sc['cartes']))
        note = '<div class="ca-note" id="%s-note">%s</div>' % (i, sc['note']) if sc.get('note') else ''
        html = ('<div id="%s-in"><div class="ca-tete" id="%s-tete"><div class="kicker">%s</div><div class="titre">%s</div></div>'
                '<div class="ca-grille" style="grid-template-columns:repeat(%d,1fr);top:%dpx">%s</div>%s</div>'
                % (i, i, e(sc['kicker']), e(sc['titre']), n, sc.get('haut', 390), cartes, note))
        self.clip('sc-' + i, t, d, html)
        self.entree('#%s-tete' % i, t + 0.1, y=24)
        self.entree('#%s-in .ca-carte' % i, t + 0.5, d=0.6, y=50, decalage=0.25)
        if note:
            self.entree('#%s-note' % i, t + 0.6 + 0.25 * n, y=20)
        self.sortie('#%s-in' % i, t + d - SORTIE)
        self.poser_voix(i, t)
        return t + d

    def scene_chiffres(self, sc, t):
        i = sc['id']
        d = self.duree(i, BASE['chiffres'])
        items = []
        for k, it in enumerate(sc['chiffres']):
            items.append('<div class="chi"><div class="chi-n %s" id="%s-n%d">%s</div><div class="chi-l">%s</div></div>'
                         % (COULEURS[k % 3], i, k, e(it['affiche']), it['libelle']))
        html = ('<div id="%s-in"><div class="ca-tete" id="%s-tete"><div class="kicker">%s</div><div class="titre">%s</div></div>'
                '<div class="chi-grille" style="grid-template-columns:repeat(%d,1fr)">%s</div></div>'
                % (i, i, e(sc['kicker']), e(sc['titre']), sc.get('colonnes', 3), ''.join(items)))
        self.clip('sc-' + i, t, d, html)
        self.entree('#%s-tete' % i, t + 0.1, y=24)
        self.entree('#%s-in .chi' % i, t + 0.45, d=0.55, y=40, decalage=0.15)
        for k, it in enumerate(sc['chiffres']):
            if 'compte' in it:
                self.op(op='compteur', sel='#%s-n%d' % (i, k), de=0, a=it['compte'], d=1.4, decimales=0,
                        avant='', apres=it.get('suffixe', ''), t=round(t + 0.6 + 0.15 * k, 3))
        self.sortie('#%s-in' % i, t + d - SORTIE)
        self.poser_voix(i, t)
        return t + d

    def scene_ecran(self, sc, t):
        """Odoo rejoué : la fenêtre entre, puis chaque étape et sa légende."""
        i = sc['id']
        self.vues[sc['fenetre']] = sc.get('vue_initiale')
        legendes = []
        debut = t
        self.entree('#' + sc['fenetre'], t + 0.05, d=0.7, y=50, echelle=0.97)
        self.curseur_visible(t, True)
        cle = self.cible('#' + sc['fenetre'], 0.55, 0.6)
        self.op(op='curseur', cle=cle, t=round(t + 0.3, 3), d=0.8)
        k = t + 0.9
        etapes = sc['etapes']
        for n, etape in enumerate(etapes, 1):
            case = '%s-%d' % (i, n)
            t0 = k
            fin_gestes = self.jouer(etape['gestes'], t0 + 0.35)
            d = max(fin_gestes - t0 + 0.5, etape.get('min', 0))
            dv = self.durees_voix.get(case)
            if dv and d - (AVANT_VOIX + dv) > 3.0:
                self.alertes.append('%s, étape %d : %.1f s d\'image pour %.1f s de voix' % (i, n, d, dv))
            d = self.duree(case, d)
            self.etapes_t[(i, n)] = (round(t0, 3), round(d, 3))
            pas = ''.join('<i class="%s"></i>' % ('on' if m <= n else '') for m in range(1, len(etapes) + 1))
            legendes.append('<div class="leg masque" id="leg-%s-%d"><div class="num"><small>ÉTAPE</small><b>%d</b></div>'
                            '<div><div class="t">%s</div><div class="s">%s</div></div><div class="pas">%s</div></div>'
                            % (i, n, n, e(etape['titre']), e(etape['texte']), pas))
            self.entree('#leg-%s-%d' % (i, n), t0, d=0.45, y=20)
            self.sortie('#leg-%s-%d' % (i, n), t0 + d - 0.3, d=0.3)
            self.poser_voix(case, t0)
            self.reperes.append(round(t0 + d - 0.6, 2))
            k = t0 + d
        fin = k + 0.5
        self.sortie('#' + sc['fenetre'], fin - SORTIE)
        self.clip('sc-' + i, debut, fin - debut, sc['ecran'], classes='clip')
        self.clip('leg-' + i, debut, fin - debut, ''.join(legendes), classes='clip legende')
        self.curseur_visible(fin, False)
        return fin

    def scene_fin(self, sc, t):
        i = sc['id']
        d = self.duree(i, BASE['fin'])
        html = ('<div id="%s-in"><div class="fin-bloc"><div class="carte-logo" id="%s-logo"><img src="assets/logos/aite.jpg" alt="">'
                '</div><div class="fin-titre" id="%s-t">%s</div><div class="fin-sous" id="%s-s">%s</div>'
                '<div class="fin-trait" id="%s-trait"></div><div class="fin-contact" id="%s-c">%s</div></div>'
                '<div class="fin-pied" id="%s-p">%s</div></div>'
                % (i, i, i, sc['titre'], i, e(sc['sous']), i, i, sc['contact'], i, e(sc['pied'])))
        self.clip('sc-' + i, t, d, html)
        self.entree('#%s-logo' % i, t + 0.1, d=0.6, y=30, echelle=0.9)
        self.entree('#%s-t' % i, t + 0.5, d=0.6, y=40)
        self.entree('#%s-s' % i, t + 0.8, y=20)
        self.op(op='fromTo', sel='#%s-trait' % i, de={'scaleX': 0},
                a={'scaleX': 1, 'duration': 0.6, 'ease': 'power2.out', 'immediateRender': True}, t=round(t + 1.0, 3))
        self.entree('#%s-c' % i, t + 1.2, y=16)
        self.entree('#%s-p' % i, t + 1.5, y=10)
        self.poser_voix(i, t)
        return t + d

    # ---------------------------------------------------- les gestes posés --
    def jouer(self, gestes, t):
        """Pose une suite de gestes à partir de ``t`` ; rend l'instant de fin."""
        fin = t
        debut_prec = t
        for g in gestes:
            if isinstance(g, list):
                for h in g:
                    debut = (debut_prec if h.get('avec') else fin) + h.get('decale', 0)
                    duree = self._poser(h, round(debut, 3))
                    debut_prec = debut
                    fin = max(fin, debut + duree + h.get('puis', PUIS[h['geste']]))
                continue
            debut = (debut_prec if g.get('avec') else fin) + g.get('decale', 0)
            duree = self._poser(g, round(debut, 3))
            debut_prec = debut
            fin = max(fin, debut + duree + g.get('puis', PUIS[g['geste']]))
        return fin

    def _poser(self, g, t):
        k = g['geste']
        if k == 'curseur':
            cle = self.cible(g['sel'], g['fx'], g['fy'])
            self.op(op='curseur', cle=cle, t=t, d=g['d'])
            return g['d']
        if k == 'clic':
            cle = self.cible(g['sel'], g['fx'], g['fy'])
            dt = 0
            if g['deplacer']:
                self.op(op='curseur', cle=cle, t=t, d=g['d'])
                dt = g['d'] + 0.08
            self.op(op='clic', cle=cle, t=round(t + dt, 3))
            return dt + 0.3
        if k == 'saisir':
            i = g['ident']
            self.op(op='classe', sel='#' + i, ajouter=['focus'], retirer=[], t=t)
            self.op(op='set', sel='#%s-ph' % i, vars={'autoAlpha': 0}, t=t)
            self.op(op='saisie', sel='#%s-val' % i, texte=g['texte'], t=t, d=g['d'])
            self.op(op='classe', sel='#' + i, ajouter=[], retirer=['focus'], t=round(t + g['d'] + 0.4, 3))
            return g['d']
        if k == 'vue':
            ancienne = self.vues.get(g['groupe'])
            if ancienne:
                self.op(op='fromTo', sel='#' + ancienne, de={'autoAlpha': 1}, a={'autoAlpha': 0, 'duration': 0.25}, t=t)
            self.op(op='fromTo', sel='#' + g['ident'], de={'autoAlpha': 0, 'x': 30},
                    a={'autoAlpha': 1, 'x': 0, 'duration': 0.4, 'ease': 'power2.out'}, t=round(t + 0.15, 3))
            self.vues[g['groupe']] = g['ident']
            return 0.55
        if k == 'montrer':
            self.op(op='fromTo', sel=g['sel'], de={'autoAlpha': 0, 'y': g['y']},
                    a={'autoAlpha': 1, 'y': 0, 'duration': g['d'], 'ease': 'power3.out'}, t=t)
            return g['d']
        if k == 'cacher':
            self.sortie(g['sel'], t, d=g['d'])
            return g['d']
        if k == 'apparaitre':
            self.op(op='fromTo', sel=g['sel'], de={'autoAlpha': 0, 'y': g['y']},
                    a={'autoAlpha': 1, 'y': 0, 'duration': g['d'], 'ease': 'power2.out', 'stagger': g['decalage']}, t=t)
            return g['d'] + g['decalage'] * (g['nombre'] - 1)
        if k == 'classe':
            self.op(op='classe', sel=g['sel'], ajouter=g['ajouter'], retirer=g['retirer'], t=t)
            return 0.05
        if k == 'texte':
            self.op(op='texte', sel=g['sel'], apres=g['apres'], t=t)
            return 0.05
        if k == 'compter':
            self.op(op='compteur', sel=g['sel'], de=g['de'], a=g['a'], d=g['d'], decimales=g['decimales'],
                    avant=g['avant'], apres=g['apres'], t=t)
            return g['d']
        if k == 'pause':
            return g['d']
        if k == 'defiler':
            avant = self.positions.get(g['sel'], 0)
            self.op(op='fromTo', sel=g['sel'], de={'y': avant}, a={'y': g['y'], 'duration': g['d'], 'ease': 'power2.inOut'}, t=t)
            self.positions[g['sel']] = g['y']
            self.defilements.append({'sel': g['sel'], 't': round(t + g['d'], 3), 'y': g['y']})
            return g['d']
        if k == 'anneau':
            cle = self.cible(g['sel'])
            self.op(op='anneau', sel='#anneau', cle=cle, t=t, d=g['d'])
            return g['d']
        if k == 'notifier':
            i = '#' + g['ident']
            self.op(op='fromTo', sel=i, de={'autoAlpha': 0, 'x': 50},
                    a={'autoAlpha': 1, 'x': 0, 'duration': 0.4, 'ease': 'power3.out'}, t=t)
            self.sortie(i, t + g['duree'], d=0.3)
            return 0.4
        raise ValueError('geste inconnu : %s' % k)

    def vignette(self):
        """L'instant de la vignette : {'scene': id, 'etape': n, 'apres': s}."""
        v = self.s['vignette']
        t0, d = self.etapes_t[(v['scene'], v['etape'])]
        return round(t0 + v.get('apres', d / 2.0), 2)

    # -------------------------------------------------------- assemblage --
    def construire(self):
        """Rend (html, durée totale)."""
        t = 0.0
        for sc in self.s['scenes']:
            if sc['type'] != 'ecran':
                self.curseur_visible(t, False)
            t = getattr(self, 'scene_' + sc['type'])(sc, t)
        total = round(t, 2)
        self.couches.append(
            '<div id="couche-curseur" class="clip" data-start="0" data-duration="%.3f" data-track-index="%d">'
            '<div id="curseur-zone"><div id="curseur">%s</div><div id="onde"></div><div class="anneau" id="anneau"></div></div></div>'
            % (total, self.piste, curseur_svg()))
        fond = ('<div id="fond" class="clip" data-start="0" data-duration="%.3f" data-track-index="0">'
                '<div class="cercle"></div><div class="cercle2"></div><div class="bande"></div></div>' % total)
        audios = ''.join(
            '<audio id="voix-%s" src="%s" data-start="%.3f" data-duration="%.3f" data-track-index="%d"></audio>'
            % (case, chemin, debut, max(0.1, duree - 0.06), 200 + i)
            for i, (case, chemin, debut, duree) in enumerate(self.audios))
        self.sons.extend(sorted((round(o['t'] + CLIC_SONORE, 3), 'clic') for o in self.ops if o['op'] == 'clic'))
        if self.bruitages:
            audios += ('<audio id="bruitages" src="%s" data-start="0" data-duration="%.3f" data-track-index="199"></audio>'
                       % (self.bruitages, total))
        plan = {'duree': total, 'cibles': self.cibles, 'defilements': sorted(self.defilements, key=lambda d: d['t']),
                'ops': self.ops}
        plan_json = json.dumps(plan, ensure_ascii=False).replace('</', '<\\/')
        html = TEMPLATE % {
            'titre': escape(self.s['titre']), 'id': self.id, 'duree': total,
            'couches': fond + ''.join(self.couches) + audios, 'plan': plan_json,
        }
        return html, total


TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1920, height=1080">
<title>%(titre)s</title>
<script src="assets/gsap.min.js"></script>
<link rel="stylesheet" href="assets/aite.css">
</head>
<body>
<div id="root" data-composition-id="%(id)s" data-start="0" data-duration="%(duree).3f" data-width="1920" data-height="1080">
%(couches)s
</div>
<script type="application/json" id="plan">%(plan)s</script>
<script src="assets/aite-motion.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  document.fonts.ready.then(function () {
    window.__timelines["%(id)s"] = AITE.construire(JSON.parse(document.getElementById("plan").textContent));
  });
</script>
</body>
</html>
"""
