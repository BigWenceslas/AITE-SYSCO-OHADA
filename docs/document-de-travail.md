# Odoo 18 et SYSCOHADA révisé : table de correspondance et audit Enterprise / Community

> Export du document de travail (Claude Docs), créé le 25 septembre 2026 et exporté le 6 octobre 2026.
> Instantané en lecture seule : en cas de divergence, `ROADMAP.md`, `CLAUDE.md` et le code font foi.
> Formules exactes des rubriques : `addons/aite_syscohada_base/tools/gen_rubriques.py` et le CSV qu'il génère.

## Synthèse

Odoo 18 livre le socle SYSCOHADA (plan de comptes révisé, TVA à 19,25 %, trame TVA de la déclaration mensuelle), mais aucune édition ne produit la DSF camerounaise, le tableau des flux de trésorerie SYSCOHADA ni les notes annexes. L'écart se comble avec un socle commun de correspondances comptes → rubriques, rendu par le moteur de rapports en Enterprise et par MIS Builder en Community, puis un export DSF au format DGI.

| Besoin | Community 18 | Enterprise 18 | Écart à combler (les deux éditions) |
| --- | --- | --- | --- |
| Plan de comptes SYSCOHADA révisé | Natif (l10n\_syscohada + l10n\_cm), 1 134 comptes | Identique | Libellés français et types de comptes à corriger |
| Taxes camerounaises | 6 taxes : ventes 19,25 %, achats biens et services 19,25 %, export, exonéré | Identique | TVA des services à l'encaissement, TVA sur immobilisations, précomptes, taxe de séjour, accises |
| Déclaration mensuelle DGI | Lignes L10 à L35 définies, sans écran pour les afficher | Rapport TVA affiché et clôture de TVA assistée | Sections TSR, accises, acomptes, précomptes, IRCM, impôts sur salaires (L0 à L80) |
| Bilan et compte de résultat SYSCOHADA | Absents (à construire sous MIS Builder) | Menu « Syscohada » prévu dans les rapports, contenu à vérifier | Bascules selon le sens du solde, colonnes brut / amortissements / net, exercice N-1 |
| Tableau des flux de trésorerie | Absent | Tableau de flux générique, pas au format SYSCOHADA | À construire |
| Notes annexes et tableaux fiscaux | Absents | Absents | À construire, en commençant par les pièces exigées par la DGI |
| DSF | Absente | Absente | Remplissage du classeur Excel DGI, puis dépôt par l'API de la DGI |
| Rapprochement, immobilisations, clôture | Modules OCA disponibles en 18.0 | Natifs | Rien de bloquant |
| Paie camerounaise | Moteur OCA générique | Application Paie, règles camerounaises non vérifiées | CNPS, IRPP, CFC, FNE, redevance audiovisuelle, TDL |

Recommandation : un module commun porte les rubriques et les contrôles, deux couches de rendu s'adaptent à l'édition, et un module DSF indépendant de l'édition lit les montants par rubrique. La DGI accepte trois modes de dépôt de la DSF : saisie en ligne, téléversement du classeur Excel au format DGI, ou API pour les systèmes comptables web ([guide DGI de télédéclaration](https://www.impots.cm/sites/default/files/documents/GUIDE%20TELEDECLARATION%20DSF%202023.pdf)). Odoo étant web, l'API est la cible finale ; le classeur Excel est la première étape, plus rapide à valider.

## Audit détaillé d'Odoo 18

Constat établi dans le code source d'Odoo 18 (branche 18.0) et dans les dépôts OCA, le 25 septembre 2026 : la base est saine, mais le paramétrage camerounais livré reste minimal.

### Plan de comptes

Le modèle « SYSCOHADA - Revised » de [l10n\_syscohada](https://github.com/odoo/odoo/tree/18.0/addons/l10n_syscohada) compte 1 134 comptes, avec des codes à 6 chiffres. [l10n\_cm](https://github.com/odoo/odoo/tree/18.0/addons/l10n_cm) le reprend et fixe les préfixes : banques 521, caisses 571, virements internes 585, client du point de vente 4113, écarts de change 776 et 676, escomptes 6019 et 7019.

- Libellés français issus d'une traduction automatique : 121 « Créancier reporté », 131 « Revenu net : profit », 2441 « Fournitures de bureau », 4091 « Avances et acomptes versés par les fournisseurs », 4281 « Dettes de vacances à payer », 6613 « Vacances payées », 476 « Dépenses prépayées », 477 « Revenu différé » ; 109 et 465 sont restés en anglais.
- Types de comptes contraires au sens du solde : 4451, 4452, 4454 et 4455 (TVA récupérable) sont typés passif courant ; 162 (emprunts) est typé passif courant au lieu de non courant. Sans effet sur un état calculé par rubriques, mais faux dans les rapports génériques d'Odoo.
- Aucun compte de résultat non affecté dans le modèle : Odoo calcule à part le résultat de l'exercice en cours. La rubrique CJ doit additionner les comptes 13 et ce résultat calculé.

### Taxes et déclaration mensuelle

| Taxe livrée (l10n\_cm) | Compte | Ligne de la déclaration DGI |
| --- | --- | --- |
| TVA 19,25 % sur ventes | 4431 | L10 |
| TVA 19,25 % sur achats de biens | 4452 | L18 |
| TVA 19,25 % sur services achetés | 4452 (et non 4454) | L19 |
| 0 % export | — | L13 |
| 0 % exonéré (ventes) | — | L14 |
| 0 % import, 0 % exonéré (achats) | — | Aucune |

Manquent : la TVA facturée sur prestations (4432) avec exigibilité à l'encaissement, la TVA récupérable sur immobilisations (4451) et sur services (4454), la TVA retenue à la source, les précomptes, la taxe de séjour et les droits d'accises.

Le module définit un rapport de TVA calqué sur les lignes L10 à L35 du formulaire I/TVA-IR. Enterprise l'affiche et prépare l'écriture de clôture de TVA ; en Community, la définition existe mais aucun écran ne l'exploite. Le formulaire complet va de L0 à L80 (voir la section fiscalité).

### États financiers

- Community : pas de bilan, compte de résultat, balance ni grand livre dans le standard. Les modules OCA account\_financial\_report (balance, grand livre, balance âgée) et mis\_builder (états sur mesure) comblent le manque.
- Enterprise : moteur de rapports avec bilan et compte de résultat génériques, exports PDF et XLSX, comparaison N-1. Le module OHADA crée un menu « Syscohada » sous Rapports, destiné aux états OHADA d'Enterprise : leur contenu exact (lignes, comptes, bascules, présence du TFT) est à vérifier sur une instance 18 Enterprise de test.

### Autres briques

| Brique | Community 18 (OCA, branche 18.0) | Enterprise 18 |
| --- | --- | --- |
| Rapprochement bancaire | [account\_reconcile\_oca](https://github.com/OCA/account-reconcile/tree/18.0) 18.0.1.1.14 | Natif |
| Import des relevés | [account\_statement\_import\_file et \_sheet\_file](https://github.com/OCA/bank-statement-import/tree/18.0) | Natif |
| Immobilisations | [account\_asset\_management](https://github.com/OCA/account-financial-tools/tree/18.0) 18.0.1.1.11 | Natif |
| États sur mesure | [mis\_builder](https://github.com/OCA/mis-builder/tree/18.0) 18.0.1.10.0, avec date\_range | Moteur account.report |
| Balance, grand livre | [account\_financial\_report](https://github.com/OCA/account-financial-reporting/tree/18.0) 18.0.1.4.26 | Natif |
| Régularisations et clôture | [account\_cutoff\_base, account\_fiscal\_year\_closing](https://github.com/OCA/account-closing/tree/18.0) | Natif |
| Modèles d'écritures | account\_move\_template 18.0.1.0.0 | Natif |
| Paie | [payroll et payroll\_account](https://github.com/OCA/payroll/tree/18.0) (moteur générique) | Application Paie ; règles camerounaises à construire ou vérifier |
| Exports Excel | report\_xlsx 18.0.1.1.3 | Natif sur tous les rapports |

## Architecture cible

Une seule vérité, plusieurs sorties : les rubriques SYSCOHADA sont décrites une fois, en données, puis rendues par l'édition disponible et exportées vers la DSF.

| Module proposé | Édition | Contenu |
| --- | --- | --- |
| aite\_syscohada\_base | Les deux | Libellés et types corrigés, sous-comptes utiles, taxes camerounaises complètes, positions fiscales, référentiel des rubriques et des correspondances, contrôles |
| aite\_syscohada\_reports | Enterprise | Bilan, compte de résultat, TFT et déclaration I/TVA-IR complète, en account.report |
| aite\_syscohada\_mis | Community | Mêmes états en modèles MIS Builder, générés depuis le référentiel |
| aite\_dsf\_cm | Les deux | Montants par rubrique, fiches de renseignements, notes et tableaux fiscaux, export du classeur DGI, puis dépôt par API |
| aite\_payroll\_cm | Les deux, règles propres à chaque moteur | CNPS, IRPP, CFC, FNE, redevance audiovisuelle, TDL ; lignes L67 à L73 ; DIPE |

### Principes de conception

1. **Correspondances en données.** Chaque rubrique (code, libellé, état, formule) et chaque rattachement (préfixe de compte, exclusions, colonne brut ou amortissement, condition de solde) vivent dans une table. Les deux rendus en sont générés : aucune correspondance n'est codée deux fois.
2. **Enterprise.** Les formules du moteur account.report acceptent des préfixes, des exclusions et un filtre sur le sens du solde de chaque compte. Les tableaux SYSCOHADA s'y traduisent presque mot pour mot : « 24 sauf 245 et 2495 » devient `24\(245,2495)`, « 52 si débiteur » devient `52D`.
3. **Community.** MIS Builder sait ne retenir que les soldes débiteurs (pbal) ou créditeurs (nbal), compte par compte : les bascules s'y traduisent sans extension.
4. **Bascules.** Elles se calculent compte par compte. Une bascule client par client (clients créditeurs vers DI) demande un calcul spécifique dans les deux éditions : à trancher avec l'expert-comptable.
5. **Colonnes.** Bilan : exercice N en brut, amortissements et dépréciations, net, puis net N-1. Compte de résultat et TFT : N et N-1.
6. **Quotes-parts.** Les comptes partagés entre deux rubriques (2818, 2918, 2919, 2939, 2949) sont éclatés en sous-comptes, un par rubrique, pour supprimer toute ventilation manuelle.
7. **DSF.** Une table rubrique → onglet et cellule du classeur DGI alimente l'export Excel. L'API réutilise la même table page par page ; la DGI documente huit appels, de la connexion à la soumission ([guide DGI](https://www.impots.cm/sites/default/files/documents/GUIDE%20TELEDECLARATION%20DSF%202023.pdf)).

## Correspondance du bilan actif

Chaque rubrique d'actif vaut brut moins amortissements et dépréciations ; les lignes « soldes débiteurs » ne retiennent que les comptes dont le solde est débiteur. « qp » signale une quote-part, à éclater en sous-comptes dans Odoo.

| Réf | Rubrique | Brut | Amortissements et dépréciations | Condition |
| --- | --- | --- | --- | --- |
| AD | Immobilisations incorporelles | AE + AF + AG + AH |  | Sous-total |
| AE | Frais de développement et de prospection | 211, 2181, 2191 | 2811, 2818 qp, 2911, 2918 qp, 2919 qp |  |
| AF | Brevets, licences, logiciels et droits similaires | 212, 213, 214, 2193 | 2812, 2813, 2814, 2912, 2913, 2914, 2919 qp |  |
| AG | Fonds commercial et droit au bail | 215, 216 | 2815, 2816, 2915, 2916 |  |
| AH | Autres immobilisations incorporelles | 217, 218 sauf 2181, 2198 | 2817, 2818 qp, 2917, 2918 qp, 2919 qp |  |
| AI | Immobilisations corporelles | AJ + AK + AL + AM + AN |  | Sous-total |
| AJ | Terrains | 22 | 282, 292 |  |
| AK | Bâtiments | 231, 232, 233, 237, 2391 | 2831, 2832, 2833, 2837, 2931, 2932, 2933, 2937, 2939 qp |  |
| AL | Aménagements, agencements et installations | 234, 235, 238, 2392, 2393 | 2834, 2835, 2838, 2934, 2935, 2938, 2939 qp |  |
| AM | Matériel, mobilier et actifs biologiques | 24 sauf 245 et 2495 | 284 sauf 2845 ; 294 sauf 2945 et 2949 ; 2949 qp |  |
| AN | Matériel de transport | 245, 2495 | 2845, 2945, 2949 qp |  |
| AP | Avances et acomptes versés sur immobilisations | 251, 252 | 2951, 2952 |  |
| AQ | Immobilisations financières | AR + AS |  | Sous-total |
| AR | Titres de participation | 26 | 296 |  |
| AS | Autres immobilisations financières | 27 | 297 |  |
| AZ | Total actif immobilisé | AD + AI + AP + AQ |  | Total |
| BA | Actif circulant HAO | 485, 488 | 498 |  |
| BB | Stocks et encours | 31 à 38 | 39 |  |
| BG | Créances et emplois assimilés (codé BC dans le classeur DGI) | BH + BI + BJ |  | Sous-total |
| BH | Fournisseurs, avances versées | 409 | 490 |  |
| BI | Clients | 411, 412, 413, 414, 415, 416, 418 | 491 |  |
| BJ | Autres créances | 185, 42, 43, 44, 45, 46, 47 sauf 478 | 492 à 497 | Soldes débiteurs |
| BK | Total actif circulant | BA + BB + BG |  | Total |
| BQ | Titres de placement | 50 | 590 |  |
| BR | Valeurs à encaisser | 51 | 591 |  |
| BS | Banques, chèques postaux, caisse et assimilés | 52, 53, 54, 55, 57, 581, 582 | 592, 593, 594 | Soldes débiteurs |
| BT | Total trésorerie-actif | BQ + BR + BS |  | Total |
| BU | Écart de conversion-actif | 478 |  |  |
| BZ | Total général | AZ + BK + BT + BU |  | Doit égaler DZ |

Traduction Enterprise de deux lignes : BJ brut = `185D + 42D + 43D + 44D + 45D + 46D + 47\(478,479)D` ; BS brut = `52D + 53D + 54D + 55D + 57D + 581D + 582D`. Dans Odoo, les comptes 52 et 57 naissent des journaux (préfixes 521 et 571) ; le compte mobile money 552 doit être rattaché à un journal de type banque.

Cette table suit le tableau de correspondance postes/comptes du SYSCOHADA révisé. Le texte officiel n'a pas pu être consulté en ligne pour cette version : chaque ligne est à confronter à l'Acte uniforme et au classeur DSF Normal de la DGI avant développement.

## Correspondance du bilan passif

Le passif se lit en net ; trois rubriques récupèrent les soldes créditeurs des comptes qui basculent (DK, DM, DR), et CJ doit intégrer le résultat qu'Odoo calcule à part.

| Réf | Rubrique | Comptes | Condition |
| --- | --- | --- | --- |
| CA | Capital | 101, 102, 103, 104 |  |
| CB | Apporteurs, capital non appelé | 109 | En déduction |
| CD | Primes liées au capital social | 105 |  |
| CE | Écarts de réévaluation | 106 |  |
| CF | Réserves indisponibles | 111, 112, 113 |  |
| CG | Réserves libres | 118 |  |
| CH | Report à nouveau | 121, 129 | Signé (+ ou −) |
| CJ | Résultat net de l'exercice | 13 + résultat de l'exercice non encore affecté | Signé ; voir note |
| CL | Subventions d'investissement | 14 |  |
| CM | Provisions réglementées | 15 |  |
| CP | Total capitaux propres et ressources assimilées | CA à CM | Total |
| DA | Emprunts et dettes financières diverses | 16, 181, 182, 183, 184 |  |
| DB | Dettes de location-acquisition | 17 |  |
| DC | Provisions pour risques et charges | 19 |  |
| DD | Total dettes financières et ressources assimilées | DA + DB + DC | Total |
| DF | Total ressources stables | CP + DD | Total |
| DH | Dettes circulantes HAO | 481, 482, 484, 4998 |  |
| DI | Clients, avances reçues | 419 |  |
| DJ | Fournisseurs d'exploitation | 40 sauf 409 |  |
| DK | Dettes fiscales et sociales | 42, 43, 44 | Soldes créditeurs |
| DM | Autres dettes | 185, 45, 46, 47 sauf 479 | Soldes créditeurs |
| DN | Provisions pour risques à court terme | 499 sauf 4998, 599 |  |
| DP | Total passif circulant | DH + DI + DJ + DK + DM + DN | Total |
| DQ | Banques, crédits d'escompte | 564, 565 |  |
| DR | Banques, établissements financiers et crédits de trésorerie | 52, 53, 561, 566 | Soldes créditeurs (découverts) |
| DT | Total trésorerie-passif | DQ + DR | Total |
| DV | Écart de conversion-passif (codé DY dans le classeur DGI) | 479 |  |
| DZ | Total général | DF + DP + DT + DV | Doit égaler BZ |

Points propres à Odoo :

- **CJ.** Odoo ne vire pas le résultat en classe 13 en cours d'exercice : il le calcule à partir des classes 6 à 8. CJ = soldes des comptes 13 + résultat de l'exercice non affecté (agrégat dédié en Enterprise, somme des classes 6 à 8 dans MIS).
- **DH et le compte 481.** Le compte fournisseur d'une facture vient de la fiche du partenaire (4011 par défaut). Un achat d'immobilisation tomberait donc en DJ. Il faut un compte fournisseur d'investissement sur les partenaires concernés, ou un reclassement à la clôture. Dans le modèle livré, 4811 et 4812 ne sont ni de type fournisseur ni lettrables : à corriger pour cet usage.
- **DK.** Les comptes 44 débiteurs (crédit de TVA 4449, acomptes d'impôt 441 excédentaires) partent en BJ ; les créditeurs restent ici.
- **DR.** Un journal bancaire à découvert bascule ici : même compte que BS, sens opposé (`52C` contre `52D`).

## Correspondance du compte de résultat

Le compte de résultat SYSCOHADA enchaîne neuf soldes, de la marge commerciale (XA) au résultat net (XI) ; chaque formule additionne des montants signés, produits positifs et charges négatives.

| Réf | Rubrique | Comptes ou formule | Signe |
| --- | --- | --- | --- |
| TA | Ventes de marchandises | 701 | + |
| RA | Achats de marchandises | 601 | − |
| RB | Variation de stocks de marchandises | 6031 | − ou + |
| **XA** | **Marge commerciale** | TA + RA + RB |  |
| TB | Ventes de produits fabriqués | 702, 703, 704 | + |
| TC | Travaux, services vendus | 705, 706 | + |
| TD | Produits accessoires | 707 | + |
| **XB** | **Chiffre d'affaires** | TA + TB + TC + TD |  |
| TE | Production stockée ou déstockage | 73 | + ou − |
| TF | Production immobilisée | 72 | + |
| TG | Subventions d'exploitation | 71 | + |
| TH | Autres produits | 75 | + |
| TI | Transferts de charges d'exploitation | 781 | + |
| RC | Achats de matières premières et fournitures liées | 602 | − |
| RD | Variation de stocks de matières premières et fournitures | 6032 | − ou + |
| RE | Autres achats | 604, 605, 608 | − |
| RF | Variation de stocks d'autres approvisionnements | 6033 | − ou + |
| RG | Transports | 61 | − |
| RH | Services extérieurs | 62, 63 | − |
| RI | Impôts et taxes | 64 | − |
| RJ | Autres charges | 65 | − |
| **XC** | **Valeur ajoutée** | XB + RA + RB + (TE à RJ) |  |
| RK | Charges de personnel | 66 | − |
| **XD** | **Excédent brut d'exploitation** | XC + RK |  |
| TJ | Reprises d'amortissements, provisions et dépréciations | 791, 798, 799 | + |
| RL | Dotations aux amortissements, provisions et dépréciations | 681, 691 | − |
| **XE** | **Résultat d'exploitation** | XD + TJ + RL |  |
| TK | Revenus financiers et assimilés | 77 | + |
| TL | Reprises de provisions et dépréciations financières | 797 | + |
| TM | Transferts de charges financières | 787 | + |
| RM | Frais financiers et charges assimilées | 67 | − |
| RN | Dotations aux provisions et dépréciations financières | 697 | − |
| **XF** | **Résultat financier** | TK + TL + TM + RM + RN |  |
| **XG** | **Résultat des activités ordinaires** | XE + XF |  |
| TN | Produits des cessions d'immobilisations | 82 | + |
| TO | Autres produits HAO | 84, 86, 88 | + |
| RO | Valeurs comptables des cessions d'immobilisations | 81 | − |
| RP | Autres charges HAO | 83, 85 | − |
| **XH** | **Résultat hors activités ordinaires** | TN + TO + RO + RP |  |
| RQ | Participation des travailleurs | 87 | − |
| RS | Impôts sur le résultat | 89 | − |
| **XI** | **Résultat net** | XG + XH + RQ + RS | Doit égaler CJ |

Points propres à Odoo :

- Les produits ont un solde créditeur, donc négatif pour Odoo : les formules inversent le signe (`-701` en Enterprise, `-balp[701%]` dans MIS).
- Les ristournes obtenues (6019) et accordées (7019) restent dans leur compte : RA et TA se lisent nets de remises.
- Les dépréciations à court terme d'exploitation (659) tombent en RJ et leurs reprises (759) en TH, donc avant la valeur ajoutée : point à confirmer avec l'expert-comptable.
- Les écarts de change de l'installation (676 et 776) alimentent RM et TK sans paramétrage supplémentaire.

## Tableau des flux de trésorerie

Le TFT explique la variation de la trésorerie nette (BT − DT) à partir de la capacité d'autofinancement ; il se calcule avec les bilans N et N-1 plus quelques mouvements de comptes, lisibles dans les deux éditions.

| Réf | Rubrique | Source des montants |
| --- | --- | --- |
| ZA | Trésorerie nette au 1er janvier | BT − DT du bilan N-1 |
| FA | Capacité d'autofinancement globale (CAFG) | Formule ci-dessous |
| FB | Variation de l'actif circulant HAO | − (BA N − BA N-1) |
| FC | Variation des stocks | − (BB N − BB N-1) |
| FD | Variation des créances | − variation de BH + BI + BJ |
| FE | Variation du passif circulant | + variation de DI à DN ; la part HAO liée aux investissements passe en FF à FH |
| **ZB** | **Flux des activités opérationnelles** | FA à FE |
| FF | Acquisitions d'immobilisations incorporelles | Débits des comptes 21, corrigés de la variation des fournisseurs d'investissement (481, 482) |
| FG | Acquisitions d'immobilisations corporelles | Débits des comptes 22 à 25, même correction |
| FH | Acquisitions d'immobilisations financières | Débits des comptes 26 et 27 |
| FI | Cessions d'immobilisations incorporelles et corporelles | Prix de cession (82, 754), corrigés de la variation de 485 |
| FJ | Cessions d'immobilisations financières | Prix de cession des titres et remboursements des prêts (crédits 26 et 27) |
| **ZC** | **Flux des activités d'investissement** | FF à FJ |
| FK | Augmentations de capital par apports nouveaux | Crédits de 101 à 104 encaissés |
| FL | Subventions d'investissement reçues | Crédits de 14 encaissés |
| FM | Prélèvements sur le capital | Débits de 104 |
| FN | Dividendes versés | Paiements imputés au 465 |
| **ZD** | **Flux des capitaux propres** | FK à FN |
| FO | Emprunts | Crédits de 16 encaissés |
| FP | Autres dettes financières | Crédits de 17 et 18 encaissés |
| FQ | Remboursements des emprunts et autres dettes financières | Débits de 16, 17, 18 |
| **ZE** | **Flux des capitaux étrangers** | FO + FP + FQ |
| **ZF** | **Flux des activités de financement** | ZD + ZE |
| **ZG** | **Variation de la trésorerie nette** | ZB + ZC + ZF |
| **ZH** | **Trésorerie nette au 31 décembre** | ZA + ZG ; contrôle : BT − DT du bilan N |

La DGI définit la CAFG dans la note 34 du classeur DSF, par addition à partir de l'EBE :

```latex
\text{CAFG} = \text{EBE} + \text{VNC}_{654} - \text{Prix}_{754} + \text{Revenus financiers} + \text{Gains de change} + \text{Transferts de charges financières} + \text{Produits HAO} + \text{Transferts de charges HAO} - \text{Frais financiers} - \text{Pertes de change} - \text{Participation} - \text{Impôts sur le résultat}
```

Le calcul par le résultat net (XI + dotations − reprises + valeurs cédées − prix de cession) doit donner le même montant. La note 34 ne retranche pas les charges HAO et sa propre formule oublie un terme (voir le relevé du classeur) : la définition retenue est à valider. Le tableau de flux générique d'Enterprise ne suit pas cette présentation : le TFT est à construire dans les deux éditions.

## Fiscalité camerounaise : déclaration mensuelle et DSF

Deux productions fiscales structurent le projet : la déclaration mensuelle I/TVA-IR, avant le 15 du mois suivant, et la DSF annuelle, au plus tard le 15 mars, le 15 avril ou le 15 mai selon le centre des impôts de rattachement.

### Déclaration mensuelle I/TVA-IR

Odoo 18 ne couvre que les sections TVA du [formulaire DGI](https://www.impots.cm/sites/default/files/documents/ITVA-IR.pdf) ; tout le reste est à construire, en données de taxes ou depuis la paie.

| Section | Lignes | Alimentation prévue | Couverture Odoo 18 |
| --- | --- | --- | --- |
| Taxe spéciale sur le revenu (rémunérations versées à l'étranger) | L0 | Taxe de retenue sur factures de fournisseurs étrangers | Absente |
| Droits d'accises | L1 à L9 | Taxe d'accise par produit, pour les assujettis (producteurs, importateurs) | Absente |
| Chiffre d'affaires | L10 à L15 | Grilles des taxes de vente | Définie, sauf L11 (accises) |
| TVA déductible | L16 à L23 | Grilles des taxes d'achat, report du crédit précédent | Définie, sans prorata |
| Régularisations | L24 à L27 | Écritures de régularisation taguées | Définie |
| TVA à payer ou crédit | L28 à L35 | Calcul | Définie |
| Total TVA à payer | L36 à L39 | TVA retenue à la source par les entreprises habilitées | Absente |
| Acomptes et précomptes à reverser | L40 à L44 | Précomptes retenus sur fournisseurs et sur loyers | Absente |
| Acomptes et précomptes à déduire | L45 à L49 | Précomptes subis sur les factures d'achat | Absente |
| Acomptes d'impôt sur le revenu | L50 à L55 | Chiffre d'affaires du mois × taux, plus CAC, moins déductions | Absente |
| Revenus de capitaux mobiliers | L56 à L62 | Dividendes, intérêts, rémunérations de dirigeants versés | Absente |
| Revenus non commerciaux retenus | L63 à L66 | Conseils, commissions, artistes | Absente |
| Impôts retenus sur salaires | L67 à L73 | Paie : IRPP, CFC salarial et patronal, FNE, redevance audiovisuelle, TDL | Absente |
| Plus-values | L74 à L77 | Cessions | Absente |
| Droit de timbre d'aéroport | L78 à L80 | Sans objet pour la plupart des clients | Absente |

Repères à paramétrer, jamais à coder en dur :

- **TVA** : 19,25 % ; exigible à la livraison pour les biens, à l'encaissement du prix pour les services. La déduction suppose des factures conformes issues du système de facturation de l'administration et aucun paiement en espèces au-delà de 100 000 FCFA ; le crédit se reporte sans limite de durée ([fiche TVA de la DGI](https://impots.cm/sites/default/files/documents/FICHE%20TVA.pdf)).
- **Impôt sur les sociétés** : 30 %, ou 25 % si le chiffre d'affaires ne dépasse pas 3 milliards, majorés de 10 % de CAC. Acomptes de 2 % du chiffre d'affaires mensuel au réel, majorés des CAC, avant le 15 du mois suivant ; solde = impôt calculé moins acomptes ([fiche IS de la DGI](https://impots.cm/sites/default/files/documents/ok%20FT%20IS%20ok.pdf)).

### DSF

Depuis la loi de finances 2019, la DSF suit le SYSCOHADA révisé : format du système normal ou du système minimal de trésorerie, plus des formats banque et assurance. Elle réunit une page de garde et des fiches de renseignements, les états financiers avec leurs notes annexes, et des tableaux fiscaux ; le dépôt est exclusivement électronique ([page DSF de la DGI](https://www.impots.cm/fr/declarations-statistiques-et-fiscalesdsf)).

- **Délais** : 15 mars pour la Direction des grandes entreprises ; 15 avril pour les CIME, CSI-EPA et CSIPLI ; 15 mai pour les centres divisionnaires.
- **Classeur officiel** : la DGI publie un classeur Excel verrouillé par format ([DSF Normal](https://www.impots.cm/sites/default/files/uploads/DSF_Normal_DGIFORMAT_VERROUILLEVF.xlsx)). C'est la cible de l'export ; son relevé détaillé suit dans la section suivante.
- **Modes de dépôt** : saisie en ligne (déconseillée), téléversement du classeur, ou API pour les systèmes web ([guide DGI](https://www.impots.cm/sites/default/files/documents/GUIDE%20TELEDECLARATION%20DSF%202023.pdf)). Les spécifications JSON de l'API ne sont visibles que depuis l'espace de télédéclaration d'un contribuable, après activation de l'API.

Pièces jointes obligatoires de la DSF Normal selon le guide DGI, et leur source dans Odoo :

| Pièce | Référence | Source Odoo |
| --- | --- | --- |
| Attestation de visa de l'expert-comptable | Fiche R1 | Document externe |
| Balance auxiliaire clients, au format Excel | Note 7 | Grand livre des partenaires |
| Balance auxiliaire fournisseurs et achats annuels par fournisseur | Note 17 | Grand livre des partenaires, analyse des achats |
| Sommes versées aux tiers | Note 24 | Paiements par nature de charge et par bénéficiaire |
| Tableau des amortissements | Note 3C | Registre des immobilisations |
| Document d'information sur le personnel employé (DIPE) | Note 27A | Paie |
| Précomptes et acomptes retenus, à reverser et à déduire | CF1 quater | Comptes de précomptes et déclarations mensuelles |
| Dépenses fiscales et prix de transfert | Fiche R2 | Saisie annuelle ; codes d'activité NACAM de l'INS |
| Attestation de dématérialisation des titres | Fiche R3 | Document externe |

## Relevé du classeur DSF Normal

Le classeur fourni (version verrouillée du 9 mars 2021) compte 74 onglets protégés, sans plage nommée ni liste de validation : l'export écrira cellule par cellule. Une dizaine de ses formules sont fausses et plusieurs totaux n'en ont pas : Odoo doit écrire toutes les valeurs, totaux compris.

### Structure

| Partie | Pages | Onglets | Contenu |
| --- | --- | --- | --- |
| I. Informations générales | 1 à 3 | Page de garde, fiches R1, R2, R3 | Identification, activités par code de nomenclature, dirigeants |
| II. Notes statistiques et de synthèse | 4 à 49 | Grille d'analyse, bilan, compte de résultat, TFT, notes 1 à 34 et leurs compléments C1, C2, CO1 | États financiers et notes annexes |
| III. Notes sociales et environnementales | 50 à 57 | Notes 16B, 16B bis, 16C, 18, 27A et C1, 27B, 35 | Retraites, dettes fiscales et sociales, personnel |
| IV. Notes commerciales | 58 et 59 | Notes 21 et 22 | Chiffre d'affaires, achats |
| V. Annexes fiscales | 60 à 66 | CF1, CF1 bis, ter, quater ; CF2, CF2 bis, ter | Résultat fiscal, impôt, minimum de perception, acomptes, TVA annuelle |

### Cellules des états

| État | Onglet | Références | Colonnes de valeurs |
| --- | --- | --- | --- |
| Bilan actif | « BILAN PAYSAGE » | Colonne A, lignes 12 à 40 | D brut, E amortissements et dépréciations, F net N, G net N-1 |
| Bilan passif | « BILAN PAYSAGE » | Colonne H, lignes 12 à 40 | K net N, L net N-1 |
| Compte de résultat | « COMPTE DE RESULTAT » | Colonne A, lignes 11 à 52 | E exercice N, F exercice N-1 ; signe en C, note en D |
| TFT | « TABLEAU DES FLUX DE TRESORERIE » | Colonne A, lignes 10 à 39 | E exercice N, F exercice N-1 |

Le classeur de relevé joint à la conversation (Releve\_classeur\_DSF\_Normal\_2021.xlsx) détaille chaque rubrique, les 104 liens des états vers les notes et 4 435 cellules de notes, dont 3 215 à saisir. Ce relevé des notes est automatique : les tableaux libres (associés, dirigeants, filiales, extrait de balance fournisseurs) sont à compléter à la main.

### Ce que le classeur impose à l'export

1. **Tout écrire.** XC, XG, XH, XI, ZA, ZF, ZG, ZH et CJ n'ont pas de formule ; plusieurs nets et comparatifs N-1 non plus.
2. **Suivre la convention du modèle.** Charges en valeur positive, le signe figurant dans la colonne C du compte de résultat ; TFT en valeurs absolues, sens donné par le libellé ; note 34 en milliers de francs.
3. **Garder notes et états cohérents.** Les états lisent 104 cellules de notes : un état rempli sans ses notes, ou l'inverse, se contredit.
4. **Adresser les onglets par leur nom exact.** 25 noms portent des espaces en fin ou doublés, par exemple « NOTE 14    » ou « NOTE  3C ».
5. **Recalculer avant dépôt.** Un classeur écrit par programme perd les valeurs de ses formules : recalcul par LibreOffice sans interface, puis comparaison des totaux avec Odoo.
6. **Versionner la table de correspondance.** Sans plages nommées, tout nouveau modèle de la DGI déplace des cellules.

### Anomalies des formules du modèle

| Cellules | Constat | Correction |
| --- | --- | --- |
| Bilan E13 à E16 | Amortissements des incorporels lus dans les dotations de l'exercice (note 3C, colonne C) | Cumul à la clôture (colonne E) |
| Bilan G13 à G16 | Net N-1 lu dans le brut à l'ouverture de la note 3A, avec une ligne de décalage | Net N-1 de la DSF précédente |
| Bilan E29 | Dépréciations des stocks = total net de la note 6 | Note 6, cellule B21 |
| Bilan K23 à K25 | Dettes financières (DA, DB, DC) lues dans la note 15A | Note 16A : B19, B26, B41 |
| Bilan K32 | Autres dettes (DM) = « Autres dettes État » de la note 18 | Note 19, cellule B31 |
| Bilan K40 | Total DZ sans l'écart de conversion-passif | Ajouter K39 |
| Résultat E13 | RB = variation de tous les stocks nets, en sens inverse | Marchandises seules : stock initial − stock final |
| Résultat E34 | XD = XC + RK en N, mais XC − RK en N-1 | XC − RK |
| Résultat E36 et E42 | Dotations financières et HAO comptées dans RL puis dans RN | RL limité à l'exploitation |
| Résultat E43 | XF additionne les frais financiers | TK + TL + TM − RM − RN |
| Note 34, B36 | La CAFG oublie la capacité d'autofinancement d'exploitation (B26) | B26 + B27 + … − B35 |

Le classeur code BC la rubrique « Créances et emplois assimilés » et DY l'écart de conversion-passif : l'export suit ces codes.

### À faire valider

- [ ] Version : ce fichier date de 2021 et ses tableaux fiscaux affichent un taux d'impôt sur les sociétés de « 30 % ou 28 % », contre 30 % ou 25 % aujourd'hui selon la DGI. Récupérer le classeur de l'espace de télédéclaration avant de figer les cellules.
- [ ] Traitement des anomalies : la plateforme reprend-elle les formules du modèle ou les valeurs téléversées ? Un téléversement test sur l'espace d'un client pilote tranche la question.
- [ ] Rabais obtenus : la note 22 range les remises, rabais et ristournes dans les autres achats, alors que 6019 relève des achats de marchandises (RA).

## Contrôles de cohérence automatiques

Seize contrôles conditionnent la fiabilité des états ; les bloquants empêchent l'export DSF tant qu'ils ne sont pas levés.

| Contrôle | Règle | Moment | Effet |
| --- | --- | --- | --- |
| Balance | Total des débits = total des crédits ; aucune pièce en brouillon sur la période | Avant tout état | Bloquant |
| Rattachement | Tout compte mouvementé est rattaché à une rubrique | Avant tout état | Bloquant |
| Comptes de passage | 471, 585, 588 et comptes d'attente d'Odoo (paiements en cours, suspens bancaire) à zéro | Clôtures mensuelle et annuelle | Bloquant à l'annuelle |
| Caisses | Aucun compte 57 créditeur | Chaque jour | Alerte |
| Équilibre du bilan | BZ = DZ | Chaque édition | Bloquant |
| Résultat | XI du compte de résultat = CJ du bilan | Chaque édition | Bloquant |
| Trésorerie | ZH du TFT = BT − DT du bilan N | Chaque édition | Bloquant |
| Intangibilité | Bilan d'ouverture N = bilan de clôture N-1 | Ouverture de l'exercice | Bloquant |
| TVA | 4431 + 4432 du mois = L28 ; comptes 445 = L22 ; solde 4441 ou 4449 = résultat de la déclaration | Chaque mois | Alerte |
| Chiffre d'affaires | XB annuel = somme des L15 des douze déclarations, hors éléments justifiés | Clôture annuelle | Alerte |
| Acomptes d'impôt | Cumul des acomptes déclarés (L54) = débits du compte 441 | Clôture annuelle | Alerte |
| Paie | Comptes 66 = masse du livre de paie ; L67 à L73 = crédits de 431, 447 et 442 | Chaque mois | Alerte |
| Immobilisations | Brut − amortissements − dépréciations = valeur nette du registre ; 681 = dotations du registre | Clôture annuelle | Alerte |
| Stocks | Comptes 31 à 38 = valorisation de l'inventaire | Clôture annuelle, mensuelle en valorisation automatisée | Alerte |
| Bascules | Liste des comptes basculés : clients créditeurs, fournisseurs débiteurs, banques à découvert | Clôture annuelle | Information |
| Déductibilité de la TVA | Paiement fournisseur en espèces au-delà de 100 000 FCFA : TVA de la facture signalée non déductible | Au paiement | Alerte |

Le contrôle sur les paiements en espèces compte particulièrement pour les bars et caves, qui règlent souvent leurs fournisseurs en liquide.

## Plan de développement par lots

Sept lots, dans cet ordre : le socle d'abord, puis les états et la déclaration mensuelle en parallèle, la DSF ensuite ; la paie avance à part dès que le socle existe. Bancs d'essai : les instances 18 Community et 18 Enterprise déjà en place sur le serveur d'AITE, puis un client pilote par édition.

| Lot | Contenu | Éditions | Critère de sortie |
| --- | --- | --- | --- |
| 0. Socle | Relevé du menu « Syscohada » d'Enterprise (états, lignes, formules) pour réutiliser ce qui est juste ; libellés et types corrigés ; sous-comptes (quotes-parts, 4811 lettrable, un 552 par opérateur mobile money) ; taxes complètes (4432 à l'encaissement, 4451, 4454, précomptes, TVA retenue à la source, taxe de séjour) ; référentiel des rubriques | Les deux | 100 % des comptes mouvementés d'une base de test rattachés ; factures de test correctement taxées |
| 1. États financiers | Bilan actif et passif (brut, amortissements, net, N-1), compte de résultat, TFT, contrôles bloquants | Enterprise (account.report) et Community (MIS Builder) | La balance réelle d'un client produit les mêmes états que ceux validés par son expert-comptable |
| 2. Déclaration mensuelle | Formulaire I/TVA-IR complet : TVA, précomptes, acomptes d'impôt, IRCM, impôts sur salaires ; écritures de liquidation | Les deux | Trois déclarations réelles reproduites sans écart |
| 3. Notes et tableaux fiscaux | Notes exigées en pièces jointes (3C, 7, 17, 24, 27A, CF1 quater), passage au résultat fiscal, puis autres notes | Les deux | Pièces jointes générées au format demandé par la DGI |
| 4. DSF Excel | Table rubrique → cellule (relevé du classeur fait), écriture de toutes les valeurs, recalcul et contrôle des totaux avant dépôt | Les deux | Classeur accepté au téléversement sur l'espace d'un client pilote |
| 5. Paie camerounaise | Règles CNPS, IRPP, CFC, FNE, redevance audiovisuelle, TDL ; lignes L67 à L73 ; DIPE | Paie Enterprise et OCA payroll | Trois mois de bulletins reproduits au franc près |
| 6. API DSF | Appels de la DGI depuis Odoo : connexion, déclaration, pages, soumission | Les deux | Dépôt réussi pour un client pilote |

Le relevé du classeur DSF Normal est fait : le lot 4 commence par la table rubrique → cellule, sur la version du classeur en vigueur. Le lot 6 suppose l'accès à l'espace de télédéclaration d'un client, seul endroit où la DGI publie les spécifications de l'API.

## État d'avancement : lots 0 et 1

Les lots 0 et 1 sont développés et testés sur Odoo 18 Community : 51 tests automatiques passent sur une base vierge. Le calcul par le moteur de rapports Enterprise lui-même reste à vérifier sur une instance Enterprise.

| Livrable | Module | Édition | Statut |
| --- | --- | --- | --- |
| Référentiel de 124 rubriques et moteur de calcul | aite\_syscohada\_base | Les deux | Fait et testé |
| Paramétrage du plan « cm » : libellés, types, sous-comptes, écarts de caisse | aite\_syscohada\_base | Les deux | Fait et testé |
| Taxes : TVA sur encaissement (4432 via 4438), immobilisations (4451), services achetés (4454) | aite\_syscohada\_base | Les deux | Fait et testé ; taxe de séjour et précompte créés inactifs |
| Contrôles et assistant « États et contrôles (AITE) » | aite\_syscohada\_base | Les deux | Fait et testé |
| Bilan, compte de résultat, TFT en MIS Builder | aite\_syscohada\_mis | Community | Fait et testé : mêmes montants que le moteur |
| Bilan, compte de résultat, TFT en account.report | aite\_syscohada\_reports | Enterprise | Généré et validé en Community ; à exécuter sur Enterprise |
| Relevé des états SYSCOHADA déjà livrés par Enterprise | Script d'export | Enterprise | Prêt, à lancer sur l'instance Enterprise |

### Tests réalisés

| Domaine | Ce qui est vérifié | Tests |
| --- | --- | --- |
| Formules et référentiel | Syntaxe identique au moteur Enterprise, totaux, cellules DSF | 13 |
| Paramétrage | Libellés, types, sous-comptes, taxes, idempotence, société hors OHADA intacte | 10 |
| Rattachement | Chacun des quelque 1 150 comptes capté une seule fois, en solde débiteur comme créditeur | 5 |
| Factures | TVA collectée, encaissement total et partiel, immobilisations, services | 5 |
| Scénario chiffré | Bilan, résultat, TFT, contrôles et assistant sur 2025 et 2026, montants calculés à la main | 8 |
| Propriétés du TFT | 49 gabarits d'écritures isolés, 3 grands livres aléatoires de 120 écritures | 2 |
| Rapports Enterprise | Chargement du XML par Odoo, calcul émulé égal au moteur, fichier livré à jour | 4 |
| MIS Builder | Mêmes montants que le moteur sur le scénario et un grand livre aléatoire | 4 |

### Écarts et précisions par rapport au plan

- MIS Builder n'a pas besoin d'extension : il retient les soldes débiteurs (pbal) ou créditeurs (nbal), compte par compte.
- Odoo 18 crée des comptes hors plan : 999001 et 999002 pour les écarts de caisse, 999999 pour le résultat non affecté. Les écarts partent désormais en 658800 et 758800 ; 999999 est intégré à CJ.
- Odoo ne solde pas les comptes de gestion à la clôture : CJ inclut les résultats antérieurs non affectés, et un contrôle le signale tant que l'affectation n'est pas passée.
- TFT : chaque ligne a sa formule dans le référentiel et le tableau s'équilibre par construction. MIS et Enterprise ne neutralisent pas les virements internes entre comptes d'immobilisations ; le moteur de base, si.
- Les codes DGI BC et DY sont portés par le référentiel, prêts pour l'export DSF.

### À faire sur une instance Enterprise (facultatif : la cible retenue est Community)

- [ ] Installer aite\_syscohada\_reports et lancer ses deux tests (balise aite\_syscohada\_enterprise).
- [ ] Lancer export\_existing\_syscohada\_reports.py pour relever les états SYSCOHADA livrés par Enterprise et les comparer au référentiel.
- [ ] Sur une base client, lancer compare\_with\_engine.py sur un exercice clos.

## Adaptation à Odoo Community

La cible retenue est Odoo 18 Community : trois modules suffisent, sans aucune dépendance à Enterprise, et les 62 tests passent sur une base vierge. Le module de rapports Enterprise devient facultatif.

| Module | Rôle |
| --- | --- |
| aite\_syscohada\_base | Référentiel, moteur de calcul, paramétrage du plan « cm » et des taxes, contrôles, assistant « États et contrôles (AITE) » |
| aite\_syscohada\_mis | Bilan actif, bilan passif, compte de résultat et TFT en modèles MIS Builder |
| aite\_syscohada\_community | États en un clic depuis le menu Syscohada (exercices N et N-1, exports PDF et Excel), déclaration mensuelle de TVA et écriture de liquidation |

Dépendances OCA en branche 18.0 : mis\_builder, date\_range, report\_xlsx, plus le paquet Python openupgradelib.

### Ce qui remplace les fonctions natives d'Enterprise

| Fonction Enterprise | Équivalent en Community |
| --- | --- |
| Rapports financiers et menu Syscohada | MIS Builder et assistant « États et contrôles (AITE) » |
| Affichage du rapport de TVA (L10 à L35) | Déclaration mensuelle I/TVA-IR complète (L0 à L80) du module aite\_syscohada\_community |
| Clôture de TVA | Écriture de liquidation : 4441 si TVA due, 4449 si crédit, 4445 si remboursement demandé |
| Report du crédit de TVA | L17 repris automatiquement de la ligne L35 de la déclaration validée précédente |
| Rapprochement et import des relevés | OCA account\_reconcile\_oca, account\_statement\_import\_file et \_sheet\_file |
| Immobilisations | OCA account\_asset\_management |
| Balance et grand livre | OCA account\_financial\_report |
| Paie (lot 5) | OCA payroll et payroll\_account |

### Déclaration de TVA : ce que vérifient les 7 premiers tests du module

- Mars : ventes, prestation encaissée et prestation impayée, export, exonéré, achats de biens, de services et d'immobilisations ; crédit de 96 250 FCFA reporté.
- Avril : crédit antérieur repris, prestation de mars encaissée, TVA à payer de 269 500 FCFA ; comptes de TVA soldés après liquidation.
- Avoir, régularisation manuelle avec compte de contrepartie, remboursement demandé, contrôles de saisie.
- Ouverture des quatre états en un clic, pour la société courante, avec les colonnes N et N-1.

Réglage à prévoir en Community : donner aux comptables le droit technique « Afficher toutes les fonctionnalités comptables », en mode développeur, pour qu'ils voient les écritures et le plan comptable.

### Lot 2 terminé : déclaration mensuelle I/TVA-IR complète

La déclaration couvre désormais tout le formulaire, de L0 à L80, avec le récapitulatif et le total à payer. Chaque ligne alimentée par la comptabilité lit les mouvements de la période sur un compte dédié, créé par le socle.

| Section du formulaire | Lignes | Source dans Odoo |
| --- | --- | --- |
| 0. TSR | L0 | Retenue sur factures de prestataires étrangers, compte 447120 |
| 1. Droits d'accises | L1 à L8 | Saisie du déclarant |
| 2 à 5. TVA | L10 à L35 | Étiquettes de taxe des écritures exigibles ; L11, L24 à L27 et L34 saisis |
| 6. TVA à payer | L36 à L39 | L32, TVA retenue à la source (447160), TVA autoliquidée sur prestations étrangères (447161) |
| 7. À reverser | L40 à L44 | Retenues opérées sur factures fournisseurs : 447170, 447180, 447130, 447140 |
| 8. À déduire | L45 à L49 | Retenues subies : 449220, 449210, 449230, 449240 |
| 9. Acomptes d'impôt | L50 à L55 | Chiffre d'affaires déclaré (L15) × taux de l'acompte + CAC, moins L49 et le crédit reporté |
| 10. IRCM, 11. IRNC | L56 à L66 | Bases saisies, taux de 15 % et CAC de 10 % modifiables |
| 12. Salaires | L67 à L73 | Écritures de paie sur 447210 (IRPP), 447215 (CAC), 447220 à 447260 (CFC, FNE, RAV, TDL) |
| 13. Plus-values, 14. Timbre d'aéroport | L74 à L80 | Saisie du déclarant |

- **Crédits reportés automatiquement** : TVA (L35 vers L17) et acompte (L55 vers L53), d'une déclaration validée à la suivante.
- **Écritures de liquidation** : TVA vers 4441, 4449 ou 4445 ; acompte en débit de 449250 et en crédit de 441100. Les retenues restent sur leurs comptes jusqu'au paiement.
- **Impression PDF** du formulaire, document de travail pour la saisie sur le portail de la DGI ; date limite au 15 du mois suivant.
- **Socle 18.0.1.1.0** : 22 comptes de retenues et d'avances d'impôt, 9 taxes de retenue à la source créées inactives (taux à valider), dont l'autoliquidation de la TVA sur prestations étrangères ; paramétrage appliqué à la mise à jour ou par le menu Configuration > SYSCOHADA > Appliquer le paramétrage.

Trois nouveaux tests, chiffrés à la main : un mois de mars complet (ventes, retenue d'acompte par un client, loyer et honoraires avec retenue, achat avec précompte, paie, dividendes) aboutit à 809 000 FCFA à payer ; un crédit d'acompte de 17 800 FCFA passe d'avril à mai ; l'autoliquidation alimente L21 et L38 à hauteur de 192 500 FCFA.

Points à valider avec l'expert-comptable avant la mise en production :

- les taux des taxes de retenue, avant de les activer ;
- la base de l'acompte (L15, où les prestations ne comptent qu'une fois encaissées) et les centimes additionnels appliqués à l'acompte, à l'IRCM et à l'IRNC mais pas aux retenues ;
- l'imputation des déductions L52 sur le total, centimes compris.

Limites : L24 (TVA retenue par les clients) et les sections 1, 10, 11, 13 et 14 restent en saisie ; la section 12 suppose une paie qui crédite les comptes 447210 à 447260. Le critère de recette du lot (trois déclarations réelles reproduites sans écart) reste à passer sur les données d'un client.

## Points à faire valider par l'expert-comptable

Dix choix sont à trancher avant le développement des lots 1 à 3 ; chacun modifie une formule ou un paramétrage.

- [ ] Bascules : au niveau du compte ou client par client (clients créditeurs vers DI, fournisseurs débiteurs vers BH) ?
- [ ] Quotes-parts des comptes 2818, 2918, 2919, 2939 et 2949 : clé d'éclatement en sous-comptes.
- [ ] TFT : formule exacte de la CAFG, sort des dépréciations à court terme (659, 759) et des cessions courantes (654, 754).
- [ ] Compte de résultat : 659 en RJ et 759 en TH, donc avant la valeur ajoutée ?
- [ ] Taxes patronales sur salaires (CFC patronal, FNE) : compte 442 ou 447, sachant que la DGI les déclare avec les impôts retenus sur salaires.
- [ ] TVA des prestations exigible à l'encaissement : compte d'attente retenu avant le transfert vers 4432.
- [ ] Précompte subi sur les achats : compte d'imputation et régime de déduction.
- [ ] Taxe de séjour : compte, base de calcul et exigibilité.
- [ ] Factures conformes issues du système de facturation de l'administration : incidence sur les factures émises et reçues dans Odoo.
- [ ] Format de DSF de chaque client : système normal ou système minimal de trésorerie.

## Sources

Consultées le 25 septembre 2026.

- Odoo 18, code source : [l10n\_cm](https://github.com/odoo/odoo/tree/18.0/addons/l10n_cm) et [l10n\_syscohada](https://github.com/odoo/odoo/tree/18.0/addons/l10n_syscohada) (modèle comptable, taxes, rapport de TVA, menu Syscohada).
- OCA, branche 18.0 : [mis-builder](https://github.com/OCA/mis-builder/tree/18.0), [account-financial-reporting](https://github.com/OCA/account-financial-reporting/tree/18.0), [account-financial-tools](https://github.com/OCA/account-financial-tools/tree/18.0), [account-reconcile](https://github.com/OCA/account-reconcile/tree/18.0), [bank-statement-import](https://github.com/OCA/bank-statement-import/tree/18.0), [account-closing](https://github.com/OCA/account-closing/tree/18.0), [payroll](https://github.com/OCA/payroll/tree/18.0).
- Direction générale des impôts : [page DSF et classeurs officiels](https://www.impots.cm/fr/declarations-statistiques-et-fiscalesdsf), [guide de télédéclaration de la DSF](https://www.impots.cm/sites/default/files/documents/GUIDE%20TELEDECLARATION%20DSF%202023.pdf), [formulaire I/TVA-IR](https://www.impots.cm/sites/default/files/documents/ITVA-IR.pdf), [fiche TVA](https://impots.cm/sites/default/files/documents/FICHE%20TVA.pdf), [fiche impôt sur les sociétés](https://impots.cm/sites/default/files/documents/ok%20FT%20IS%20ok.pdf).

* Classeur DSF Normal de la DGI, version verrouillée du 9 mars 2021, transmis par AITE Consulting le 25 septembre 2026.
