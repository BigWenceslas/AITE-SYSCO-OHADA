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
| `addons/mis_builder`, `addons/date_range`, `addons/report_xlsx` | Dépendances OCA (branche 18.0, licence AGPL-3), indispensables : `aite_syscohada_mis` et `aite_syscohada_community` ne s'installent pas sans elles |
| `requirements.txt` | Dépendance Python de `mis_builder` : `openupgradelib` |
| `licences/` | Licences AGPL-3 des dépôts OCA |
| `docs/` | Guide complet (`guide-syscohada-odoo18.html`) et cartographie des flux comptables |

Le dossier `addons/` contient les dix modules : c'est le seul chemin à déclarer dans `addons_path`.

## Prérequis

- Odoo 18, Community ou Enterprise, avec la localisation camerounaise `l10n_cm` (fournie avec Odoo).
- Le paquet Python `openupgradelib`, exigé par mis_builder, installé dans l'environnement Python d'Odoo :
  `pip install -r requirements.txt` (ou `pip install openupgradelib`).
- Des sociétés en FCFA (XAF) avec le plan comptable camerounais « cm » (SYSCOHADA révisé).

## Installation

1. Copier **tout le contenu** de `addons/` (les dix modules, AITE et OCA) dans un dossier d'extensions du
   serveur, par exemple `/opt/odoo/extra-addons`. Si `mis_builder`, `date_range` ou `report_xlsx` sont déjà
   installés sur le serveur depuis les dépôts OCA, garder ces versions et ne pas copier ces trois dossiers.
2. Ajouter ce dossier à `addons_path` dans le fichier de configuration d'Odoo (s'il n'y est pas déjà).
3. Installer la dépendance Python dans l'environnement d'Odoo : `pip install -r requirements.txt`.
4. Redémarrer Odoo. Activer le mode développeur, puis Applications > Mettre à jour la liste des applications.
   Contrôle : en retirant le filtre « Applications » et en cherchant `mis_builder`, le module « MIS Builder »
   doit apparaître ; sinon, Odoo ne voit pas les modules OCA (voir Dépannage).
5. Installer « SYSCOHADA révisé – adaptation Odoo Community (Cameroun) » (`aite_syscohada_community`) :
   le socle, les états MIS et les modules OCA s'installent avec lui. Sur Odoo Enterprise, installer aussi
   `aite_syscohada_reports`. Ne pas installer les modules de démonstration sur une base de recette ou de
   production (voir plus bas).
6. Le paramétrage (libellés et types de comptes, sous-comptes, taxes) s'applique tout seul aux sociétés au
   plan « cm ». Pour une société créée plus tard : Configuration > SYSCOHADA > Appliquer le paramétrage.
7. Pour les comptables, cocher sur leur fiche utilisateur (mode développeur) le droit technique
   « Afficher toutes les fonctionnalités comptables ».

En ligne de commande :

```bash
odoo-bin -c odoo.conf -d MA_BASE -i aite_syscohada_community --stop-after-init
```

Le menu Facturation (ou Comptabilité) > Analyse > Syscohada donne accès aux états et contrôles, au bilan actif,
au bilan passif, au compte de résultat, au tableau des flux de trésorerie et aux déclarations de TVA (Cameroun).

## Données de démonstration (facultatif)

Deux sociétés de démonstration, à installer uniquement sur une base de test ou de formation, jamais sur une base
de production ni sur une base de recette qui sert à autre chose : chaque module crée une société et plusieurs
centaines de pièces comptabilisées. Chacune s'installe seule ; les deux peuvent cohabiter dans la même base.

```bash
odoo-bin -c odoo.conf -d BASE_DE_TEST -i aite_syscohada_demo,aite_syscohada_demo_services --stop-after-init
```

Pour des libellés en français partout (lignes de TVA de la localisation comprises), créer la base en français :
ajouter `--load-language=fr_FR` à la première installation.

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
`aite_syscohada_demo_common` notamment), redémarrer Odoo, puis mettre à jour le socle : tous les modules AITE qui en
dépendent sont mis à jour avec lui, et les nouvelles dépendances s'installent.

```bash
odoo-bin -c odoo.conf -d MA_BASE -u aite_syscohada_base --stop-after-init
```

Les scripts de migration fournis relancent le paramétrage quand il change. Le paramétrage ne modifie jamais un
compte ou une taxe déjà utilisé par des écritures comptabilisées. Les données de démonstration déjà générées ne
sont pas recalculées par une mise à jour : pour la dernière version des scénarios, créer une nouvelle base de test.

## Vérifier l'installation

Sur une base de test :

```bash
odoo-bin -c odoo.conf -d BASE_DE_TEST -u aite_syscohada_base,aite_syscohada_mis,aite_syscohada_community \
  --test-enable --test-tags aite_syscohada --stop-after-init
```

Résultat attendu : 106 tests, 0 échec. Trois d'entre eux sont des « échecs attendus » : ils documentent les défauts
connus listés ci-dessous. Après installation des données de démonstration,
`-u aite_syscohada_demo,aite_syscohada_demo_services --test-enable --test-tags aite_syscohada_demo` lance leurs
34 tests (15 pour le bar-hôtel, 19 pour les services informatiques).

## Dépannage de l'installation

| Message ou symptôme | Cause | Remède |
| --- | --- | --- |
| « Vous essayez d'installer le module "aite_syscohada_mis" qui dépend du module "mis_builder". Mais ce dernier n'est pas disponible sur votre système. » | Odoo ne voit pas les modules OCA : ils n'ont pas été copiés avec les modules AITE, ou leur dossier n'est pas dans `addons_path` (paquets antérieurs au 8 octobre 2026 : dossier `oca/` séparé) | Copier `mis_builder`, `date_range` et `report_xlsx` dans le même dossier que les modules AITE (ou ajouter leur dossier à `addons_path`), redémarrer Odoo, puis Applications > Mettre à jour la liste des applications, et relancer l'installation |
| « Impossible d'installer le module "mis_builder" à cause d'une dépendance externe non trouvée : External dependency openupgradelib not installed… » | Paquet Python de `mis_builder` absent de l'environnement d'Odoo | `pip install -r requirements.txt` dans l'environnement Python d'Odoo (image Docker : l'ajouter à l'image ; Odoo.sh : `requirements.txt` à la racine du dépôt), puis redémarrer Odoo |
| Les modules AITE n'apparaissent pas dans Applications | Liste des applications non mise à jour, ou dossier absent de `addons_path` | Mode développeur, Applications > Mettre à jour la liste des applications ; vérifier `addons_path` et redémarrer Odoo |
| Le menu Syscohada n'apparaît pas après l'installation | Droit « Afficher toutes les fonctionnalités comptables » non coché | Étape 7 de l'installation |

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
