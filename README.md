# SYSCOHADA révisé pour Odoo 18 — AITE Consulting

États financiers SYSCOHADA, déclaration mensuelle I/TVA-IR et, à venir, notes annexes, DSF et paie camerounaise, pour Odoo 18 Community (Enterprise en option).

## Organisation du dépôt

| Chemin | Contenu |
| --- | --- |
| `addons/` | Les modules Odoo |
| `CLAUDE.md` | Contexte du projet pour Claude Code, lu à chaque session |
| `ROADMAP.md` | Feuille de route, état d'avancement, questions ouvertes |
| `.claude/skills/` | Savoirs chargés par Claude Code à la demande : tests, fiscalité camerounaise, classeur DSF |
| `scripts/` | Installation de l'environnement et lancement des tests |
| `docs/` | Cartographie des flux comptables, relevé du classeur DSF de la DGI |

## Travailler avec Claude Code

1. `git init` dans ce dossier, puis `scripts/setup_dev.sh` (Odoo 18 Community, OCA, environnement Python, `odoo.conf`).
2. Lancer `claude` à la racine du dépôt : `CLAUDE.md` est chargé automatiquement ; la commande `/memory` permet de le vérifier.
3. Demander par exemple : « Lis ROADMAP.md et propose le plan du lot 3 ». La commande `/odoo-tests` lance les tests.

## Modules

Trois modules Community, sans aucune dépendance à Odoo Enterprise, plus un module facultatif pour Enterprise.

| Module | Rôle |
| --- | --- |
| `aite_syscohada_base` | Référentiel des 124 rubriques (bilan, compte de résultat, TFT), moteur de calcul, paramétrage du plan « cm » et des taxes camerounaises, contrôles, assistant « États et contrôles (AITE) » |
| `aite_syscohada_mis` | Bilan actif, bilan passif, compte de résultat et TFT en modèles MIS Builder |
| `aite_syscohada_community` | Menus « Syscohada » ouvrant chaque état en un clic (exercices N et N-1, exports PDF et Excel de MIS), déclaration mensuelle I/TVA-IR complète (lignes L0 à L80), écritures de liquidation de la TVA et de l'acompte, impression PDF |
| `aite_syscohada_reports` | Les quatre états en rapports `account.report`, pour Odoo Enterprise seulement (facultatif) |

## Installation

1. Odoo 18 Community avec la localisation `l10n_cm`.
2. Modules OCA, branche 18.0 : `mis_builder` (dépôt mis-builder), `date_range` (server-ux), `report_xlsx` (reporting-engine).
3. `pip install openupgradelib` (dépendance Python de mis_builder).
4. Installer `aite_syscohada_community` : les deux autres modules suivent.
5. Pour les comptables : en mode développeur, cocher sur leur utilisateur le droit technique « Afficher toutes les fonctionnalités comptables » (Show Full Accounting Features), pour voir les écritures et le plan comptable.

Le menu Facturation (ou Comptabilité) > Analyse > Syscohada donne accès à : États et contrôles (AITE), Bilan actif, Bilan passif, Compte de résultat, Tableau des flux de trésorerie, Déclarations de TVA (Cameroun).

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

Résultat sur Odoo 18 Community, base vierge, 6 octobre 2026 : 104 tests (62 de base et 42 avancés), 0 échec, dont 3 échecs attendus qui documentent des défauts connus listés dans `ROADMAP.md`. Le test de volume se lance à part : `scripts/run_tests.sh <base> aite_syscohada_community aite_syscohada_volume` (1 test, 38 s). L'intégration continue `.github/workflows/tests.yml` exécute les deux à chaque push.

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
