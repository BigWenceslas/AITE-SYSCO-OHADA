---
name: dsf-classeur
description: Structure du classeur DSF Normal de la DGI camerounaise (74 onglets), anomalies connues de ses formules et correspondances rubriques → cellules. À charger pour le lot 3 (notes annexes), le lot 4 (export Excel de la DSF) ou toute question sur la DSF.
user-invocable: false
---

# Classeur DSF Normal de la DGI

Version relevée : celle du 9 mars 2021, téléchargée sur impots.cm. Avant le lot 4, obtenir la version en vigueur et refaire le relevé si elle a changé.

## Structure

74 onglets protégés, sans plage nommée ni validation, en cinq parties :
- I (pages 1 à 3) : page de garde, fiches R1 (identification), R2 (activités), R3 (dirigeants).
- II (pages 4 à 49) : grille d'analyse, bilan, compte de résultat, TFT, notes 1 à 34 et compléments.
- III (pages 50 à 57) : notes 16B, 16C, 18 (dettes fiscales et sociales), 27A et C1 (paie, régularisation IRPP), 27B (effectifs), 35.
- IV (pages 58 et 59) : notes 21 (chiffre d'affaires) et 22 (achats).
- V (pages 60 à 66) : CF1 (passage au résultat fiscal), CF1 bis et ter (IS), CF1 quater (acomptes mensuels), CF2, bis et ter (TVA annuelle).

## Le relevé : `docs/dsf/Releve_classeur_DSF_Normal_2021.xlsx`

| Onglet du relevé | Contenu |
| --- | --- |
| Onglets | Les 74 onglets : page, partie, contenu, source dans Odoo, lot, nombre de cellules à saisir et calculées |
| États - Bilan, États - Résultat, États - TFT | Pour chaque rubrique : cellules N et N-1 (brut, amortissements, net), formules du modèle, anomalie |
| Liens états-notes | 104 cellules d'état qui lisent une note |
| Cellules des notes | 4 435 cellules : onglet, adresse, code, libellé de ligne, en-tête de colonne, nature (saisie ou calcul), formule |
| Anomalies du modèle | Les 18 anomalies, avec correction proposée et effet |

Chaque rubrique du référentiel (`aite.syscohada.rubrique.csv`) porte sa ligne dans le classeur et, s'il diffère, son code DGI.

## Anomalies connues du classeur 2021

- Bilan : amortissements (E13 à E16) lus dans les dotations ; net N-1 (G13 à G16) lu dans le brut d'ouverture ; dépréciation des stocks (E29) égale au total net ; DA, DB, DC (K23 à K25) lus dans la note 15A au lieu de 16A ; DM (K32) lu dans « autres dettes État » au lieu de la note 19 ; DZ (K40) sans DV.
- Compte de résultat : RB (E13) égal à la variation de tous les stocks ; XD N-1 (E34) = XC + RK ; RL (E36, E42) lu dans le compte de dotations financières ou HAO ; XF (E43) additionne au lieu de soustraire.
- Note 34 : CAFG incomplète. Taux d'IS affiché « 30 % ou 28 % », antérieur à la révision.

Conséquence : le classeur n'est jamais une référence de calcul. Les montants viennent du moteur ; un écart avec une formule du classeur se documente.

## Codes particuliers

- La rubrique BG est codée BC dans le classeur ; DV y est codée DY.
- CJ (résultat net) regroupe les comptes 13 et le résultat non affecté des classes 6, 7 et 8 calculé par Odoo ; le compte 999999 y est rattaché.

## Démarche du lot 4

Ouvrir le classeur officiel avec `openpyxl`, écrire des valeurs dans les seules cellules de nature « saisie », ne jamais toucher aux formules ni aux protections, contrôler les équilibres avant export, puis tester le téléversement sur l'espace d'un client pilote.
