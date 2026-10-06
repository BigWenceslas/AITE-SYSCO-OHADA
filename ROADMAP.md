# Feuille de route — SYSCOHADA révisé pour Odoo 18

État au 6 octobre 2026. Cible : Odoo 18 Community. Claude Code met ce fichier à jour à la fin de chaque tâche (cases, statuts, date).

## Où en est le projet

| Lot | Contenu | Développement | Recette (critère de sortie) |
| --- | --- | --- | --- |
| 0. Socle | Plan corrigé, sous-comptes, taxes camerounaises, référentiel des rubriques | Terminé | Atteinte sur base de test : tous les comptes rattachés, factures correctement taxées |
| 1. États financiers | Bilan, compte de résultat, TFT, contrôles | Terminé (Community et Enterprise) | À faire : la balance réelle d'un client donne les états validés par son expert-comptable |
| 2. Déclaration mensuelle | Formulaire I/TVA-IR complet, écritures de liquidation | Terminé (Community) | À faire : trois déclarations réelles reproduites sans écart |
| 3. Notes et tableaux fiscaux | Notes exigées en pièces jointes, passage au résultat fiscal | À faire | Pièces jointes au format demandé par la DGI |
| 4. DSF Excel | Remplissage du classeur DSF Normal de la DGI | À faire (relevé du classeur fait) | Classeur accepté au téléversement sur l'espace d'un client pilote |
| 5. Paie camerounaise | CNPS, IRPP, CFC, FNE, RAV, TDL ; L67 à L73 ; DIPE | À faire | Trois mois de bulletins reproduits au franc près |
| 6. API DSF | Dépôt depuis Odoo par l'API de la DGI | À faire | Dépôt réussi pour un client pilote |

**Prochaine action** : la recette des lots 1 et 2 avec des données réelles, avant d'ouvrir le lot 3. Elle demande un client pilote, ses données et son expert-comptable (voir « Données à obtenir »).

Ordre conseillé : recette 1 et 2 → lot 3 (notes exigées) → lot 4 → lot 6 ; le lot 5 peut avancer en parallèle dès maintenant.

## Lot 0 — Socle (terminé)

- [x] Libellés français corrigés (45), types de comptes alignés, sous-comptes (quotes-parts, 4811 lettrable, un 552 par opérateur de monnaie électronique)
- [x] Écarts de caisse vers 658800 et 758800
- [x] Taxes : TVA des prestations à l'encaissement (4432 via 4438), TVA des immobilisations (4451), TVA des services achetés (4454), taxe de séjour et précompte (inactifs)
- [x] Référentiel de 124 rubriques avec cellules DSF ; test de couverture du plan
- [ ] Faire valider les libellés et les sous-comptes par l'expert-comptable

## Lot 1 — États financiers (développement terminé)

- [x] Moteur de référence, 9 contrôles, assistant « États et contrôles (AITE) »
- [x] Modèles MIS Builder, identiques au moteur sur scénarios et grands livres aléatoires
- [x] Rapports `account.report` pour Enterprise (module facultatif)
- [x] États en un clic dans Community, exercices N et N-1, exports PDF et Excel
- [ ] Recette : comparer les états d'un client réel à ceux validés par son expert-comptable ; consigner chaque écart (formule, paramétrage ou saisie)
- [ ] Si Enterprise est utilisé : installer `aite_syscohada_reports`, lancer ses tests (étiquette `aite_syscohada_enterprise`), puis `tools/compare_with_engine.py` sur une base réelle
- [ ] Option : neutraliser les virements internes d'immobilisations dans le TFT MIS (aujourd'hui seul le moteur le fait)

## Lot 2 — Déclaration mensuelle I/TVA-IR (développement terminé, Community)

- [x] TVA, lignes L10 à L35, depuis la définition officielle du rapport `l10n_cm` ; TVA des prestations à l'encaissement
- [x] Lignes L0 à L80 hors TVA : TSR, accises, TVA retenue et autoliquidée, précomptes et retenues à reverser ou à déduire, acompte d'impôt, IRCM, IRNC, impôts sur salaires, plus-values, timbre d'aéroport, total à payer
- [x] Reports de crédit automatiques (L35 vers L17, L55 vers L53)
- [x] Écritures de liquidation : TVA (4441, 4449, 4445) et acompte (449250 contre 441100)
- [x] Impression PDF, date limite au 15 du mois suivant
- [x] Socle 18.0.1.1.0 : 22 comptes de retenues et d'avances d'impôt, 9 taxes de retenue (inactives), migration automatique
- [ ] Recette : reproduire trois déclarations déjà déposées par un client, ligne par ligne
- [ ] Activer les taxes de retenue une fois leurs taux validés
- [ ] Calculer L24 (TVA retenue par les clients) depuis un compte dédié au lieu d'une saisie
- [ ] Option : écriture de paiement groupée (débit des comptes de l'État, crédit de la banque)
- [x] Tests avancés : exercice d'un bar-hôtel, séquence de déclarations, retenues mixtes, multi-sociétés, cycle de vie de la liquidation, volume (450 factures)
- [ ] Défaut : L17 non recalculé si la déclaration du mois suivant existe avant la validation du mois précédent (`test_order_of_entry_vat_credit`)
- [ ] Défaut : extourne d'une facture avec retenue non déduite des lignes L40 à L43 (et L45 à L48) (`test_may_l43_excludes_reversed_invoice`)
- [ ] Défaut : liquidation refusée quand la société courante n'est pas celle de la déclaration (`_closing_balances`, `test_closing_entry_of_b_from_company_a_context`)
- [ ] Option : export au format attendu par le portail de télédéclaration, si la DGI en publie un

## Livraison et démonstration

- [x] Module `aite_syscohada_demo` : société « Bar-Hôtel Démo AITE », 21 mois d'opérations (bar, hôtel, achats, retenues, paie, immobilisations, emprunt, impôt, affectation, dividendes), 20 déclarations liquidées, payées et validées, septembre 2026 en brouillon ; 15 tests chiffrés à la main ; génération en une minute
- [x] Paquet de livraison `scripts/build_release.sh` : modules AITE, OCA figés avec leur licence, guide, lisez-moi `docs/installation.md` ; installation depuis le zip vérifiée sur une base vierge (104 tests sans échec, démonstration comprise)
- [x] Intégration continue : installation et tests de la démonstration, zip publié en artefact
- [ ] Option : choisir le journal de la liquidation (aujourd'hui le premier journal d'opérations diverses dans l'ordre d'affichage)

## Lot 3 — Notes annexes et tableaux fiscaux

Objectif : produire d'abord les notes exigées en pièces jointes de la DSF, puis le passage au résultat fiscal, puis les autres notes.

- [ ] Note 3C (immobilisations, amortissements)
- [ ] Note 7 (clients)
- [ ] Note 17 (fournisseurs d'exploitation)
- [ ] Note 24 (services extérieurs)
- [ ] Note 27A (charges de personnel)
- [ ] CF1 quater (acomptes mensuels) : alimentée par les déclarations du lot 2 (ligne L54)
- [ ] CF1 (passage du résultat comptable au résultat fiscal) : modèle de réintégrations et déductions, saisie et calcul, IS au taux applicable avec CAC
- [ ] Autres notes, en suivant le relevé du classeur (`docs/dsf/`)

Démarche : un référentiel des notes généré depuis le relevé, comme celui des rubriques ; calcul par le moteur ; saisies manuelles là où la comptabilité ne suffit pas. Prérequis : immobilisations suivies dans Odoo (OCA `account_asset_management`) pour la note 3C.

## Lot 4 — DSF Excel

- [x] Relevé du classeur DSF Normal 2021 : 74 onglets, 4 435 cellules dont 3 215 à saisir, 104 liens états → notes, 18 anomalies de formules
- [x] Cellule DSF portée par chaque rubrique du référentiel
- [ ] Obtenir la version en vigueur du classeur (DGI ou client) et refaire le relevé si elle a changé
- [ ] Remplir le classeur : valeurs dans les seules cellules de saisie, formules et protections intactes
- [ ] Contrôles avant export : équilibres, cohérence états et notes, cellules obligatoires
- [ ] Test de téléversement sur l'espace d'un client pilote
- [ ] Prévoir le système minimal de trésorerie si un client y est soumis

## Lot 5 — Paie camerounaise

- [ ] Choisir la base : OCA `payroll` et `payroll_account` (Community)
- [ ] Règles et barèmes sourcés dans les textes en vigueur : CNPS, IRPP et CAC, CFC (parts salariale et patronale), FNE, redevance audiovisuelle, taxe de développement local
- [ ] Comptabilisation sur les comptes 447210 à 447260, pour alimenter les lignes L67 à L73 du lot 2
- [ ] Livre de paie et DIPE
- [ ] Recette : trois mois de bulletins réels reproduits au franc près

## Lot 6 — API DSF

- [ ] Obtenir l'accès à l'espace de télédéclaration d'un client : la DGI n'y publie les spécifications de l'API qu'aux contribuables
- [ ] Connexion, création de la déclaration, envoi des pages, soumission, accusé de réception
- [ ] Recette : dépôt réussi pour un client pilote

## Données à obtenir

| Pour | Quoi | Auprès de |
| --- | --- | --- |
| Recette lot 1 | Balance et états validés d'un exercice clos | Client pilote et son expert-comptable |
| Recette lot 2 | Trois déclarations I/TVA-IR déposées et les écritures des mêmes mois | Client pilote |
| Lot 4 | Classeur DSF Normal en vigueur | DGI ou client |
| Lot 5 | Trois mois de bulletins et de livres de paie | Client pilote |
| Lot 6 | Accès à l'espace de télédéclaration | Client pilote |

## Questions ouvertes pour l'expert-comptable

Chacune modifie une formule ou un paramétrage ; les trancher avant la recette.

- [ ] Bascules : au niveau du compte ou client par client (clients créditeurs vers DI, fournisseurs débiteurs vers BH) ?
- [ ] Quotes-parts des comptes 2818, 2918, 2919, 2939 et 2949 : clé d'éclatement en sous-comptes
- [ ] TFT : formule exacte de la CAFG, sort des dépréciations à court terme (659, 759) et des cessions courantes (654, 754)
- [ ] Compte de résultat : 659 en RJ et 759 en TH, donc avant la valeur ajoutée ?
- [ ] Taxes patronales sur salaires (CFC patronal, FNE) : compte 442 ou 447 (le lot 2 utilise 447230 et 447240)
- [ ] TVA des prestations à l'encaissement : compte d'attente (4438 aujourd'hui) avant le transfert vers 4432
- [ ] Précompte subi sur les achats : compte d'imputation (449210 aujourd'hui) et régime de déduction
- [ ] Taxe de séjour : compte, base de calcul et exigibilité
- [ ] Factures conformes issues du système de facturation de l'administration : incidence sur les factures émises et reçues dans Odoo
- [ ] Format de DSF de chaque client : système normal ou système minimal de trésorerie
- [ ] Taux des retenues : loyers, honoraires, TSR, TVA retenue, acompte retenu à la source
- [ ] Acompte d'impôt : base (ligne L15, où les prestations ne comptent qu'une fois encaissées), centimes additionnels, imputation des précomptes sur le total
- [ ] CAC sur les précomptes et retenues : à ajouter ou non (aujourd'hui non)

## Risques

- La loi de finances change chaque année des taux, des lignes du formulaire ou le classeur DSF : vérifier les sources DGI à chaque début d'exercice.
- Le rapport de TVA `l10n_cm` d'Odoo peut évoluer : la déclaration le lit dynamiquement, mais les tests doivent repasser après chaque mise à jour d'Odoo.
- Modules OCA en branche 18.0 : figer les versions en production.
- L'API DSF n'est documentée que dans l'espace d'un contribuable : le lot 6 dépend d'un client.

## Sources

- Odoo 18 : `addons/l10n_cm` et `addons/l10n_syscohada` (plan, taxes, rapport de TVA, menu Syscohada)
- OCA 18.0 : mis-builder, server-ux, reporting-engine ; pour la suite : account-financial-reporting, account-financial-tools, account-reconcile, bank-statement-import, account-closing, payroll
- DGI : https://www.impots.cm/fr/declarations-statistiques-et-fiscalesdsf (DSF et classeurs) ; https://www.impots.cm/sites/default/files/documents/ITVA-IR.pdf (formulaire I/TVA-IR) ; https://impots.cm/sites/default/files/documents/FICHE%20TVA.pdf (TVA) ; https://impots.cm/sites/default/files/documents/ok%20FT%20IS%20ok.pdf (IS)
