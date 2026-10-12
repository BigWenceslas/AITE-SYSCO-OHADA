# -*- coding: utf-8 -*-
"""Produire la vidéo de présentation : voix off, projet HyperFrames, contrôles, rendu.

    python3 docs/videos/produire.py presentation               # projet + voix + check
    python3 docs/videos/produire.py presentation --planche     # + planche contact
    python3 docs/videos/produire.py presentation --rendu       # + rendu et compression

Les projets, les rendus et les voix vivent **hors du dépôt**, dans le dossier
de travail (``--dossier``, par défaut ``../aite-videos`` à côté du dépôt) : ce
sont des sorties régénérables. Seule la vidéo compressée et sa vignette entrent
dans ``docs/videos/livrees``.

Voix off : Kokoro, gratuit et local, voix féminine française ``ff_siwis``,
installé à la première utilisation dans ``<dossier>/.venv-tts``. Ou
ElevenLabs, payant, avec ``--moteur-voix elevenlabs --voix-id <ID>`` et la clé
dans ``ELEVENLABS_API_KEY`` (ou ``<dossier>/.env``), jamais dans le dépôt.
Chaque phrase est mise en cache : relancer ne resynthétise que les phrases
modifiées.

Piège : espeak-ng, dont Kokoro tire sa phonétisation, refuse un dossier de
données dont le chemin dépasse sa limite interne (« Error processing file
…/phontab »). Garder un dossier de travail à chemin court (pas le dossier
temporaire d'une session) : ``/home/user/aite-videos`` convient.
"""

import argparse
import glob
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import moteur  # noqa: E402
import sons  # noqa: E402

RACINE = os.path.abspath(os.path.join(ICI, '..', '..'))
HYPERFRAMES = 'hyperframes@0.8.139'
GSAP = 'gsap@3.14.2'
VOIX = 'ff_siwis'
VITESSE = '1.0'
SORTIE_DEPOT = os.path.join(ICI, 'livrees')
NAVIGATEURS_LOCAUX = ['/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell']


def journal(*morceaux):
    print(' '.join(str(m) for m in morceaux), flush=True)


def lancer(commande, dossier=None, env=None, capture=True, delai=3600):
    return subprocess.run(commande, cwd=dossier, env=env, capture_output=capture, text=True, timeout=delai)


def sans_couleurs(texte):
    return re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', texte or '')


# ------------------------------------------------------------ prérequis --

def navigateur():
    """Un Chrome sans interface déjà présent (Playwright des environnements
    cloud) : HyperFrames n'a alors rien à télécharger."""
    if os.environ.get('HYPERFRAMES_BROWSER_PATH'):
        return
    cache = os.path.expanduser('~/.cache/hyperframes/chrome')
    if os.path.isdir(cache) and os.listdir(cache):
        return
    for motif in NAVIGATEURS_LOCAUX:
        trouves = sorted(glob.glob(motif))
        if trouves:
            os.environ['HYPERFRAMES_BROWSER_PATH'] = trouves[-1]
            return


def preparer(dossier):
    os.makedirs(dossier, exist_ok=True)
    navigateur()
    gsap = os.path.join(dossier, 'node_modules', 'gsap', 'dist', 'gsap.min.js')
    if not os.path.exists(gsap):
        journal('· installation de', GSAP)
        if not os.path.exists(os.path.join(dossier, 'package.json')):
            with open(os.path.join(dossier, 'package.json'), 'w') as f:
                f.write('{"name": "aite-videos", "private": true}\n')
        r = lancer(['npm', 'install', '--no-audit', '--no-fund', GSAP], dossier)
        if r.returncode != 0:
            sys.exit('npm install %s a échoué :\n%s' % (GSAP, r.stderr))
    return gsap


def python_tts(dossier):
    venv = os.path.join(dossier, '.venv-tts')
    py = os.path.join(venv, 'bin', 'python')
    if not os.path.exists(py):
        journal('· installation de Kokoro (voix off locale)')
        lancer([sys.executable, '-m', 'venv', venv], capture=False)
        r = lancer([os.path.join(venv, 'bin', 'pip'), 'install', '-q', 'kokoro-onnx', 'soundfile'])
        if r.returncode != 0:
            sys.exit('Installation de Kokoro impossible :\n%s' % r.stderr)
    return py


def duree_media(chemin):
    r = lancer(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', chemin])
    return float(r.stdout.strip())


# ------------------------------------------------------------- voix off --

def textes_voix(scenario):
    """{case: phrase} : une phrase par scène, une par étape d'écran."""
    textes = {}
    for sc in scenario['scenes']:
        if sc['type'] == 'ecran':
            for n, etape in enumerate(sc['etapes'], 1):
                textes['%s-%d' % (sc['id'], n)] = etape['voix']
        elif sc.get('voix'):
            textes[sc['id']] = sc['voix']
    return textes


def cle_elevenlabs(dossier):
    cle = os.environ.get('ELEVENLABS_API_KEY')
    env = os.path.join(dossier, '.env')
    if not cle and os.path.exists(env):
        for ligne in open(env):
            if ligne.startswith('ELEVENLABS_API_KEY='):
                cle = ligne.split('=', 1)[1].strip().strip('"\'')
    return cle or None


def elevenlabs(dossier, texte, voix_id, modele, sortie):
    import urllib.error
    import urllib.request
    corps = {'text': texte, 'model_id': modele,
             'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}}
    requete = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128' % voix_id,
        data=json.dumps(corps).encode(), method='POST', headers={'Content-Type': 'application/json'})
    cle = cle_elevenlabs(dossier)
    if cle:
        requete.add_header('xi-api-key', cle)
    try:
        with urllib.request.urlopen(requete, timeout=120) as reponse:
            with open(sortie, 'wb') as f:
                f.write(reponse.read())
    except urllib.error.HTTPError as erreur:
        sys.exit('ElevenLabs %s : %s' % (erreur.code, erreur.read().decode(errors='replace')[:300]))


def synthetiser(dossier, textes, moteur_voix='kokoro', voix_id=None, modele='eleven_multilingual_v2'):
    """Rend {case: chemin du .wav normalisé}, {case: durée}."""
    cache = os.path.join(dossier, 'voix-cache')
    os.makedirs(cache, exist_ok=True)
    if moteur_voix == 'elevenlabs' and not voix_id:
        sys.exit('--voix-id est requis avec ElevenLabs (Voices → Copy voice ID).')
    env = dict(os.environ, HYPERFRAMES_PYTHON=python_tts(dossier)) if moteur_voix == 'kokoro' else None
    fichiers, durees = {}, {}
    for case, texte in textes.items():
        cle = [VOIX, VITESSE, texte] if moteur_voix == 'kokoro' else ['elevenlabs', voix_id, modele, texte]
        empreinte = hashlib.sha256(json.dumps(cle).encode()).hexdigest()[:16]
        brut = os.path.join(cache, empreinte + ('.wav' if moteur_voix == 'kokoro' else '.mp3'))
        norme = os.path.join(cache, empreinte + '-n.wav')
        if not os.path.exists(norme):
            journal('  voix', case, '—', texte[:70] + ('…' if len(texte) > 70 else ''))
            if moteur_voix == 'kokoro':
                r = lancer(['npx', '--yes', HYPERFRAMES, 'tts', texte, '-v', VOIX, '-s', VITESSE, '-o', brut],
                           dossier, env=env)
                if r.returncode != 0 or not os.path.exists(brut):
                    sys.exit('Synthèse impossible pour %s :\n%s' % (case, sans_couleurs(r.stdout + r.stderr)[-2000:]))
            else:
                elevenlabs(dossier, texte, voix_id, modele, brut)
            # volume homogène d'une phrase à l'autre
            r = lancer(['ffmpeg', '-v', 'error', '-y', '-i', brut, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7',
                        '-ar', '48000', '-ac', '1', norme])
            if r.returncode != 0:
                sys.exit('Normalisation impossible pour %s :\n%s' % (case, r.stderr))
        fichiers[case] = norme
        durees[case] = round(duree_media(norme), 3)
    return fichiers, durees


# -------------------------------------------------------------- projet --

def charger(nom):
    module = importlib.import_module('scenarios.%s' % nom)
    importlib.reload(module)
    return module.SCENARIO


def ecrire_projet(dossier, scenario, gsap, voix):
    projet = os.path.join(dossier, 'fr', scenario['slug'])
    assets = os.path.join(projet, 'assets')
    for sous in ('fonts', 'logos', 'voix', 'sons'):
        shutil.rmtree(os.path.join(assets, sous), ignore_errors=True)
    os.makedirs(assets, exist_ok=True)
    shutil.copytree(os.path.join(ICI, 'shared', 'fonts'), os.path.join(assets, 'fonts'))
    shutil.copytree(os.path.join(ICI, 'shared', 'logos'), os.path.join(assets, 'logos'))
    os.makedirs(os.path.join(assets, 'voix'))
    os.makedirs(os.path.join(assets, 'sons'))
    shutil.copy(os.path.join(ICI, 'shared', 'aite.css'), assets)
    shutil.copy(os.path.join(ICI, 'shared', 'aite-motion.js'), assets)
    shutil.copy(gsap, assets)

    fichiers, durees = voix if voix else ({}, {})
    relatifs = {}
    for case, chemin in fichiers.items():
        nom = os.path.basename(chemin)
        shutil.copy(chemin, os.path.join(assets, 'voix', nom))
        relatifs[case] = 'assets/voix/' + nom
    video = moteur.Presentation(scenario, durees_voix=durees, fichiers_voix=relatifs,
                                bruitages='assets/sons/bruitages.wav' if voix else None)
    html, total = video.construire()
    if video.bruitages:
        sons.piste(video.sons, total, os.path.join(projet, video.bruitages))
    with open(os.path.join(projet, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    with open(os.path.join(projet, 'hyperframes.json'), 'w') as f:
        json.dump({'paths': {'blocks': 'compositions', 'components': 'compositions/components', 'assets': 'assets'},
                   'media': {'autoProxy': True}}, f, indent=2)
    with open(os.path.join(projet, 'meta.json'), 'w') as f:
        json.dump({'id': video.id, 'name': scenario['titre']}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(projet, 'package.json'), 'w') as f:
        json.dump({'name': 'aite-' + video.id, 'private': True, 'type': 'module'}, f, indent=2)
    with open(os.path.join(projet, 'plan-scenes.json'), 'w') as f:
        json.dump(instants_cles(video), f, indent=2)
    return projet, total, video


def instants_cles(video):
    """Les instants de la planche contact : la fin de chaque scène (avant son
    fondu) et de chaque étape d'écran, et les repères posés par le moteur."""
    instants = [round(debut + duree - 0.55, 2) for _i, debut, duree in video.scenes_t if not _i.startswith('leg-')]
    instants.extend(video.reperes)
    return sorted(set(instants))


def verifier(projet):
    r = lancer(['npx', '--yes', HYPERFRAMES, 'check'], projet)
    sortie = sans_couleurs(r.stdout + r.stderr)
    resume = [l for l in sortie.splitlines() if re.search(r'error|✗|issues|checks pass|Check (passed|failed)', l)]
    return r.returncode, sortie, resume


def planche(projet, instants=None):
    if instants is None:
        with open(os.path.join(projet, 'plan-scenes.json')) as f:
            instants = json.load(f)
    shutil.rmtree(os.path.join(projet, 'snapshots'), ignore_errors=True)
    r = lancer(['npx', '--yes', HYPERFRAMES, 'snapshot', '--at', ','.join('%.2f' % t for t in instants), '--no-end',
                '--timeout', '20000'], projet)
    planches = sorted(glob.glob(os.path.join(projet, 'snapshots', 'contact-sheet*.jpg')))
    return planches, sans_couleurs(r.stdout + r.stderr)


def rendre(projet, scenario):
    sortie = os.path.join(projet, 'renders', '%s-fr.mp4' % scenario['slug'])
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    r = lancer(['npx', '--yes', HYPERFRAMES, 'render', '-o', sortie, '-w', '2', '-q', 'high'], projet, delai=7200)
    if r.returncode != 0 or not os.path.exists(sortie):
        sys.exit('Rendu impossible :\n%s' % sans_couleurs(r.stdout + r.stderr)[-3000:])
    return sortie


# La piste stéréo du rendu ramenée en mono par la moyenne des deux canaux
# (« -ac 1 » les additionne : +3 dB, et les crêtes saturaient après l'AAC).
MONO = 'pan=mono|c0=0.5*c0+0.5*c1'
SONIE = -16.0        # LUFS
PLAFOND = 0.794      # −2 dBFS


def sonie(source):
    r = lancer(['ffmpeg', '-hide_banner', '-nostats', '-i', source, '-vn', '-af', MONO + ',ebur128', '-f', 'null', '-'])
    valeurs = re.findall(r'^\s+I:\s+(-?[\d.]+) LUFS', r.stderr, re.M)
    if not valeurs:
        sys.exit('Sonie illisible pour %s :\n%s' % (source, r.stderr[-1500:]))
    return float(valeurs[-1])


def compresser(source, scenario, instant, sortie=SORTIE_DEPOT):
    """Copie web : H.264 CRF 28, +faststart ; voix et bruitages en AAC mono à
    ``SONIE`` LUFS, crêtes plafonnées ; vignette à ``instant``."""
    os.makedirs(sortie, exist_ok=True)
    cible = os.path.join(sortie, scenario['slug'] + '.mp4')
    gain = SONIE - sonie(source)
    r = lancer(['ffmpeg', '-v', 'error', '-y', '-i', source, '-c:v', 'libx264', '-preset', 'slow', '-crf', '28',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                '-af', '%s,volume=%.2fdB,alimiter=limit=%.3f:level=false' % (MONO, gain, PLAFOND),
                '-c:a', 'aac', '-b:a', '96k', cible])
    if r.returncode != 0:
        sys.exit('Compression impossible :\n%s' % r.stderr)
    image = os.path.splitext(cible)[0] + '.jpg'
    lancer(['ffmpeg', '-v', 'error', '-y', '-ss', '%.2f' % instant, '-i', cible, '-frames:v', '1', '-q:v', '3',
            '-vf', 'scale=1280:-2', image])
    return cible, image


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('scenario', help='nom du fichier de scénario (scenarios/<nom>.py)')
    p.add_argument('--dossier', default=os.path.abspath(os.path.join(RACINE, '..', 'aite-videos')))
    p.add_argument('--muet', action='store_true', help='sans voix off')
    p.add_argument('--moteur-voix', choices=['kokoro', 'elevenlabs'], default='kokoro')
    p.add_argument('--voix-id', help='identifiant de la voix ElevenLabs')
    p.add_argument('--sortie', default=SORTIE_DEPOT, help='dossier de la vidéo compressée (un autre pour un essai)')
    p.add_argument('--planche', action='store_true', help='planche contact (snapshots)')
    p.add_argument('--a', help='instants de la planche, séparés par des virgules (au lieu des instants clés)')
    p.add_argument('--rendu', action='store_true', help='rendu MP4 et compression')
    p.add_argument('--sans-check', action='store_true')
    args = p.parse_args()
    args.dossier = os.path.abspath(args.dossier)
    gsap = preparer(args.dossier)
    scenario = charger(args.scenario)
    journal('▶', scenario['slug'], '—', scenario['titre'])
    voix = None if args.muet else synthetiser(args.dossier, textes_voix(scenario), args.moteur_voix, args.voix_id)
    projet, total, video = ecrire_projet(args.dossier, scenario, gsap, voix)
    journal('  projet', projet, '— %d min %02d s' % (int(total) // 60, int(total) % 60))
    for alerte in video.alertes:
        journal('  ⚠', alerte)
    bilan = {'slug': scenario['slug'], 'duree': total, 'projet': projet,
             'caracteres_voix': sum(len(t) for t in textes_voix(scenario).values())}
    if not args.sans_check:
        code, sortie, resume = verifier(projet)
        bilan['check'] = 'ok' if code == 0 else 'échec'
        for ligne in resume:
            journal('   ', ligne.strip())
        with open(os.path.join(projet, 'check.log'), 'w') as f:
            f.write(sortie)
    if args.planche:
        instants = [float(x) for x in args.a.split(',')] if args.a else None
        planches, _sortie = planche(projet, instants)
        bilan['planches'] = planches
        journal('  planches', ', '.join(planches) or '(aucune)')
    if args.rendu:
        source = rendre(projet, scenario)
        cible, image = compresser(source, scenario, video.vignette(), args.sortie)
        bilan.update({'video': cible, 'vignette': image, 'mo': round(os.path.getsize(cible) / 1e6, 2)})
        journal('  vidéo', cible, '— %.1f Mo' % bilan['mo'])
    with open(os.path.join(args.dossier, 'bilan.json'), 'w') as f:
        json.dump(bilan, f, ensure_ascii=False, indent=2)
    journal('bilan :', os.path.join(args.dossier, 'bilan.json'))


if __name__ == '__main__':
    main()
