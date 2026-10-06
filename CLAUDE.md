# SYSCOHADA révisé pour Odoo 18 — AITE Consulting

Ce fichier est lu par Claude Code au début de chaque session. Il décrit le projet, les commandes, l'architecture et les règles à respecter.
La feuille de route, l'état d'avancement et les questions ouvertes sont dans `ROADMAP.md` : le lire avant de commencer une tâche, le mettre à jour en la terminant.

## Le projet

- **But** : rendre Odoo 18 conforme au SYSCOHADA révisé et à la fiscalité camerounaise : états financiers (bilan, compte de résultat, tableau des flux de trésorerie), déclaration mensuelle I/TVA-IR, notes annexes, DSF (classeur Excel de la DGI, puis API), paie camerounaise.
- **Intégrateur** : AITE Consulting, Douala. Responsable technique : Aristide BESSALA (CTO). Projet né du dossier LAVERANDAH (bar-hôtel, Douala).
- **Cible principale : Odoo 18 Community** avec des modules OCA. Enterprise reste pris en charge par un module facultatif.
- **Langue** : tout ce que voit l'utilisateur est en français (libellés, messages, rapports, documentation, commentaires). Identifiants de code en anglais, préfixés `aite_`.
- **Devise** : XAF (FCFA), sans décimale.

## Commandes

```bash
scripts/setup_dev.sh [dossier]          # une fois : Odoo 18 Community, OCA, venv, odoo.conf
# créer une base de développement
../venv/bin/python ../odoo18/odoo-bin -c odoo.conf -d aite_dev -i aite_syscohada_community --stop-after-init
# toute la suite de tests (2 à 3 minutes)
scripts/run_tests.sh aite_dev aite_syscohada_base,aite_syscohada_mis,aite_syscohada_community
# un seul test
scripts/run_tests.sh aite_dev aite_syscohada_community "/aite_syscohada_community:TestItvairForm.test_march_full_form"
# données de démonstration sur une copie de base, puis leurs tests
createdb -T aite_dev aite_demo && ../venv/bin/python ../odoo18/odoo-bin -c odoo.conf -d aite_demo -i aite_syscohada_demo --stop-after-init
scripts/run_tests.sh aite_demo aite_syscohada_demo aite_syscohada_demo
# paquet de livraison dist/aite_syscohada_odoo18_<version>_<date>.zip (modules AITE, OCA figés, guide, lisez-moi)
scripts/build_release.sh
# régénérer le référentiel des rubriques puis le XML Enterprise (jamais d'édition à la main)
python addons/aite_syscohada_base/tools/gen_rubriques.py
../venv/bin/python ../odoo18/odoo-bin shell -c odoo.conf -d aite_dev --no-http < addons/aite_syscohada_reports/tools/generate_enterprise_xml.py
```

Résultat de référence : 104 tests (62 de base et 42 avancés `test_adv_*.py`), 0 échec, dont 3 échecs attendus qui documentent des défauts connus (un test ignoré si `aite_syscohada_reports` est absent). Test de volume à part, sur une base neuve : `scripts/run_tests.sh <base> aite_syscohada_community aite_syscohada_volume`. Données de démonstration : 15 tests (étiquette `aite_syscohada_demo`), sur une base où le module est installé.

## Architecture

| Module | Rôle | Édition |
| --- | --- | --- |
| `aite_syscohada_base` | Référentiel des 124 rubriques, moteur de calcul de référence, paramétrage du plan « cm » et des taxes, 9 contrôles, assistant « États et contrôles (AITE) » | Les deux |
| `aite_syscohada_mis` | Bilan actif, bilan passif, compte de résultat et TFT en modèles MIS Builder, générés depuis le référentiel | Community |
| `aite_syscohada_community` | États en un clic (MIS, N et N-1), déclaration mensuelle I/TVA-IR complète (L0 à L80), écritures de liquidation, impression | Community |
| `aite_syscohada_reports` | Les quatre états en `account.report`, XML généré depuis le référentiel | Enterprise seulement |
| `aite_syscohada_demo` | Société « Bar-Hôtel Démo AITE » générée à l'installation : 21 mois de pièces et de déclarations (scénario chiffré dans `models/demo_scenario.py`) | Community, bases de test |

Flux de données : `data/aite.syscohada.rubrique.csv` (124 rubriques, formules de comptes, cellules DSF) → `syscohada_engine.compute(company, date_from, date_to)` (moteur pur Python, référence) → rendus : assistant, MIS, `account.report`, et demain la DSF. Les tests comparent chaque rendu au moteur.

Fichiers clés :
- `addons/aite_syscohada_base/tools/gen_rubriques.py` : source du référentiel (rubriques, formules, cellules du classeur DSF).
- `addons/aite_syscohada_base/models/syscohada_engine.py` : analyse des formules, soldes, flux, calcul des états.
- `addons/aite_syscohada_base/models/res_company.py` : `_aite_syscohada_setup()` ; libellés, types et sous-comptes du plan, taxes, retenues à la source.
- `addons/aite_syscohada_base/models/syscohada_check.py` : contrôles (équilibre, résultat, TFT, comptes d'attente, caisses, espèces, bascules).
- `addons/aite_syscohada_community/models/vat_declaration.py` : TVA (lignes L10 à L35 lues dans la définition officielle de `l10n_cm`) et liquidation.
- `addons/aite_syscohada_community/models/itvair.py` : lignes L0 à L80 hors TVA (table `LINES`), reports de crédit, total à payer.

Syntaxe des formules du référentiel (celle du moteur `account_codes` d'Enterprise) : préfixes de comptes additionnés, exclusions `\(...)`, suffixe `D` ou `C` pour ne retenir que les soldes débiteurs ou créditeurs ; actif en deux formules (brut, amortissements) ; agrégations `AE+AF-AG` ; TFT en termes `TYPE:ARG` (`R:` rubrique de résultat, `B:` et `B0:` bilan de fin et de début, `V:` variation, `P:`, `E:`, `S:`, `D:`, `C:`, `DX:` et `CX:` hors virements internes).

## Règles à respecter

1. **Le référentiel est la source unique.** On modifie `gen_rubriques.py`, on régénère le CSV et le XML Enterprise, on relance les tests (l'un d'eux vérifie que le XML livré est à jour).
2. **Montants attendus calculés à la main.** Chaque test chiffré explique son calcul ; on ne recopie jamais la sortie du code dans une assertion.
3. **Paramétrage idempotent.** Tout passe par `res.company._aite_syscohada_setup()`. Les objets créés sont enregistrés sous `aite_syscohada_base.<id société>_<clé>` (`_aite_register_tax`, `_aite_tax_ref`). `_aite_safe_write` ne modifie jamais un objet déjà utilisé par des écritures comptabilisées.
4. **Taux non validés : taxe inactive**, libellé suffixé « (taux à valider) ». Ne jamais inventer un taux ou une règle fiscale : citer la source (DGI, loi de finances) ou écrire « à valider ».
5. **Paramétrage modifié : version incrémentée** dans `__manifest__.py` et script `migrations/<version>/post-migrate.py` qui relance le paramétrage.
6. **Comptes** : passer par `company._aite_account("447210")` ou `_aite_accounts_prefix("445")`. En Odoo 18, le code de compte dépend de la société (`code_store`).
7. **Odoo 18** : vues `<list>` (pas `<tree>`), `invisible=` et `readonly=` en expressions (plus d'`attrs`), `Command.create/set`, `_read_group`.
8. **Community d'abord** : aucune dépendance Enterprise (`account_reports`, `account_accountant`…) dans base, mis ou community.
9. **Invariants à ne jamais casser** : total actif BZ = total passif DZ ; résultat XI = CJ hors résultats antérieurs ; variation de trésorerie ZH = BT − DT ; chaque compte du plan capté exactement une fois au débit et une fois au crédit (`test_coverage`).
10. **Déclaration mensuelle** : la liquidation de TVA ne touche que les comptes 443 et 445 (hors compte d'attente 4438) ; chaque ligne de retenue a son compte dédié (table dans le skill `fiscalite-cameroun`) ; les crédits (L35 vers L17, L55 vers L53) ne se reportent que depuis une déclaration validée.

## Pièges connus

- `--test-tags` sans `-u` importe les tests de tous les modules installés, dont `web`, qui échoue à l'import : toujours passer `-u <modules>` (ce que fait `run_tests.sh`).
- Mettre à jour `aite_syscohada_base` met aussi à jour les modules qui en dépendent : leurs tests tournent aussi.
- MIS Builder exige le paquet Python `openupgradelib`.
- Rapport de TVA `l10n_cm` : montant d'une étiquette = solde × (−1 si `tax_tag_invert`) × (−1 si `tax_negate`) ; lignes retenues par `account.move.line._get_tax_exigible_domain()` (TVA sur encaissements).
- Le TFT de MIS et d'Enterprise ne neutralise pas les virements internes entre comptes d'immobilisations (le moteur, si) : écart connu et documenté.
- Le classeur DSF 2021 de la DGI contient 18 formules fausses et un taux d'IS obsolète : ne jamais s'en servir comme référence de calcul (skill `dsf-classeur`).
- `aite_syscohada_reports` ne s'installe que sur Enterprise ; sans lui, le test « XML livré à jour » est ignoré, c'est normal.
- Le lanceur d'Odoo 18 ignore `@unittest.expectedFailure` : les tests avancés redéfinissent `_callTestMethod` (voir `test_adv_declaration_sequence.py`). Un échec attendu qui réussit fait échouer le test : retirer alors le décorateur.
- Port 8069 occupé par un autre Odoo : `http_enable = False` ne suffit pas pendant les tests ; passer par `ODOO_CONF` une copie d'`odoo.conf` avec un autre `http_port` et `gevent_port`.
- Le test de volume, lancé après les autres dans le même processus, peut dépasser 10 minutes (statistiques PostgreSQL faussées) : il a son étiquette `aite_syscohada_volume`. Il lui faut une base vraiment neuve : copiée après une suite de tests, la base hérite de statistiques qui disent les tables comptables vides (`reltuples` à 0, pages non nulles) et le test passe de 30 s à plus de 4 minutes, selon le passage de l'autovacuum. La CI copie donc ses bases avant la suite.
- Même cause pour la démonstration, générée en une seule transaction : sans `ANALYZE` des tables comptables à chaque mois, elle passe de 1 à plus de 10 minutes sur une base dont les statistiques disent ces tables vides (base copiée après une suite de tests).
- La liquidation de TVA passe par le premier journal d'opérations diverses (ordre `sequence, type, code`) : un journal général ajouté (paie) prend une séquence plus grande.
- Sans relevés bancaires, les paiements restent sur les comptes de paiements en attente : la démonstration met le compte du journal dans `payment_account_id` des modes de paiement.
- Créer des pièces une à une coûte trois à cinq fois plus cher qu'en lot (`create` d'une liste, puis `action_post`, paiements lettrés par `_reconcile_plan`) : c'est ce que fait la démonstration.

## Façon de travailler

- Avant un lot : lire sa section dans `ROADMAP.md` et lister les questions ouvertes qui le bloquent.
- Tests d'abord (scénario chiffré à la main), code ensuite, toute la suite avant de conclure.
- En fin de tâche : cocher `ROADMAP.md`, mettre à jour `README.md` si l'installation change.
- Livraison : un seul zip de tous les modules avec son README (`scripts/build_release.sh`, lisez-moi `docs/installation.md`), jamais de livraison partielle.

## Contexte métier

- Skill `fiscalite-cameroun` : TVA, formulaire I/TVA-IR ligne par ligne, retenues, acomptes, IS, calendrier, comptes.
- Skill `dsf-classeur` : structure du classeur DSF, anomalies, correspondances rubriques → cellules.
- `docs/flux-comptables-syscohada.html` : cartographie des flux comptables (lecture humaine).
- `docs/dsf/Releve_classeur_DSF_Normal_2021.xlsx` : relevé cellule par cellule du classeur DGI.
- Document de travail (audit, correspondances, plan) : https://claude.ai/code/artifact/829a1e6e-2d6c-415f-9dd6-5793752963b2
