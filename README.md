# SYSCOHADA révisé pour Odoo 18 — AITE Consulting

États financiers SYSCOHADA, déclaration mensuelle I/TVA-IR et, à venir, notes annexes, DSF et paie camerounaise, pour Odoo 18 Community (Enterprise en option).

## Organisation du dépôt

| Chemin | Contenu |
| --- | --- |
| `addons/` | Les modules Odoo |
| `CLAUDE.md` | Contexte du projet pour Claude Code, lu à chaque session |
| `ROADMAP.md` | Feuille de route, état d'avancement, questions ouvertes |
| `.claude/skills/` | Savoirs chargés par Claude Code à la demande : tests, fiscalité camerounaise, classeur DSF |
| `scripts/` | Installation de l'environnement, lancement des tests, construction du paquet de livraison |
| `docs/` | Guide complet en HTML (`guide-syscohada-odoo18.html`, un seul fichier illustré de 27 captures d'écran ; source `guide/guide.md` et captures `guide/captures/`, outils dans `scripts/guide/`), lisez-moi d'installation du paquet (`installation.md`), document de travail (`document-de-travail.md` : audit, correspondances, fiscalité, plan), cartographie des flux comptables, relevé du classeur DSF de la DGI |
| `dist/` | Paquet de livraison construit par `scripts/build_release.sh` (non versionné) |

## Travailler avec Claude Code

1. `git init` dans ce dossier, puis `scripts/setup_dev.sh` (Odoo 18 Community, OCA, environnement Python, `odoo.conf`).
2. Lancer `claude` à la racine du dépôt : `CLAUDE.md` est chargé automatiquement ; la commande `/memory` permet de le vérifier.
3. Demander par exemple : « Lis ROADMAP.md et propose le plan du lot 3 ». La commande `/odoo-tests` lance les tests.

## Modules

Trois modules Community, sans aucune dépendance à Odoo Enterprise, un module facultatif pour Enterprise et deux modules facultatifs de données de démonstration (avec leur moteur commun).

| Module | Rôle |
| --- | --- |
| `aite_syscohada_base` | Référentiel des 124 rubriques (bilan, compte de résultat, TFT), moteur de calcul, paramétrage du plan « cm » et des taxes camerounaises, contrôles, assistant « États et contrôles (AITE) » |
| `aite_syscohada_mis` | Bilan actif, bilan passif, compte de résultat et TFT en modèles MIS Builder |
| `aite_syscohada_community` | Menus « Syscohada » ouvrant chaque état en un clic (exercices N et N-1, exports PDF et Excel de MIS), déclaration mensuelle I/TVA-IR complète (lignes L0 à L80), écritures de liquidation de la TVA et de l'acompte, impression PDF |
| `aite_syscohada_reports` | Les quatre états en rapports `account.report`, pour Odoo Enterprise seulement (facultatif) |
| `aite_syscohada_demo` | Société de démonstration « Bar-Hôtel Démo AITE » : 21 mois d'opérations (janvier 2025 à septembre 2026) et de déclarations I/TVA-IR, générés à l'installation ; bases de test seulement (facultatif) |
| `aite_syscohada_demo_services` | Société de démonstration « Services Informatiques Démo AITE » : infogérance, régie, projets, formations, support annuel, revente de matériel, mêmes 21 mois ; bases de test seulement (facultatif) |
| `aite_syscohada_demo_common` | Moteur commun des démonstrations (pièces par lots, paie, amortissements, déclarations, clôture), sans données |

## Installation

Chez un client, installer depuis le paquet de livraison (zip, voir plus bas) : ses dix modules, AITE et OCA, sont dans un seul dossier `addons/` ; suivre son lisez-moi (`docs/installation.md`). Les étapes ci-dessous valent pour un environnement monté à la main.

1. Odoo 18 Community avec la localisation `l10n_cm`.
2. Modules OCA, branche 18.0 : `mis_builder` (dépôt mis-builder), `date_range` (server-ux), `report_xlsx` (reporting-engine).
3. `pip install openupgradelib` (dépendance Python de mis_builder).
4. Installer `aite_syscohada_community` : les deux autres modules suivent.
5. Pour les comptables : en mode développeur, cocher sur leur utilisateur (et sur l'administrateur), section Technique, le droit « Montrer les fonctions de comptabilité complètes » (Show Full Accounting Features), pour voir les écritures et le plan comptable.

Le menu Facturation (ou Comptabilité) > Analyse > Syscohada donne accès à : États et contrôles (AITE), Bilan actif, Bilan passif, Compte de résultat, Tableau des flux de trésorerie, Déclarations de TVA (Cameroun).

### Paquet de livraison

`scripts/build_release.sh` construit `dist/aite_syscohada_odoo18_<version>_<date>.zip` : dans un même dossier `addons/` (un seul chemin à déclarer dans `addons_path`), les sept modules AITE et les modules OCA `mis_builder`, `date_range` et `report_xlsx` aux versions testées (textes des licences dans `licences/`, licence de chaque module dans `VERSIONS.txt`) ; `requirements.txt` (`openupgradelib`), le guide HTML, un lisez-moi d'installation (copie de `docs/installation.md`) et `VERSIONS.txt` (versions et commits d'origine). L'intégration continue le publie en artefact « paquet-odoo18 ». Installation depuis le zip vérifiée sur une base vierge, avec le seul dossier `addons/` du paquet dans `addons_path` : 107 tests sans échec ; l'intégration continue refait cette installation à chaque push.

### Données de démonstration

Sur une base de test seulement : `odoo-bin -c odoo.conf -d <base> -i aite_syscohada_demo,aite_syscohada_demo_services --stop-after-init` (une à deux minutes ; ajouter `--load-language=fr_FR` à la création de la base pour des libellés de TVA en français). Chaque module s'installe aussi seul.

`aite_syscohada_demo` crée la société « Bar-Hôtel Démo AITE » et environ 700 pièces :
- ventes du bar encaissées en espèces, Orange Money et MTN Mobile Money ;
- nuitées et séminaires avec TVA sur encaissements ;
- achats avec précompte, loyers, honoraires, logiciel étranger (TVA autoliquidée et TSR) ;
- paie, immobilisations, emprunt, stocks, impôt, affectation du résultat et dividendes ;
- 20 déclarations I/TVA-IR liquidées, payées et validées, plus celle de septembre 2026 en brouillon.

`aite_syscohada_demo_services` crée la société « Services Informatiques Démo AITE » :
- infogérance d'une banque (TVA sur encaissement, acompte de 2 % retenu par le client), régie au jour, projets au forfait avec retenue sur honoraires, formations ;
- contrat de support annuel facturé d'avance et produits constatés d'avance au 31/12/2025 ;
- revente de matériel informatique, stock inventorié ;
- services en nuage d'un éditeur étranger (TVA autoliquidée et TSR), sous-traitance avec retenue, loyer avec précompte ;
- paie, ordinateurs, serveurs et progiciel amortis, impôt, affectation et dividendes avec IRCM ;
- les mêmes 20 déclarations validées et septembre 2026 en brouillon, dont un crédit d'acompte reporté (L55 vers L53).

Les scénarios et leurs calculs à la main sont dans `addons/aite_syscohada_demo/models/demo_scenario.py`, `addons/aite_syscohada_demo_services/models/scenario.py` et les tests de chaque module.

## Déclaration mensuelle I/TVA-IR (lot 2)

Menu Syscohada > Déclarations de TVA (Cameroun) : une déclaration par mois, à déposer et payer avant le 15 du mois suivant.

| Section du formulaire | Lignes | Source dans Odoo |
| --- | --- | --- |
| 0. TSR | L0 | Retenue sur factures de prestataires étrangers, compte 447120 |
| 1. Droits d'accises | L1 à L8 | Saisie du déclarant |
| 2 à 5. TVA | L10 à L35 | Étiquettes de taxe des écritures exigibles (définition officielle de `l10n_cm`) ; L11, L24 à L27 et L34 saisis |
| 6. TVA à payer | L36 à L39 | L32, TVA retenue à la source (447160), TVA autoliquidée sur prestations étrangères (447161) |
| 7. À reverser | L40 à L44 | Retenues opérées sur factures fournisseurs : 447170, 447180, 447130, 447140 |
| 8. À déduire | L45 à L49 | Retenues subies : 449220, 449210, 449230, 449240 |
| 9. Acomptes d'impôt | L50 à L55 | Chiffre d'affaires déclaré (L15) × taux de l'acompte (2 % par défaut) + CAC (10 %), moins L49 et le crédit reporté |
| 10. IRCM, 11. IRNC | L56 à L66 | Bases saisies, taux de 15 % et CAC modifiables |
| 12. Salaires | L67 à L73 | Écritures de paie sur 447210 (IRPP), 447215 (CAC), 447220 à 447260 (CFC, FNE, RAV, TDL) |
| 13. Plus-values, 14. Timbre d'aéroport | L74 à L80 | Saisie du déclarant |
| Récapitulatif | Total à payer | Somme des totaux de section |

- Crédits reportés automatiquement d'un mois sur l'autre : TVA (L35 vers L17) et acompte (L55 vers L53).
- Écriture de liquidation : comptes de TVA soldés vers 4441 (à payer), 4449 (crédit) ou 4445 (remboursement) ; acompte en débit de 449250 et crédit de 441100. Refusée si le grand livre ne concorde pas avec la déclaration.
- Impression PDF du formulaire (bouton Imprimer), document de travail pour la saisie sur le portail de la DGI.

Paramétrage ajouté au socle (version 18.0.1.1.0) : 22 comptes de retenues et d'avances d'impôt, 9 taxes de retenue à la source (dont l'autoliquidation de la TVA sur prestations étrangères), créées inactives car leurs taux restent à valider. Il s'applique automatiquement à la mise à jour du module, ou par Configuration > SYSCOHADA > Appliquer le paramétrage.

## Tests

```bash
scripts/run_tests.sh <base> aite_syscohada_base,aite_syscohada_mis,aite_syscohada_community
```

Résultat sur Odoo 18 Community, base vierge, 8 octobre 2026 : 107 tests (65 de base et 42 avancés), 0 échec, dont 3 échecs attendus qui documentent des défauts connus listés dans `ROADMAP.md`. Le test de volume se lance à part : `scripts/run_tests.sh <base> aite_syscohada_community aite_syscohada_volume` (1 test, 36 s). Les données de démonstration ont leurs 34 tests (15 pour le bar-hôtel, 19 pour les services informatiques), à lancer sur une base où les deux modules sont installés : `scripts/run_tests.sh <base> aite_syscohada_demo,aite_syscohada_demo_services aite_syscohada_demo`. L'intégration continue `.github/workflows/tests.yml` exécute le tout à chaque push et construit le paquet de livraison.

## Autres besoins couverts en Community par des modules OCA (branche 18.0)

| Besoin | Module OCA |
| --- | --- |
| Rapprochement bancaire | account_reconcile_oca (account-reconcile) |
| Import des relevés | account_statement_import_file, account_statement_import_sheet_file (bank-statement-import) |
| Immobilisations | account_asset_management (account-financial-tools) |
| Balance, grand livre, balance âgée | account_financial_report (account-financial-reporting) |
| Régularisations de clôture | account_cutoff_base (account-closing) |
| Paie (lot 5) | payroll, payroll_account (payroll) |

## Limites connues

- TFT dans MIS : les virements internes entre comptes d'immobilisations ne sont pas neutralisés (l'assistant « États et contrôles » les neutralise).
- Taux des retenues, du précompte et de la taxe de séjour à valider avant activation des taxes.
- À valider avec l'expert-comptable : base de l'acompte (L15), CAC appliqués à l'acompte, à l'IRCM et à l'IRNC mais pas aux retenues, déductions L52 imputées sur le total CAC compris.
- L24 (TVA retenue par les clients) et les sections 1, 10, 11, 13 et 14 restent en saisie.
- La paie doit créditer les comptes 447210 à 447260 pour alimenter la section 12.
