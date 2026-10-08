# SYSCOHADA révisé pour Odoo 18 — paquet d'installation

Modules Odoo 18 d'AITE Consulting pour la conformité au SYSCOHADA révisé et à la fiscalité camerounaise :
états financiers (bilan, compte de résultat, tableau des flux de trésorerie), contrôles, déclaration mensuelle
I/TVA-IR complète et écritures de liquidation. Cible principale : Odoo 18 Community ; Enterprise est pris en charge
par un module facultatif.

Versions des modules et commits des sources : fichier `VERSIONS.txt`.

## Contenu du paquet

| Dossier | Contenu |
| --- | --- |
| `addons/aite_syscohada_base` | Socle : référentiel des 124 rubriques, moteur de calcul, paramétrage du plan « cm » et des taxes camerounaises, contrôles, assistant « États et contrôles (AITE) » |
| `addons/aite_syscohada_mis` | Bilan actif, bilan passif, compte de résultat et TFT dans MIS Builder |
| `addons/aite_syscohada_community` | Menu Syscohada : états en un clic (N et N-1), déclaration mensuelle I/TVA-IR (L0 à L80), liquidation, impression |
| `addons/aite_syscohada_reports` | Facultatif, **Odoo Enterprise seulement** : les quatre états dans le moteur de rapports d'Enterprise |
| `addons/aite_syscohada_demo` | Facultatif, **bases de test seulement** : société de démonstration « Bar-Hôtel Démo AITE », 21 mois d'opérations |
| `addons/aite_syscohada_demo_services` | Facultatif, **bases de test seulement** : société de démonstration « Services Informatiques Démo AITE », 21 mois d'opérations |
| `addons/aite_syscohada_demo_common` | Moteur commun des deux démonstrations (installé avec elles, sans données) |
| `addons/mis_builder`, `addons/date_range`, `addons/report_xlsx` | Dépendances OCA (branche 18.0, livrées sans leurs tests), indispensables : `aite_syscohada_mis` et `aite_syscohada_community` ne s'installent pas sans elles |
| `requirements.txt` | Dépendance Python de `mis_builder` : `openupgradelib` |
| `paquets-python/` | `openupgradelib` et sa dépendance `cssselect`, en roues universelles : installation sans accès à Internet (étape 3) |
| `licences/` | Textes des licences (AGPL-3 ; LGPL-3 et GPL-3 ; BSD-3-Clause de `cssselect`) ; la licence de chaque module est dans `VERSIONS.txt` |
| `docs/` | Guide complet (`guide-syscohada-odoo18.html`) et cartographie des flux comptables |

Les dix modules (AITE et OCA) sont dans le même dossier `addons/`. Soit on déclare directement ce dossier dans
`addons_path`, soit on copie son contenu dans un dossier d'extensions déjà déclaré : dans les deux cas, un seul
chemin pour les dix modules, et jamais deux copies d'un même module (Odoo prend sans prévenir la première trouvée).

## Prérequis

- Un serveur Odoo 18 où l'on peut ajouter des modules Python et redémarrer Odoo : serveur propre, image Docker
  ou Odoo.sh. Odoo Online (l'offre SaaS d'Odoo) ne convient pas. Ne pas passer par Apps > Importer un module :
  ce menu ne charge que des modules de données, jamais le code Python (Odoo le signale dans sa fenêtre).
- Odoo 18, Community ou Enterprise, avec la localisation camerounaise `l10n_cm` (fournie avec Odoo).
- Le paquet Python `openupgradelib`, exigé par `mis_builder`, livré dans `paquets-python/` (étape 3).
- Le français installé dans la base (langue Français à la création de la base, `--load-language=fr_FR` à la
  première installation, ou Paramètres > Traductions > Langues) : les libellés des lignes de TVA de la
  déclaration viennent de la localisation `l10n_cm` et suivent la langue de l'utilisateur.
- Des sociétés en FCFA (XAF) au plan comptable camerounais « cm » (SYSCOHADA révisé). Le paramétrage AITE ne
  s'applique qu'à elles : à l'installation, les autres sociétés sont laissées telles quelles sans
  avertissement ; le menu Appliquer le paramétrage les refuse par un message. Une société dont le pays est le Cameroun reçoit ce
  plan avec la Facturation. Pour une société qui n'a pas encore d'écritures : Facturation > Configuration >
  Paramètres, Localisation fiscale, Pack « SYSCOHADA pour Sociétés » (version 18.0.1.3.0 au moins : les versions
  antérieures échouaient sur « Invalid language code: fr_BE »). Dès que la société a des écritures, Odoo met le
  champ Pack en lecture seule : une société déjà en exploitation sur un autre plan se traite avec
  l'expert-comptable (reprise dans une société au plan « cm »).

## Installation

1. Copier tout le contenu de `addons/` (les dix modules) dans un dossier d'extensions du serveur, par exemple
   `/opt/odoo/extra-addons`, ou déclarer directement le dossier `addons/` du paquet. Si l'un des modules OCA
   (`mis_builder`, `date_range`, `report_xlsx`) est déjà présent dans un dossier de `addons_path`, en branche 18.0
   et dans une version au moins égale à celle de `VERSIONS.txt`, n'en garder qu'une copie : ne pas copier ce
   module, ou, si l'on déclare directement le dossier `addons/` du paquet, le supprimer de ce dossier. Avec deux
   copies, Odoo charge sans avertissement celle du premier dossier listé dans `addons_path`.
2. Ajouter ce dossier à `addons_path` dans le fichier de configuration d'Odoo, s'il n'y est pas déjà.
   Le chemin déclaré doit contenir directement les dossiers des modules : `…/aite_syscohada_odoo18/addons` (ou le
   dossier d'extensions où l'on a copié son contenu), jamais la racine `…/aite_syscohada_odoo18` ni un dossier qui
   contient `addons/`. Odoo accepte un tel chemin sans erreur mais n'y trouve aucun module ; même piège si l'on
   copie le dossier `addons/` lui-même au lieu de son contenu. Contrôle :
   `ls <dossier>/aite_syscohada_base/__manifest__.py <dossier>/mis_builder/__manifest__.py` répond sans erreur.
   - Odoo.sh : placer les dix dossiers de modules à la racine du dépôt de la branche, et `requirements.txt` à la
     racine de la branche (la plateforme installe les bibliothèques qu'il liste). Les builds de développement
     installent par défaut tous les modules de la branche, démonstrations comprises : pour l'éviter, réglages de
     la branche, installation des modules, liste limitée à `aite_syscohada_community`.
   - Image Docker officielle (`odoo:18.0`) : monter le dossier `addons/` du paquet, pas sa racine, sur
     `/mnt/extra-addons` : `-v <chemin>/aite_syscohada_odoo18/addons:/mnt/extra-addons`.
3. Installer la dépendance Python de `mis_builder` (`openupgradelib`, avec `cssselect`) avec le Python qui exécute
   Odoo, depuis le dossier décompressé du paquet. Les deux bibliothèques sont livrées dans `paquets-python/` : la
   commande marche aussi sans accès à Internet (la troisième dépendance, `lxml`, est déjà fournie avec Odoo).
   - Odoo dans un environnement virtuel :
     `<venv>/bin/pip install --no-index --find-links paquets-python -r requirements.txt`.
   - Odoo installé par le paquet .deb : la même commande avec `sudo pip3` (sans `sudo`, pip installe dans le
     dossier personnel de l'utilisateur, invisible pour le service Odoo ; si `pip3` manque :
     `sudo apt install python3-pip`). Si pip refuse avec « error: externally-managed-environment » (Debian 12,
     Ubuntu 24.04), ajouter `--break-system-packages`.
   - Image Docker officielle : construire une image dérivée, avec ce `Dockerfile` placé dans le dossier décompressé
     du paquet, puis `docker build -t odoo18-aite .` et lancer le conteneur sur l'image `odoo18-aite` (en gardant
     le montage de l'étape 2) :

     ```dockerfile
     FROM odoo:18.0
     USER root
     COPY requirements.txt /tmp/aite/requirements.txt
     COPY paquets-python /tmp/aite/paquets-python
     RUN pip3 install --no-cache-dir --break-system-packages --no-index \
         --find-links /tmp/aite/paquets-python -r /tmp/aite/requirements.txt
     USER odoo
     ```
   - Odoo pour Windows (installateur officiel, service `odoo-server-18.0`) : ouvrir l'invite de commandes **en
     tant qu'administrateur** (clic droit sur « Invite de commandes » > Exécuter en tant qu'administrateur), se
     placer dans le dossier décompressé du paquet, puis lancer le Python livré avec Odoo (adapter le nom du dossier
     d'installation d'Odoo, par exemple `C:\Program Files\Odoo 18.0` suivi d'une date) :

     ```bat
     cd /d C:\chemin\vers\aite_syscohada_odoo18
     "C:\Program Files\Odoo 18.0\python\python.exe" -m pip install --no-index --find-links paquets-python -r requirements.txt
     net stop odoo-server-18.0
     net start odoo-server-18.0
     ```

     `C:\chemin\vers\aite_syscohada_odoo18` est à remplacer par le dossier où le zip a été décompressé (avec
     « Extraire tout » de Windows, en général
     `C:\Users\<nom>\Downloads\aite_syscohada_odoo18_<version>_<date>\aite_syscohada_odoo18`). Astuce : taper
     `cd /d ` puis glisser ce dossier depuis l'Explorateur dans la fenêtre, et valider. Pour retrouver le dossier :
     `where /r "%USERPROFILE%\Downloads" requirements.txt`. Avec un accès à Internet, une seule commande suffit,
     depuis n'importe quel dossier :
     `"C:\Program Files\Odoo 18.0\python\python.exe" -m pip install openupgradelib`.

     Sans les droits d'administrateur, pip annonce « Defaulting to user installation » et installe dans le profil
     de l'utilisateur, que le service Odoo (compte LOCALSERVICE) ne voit pas : l'erreur demeure. Le service peut
     aussi se redémarrer dans services.msc (« odoo-server-18.0 », Redémarrer). Sur Windows, `addons_path` se règle
     dans `C:\Program Files\Odoo 18.0…\server\odoo.conf`, chemins séparés par des virgules.
   - Odoo.sh : rien à faire, `requirements.txt` à la racine de la branche suffit (étape 2).

   Contrôle : `python3 -c "import openupgradelib"`, lancé avec le Python d'Odoo (sous Windows :
   `"C:\Program Files\Odoo 18.0\python\python.exe" -c "import openupgradelib"`), n'affiche aucune erreur.
4. Redémarrer Odoo. Activer le mode développeur, puis Apps > Mettre à jour la liste des Apps.
   Contrôle : une recherche de « MIS Builder » dans Apps doit trouver le module ; sinon, Odoo ne voit pas les
   modules OCA (voir Dépannage).
5. Installer « SYSCOHADA révisé – adaptation Odoo Community (Cameroun) » (`aite_syscohada_community`) :
   le socle, les états MIS et les modules OCA s'installent avec lui. Sur Odoo Enterprise,
   `aite_syscohada_reports` s'installe de lui-même avec les rapports d'Enterprise (`account_reports`) ; s'il reste
   « Activer » dans Apps, l'activer. Sur Odoo Community, ne pas l'activer : il dépend d'un module d'Enterprise et
   son installation échoue (on peut aussi ne pas copier son dossier). Ne pas installer les modules de
   démonstration sur une base de recette ou de production (voir plus bas).
6. Pour voir les menus Tableau de bord et Comptabilité de Facturation, le menu Facturation > Analyse >
   Syscohada et le plan comptable, cocher sur la fiche de chaque utilisateur concerné (comptables, et aussi
   l'administrateur qui installe), en mode développeur, section Technique, le droit « Montrer les fonctions de
   comptabilité complètes », puis recharger la page. Odoo Community ne donne ce droit à personne d'office : sans
   lui, Facturation n'affiche que Clients, Fournisseurs, Analyse et Configuration. Odoo 18 Community masque cette
   case : le socle AITE la remet depuis la version 18.0.1.3.2. Autre voie, valable avec toute version et pour
   plusieurs utilisateurs à la fois : Paramètres > Utilisateurs & Sociétés > Groupes (mode développeur),
   rechercher « comptabilité complètes », ouvrir « Technique / Montrer les fonctions de comptabilité complètes »,
   onglet Utilisateurs, Ajouter une ligne, cocher les utilisateurs, Sélectionner, enregistrer.
7. Le paramétrage (libellés et types de comptes, sous-comptes, taxes) s'applique tout seul aux sociétés au
   plan « cm ». Pour une société passée au plan « cm » plus tard : Facturation > Configuration > SYSCOHADA >
   Appliquer le paramétrage. Contrôle (droit de l'étape 6 coché) : Facturation > Configuration > Plan comptable,
   le compte 447210 « État, IRPP retenu sur salaires » existe.

En ligne de commande :

```bash
sudo -u odoo odoo-bin -c /etc/odoo/odoo.conf -d MA_BASE -i aite_syscohada_community --stop-after-init
```

Lancer `odoo-bin` (commande `odoo` avec le paquet .deb) sous l'utilisateur du service Odoo, souvent `odoo`, et avec
le fichier de configuration du service, jamais sous root ; même règle pour toutes les commandes de ce document
(mise à jour, données de démonstration, tests). Ces commandes écrivent dans le dossier de données d'Odoo
(`<data_dir>/filestore/MA_BASE`, par exemple les logos des sociétés de démonstration) : lancées sous root, elles y
créent des sous-dossiers que le service ne peut plus modifier. Si c'est déjà fait :
`chown -R odoo: <data_dir>/filestore/MA_BASE`.

Une sortie sans erreur ne prouve pas que l'installation a eu lieu : si le journal contient « invalid module names,
ignored: aite_syscohada_community », Odoo n'a pas trouvé le module (voir Dépannage).

Le menu Facturation (ou Comptabilité) > Analyse > Syscohada donne accès aux états et contrôles, au bilan actif,
au bilan passif, au compte de résultat, au tableau des flux de trésorerie et aux déclarations de TVA (Cameroun).

## Données de démonstration (facultatif)

Deux sociétés de démonstration, à installer uniquement sur une base de test ou de formation, jamais sur une base
de production ni sur une base de recette qui sert à autre chose : chaque module crée une société et plusieurs
centaines de pièces comptabilisées. Cette installation n'est pas réversible : la désinstallation du module semble
réussir, mais laisse la société de démonstration et ses pièces (Odoo ne peut pas supprimer une société qui porte
des données comptables ; seul le journal du serveur le signale). Pour l'effacer, restaurer une sauvegarde prise
avant l'installation ; à défaut, archiver la société (Paramètres > Utilisateurs & Sociétés > Sociétés) : elle
disparaît du sélecteur, ses pièces restent dans la base. Pour essayer les démonstrations sur des données proches
de la recette, travailler sur une copie de la base (gestionnaire de bases de données d'Odoo, bouton Dupliquer, ou
`createdb -T BASE_DE_RECETTE BASE_DE_TEST`). Chacune s'installe seule ; les deux peuvent cohabiter dans la même base.

```bash
odoo-bin -c odoo.conf -d BASE_DE_TEST -i aite_syscohada_demo,aite_syscohada_demo_services --stop-after-init
```

Pour des libellés en français partout (lignes de TVA de la localisation comprises), créer la base en français
(voir Prérequis) : ajouter `--load-language=fr_FR` à la première installation.

### Bar-hôtel (`aite_syscohada_demo`)

Le module crée la société « Bar-Hôtel Démo AITE » (Douala, FCFA, plan « cm ») et génère environ 700 pièces de
janvier 2025 à septembre 2026 :
- ventes du bar encaissées en espèces, Orange Money et MTN Mobile Money ;
- nuitées et séminaires, avec TVA sur encaissements ;
- achats avec précompte, loyers avec précompte de 15 %, honoraires avec retenue de 5 % ;
- logiciel étranger avec TVA autoliquidée et TSR ;
- paie, immobilisations, emprunt et inventaires ;
- impôt sur le résultat, affectation du résultat et dividendes avec IRCM.

Les 21 déclarations I/TVA-IR sont calculées. Les vingt premières sont liquidées, payées le 15 du mois suivant et validées. Celle de septembre 2026 reste en brouillon pour essayer la liquidation. Pour explorer, choisir la société « Bar-Hôtel Démo AITE » dans le sélecteur de sociétés, puis ouvrir le menu Syscohada.

### Services informatiques (`aite_syscohada_demo_services`)

Le module crée la société « Services Informatiques Démo AITE » (Douala, FCFA, plan « cm ») et génère les
opérations d'une société de services de janvier 2025 à septembre 2026 :
- infogérance mensuelle d'une banque, avec TVA sur encaissement et acompte de 2 % retenu par le client ;
- conseil en régie facturé au jour, projets au forfait avec retenue de 5 % sur honoraires, formations ;
- contrat de support annuel facturé d'avance, avec produits constatés d'avance au 31/12/2025 ;
- revente de matériel informatique (stock inventorié) ;
- services en nuage d'un éditeur étranger avec TVA autoliquidée et TSR, sous-traitance d'un développeur
  indépendant avec retenue, loyer avec précompte ;
- paie, ordinateurs, serveurs et progiciel amortis, impôt sur le résultat, affectation et dividendes avec IRCM.

Mêmes déclarations que le bar-hôtel : vingt validées, septembre 2026 en brouillon. On y voit en particulier le
report du crédit d'acompte (lignes L55 puis L53) né des retenues subies.

Durée de la génération : environ une minute. L'installation depuis l'interface fonctionne aussi. Sur un serveur lancé avec des workers, relever temporairement `limit_time_cpu` et `limit_time_real` (par exemple à 600) le temps de l'installation.

La paie et l'impôt sur le résultat des démonstrations sont illustratifs. Les taxes de retenue « taux à valider » y sont activées, dans ces seules sociétés.

## Mise à jour

Remplacer les dossiers des modules par ceux du nouveau paquet (y compris les nouveaux modules,
`aite_syscohada_demo_common` notamment), refaire l'étape 3 de l'installation (dépendances Python), redémarrer Odoo, puis mettre à
jour le socle : tous les modules AITE qui en dépendent sont mis à jour avec lui, et les nouvelles dépendances
s'installent.

```bash
odoo-bin -c odoo.conf -d MA_BASE -u aite_syscohada_base --stop-after-init
```

Depuis un paquet antérieur au 8 octobre 2026 (modules OCA dans un dossier `oca/` séparé) : retirer ce dossier de
`addons_path`, ou ne pas copier les trois modules OCA du nouveau paquet, pour ne jamais en avoir deux copies. Si
`VERSIONS.txt` annonce une nouvelle version de `mis_builder`, `date_range` ou `report_xlsx`, les ajouter à la
mise à jour : `-u aite_syscohada_base,mis_builder,date_range,report_xlsx`.

Les scripts de migration fournis relancent le paramétrage quand il change. Le paramétrage ne modifie jamais un
compte ou une taxe déjà utilisé par des écritures comptabilisées. Les données de démonstration déjà générées ne
sont pas recalculées par une mise à jour : pour la dernière version des scénarios, créer une nouvelle base de test.

## Vérifier l'installation

Sur une base de test :

```bash
odoo-bin -c odoo.conf -d BASE_DE_TEST -u aite_syscohada_base,aite_syscohada_mis,aite_syscohada_community \
  --test-enable --test-tags aite_syscohada --stop-after-init
```

Les modules OCA du paquet étant livrés sans leurs tests, une base de test peut aussi s'installer et se vérifier
en une seule commande : `-i aite_syscohada_community --test-enable --test-tags aite_syscohada`.

Résultat attendu : 110 tests, 0 échec. Trois d'entre eux sont des « échecs attendus » : ils documentent les défauts
connus listés ci-dessous. Après installation des données de démonstration,
`-u aite_syscohada_demo,aite_syscohada_demo_services --test-enable --test-tags aite_syscohada_demo` lance leurs
34 tests (15 pour le bar-hôtel, 19 pour les services informatiques).

## Dépannage de l'installation

| Message ou symptôme | Cause | Remède |
| --- | --- | --- |
| « Vous essayez d'installer le module "aite_syscohada_mis" qui dépend du module "mis_builder". Mais ce dernier n'est pas disponible sur votre système. » | Odoo ne voit pas les modules OCA : ils n'ont pas été copiés avec les modules AITE, ou leur dossier n'est pas dans `addons_path` (paquets antérieurs au 8 octobre 2026 : dossier `oca/` séparé) | Copier `mis_builder`, `date_range` et `report_xlsx` dans le même dossier que les modules AITE (ou ajouter leur dossier à `addons_path`), redémarrer Odoo, puis Apps > Mettre à jour la liste des Apps (mode développeur), et relancer l'installation |
| Après Apps > Importer un module : retour à l'accueil sans erreur et aucun module AITE dans Apps, ou « Erreur lors de l'importation du module 'aite_syscohada_…' » | Ce menu n'importe que des modules de données et ignore le code Python ; le zip du paquet n'y est même pas lu (ses modules sont dans `addons/`, pas à la racine du zip) | Décompresser le paquet sur le serveur et suivre l'installation. Sans accès au serveur (Odoo Online), l'installation n'est pas possible : Odoo.sh, image Docker ou serveur propre |
| En ligne de commande, `-i aite_syscohada_community` se termine sans erreur mais rien n'est installé ; le journal contient « invalid module names, ignored: aite_syscohada_community » | `addons_path` désigne la racine du paquet (`aite_syscohada_odoo18`) ou un dossier parent, au lieu du dossier qui contient directement les modules | Corriger `addons_path` (contrôle de l'étape 2), redémarrer Odoo, relancer la commande |
| « Vous essayez d'installer le module "aite_syscohada_reports" qui dépend du module "account_reports". Mais ce dernier n'est pas disponible sur votre système. » | Module réservé à Odoo Enterprise, activé sur Odoo Community | Rien à faire : sur Community, les états sont dans MIS Builder (Facturation > Analyse > Syscohada) ; ne pas activer ce module |
| « ModuleNotFoundError: No module named 'odoo_test_helper' » à l'installation (base non créée, modules non installés) | Modules OCA venant d'une autre source (dépôts OCA complets, avec leurs tests), installés avec `--test-enable` ou par un build de développement d'Odoo.sh | Utiliser les modules OCA du paquet, livrés sans tests ; ou installer sans `--test-enable` ; ou `pip install odoo-test-helper` |
| « Impossible d'installer le module "mis_builder" à cause d'une dépendance externe non trouvée : External dependency openupgradelib not installed… » | Paquet Python de `mis_builder` absent de l'environnement d'Odoo | Installer `openupgradelib` selon l'étape 3 (environnement virtuel, paquet .deb, image Docker dérivée, Windows en administrateur avec le Python d'Odoo, Odoo.sh), puis redémarrer Odoo et relancer l'installation |
| « error: externally-managed-environment » en lançant pip | Python système de Debian 12, d'Ubuntu 24.04 ou de l'image Docker officielle, protégé par la PEP 668 | Ajouter `--break-system-packages` à la commande de l'étape 3 (avec `sudo` pour un Odoo installé par le paquet .deb) ; image Docker : image dérivée de l'étape 3 |
| « Invalid language code: fr_BE » (ou un autre code fr_…) en enregistrant la Localisation fiscale | Versions 18.0.1.2.0 et antérieures : le paramétrage écrivait les libellés dans des langues non installées | Mettre à jour en 18.0.1.3.0 au moins, puis enregistrer de nouveau |
| Les modules AITE n'apparaissent pas dans Apps | Liste des Apps non mise à jour, dossier absent de `addons_path`, ou `addons_path` qui pointe sur la racine du paquet au lieu de son dossier `addons/` | Mode développeur, Apps > Mettre à jour la liste des Apps ; vérifier `addons_path` (contrôle de l'étape 2) et redémarrer Odoo |
| Facturation n'affiche que Clients, Fournisseurs, Analyse et Configuration : pas de Tableau de bord, de Comptabilité ni de menu Syscohada sous Analyse | Droit « Montrer les fonctions de comptabilité complètes » non coché sur l'utilisateur, administrateur compris : Odoo Community ne le donne à personne d'office | Étape 6 de l'installation, puis recharger la page (F5) |
| La case « Montrer les fonctions de comptabilité complètes » manque dans la section Technique de la fiche utilisateur | Odoo 18 Community la masque ; le socle AITE la remet depuis la version 18.0.1.3.2 (version antérieure, ou socle pas encore mis à jour) | Paramètres > Utilisateurs & Sociétés > Groupes (étape 6) ; ou mettre à jour le socle (voir Mise à jour) |
| États Syscohada faux (par exemple une vente rangée en report à nouveau et en fournisseurs), contrôle « Comptes non rattachés » en alerte ; ou « La société … n'est pas à un plan comptable SYSCOHADA » au menu Appliquer le paramétrage | Société hors plan « cm » (plan générique, autre pays) : le paramétrage ne s'applique pas | Tant que la société n'a pas d'écritures : Pack « SYSCOHADA pour Sociétés » (Prérequis), puis Facturation > Configuration > SYSCOHADA > Appliquer le paramétrage ; sinon, reprise dans une société au plan « cm » avec l'expert-comptable |

## Limites connues

- Les taux des retenues à la source, du précompte sur achats et de la taxe de séjour restent à valider : ces taxes
  sont créées inactives.
- La déclaration de TVA :
  - le crédit antérieur (L17) n'est pas recalculé si la déclaration du mois suivant a été créée avant la
    validation du mois précédent : le corriger à la main tant qu'elle est en brouillon, ou la recréer ;
  - l'extourne d'une facture portant une retenue n'est pas déduite des lignes L40 à L43 ;
  - la liquidation doit être lancée depuis la société de la déclaration.
- Le TFT de MIS Builder ne neutralise pas les virements internes entre comptes d'immobilisations ; l'assistant
  « États et contrôles (AITE) » les neutralise.
- Les notes annexes, la DSF et la paie camerounaise sont prévues dans les lots suivants.

## Documentation

- `docs/guide-syscohada-odoo18.html` : guide complet (installation, paramétrage, états, déclaration, contrôles,
  procédures de clôture), à ouvrir dans un navigateur.
- `docs/flux-comptables-syscohada.html` : cartographie des flux comptables, de la facture à la DSF.

AITE Consulting, Douala — https://aite-consulting.com
