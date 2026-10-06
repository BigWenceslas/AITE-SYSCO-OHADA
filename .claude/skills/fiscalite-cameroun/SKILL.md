---
name: fiscalite-cameroun
description: Règles fiscales camerounaises appliquées dans les modules AITE SYSCOHADA — TVA, formulaire I/TVA-IR ligne par ligne, retenues à la source, acomptes, IS, calendrier, comptes dédiés. À charger pour toute tâche sur les taxes, la déclaration mensuelle, la liquidation, la paie ou la DSF.
user-invocable: false
---

# Fiscalité camerounaise dans le projet

Sources : DGI (impots.cm : fiche TVA, fiche IS, formulaire I/TVA-IR, page DSF). Tout taux absent de cette page est à sourcer avant usage ; un taux non validé donne une taxe inactive « (taux à valider) ».

## Règles retenues

- TVA : 19,25 % (17,5 % + 10 % de centimes additionnels communaux, CAC). Exigible à la livraison pour les biens, à l'encaissement pour les services.
- Déclaration mensuelle I/TVA-IR : dépôt et paiement avant le 15 du mois suivant.
- Acompte d'impôt sur le résultat : 2 % du chiffre d'affaires du mois (régime du réel), 5 % (régime simplifié), plus CAC. Taux paramétrable par déclaration (`acompte_rate`, `cac_rate`).
- IS : 30 %, ou 25 % si le chiffre d'affaires ne dépasse pas 3 milliards, plus 10 % de CAC.
- DSF : solde de l'IS et dépôt au 15 mars (DGE), 15 avril (CIME), 15 mai (CDI).

## Comptes de TVA

| Compte | Usage |
| --- | --- |
| 4431 | TVA collectée sur ventes de biens |
| 4432 | TVA collectée sur services, après encaissement |
| 443800 | Compte d'attente de la TVA des services non encaissés (exclu de la liquidation) |
| 4451 | TVA récupérable sur immobilisations |
| 4452 | TVA récupérable sur achats |
| 4454 | TVA récupérable sur services |
| 4441 | TVA due (ligne L32) |
| 4449 | Crédit de TVA à reporter (L35, repris en L17) |
| 4445 | Remboursement de crédit demandé (L34) |

## Taxes créées par le socle

Clés pour `company._aite_tax_ref(clé)` : `tva_prestations_encaissement`, `tva_immobilisations`, `taxe_sejour`, `precompte_achats` (449210), `retenue_loyers` (447130), `retenue_honoraires` (447140), `retenue_tsr` (447120), `retenue_tva` (447160), `retenue_acompte_ca` (447170), `subie_acompte_ca` (449220), `subie_loyers` (449230), `subie_honoraires` (449240), `autoliquidation_services` (4454 à +100 %, 447161 à −100 %). Les retenues sont des taxes négatives, inactives tant que leurs taux ne sont pas validés, rangées dans le groupe « Retenues, précomptes et autres taxes ».

## Formulaire I/TVA-IR : source de chaque ligne

| Lignes | Contenu | Source |
| --- | --- | --- |
| L0 | TSR | crédits du mois sur 447120 |
| L1 à L8 | Droits d'accises | saisie (bases et taux, montants) |
| L10 à L35 | TVA | étiquettes de taxe du rapport `l10n_cm` ; L11, L24 à L27, L34 saisis ; L17 = L35 de la déclaration validée précédente |
| L36 à L39 | TVA à payer | L32, crédits sur 447160 (TVA retenue) et 447161 (TVA autoliquidée) |
| L40 à L44 | À reverser | crédits sur 447170, 447180, 447130, 447140 |
| L45 à L49 | À déduire | débits sur 449220, 449210, 449230, 449240 |
| L50 à L55 | Acomptes | L50 = base L15 × taux + CAC ; L51 saisie à 15 % + CAC ; L52 = L49 ; L53 = L55 précédente ; L54 et L55 calculées |
| L56 à L66 | IRCM, IRNC | saisie des bases, 15 % + CAC modifiables |
| L67 à L73 | Impôts sur salaires | crédits sur 447210 (IRPP) et 447215 (CAC), 447220 et 447230 (CFC), 447240 (FNE), 447250 (RAV), 447260 (TDL) |
| L74 à L80 | Plus-values, timbre d'aéroport | saisie |
| Total | Total à payer | L0 + L8 + L39 + L44 + L54 + L62 + L66 + L73 + L77 + L80 |

Calcul d'une étiquette de taxe : solde × (−1 si `tax_tag_invert`) × (−1 si `tax_negate`), sur les lignes du domaine `_get_tax_exigible_domain()`.

## Liquidation mensuelle

- TVA : chaque compte 443 et 445 soldé pour son montant du mois ; crédit 4441 (L32) ou débit 4449 (L35), débit 4445 (L34), crédit 4449 pour le crédit antérieur imputé. Écriture refusée si le grand livre ne concorde pas avec la déclaration ; régularisations L11 et L24 à L27 contre un compte choisi par le déclarant.
- Acompte : débit 449250, crédit 441100 pour L54.
- Les retenues restent sur leurs comptes 447 jusqu'au paiement.

## Points non validés

Taux des retenues ; base de l'acompte (L15, prestations comptées à l'encaissement) ; CAC sur l'acompte, l'IRCM et l'IRNC mais pas sur les retenues ; imputation des précomptes sur le total CAC compris ; comptes des taxes patronales (447 retenu, 442 possible). Voir `ROADMAP.md`.
