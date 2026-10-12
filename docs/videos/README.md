# Vidéo de présentation — AITE Fiscalité OHADA

Une vidéo motion design d'environ cinq minutes qui présente toute la solution : le constat, les modules,
l'installation, puis le paramétrage, la saisie, les états financiers, la déclaration mensuelle I/TVA-IR, la
clôture et la DSF, la qualité. Voix off féminine française.

L'interface d'Odoo y est **rejouée en HTML**, jamais filmée : couleurs d'Odoo 18 Community, libellés exacts
des vues des modules AITE et des captures du guide, montants de la société de démonstration « Bar-Hôtel Démo
AITE ». Le rendu en MP4 est fait par [HyperFrames](https://hyperframes.heygen.com). Méthode du skill
`aite-motion-design-1` (guides vidéo PGest), adaptée à une vidéo de présentation.

| Ce qui est versionné | Où |
| --- | --- |
| Le moteur, les écrans, les données, le scénario, la feuille de style, les polices et les logos | `docs/videos/` |
| La vidéo compressée et sa vignette | `docs/videos/livrees/` |

Les projets HyperFrames, les rendus pleine qualité et les voix sont des sorties régénérables : ils vivent hors
du dépôt, dans le dossier de travail (`../aite-videos` par défaut).

## Produire

```bash
python3 docs/videos/produire.py presentation               # voix + projet + contrôle
python3 docs/videos/produire.py presentation --planche     # + planche contact à relire
python3 docs/videos/produire.py presentation --rendu       # + rendu MP4, compression, vignette
python3 docs/videos/produire.py presentation --muet --planche   # mise en page seule, sans voix
```

Prérequis : Node.js (`npx`), `ffmpeg`, Python 3. Au premier lancement, le script installe GSAP dans le dossier
de travail et Kokoro (voix locale, gratuite) dans `<dossier>/.venv-tts`. HyperFrames est figé à la version
`0.8.139`. Le rendu prend environ deux secondes de calcul par seconde de vidéo.

**Piège : chemin du dossier de travail.** espeak-ng, dont Kokoro tire la phonétisation, refuse un dossier de
données au chemin trop long (« Error processing file …/phontab »). Garder un dossier de travail à chemin court :
`../aite-videos` convient, pas le dossier temporaire d'une session.

Voix ElevenLabs (payante) : `--moteur-voix elevenlabs --voix-id <ID>`, clé dans `ELEVENLABS_API_KEY` ou
`<dossier>/.env`, jamais dans le dépôt ; détail dans le skill (`references/voix-off.md`).

## Les fichiers

| Fichier | Rôle |
| --- | --- |
| `scenarios/presentation.py` | Le scénario : scènes, écrans rejoués, gestes, légendes, voix |
| `demo.py` | Les données affichées, chacune avec sa source (capture du guide ou calcul des modules) |
| `ecrans.py` | Les composants d'Odoo 18 : fenêtre, panneaux, listes, fiches, MIS Builder, menus, Apps, document imprimé |
| `moteur.py` | Les scènes (signature, vitrine, chapitre, cartes, chiffres, écran, fin), les gestes, la composition |
| `produire.py` | Voix off, projet, contrôle, planche, rendu, compression |
| `sons.py` | Les bruitages synthétisés : ouverture, passage d'une partie, clic |
| `shared/aite.css` | Charte AITE (scènes) et Odoo 18 (écrans), à l'échelle vidéo |
| `shared/aite-motion.js` | Le plan des gestes → timeline GSAP |
| `shared/fonts`, `shared/logos` | Space Grotesk et IBM Plex Sans (OFL, charte AITE), Inter (OFL, écrans), logo AITE, icônes des modules |

## Les règles

- **Rien d'inventé.** Un libellé à l'écran existe dans les vues des modules ou sur une capture du guide ; un
  montant vient d'une capture ou d'un calcul des modules (l'écriture de liquidation de septembre 2026 a été
  calculée sur une copie de la base de formation, puis annulée) ; une règle dite par la voix se retrouve dans le
  guide, le lisez-moi ou le document de travail.
- **Données fictives.** Les sociétés de démonstration et leurs partenaires sont fictifs ; aucune donnée d'une base
  de recette d'un client n'apparaît.
- **La voix pilote les durées.** Une scène dure le temps de sa phrase ; une étape d'écran, le temps de ses
  gestes ou de sa phrase. Une étape dont l'image tourne plus de trois secondes sans voix est signalée.
- **Contrôles avant rendu** : `hyperframes check` sans erreur (contraste WCAG AA compris), planche contact relue
  image par image.

## Prononciation (Kokoro)

La voix est écrite comme elle se dit, l'écran garde la graphie exacte.

| Écrit à l'écran | Écrit pour la voix | Parce que |
| --- | --- | --- |
| AITE | Aïté | « AITE » est lu « ète » |
| OHADA | Ohada | lu correctement |
| I/TVA-IR | I T V A I R | sinon « i té vé a ir » |
| DGI | D G I | sinon « dji » |
| MIS Builder | M I S Bildeur | sinon « mi buildé » |
| Odoo 18 | Odoo dix-huit | lu à l'anglaise, comme il se dit |
| 19,25 % | dix-neuf virgule vingt-cinq pour cent | lecture sûre |
