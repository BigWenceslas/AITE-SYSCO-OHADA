# AITE Consulting — Structuration de la comptabilité et de la trésorerie (SYSCOHADA révisé, Odoo 19 Enterprise)

Version 1 du 16 novembre 2026. Destinataires : ABOLO Cyrille Donald (Directeur Général), BESSALA Akogo Aristide (Directeur Technique), le comptable d'AITE et son expert-comptable.

Base visée : « Odoo 19.0+e-20260924 (Edition Enterprise) », expiration affichée le 25 décembre 2026, applications CRM, Facturation, Achats et Inventaire.

Conventions de ce document :

- **à valider** : règle fiscale ou comptable sans source citée (CGI, loi de finances, DGI) ; l'expert-comptable tranche.
- **à confirmer sur la base** : dépend de l'existant d'AITE, pas encore vu (aucun export reçu à ce jour).
- **CE** / **EE** : fonction vérifiée dans les sources d'Odoo 19 Community (fichier et ligne cités) / fonction d'Enterprise, non vérifiable dans ces sources.
- Les chemins de fichiers `addons/…` sans autre précision renvoient aux sources d'Odoo 19 Community consultées ; ceux du dépôt AITE sont préfixés « dépôt ».

---

## 1. Synthèse

### Objectif

Tenir la comptabilité d'AITE selon le SYSCOHADA révisé et la fiscalité camerounaise, dans la base Odoo existante, sans perdre quatre ans d'historique. Concrètement :

1. des comptes de produits et de charges justes par nature (services, marchandises, licences) ;
2. une TVA des prestations exigible à l'encaissement, des retenues tracées compte par compte ;
3. une trésorerie rapprochée chaque mois (banques, mobile money, caisse) et un plan de trésorerie ;
4. une marge suivie par ligne de métier (analytique) ;
5. une déclaration I/TVA-IR et des états SYSCOHADA (bilan, compte de résultat, TFT) produits depuis Odoo.

### Constat probable (à confirmer sur la base)

| Point | Ce que l'on sait | Conséquence |
| --- | --- | --- |
| Hébergement | Confirmé par AITE le 16/11/2026 : serveur VPS administré par AITE (serveur propre), pas Odoo Online. | Les modules Python sont installables (ajout à `addons_path`, redémarrage du service) ; une copie de la base sur le même VPS sert aux essais. |
| Comptes par défaut du plan « cm » d'Odoo 19 | Sans compte sur l'article ou sa catégorie, une vente va en 701100 (marchandises) et un achat en 601100. | Un service sans compte sur l'article ou sa catégorie part en ventes de marchandises (rubrique TA, marge commerciale XA) au lieu de 706100 (TC). |
| Taxe de vente par défaut | La taxe livrée « 19.25% » (compte 4431) est exigible à la facture ; aucune taxe à l'encaissement n'est livrée. | La TVA des prestations est probablement déclarée à la facture, alors que la règle retenue (fiche TVA de la DGI) est l'encaissement pour les services. |
| Fournisseurs étrangers | La position « International » s'applique seule et remplace la TVA d'achat par « 0% EX », sans étiquette de déclaration. | Microsoft, Odoo SA, nuage : ni autoliquidation ni TSR dans les déclarations. Régime à valider. |
| Stock | Le stock est valorisé en 382 avec 6021/6032, comptes de matières premières. | Le matériel revendu sort de la marge commerciale. |
| Application | « Facturation » annoncée ; l'application Comptabilité (module `accountant`, EE) n'est peut-être pas installée ; `account_accountant` est la Facturation d'Enterprise et ne suffit pas (à vérifier dans l'export 1). | Sans elle : ni rapprochement moderne, ni rapports (balance, grand livre, TVA), ni immobilisations. |
| Modules AITE | Écrits pour Odoo 18 ; non installables tels quels en 19 (étiquettes de taxe non signées, champs supprimés). | Portage obligatoire avant toute installation (section 3.3). |

### Décisions clés

| N° | Décision | Qui | Quand |
| --- | --- | --- | --- |
| D1 | Hébergement : confirmé, serveur VPS propre (16/11/2026). Reste à fixer la procédure de copie de test sur le VPS (duplication de la base et du `filestore`) et la sauvegarde avant chaque étape. | DT | 22/11/2026 (S47) |
| D2 | Contrat Enterprise renouvelé avant le 25/12/2026, avec multi-société si le scénario B est retenu. Point de décision le 18/12 : la nouvelle date d'expiration est lue sur la base de production (et sur ses copies) ; à défaut, répétition et bascule reportées, l'exercice 2027 démarre avec le paramétrage actuel et la coupure se fait au 01/02/2027. | DG | 18/12/2026 |
| D3 | Reprise : correction en place avec coupure au 01/01/2027 (C1) si la société est déjà au plan « cm » ; nouvelle société au plan « cm » au 01/01/2027 (B) sinon. Voir section 7. | DG, expert-comptable | 11/12/2026 |
| D4 | Natures fiscales : licences revendues, produits packagés, pose, frais refacturés, TVA sur acomptes, autoliquidation et TSR. | Expert-comptable | 11/12/2026 |
| D5 | Une seule chaîne de liquidation de TVA : clôture de TVA d'Enterprise ou liquidation AITE, jamais les deux. Avant toute clôture de TVA d'Enterprise, décocher « Écriture de clôture de taxe » sur les lignes de répartition des taxes de retenue et de précompte, et sur la ligne 447161 de l'autoliquidation (section 6.5). | DT, expert-comptable | 18/12/2026 |
| D6 | Exercices clos (2022-2025) : aucune écriture modifiée dans Odoo sur les périodes clôturées ; écarts chiffrés par le diagnostic remis à l'expert-comptable, qui décide d'une éventuelle régularisation fiscale hors Odoo (à valider). | DG, expert-comptable | 11/12/2026 |

### Calendrier en phases

| Phase | Semaines | Contenu | Jalon |
| --- | --- | --- | --- |
| 0. Cadrage | S47-S48 (16/11-29/11/2026) | Réponses aux questions de la section 2, exports, désignation de l'expert-comptable | Exports reçus |
| 1. Diagnostic et décisions | S48-S50 (23/11-13/12) | Analyse des exports, choix A/B/C, natures fiscales, table de correspondance | D1 à D6 signées |
| 2. Paramétrage sur copie et portage | S49-S52 (30/11-27/12) | Catégories, taxes, analytique, journaux sur copie ; portage du socle en 19.0 en parallèle | Répétition générale réussie |
| 3. Bascule | S53-S1 (28/12/2026-10/01/2027) | Coupure au 01/01/2027, ouverture provisoire, premiers mouvements | Facturation 2027 conforme |
| 4. Première déclaration | S2-S7 (janvier-février 2027) | Déclaration I/TVA-IR de janvier 2027 depuis Odoo, avant le 15/02/2027, comparée au calcul du comptable ; module déclaré bon pour la production seulement si la recette S52 est réussie, sinon déclaration au tableur | Écart nul ou justifié |
| 5. Clôture 2026 | Février à mai 2027 | Arrêté 2026, DSF (15 mars, 15 avril ou 15 mai selon le centre), à-nouveaux définitifs, verrouillage | DSF déposée |
| 6. Consolidation | Mars à juin 2027 | États SYSCOHADA d'Enterprise comparés au moteur AITE, plan de trésorerie, budget | Recette du lot 1 (états) |

### Effort et coûts

| Poste | Estimation | Source |
| --- | --- | --- |
| Portage du socle et de la déclaration, correction des défauts du lot 2, tests et CI | 13 à 21 jours-homme | Section 3.3 |
| Recette des rapports Enterprise AITE | 3 à 5 jours-homme | Section 3.3 |
| Diagnostic et paramétrage sur copie | À chiffrer | Sections 2 et 7 |
| Répétition et bascule | À chiffrer | Sections 7.4 et 7.5 |
| Renouvellement du contrat Enterprise | Montant du contrat | Décision D2 |
| Migration d'hébergement si la base est sur Odoo Online | À chiffrer | Décision D1 |
| Honoraires de l'expert-comptable (D3 à D6, validations) | À chiffrer | Section 10 |

---

## 2. Exports à fournir et informations à confirmer

### 2.1 Exports depuis la base

Mode opératoire commun : activer le mode développeur, ouvrir la vue liste, inclure les archivés (filtre « Archivé » ou « Actif » retiré), tout sélectionner, Action > Exporter, cocher « Je veux mettre à jour les données (export compatible import) » pour obtenir l'identifiant externe, format XLSX. Les libellés de menus sont ceux de la version française, à confirmer sur la base ; sans l'application Comptabilité, remplacer « Comptabilité » par « Facturation ». Chemins : menus d'Odoo 19 Community, réorganisation éventuelle par `accountant` à vérifier sur la base.

Prérequis : en mode développeur, donner à l'utilisateur qui exporte le groupe « Afficher les fonctionnalités de comptabilité - Lecture seule » (Paramètres > Utilisateurs & Sociétés > Groupes) si l'application Comptabilité (`accountant`) n'est pas installée : sans ce groupe, ni le Plan comptable ni les écritures ne sont visibles (`addons/account/views/account_menuitem.xml:24-26, 46-51`). Activer aussi Comptabilité analytique dans les paramètres pour l'export 14.

| N° | Export | Chemin dans Odoo 19 | Format | Pourquoi |
| --- | --- | --- | --- | --- |
| 1 | Modules installés : nom technique, nom, auteur, version installée, état | Applications, retirer le filtre « Applications », filtre « Installées », vue liste | XLSX | Savoir si Ventes, Comptabilité, rapports, immobilisations, abonnements, notes de frais, paie, site, modules tiers sont là ; vérifier la présence de `sale`, `accountant`, `account_accountant`, `account_reports`, `account_asset`, `account_followup`, `sale_subscription`, `hr_expense`, `hr_payroll` |
| 2 | Écran « À propos » | Paramètres, bas de page | Capture | Édition, version, expiration, nombre d'utilisateurs |
| 3 | Paramètres comptables | Comptabilité > Configuration > Paramètres : Localisation fiscale (Pack), option « Comptabilité de trésorerie » (`tax_exigibility`), comptes par défaut, devises, dates de verrouillage | Captures | Plan comptable réel (« cm », « syscohada » ou autre), point de départ de tout |
| 4 | Sociétés | Paramètres > Utilisateurs et sociétés > Sociétés | XLSX | Multi-société, succursales |
| 5 | Plan comptable : code, nom, type, lettrable, devise, actif, sociétés, identifiant externe | Comptabilité > Configuration > Comptabilité > Plan comptable | XLSX | Codes réels, comptes ajoutés à la main, types incohérents ; base de la table de correspondance |
| 6 | Taxes : nom, usage, type de calcul, montant, prix TTC, exigibilité, groupe, lignes de répartition (type de document, facteur, compte, grilles), positions fiscales, champ « Remplace » (`original_tax_ids`), identifiant externe | Comptabilité > Configuration > Taxes | XLSX | Comptes de TVA, étiquettes du rapport, taxes déjà utilisées |
| 7 | Groupes de taxes : comptes de TVA à payer, de créance, d'avance | Comptabilité > Configuration > Groupes de taxes (mode développeur) | XLSX | Contrepartie de la clôture de TVA d'Enterprise (4441 / 4445 dans `addons/l10n_cm/data/template/account.tax.group-cm.csv:2-3`) |
| 8 | Positions fiscales : nom, application automatique, pays, comptes de remplacement | Comptabilité > Configuration > Positions fiscales | XLSX | Clients et fournisseurs étrangers |
| 9 | Journaux : nom, code, type, devise, compte par défaut, compte d'attente, comptes de profit et de perte, compte bancaire, verrouillage par hachage, modes de paiement entrants et sortants avec leur compte | Comptabilité > Configuration > Comptabilité > Journaux | XLSX | Paramétrage de la trésorerie, paiements en attente |
| 10 | Conditions de paiement | Comptabilité > Configuration > Conditions de paiement | XLSX | Échéances du plan de trésorerie |
| 11 | Catégories d'articles : nom complet, parent, comptes de revenus et de charges, valorisation, méthode de coût, compte de valorisation, compte de variation | Comptabilité > Configuration > Facturation > Catégories de produits, société d'AITE active | XLSX | Comptes réellement utilisés à la facturation |
| 12 | Articles, archivés compris : référence, nom, type, suivi en stock, catégorie, prix, coût, taxes de vente et d'achat, comptes de revenus et de charges, politique de facturation, suivi du service, récurrent | Ventes > Produits > Produits si Ventes est installée ; sinon Facturation > Clients > Produits | XLSX | Familles de ventes, articles mal classés |
| 13 | Contacts clients et fournisseurs : nom, société ou particulier, NIU (champ TVA), RCCM, pays, comptes client et fournisseur, position fiscale, conditions de paiement, étiquettes | Contacts, vue liste | XLSX | Retenants à la source, étrangers, sous-traitants |
| 14 | Plans analytiques, comptes analytiques, modèles de distribution | Comptabilité > Configuration > Comptabilité analytique > Dimensions analytiques / Comptes analytiques / Modèles de répartition analytique (option « Comptabilité analytique » cochée, groupe `analytic.group_analytic_accounting`, `addons/account/views/account_menuitem.xml:65-68`) | XLSX | Analytique existante |
| 15 | Balance générale au 31/12 de chaque exercice et au 31/10/2026 : ouverture, débit, crédit, solde par compte | Comptabilité > Rapports > Balance générale (EE) | XLSX | Soldes à reprendre ; comparaison avec les états validés |
| 16 | Grands livres des comptes 40, 41, 42, 43, 44, 47, 52 à 58, 656, 756, 676, 776, 999 sur 2025-2026 | Comptabilité > Rapports > Grand livre (EE), filtre par compte | XLSX | TVA, retenues, attentes, trésorerie, écarts de change |
| 17 | Balance âgée clients et fournisseurs au 31/10/2026, grand livre des partenaires | Comptabilité > Rapports > Balance âgée (EE) | XLSX | Créances, relances, reprise par pièce |
| 18 | Lignes d'écritures de 4 exercices : date, pièce, journal, compte, partenaire, article, libellé, débit, crédit, taxes, grilles, distribution analytique, lettrage, résiduel, devise | Comptabilité > Révision > Contrôle > Écritures comptables (`account.move.line`, URL /odoo/items, `addons/account/views/account_menuitem.xml:31-34`) ; « Pièces comptables » = `account.move` ; emplacement à confirmer sur la base, Enterprise pouvant réorganiser les menus | XLSX ou CSV | Mesurer les ventes de services passées en 701, la TVA en 4431, les retenues |
| 19 | Factures et avoirs non soldés, paiements non lettrés, avances (4191, 409) | Comptabilité > Clients > Factures et Fournisseurs > Factures, filtre « Non payées » | XLSX | Reprise ; TVA en attente des services non encaissés |
| 20 | Commandes de vente avec leur origine CRM, factures d'acompte, abonnements actifs (client, plan, dates, prochaine facture, montant) | Ventes > Commandes, si Ventes est installée ; Abonnements (EE, si installé) | XLSX | Facturation récurrente, produits constatés d'avance |
| 21 | Opportunités ouvertes : montant, probabilité, date de clôture prévue | CRM > Pipeline, vue liste | XLSX | Plan de trésorerie |
| 22 | Stock : rapport de valorisation, quantités par article et emplacement | Rapport de valorisation d'inventaire (action `stock_account.action_report_stock_valuation`, URL /odoo/stock-valuation-closing, `addons/stock_account/report/stock_valuation_report.xml:3-9`) ; emplacement dans le menu Inventaire à confirmer sur la base ; et Stock | XLSX | Solde 31, compte 382 |
| 23 | Immobilisations : libellé, date, valeur, méthode, durée, cumul, comptes | Comptabilité > Comptabilité > Immobilisations (EE, si `account_asset`) | XLSX | Reprise du registre |
| 24 | Lignes de relevés non rapprochées et paiements en attente | Tableau de bord comptable, carte de chaque banque | XLSX | Soldes de 521xxx, 585 |
| 25 | Rapport de TVA et dernière clôture de TVA ; menu Rapports > Syscohada | Comptabilité > Rapports > Déclaration TVA (EE) | Captures et XLSX | Ce qu'Enterprise fournit déjà ; double liquidation à éviter |
| 26 | Sauvegarde complète (dump PostgreSQL et filestore, ou zip du gestionnaire de bases) et copie de test neutralisée | Serveur propre : pg_dump et filestore ; Odoo.sh : sauvegarde ou branche de préproduction ; Odoo Online : duplication depuis le portail (à vérifier sur l'abonnement) | Dump + zip | Diagnostic sur base réelle, copies de paramétrage et de répétition |

### 2.2 Pièces hors Odoo

1. Les trois dernières déclarations I/TVA-IR déposées, avec quittances (recette ligne par ligne).
2. La dernière DSF, son tableau de passage au résultat fiscal (CF1) et les balances validées 2023 à 2025.
3. Les attestations de retenue à la source reçues sur 12 mois.
4. Carte de contribuable, attestation de conformité fiscale, dernier avis d'imposition (centre et régime).
5. Avis de patente et quittances, marchés enregistrés, bail du siège.
6. Contrats de partenaire Microsoft et, le cas échéant, Odoo ; trois factures récentes de chaque fournisseur étranger (Microsoft, nuage, Odoo SA).
7. Contrats d'infogérance et de support types ; liste des sous-traitants et apporteurs avec leur statut fiscal et leur NIU.
8. Trois mois de bulletins, livres de paie et DIPE ; nombre de salariés.
9. Relevés des deux derniers mois de chaque banque et de chaque portefeuille de mobile money, au format fourni par l'établissement.
10. Contrat ou bon de commande Odoo Enterprise.

### 2.3 Informations à confirmer

| Information | Pourquoi c'est décisif | Où la trouver |
| --- | --- | --- |
| Hébergement (serveur propre, Odoo.sh, Odoo Online) et accès administrateur au serveur | Installer ou non des modules Python | Hébergeur, URL de la base, portail odoo.com |
| Le site et la base comptable sont-ils la même instance ? | Les ventes de la boutique (6 articles publiés) entrent alors en comptabilité | DT |
| Contrat Enterprise : formule, utilisateurs, multi-société, hébergement couvert, effet de l'expiration du 25/12/2026 sur la base et ses copies | Scénario B, copies de test | Contrat ; documentation officielle non consultable depuis la session de relevé |
| Plan comptable actuel (Pack) et version de départ de la base | Choix A, B ou C | Export 3 |
| Centre des impôts (DGE, CIME ou CDI) et régime (réel ou simplifié) | Échéance de la DSF et du solde d'IS, taux d'acompte | Carte de contribuable |
| Banques, comptes, devises, cartes ; portefeuilles Orange Money et MTN MoMo marchands ; caisses | Journaux de trésorerie | DG, comptable |
| Expert-comptable et outil actuel de production de la DSF | Validations, balances de référence | DG |
| Outil de paie actuel | Comptes 42, 43, 447 | Comptable |

---

## 3. Cible comptable

### 3.1 Socle

| Brique | Cible | Statut |
| --- | --- | --- |
| Plan comptable | Plan « cm » (SYSCOHADA pour Sociétés, codes à six chiffres, `addons/l10n_cm/models/template_cm.py:8-14`) | À confirmer sur la base |
| Application | Comptabilité d'Enterprise (module `accountant`, qui ajoute à `account_accountant` les groupes Lecture seule et Comptable) en plus de Facturation : rapprochement, rapports, verrouillage, immobilisations, produits différés | EE, à confirmer sur la base ; comprise dans l'abonnement Enterprise d'après notre connaissance, à vérifier |
| TVA des prestations | Taxe de vente à l'encaissement : compte 4432, compte d'attente 443800, étiquette CM_10 ; option « Comptabilité de trésorerie » (`tax_exigibility`, Paramètres > Taxes ; journal et compte de transition visibles avec les fonctions comptables complètes ; `addons/account/models/company.py:220-221`, `addons/account/models/res_config_settings.py:100`, `addons/account/views/res_config_settings_views.xml:90-96`, `addons/account/models/account_tax.py:165-176`) | Règle DGI citée par le dépôt ; détail à valider |
| Comptes par défaut | Revenus 706100, charges de la catégorie ; ne plus laisser 701100/601100 par défaut | Section 3.4 |
| Modules AITE | Socle et déclaration portés en 19.0 ; rapports Enterprise après recette | Section 3.3 |

### 3.2 Ce qu'Odoo 19 fournit déjà pour le Cameroun

- **CE** : plan « cm », 7 taxes (19,25 % ventes sur 4431 ; 19,25 % G et 19,25 % S achats, toutes deux sur 4452 ; 0 % export ; 0 % import ; deux exonérées), positions « National » et « International », définition du rapport de TVA L10 à L35 (`addons/l10n_cm/data/template/account.tax-cm.csv`, `account.fiscal.position-cm.csv`, `addons/l10n_cm/data/account_tax_report_data.xml`).
- **CE** : report du crédit L35 vers L17 défini dans le rapport (`_carryover_tax`, `account_tax_report_data.xml:366-379`).
- **EE** : affichage du rapport de TVA, clôture de TVA, balance, grand livre, balance âgée (`account_reports`) : à confirmer sur la base.
- **Manque** : taxe de vente à l'encaissement, TVA sur immobilisations (4451), TVA à l'importation (CM_20, L20 : aucune taxe livrée, ni par `l10n_cm` ni par le socle), autoliquidation des services étrangers (CM_21 et L38, socle), retenues et précomptes, lignes L0 à L9 et L36 à L80, états SYSCOHADA contrôlés. C'est ce qu'apportent les modules AITE.

### 3.3 Modules AITE à porter en 19.0

| Module | Utile chez AITE ? | Pourquoi | Effort estimé (jours, à affiner) |
| --- | --- | --- | --- |
| `aite_syscohada_base` (socle) | Oui | 45 libellés corrigés, types de comptes, 32 sous-comptes (443800, 447xxx, 449xxx, 552100, 552200), taxes à l'encaissement et sur immobilisations, retenues inactives « (taux à valider) », 9 contrôles, moteur de référence. Aucune dépendance Enterprise. | 5 à 8 |
| Déclaration I/TVA-IR, extraite d'`aite_syscohada_community` dans un module sans MIS (par exemple `aite_syscohada_itvair`) | Oui | L0 à L80 hors TVA, acompte, retenues, total à payer. Aujourd'hui `aite_syscohada_community` dépend d'`aite_syscohada_mis`, donc de `mis_builder` (dépôt `addons/aite_syscohada_community/__manifest__.py:11`) : inutile sur Enterprise. | 3 à 5 |
| `aite_syscohada_reports` | Oui, après recette | Bilan, compte de résultat, TFT en `account.report` ; jamais exécutés sur une vraie base Enterprise (dépôt `ROADMAP.md`, lot 1) | 3 à 5 (recette sur copie) |
| `aite_syscohada_mis` | Non | Doublon des rapports Enterprise | 0 |
| Démonstrations | Non sur la base d'AITE | Base de formation séparée seulement (dépôt `docs/guide/guide.md:128-131`) | Facultatif |
| Tests, CI, `setup_dev.sh` sur 19.0 | Oui | Suite de référence : 112 tests en 18 | 3 à 5 |
| Correction des trois défauts connus du lot 2 (L17, extourne, société courante) | Oui | Dépôt `ROADMAP.md`, lot 2 ; section 6.5 | 2 à 3 |

Prérequis du portage : accès aux sources Odoo 19 Enterprise de même révision que la production (19.0+e-20260924), par l'accès partenaire au dépôt Enterprise, une branche de développement Odoo.sh ou les addons Enterprise du serveur d'AITE ; `scripts/setup_dev.sh` (dépôt, qui ne récupère aujourd'hui que le Community 18) et la CI sont à étendre à Enterprise 19 (étiquette `aite_syscohada_enterprise`).

Points de portage relevés dans les sources 19 (au-delà des quatre fonctions du guide, dépôt `docs/guide/guide.md:1061-1073`) :

| Point | Source Odoo 19 | Effet si non corrigé |
| --- | --- | --- |
| Étiquettes de taxe non signées (`CM_10_base`) | `addons/account/models/account_account_tag.py:18-20`, `account.tax-cm.csv` | Taxes AITE créées sans étiquette, absentes de la déclaration |
| `tax_negate` et `tax_tag_invert` supprimés | absents des modèles d'`account` 19 | Erreur au premier calcul de la déclaration |
| `account.account.deprecated` remplacé par `active` | `addons/account/models/account_account.py:42` | Paramétrage et contrôle RATTACHEMENT en échec (dépôt `res_company.py:249-250`, `syscohada_check.py:39`) |
| `name_boolean_group` et `res.groups.category_id` disparus | `odoo/addons/base/models/res_users.py`, `res_groups.py:23` | Le socle ne se charge pas (dépôt `res_users.py:3`, `res_groups.py:25`) |
| `_sql_constraints` à passer en `models.Constraint` | style d'`account` 19 | À vérifier au chargement |
| `_get_tax_exigible_domain` renvoie un objet `Domain` | `addons/account/models/account_move_line.py:3478-3495` | À vérifier à l'exécution |

Condition : hébergement acceptant du Python. Sur Odoo Online, seul un paramétrage manuel est possible (annexes A et B du guide du dépôt), plus éventuellement un module de données ne contenant que le XML des rapports (à vérifier sur l'abonnement).

### 3.4 Familles de ventes

Taxe « S (encaissement) » = taxe de vente du socle « 19,25 % S (encaissement) » (4432, attente 443800), ou une taxe créée à la main sur ce modèle si le socle n'est pas installé. Catégories : voir `categories_produits.csv`.

Les colonnes Mode de facturation, l'acompte (419100) et `amount_to_invoice` supposent l'application Ventes (`sale`), absente de la liste des applications annoncées (CRM ne l'installe pas : `addons/crm/__manifest__.py:12-15`, `addons/sale_crm/__manifest__.py:19,28`) ; les jalons exigent en plus Projet et l'option « Jalons » (`project.group_project_milestone`, `addons/sale_project/models/product_template.py:18-19`) ; à confirmer sur la base. Sans Ventes : factures saisies directement en Facturation, échéancier des contrats tenu hors Odoo.

| Famille | Catégorie | Compte de produit | Taxe | Type d'article | Mode de facturation | Points à trancher |
| --- | --- | --- | --- | --- | --- | --- |
| Intégration ERP Odoo au forfait | Prestations / Intégration ERP et projets | 706100 (706200 hors Région) | S (encaissement) | Service | Jalons (`delivered_milestones`, `addons/sale_project/models/product_template.py:11-20`) ; acomptes en 419100 | Retenues subies du client : à valider |
| Développement sur mesure | Prestations / Développement | 706100 | S (encaissement) | Service | Forfait ou jalons | — |
| Régie et assistance technique | Prestations / Régie | 706100 | S (encaissement) | Service | Mensuelle, quantités livrées saisies (`addons/sale/models/product_template.py:14-41`) ; feuilles de temps : `sale_timesheet`, à confirmer sur la base | Saisie des temps ? |
| Infogérance, hébergement, maintenance, support | Prestations / Infogérance | 706100 | S (encaissement) | Service | Abonnement mensuel ou annuel (EE `sale_subscription`, à confirmer sur la base) ; produits constatés d'avance 477 si facturé d'avance | Contrats annuels d'avance ? |
| Audit, conseil, cybersécurité | Prestations / Audit et sécurité | 706100 | S (encaissement) | Service | Ponctuelle, acompte | — |
| Installation réseaux, contrôle d'accès, vidéosurveillance, Starlink | Prestations / Installation | 706100 ou 705100 (à valider) | S (encaissement) si la pose est facturée à part | Service | Ponctuelle, acompte | Prix global matériel + pose : ventilation à valider |
| Formation | Prestations / Formation | 706100 | S (encaissement), exonération éventuelle à valider | Service | Ponctuelle | — |
| Produits packagés AITE (AITE House, SIRH, Courrier, GMAO, School, SUP, Facture avec IR, Point de Vente) | Produits packagés AITE | 706100 ou 707600 (à valider) | S (encaissement), à valider pour une concession de droits | Service | Licence ponctuelle puis maintenance récurrente | Licence perpétuelle ou annuelle ? Prix HT ou TTC ? Coûts de développement immobilisés ? Logiciel produit en interne : 2193 (en cours) puis 2131, contrepartie 721 (TF) ; ou frais de développement : 2191 puis 211 si les critères sont remplis. Choix à valider par l'expert-comptable. |
| Licences revendues (Microsoft 365, Odoo Enterprise) | Licences et abonnements revendus | A : 701100 / 601100 (marchandises) ; B : 706100 / 605700 (services) ; C : 707200 (commission) | A : 19.25% à la livraison ; B : S (encaissement) ; C : sur la commission | Service (non stockable) | Abonnement ; option B seulement : produits constatés d'avance (477) sur la part non courue, et charges constatées d'avance (476) symétriques sur l'achat à l'éditeur. Options A et C : pas d'étalement | Choix A, B ou C : expert-comptable. Le modèle CSV met B par défaut. |
| Matériel revendu | Matériel revendu | 701100 (701200 hors Région) | 19.25% (biens, à la livraison) | Stockable | À la livraison (`invoice_policy = delivery`) ; acompte | Importations : TVA en douane à saisir depuis les pièces du transitaire (à valider) |
| Frais refacturés | Frais refacturés aux clients | 707800 ou débours en compte de tiers (à valider) | À valider | Service | Refacturation au coût (`expense_policy`, `addons/sale/models/product_template.py:22-32`) | Débours ou produit ? |

Règles communes :

- **Clients étrangers** (Madagascar, Gabon, Djibouti, RDC…) : la position « International » remplace « 19.25% » par « 0% EX » (L13). La taxe à l'encaissement du socle n'est pas dans cette correspondance : l'y ajouter (champ « Remplace » (`original_tax_ids`) de la taxe « 0% EX », modèle 19, `addons/account/models/account_tax.py:101-106`). Règle de territorialité des services : à valider.
- **Organismes internationaux et clients publics** (CAFRAD, Port Autonome de Douala) : comptes 411400 et 411500 disponibles ; régime de TVA et retenues à valider.
- **Acomptes** : régler 419100 « Clients, avances et acomptes reçus » comme compte d'acompte des ventes (`downpayment_account_id`, `addons/sale/models/res_company.py:50-57`, domaine accepté : `income`, `income_other`, `liability_current` ; 419100 (`liability_current`) convient). Sans ce réglage, l'acompte va en produit. TVA sur acompte : une source tierce non vérifiée la dit exigible dès l'encaissement de l'acompte depuis la loi de finances 2026 ; à valider.
- **Politique de facturation** : licences et infogérance en quantités commandées, matériel en quantités livrées, achats de matériel en quantités reçues (`addons/purchase/models/product.py:14-24`).
- **Boutique en ligne** : si le site est la même base, chaque vente en ligne crée une commande et un paiement ; journal et frais du prestataire de paiement à confirmer sur la base.

### 3.5 Familles d'achats

| Famille | Catégorie | Compte de charge | Taxe | Retenue opérée par AITE | Point à trancher |
| --- | --- | --- | --- | --- | --- |
| Matériel destiné à la revente | Matériel revendu | 601100 ; 601200 importé ; 601500 frais d'achat | Achat local : 19.25% G (4452, L18) ; importé : taxe « 19,25 % importation » (L20, ligne suivante) | Précompte subi éventuel (449210, taux à valider) | Importations |
| TVA payée en douane | Écriture ou facture du transitaire ou de la douane | — | Taxe d'achat « 19,25 % importation » sur 4452, étiquettes +CM_20 et −CM_20, base = valeur en douane (L20) | — | À créer, assiette à valider |
| Sous-traitance (développeurs, techniciens, partenaires) | Achats / Sous-traitance | 621000 ou 632700 (à valider) ; fournisseur en 401300 possible | 19.25% S si assujetti (4452, ou 4454 avec le socle) | Retenue sur honoraires 447140 (L43) : champ d'application (nature de la prestation, régime du prestataire), taux (5 % codé dans le dépôt) et assiette à valider sur le CGI | Statut de chaque prestataire |
| Logiciels, cloud, abonnements consommés (Odoo Enterprise, Microsoft 365, hébergeurs, domaines) | Achats / Logiciels et cloud | 634300 ; 634500 pour les sites web | Fournisseur étranger : « 0% EX » par défaut. Autoliquidation (4454 à +100 %, 447161 à −100 %, L21 et L38) : à valider | TSR 447120 (L0) : le dépôt code 15 %, taux et assiette à valider ; TSR « imputable » selon une source tierce sur la loi de finances 2026, non vérifiée | Le fournisseur facture-t-il déjà la TVA camerounaise ? Paiement brut ou net ? |
| Licences achetées pour revente | Licences revendues | 601100 ou 605700 selon l'option A ou B | Selon le fournisseur (local ou étranger) | Idem | Option A, B ou C |
| Commissions d'apporteurs (10 à 30 % des contrats, offre d'emploi du site) | Achats / Commissions | 632200 | Sans TVA si non assujetti | Retenue applicable aux commissions d'apporteurs : à valider sur le CGI (les lignes IRNC L63 à L66 visent les conseils, comités, artistes et sportifs) | Saisie actuelle ? |
| Loyer du siège (Makepe) | Achats / Loyers | 622200 | Selon bailleur | Précompte sur loyers 447130 (L42) : 15 % codé dans le dépôt ; 10 % depuis la loi de finances 2026 selon une source tierce non vérifiée | Taux 2026 et bailleur |
| Électricité | Achats / Électricité | 605200 | 19.25% G | — | — |
| Téléphone, internet | Achats / Télécommunications | 628100, 628800 | 19.25% S | — | — |
| Frais bancaires ; frais de mobile money | Achats / Frais bancaires, Frais de monnaie électronique | 631800 ; 631700 (libellé d'Odoo erroné : « Taxes sur les instruments de monnaie électronique ») | À valider | — | TVA sur commissions bancaires |
| Honoraires (expert-comptable, avocat) | Achats / Honoraires | 632400 | 19.25% S | Retenue éventuelle, à valider | — |
| Fournitures de bureau | Achats / Fournitures | 605500 | 19.25% G | — | — |
| Déplacements et missions | Achats / Déplacements | 618100 ; 638400 (libellé d'Odoo erroné : « Tâches » pour « Missions ») | Selon la pièce | — | — |
| Matériel informatique immobilisé | Immobilisations / Matériel | 244200 ; amortissements 284400 ; dette 481200 | 19,25 % I (4451, L18, socle) | — | Seuil d'immobilisation |
| Logiciel acquis | Immobilisations / Logiciels | 213100 ; amortissements 281300 ; dette 481100 | 19,25 % I | — | — |
| Patente | Écriture ou facture | 641200 (libellé d'Odoo erroné : « Brevets… » pour « Patentes… ») | Sans TVA | — | Barème et échéance : à valider |
| Droits d'enregistrement et de timbre | Écriture ou facture | 646200 (droits de timbre, existant) ; droits d'enregistrement : 646100 « Droits de mutation » ou 646800, à valider (comptes présents dans le plan, `addons/l10n_syscohada/data/template/account.account-syscohada.csv:824-828`) | Sans TVA | — | Taux et cas : à valider |

Note sur les dettes d'immobilisations : Odoo passe la dette sur le compte fournisseur du partenaire (4011). Le reclassement en 481 se fait par un partenaire dédié ou à la clôture : à valider.

### 3.6 Produits et charges constatés d'avance

- **Besoin** : contrats de support, d'infogérance ou de licences facturés à l'année d'avance ; abonnements payés d'avance par AITE. Exemple chiffré dans la démonstration du dépôt : 6 000 000 facturés le 01/10/2025, 4 500 000 en 477 au 31/12/2025, repris le 01/01/2026 (dépôt `addons/aite_syscohada_demo_services/models/scenario.py`).
- **Comptes** : 477 (produits constatés d'avance, libellé d'Odoo « Revenu différé » à corriger) et 476 (charges constatées d'avance, « Dépenses prépayées »).
- **EE** : dates de début et de fin sur les lignes de facture et écritures différées générées par l'application Comptabilité ; comptes par défaut dans les paramètres. Fonctionnement exact en 19 : à confirmer sur la base.
- **CE** : assistant de changement de période (`addons/account/wizard/account_automatic_entry_wizard.py:15-20`) et écritures de produits à recevoir et charges à payer depuis les commandes (`addons/account/wizard/accrued_orders.py:48-74` : le compte de régularisation doit être de type Actifs courants ou Passifs courants). 4181 (Clients, factures à établir) et 4081 (Fournisseurs) ont un type Recevable/Payable dans le modèle (`addons/l10n_syscohada/data/template/account.account-syscohada.csv:443, 475`) et sont refusés. Il faut soit des sous-comptes dédiés de type courant (numéros à valider par l'expert-comptable), soit des OD manuelles avec extourne sur 4181/4081.
- **Règle** : une seule méthode. Si les écritures différées d'Enterprise sont actives, ne pas passer en plus d'OD manuelle de 477.

### 3.7 Sous-traitance

Un partenaire par sous-traitant, avec NIU et statut. Une position fiscale « Prestataire soumis à retenue » ajoute la retenue sur honoraires (447140) aux factures de services. Contrat, factures et attestation de régime au dossier. Prestataire non résident : TSR (L0), pas L43.

### 3.8 Immobilisations

**EE** (`account_asset`, à confirmer sur la base) : un modèle par famille (compte d'immobilisation, compte d'amortissement 28x, dotation 681x, durée), création depuis la facture fournisseur. Durées : à valider par l'expert-comptable. Reprise : registre existant avec cumuls à la date de bascule. Sans le module : registre tenu hors Odoo et dotations par OD.

### 3.9 Notes de frais

**CE** (`hr_expense`) : la note de frais porte son état et son approbation ; deux modes, à rembourser à l'employé ou payé par la société (`addons/hr_expense/models/hr_expense.py:128-149` pour l'état, 250-256 pour `payment_mode` : `own_account` / `company_account`). La dette envers l'employé va sur le compte fournisseur de son contact, de type `liability_payable` (`addons/hr_expense/models/hr_expense.py:1809-1810`, `addons/account/models/partner.py:548`). Aucun compte de la classe 42 du modèle n'a ce type : sans réglage, la dette tombe en 401100. Proposition : un sous-compte 42 de type « À payer » pour les frais avancés par le personnel ; numéro exact à valider. Analytique « Ligne de métier » sur le domaine `expense`.

### 3.10 Paie

Hors des applications citées. Le lot 5 du dépôt (paie camerounaise) n'est pas commencé et aucun barème n'y est validé. À court terme : une écriture de paie mensuelle par journal « Paie » sur 661x (rémunérations), 664x (charges sociales), 641300 (taxes patronales : CFC part patronale, FNE), 422, 431x et 447210 à 447260 (L67 à L73) ; comptes des taxes patronales à valider (447 retenu, 442 possible). Barèmes IRPP, CNPS, CFC, FNE, RAV, TDL : à valider sur les textes. Outil actuel : à confirmer.

AITE commercialise AITE SI RH (paie Afrique centrale, Odoo 18). S'il sert déjà en interne : instance séparée en 18 avec export mensuel de l'écriture de paie vers le journal Paie de la base 19 (comptes 661x, 664x, 422, 431x, 447210 à 447260), ou portage en 19 à chiffrer.

---

## 4. Analytique

### 4.1 Plans proposés

| Plan | Comptes | Applicabilité | Remplissage |
| --- | --- | --- | --- |
| Ligne de métier (`plans_analytiques.csv`) | LM-INT, LM-DEV, LM-PRD, LM-INF, LM-SEC, LM-RES, LM-LIC, LM-MAT, LM-FOR, LM-DAT, LM-STR (`comptes_analytiques.csv`) | Facultative à l'import ; obligatoire ensuite sur factures (préfixe 70) et factures fournisseurs (préfixe 6) | Modèles de distribution par catégorie de produits |
| Projet (plan natif d'Odoo, `analytic.analytic_plan_projects`) | Compte analytique du projet (champ `account_id`, `addons/project/models/project_project.py:95`) : créé automatiquement quand le projet naît d'une commande de vente (`addons/sale_project/models/sale_order_line.py:187` et 389). Pour un projet créé à la main, le choisir ou le créer dans le champ Compte analytique. Une création automatique par Feuilles de temps (`hr_timesheet`) reste à vérifier sur la base, car le module est absent de la copie. | Facultative | Ligne de commande liée au projet (`addons/sale_project/models/sale_order_line.py:104-124`) |
| Centre de coûts | CC-DIR, CC-COM, CC-TEC, CC-SUP, CC-ADM | Facultative | Notes de frais et frais généraux |

Le suivi par client se fait par le partenaire des écritures : pas de plan « Client ». Les états SYSCOHADA ne lisent pas l'analytique : elle sert au pilotage, jamais à remplacer un compte général.

### 4.2 Mécanismes d'Odoo 19 (CE)

- Plans hiérarchisés, applicabilité par défaut dépendant de la société, règles par domaine : `general`, `invoice`, `bill`, `sale_order`, `purchase_order`, `expense`, avec préfixe de comptes et catégorie de produits (`addons/analytic/models/analytic_plan.py:77-95`, `addons/account/models/account_analytic_plan.py:10-27, 59-75`).
- Distribution en pourcentages sur plusieurs comptes de plusieurs plans (champ JSON `analytic_distribution`).
- Contrôle d'un plan obligatoire à la validation des factures (`addons/account/models/account_move_line.py:3209-3246`) à l'envoi du devis par courriel (`addons/sale/models/sale_order.py:1075`, `action_quotation_send`) et à la confirmation (`sale_order.py:1186`).
- Modèles de distribution selon partenaire, catégorie de partenaire, préfixe de compte, article, catégorie d'article (`addons/account/models/account_analytic_distribution_model.py:9-26`).

### 4.3 Modèles de distribution à créer (à l'écran)

| Condition | Distribution |
| --- | --- |
| Catégorie « Intégration ERP et projets » | 100 % LM-INT |
| Catégorie « Infogérance… » | 100 % LM-INF |
| Catégorie « Licences et abonnements revendus » | 100 % LM-LIC |
| Catégorie « Matériel revendu » | 100 % LM-MAT |
| … une par catégorie de vente | … |
| Préfixe 622, 605, 628, 631 (frais de structure) | 100 % LM-STR, centre CC-ADM |
| Partenaire « Microsoft » (si revente) | 100 % LM-LIC |

### 4.4 Ce qui se remplit seul

| Origine | Ce qui est rempli | Source |
| --- | --- | --- |
| CRM | Rien directement ; l'opportunité est liée au devis (`sale.order.opportunity_id`) | `addons/sale_crm/models/crm_lead.py:10-20` |
| Ventes | Distribution de la ligne de devis par les modèles ; compte du projet ajouté si la vente crée un projet | `addons/sale/models/sale_order_line.py:1250-1260` |
| Projets | Compte analytique du projet ; temps passés si Feuilles de temps (à confirmer) | `addons/project/models/project_project.py:95` |
| Achats | Distribution de la ligne de commande par les modèles | `addons/purchase/models/purchase_order_line.py:380` |
| Notes de frais | Distribution par les modèles, partenaire = contact de l'employé | `addons/hr_expense/models/hr_expense.py:756-761` |

Mise en route : un mois en applicabilité facultative, contrôle des lignes sans ligne de métier, puis passage en « Obligatoire » sur `invoice` et `bill`. Ne pas rendre `sale_order` obligatoire : une commande de la boutique ou d'un abonnement serait bloquée à l'envoi et à la confirmation.

---

## 5. Trésorerie

### 5.1 Journaux et comptes

Préfixes du plan : banques 521, caisses 571, virements internes 585, change 676/776 (`addons/l10n_syscohada/models/template_syscohada.py:21-26`). Le modèle n'a aucun compte 52 : chaque journal de banque crée le sien (`addons/account/models/account_journal.py:918-947`). Modèles : `comptes_tresorerie.csv` puis `journaux_tresorerie.csv`.

| Journal | Code | Type | Compte | Devise | Remarque |
| --- | --- | --- | --- | --- | --- |
| Banque 1 XAF | BQ1 | Banque | 521100 | XAF | Un journal par compte et par devise |
| Banque 1 EUR | BQ1E | Banque | 521110 | EUR | Parité fixe 655,957 |
| Banque 2 XAF | BQ2 | Banque | 521200 | XAF | — |
| Banque 2 USD | BQ2U | Banque | 521210 | USD | Taux flottant, source à documenter |
| Orange Money | OM | Banque | 552100 | XAF | Type Banque : le contrôle ESPECES ne vise que les journaux Espèces |
| MTN Mobile Money | MOMO | Banque | 552200 | XAF | Idem |
| Caisse du siège | CAI | Espèces | 571110 | XAF | Procès-verbal de comptage mensuel |
| Virements internes | — | — | 585 (compte de la société) | — | Un seul compte 585, lettré et soldé chaque mois |

Banques, devises et portefeuilles réels : à confirmer sur la base. Les numéros 521110, 521200… sont une proposition ; la subdivision des 52 hors 521 (522 et suivants, 525 dépôts à terme) est à valider. Écarts de caisse : 658800 et 758800 (le plan crée sinon des comptes 999xxx, `addons/account/models/chart_template.py:891-905`). Carte bancaire pour les abonnements étrangers : journal de type « Carte de crédit » ou paiement depuis la banque ; à décider avec l'expert-comptable.

### 5.2 Paiements en attente

- Le plan crée trois comptes `asset_current` sous 521 : attente bancaire, encaissements et décaissements en attente (`addons/account/models/chart_template.py:872-881, 913-970`).
- Banques avec relevés importés et application Comptabilité : modes de paiement sans compte d'attente ; la facture reste « En paiement » jusqu'au rapprochement (comportement probable d'après `addons/account/models/account_move.py:7424-7428`, à confirmer sur la base).
- Caisse et mobile money sans relevé : compte du journal comme compte de paiements en attente (piège connu, dépôt `CLAUDE.md`).
- Contrôle : solde nul des comptes d'attente à chaque fin de mois. Le contrôle ATTENTE couvre les comptes 471, 585 et 588, le compte d'attente bancaire et le compte de virements internes (dépôt `syscohada_check.py:114-123`). Il ne couvre pas les comptes de paiements en attente (sous 521) : les y ajouter (évolution à valider). Il signale aussi 4711 et 4712 : à restreindre au compte d'attente réel (question 29).

### 5.3 Rapprochement et import de relevés

- **CE** : saisie des lignes de relevé et paramétrage des modèles de rapprochement, lettrage manuel des écritures (hors relevés) (`addons/account/models/account_reconcile_model.py`, `addons/account/models/account_bank_statement_line.py`). Le rapprochement des relevés et l'application des modèles relèvent de l'application Comptabilité d'Enterprise (à confirmer sur la base) ; sans elle, rien ne rapproche les relevés dans Odoo. La source « synchronisation » ou « import » vient d'Enterprise.
- **EE** : synchronisation bancaire ; couverture des banques camerounaises et des opérateurs de mobile money peu probable, à confirmer sur la base. Ne pas la promettre.
- **Méthode retenue** : import de fichiers (CSV ou Excel exportés par chaque banque et chaque opérateur), un gabarit par établissement (date, libellé, référence, montant signé ou débit/crédit, solde). Formats acceptés par l'import d'Enterprise : à confirmer sur la base.
- **Modèles de rapprochement** : pointer « Bank Fees » sur 631800 (Odoo choisit sinon le premier compte de charges, probablement 601100, `addons/account/models/chart_template.py:812-822`) ; un modèle pour les frais de mobile money (631700), un pour les agios, un pour les virements internes (585).
- **Contrôle** : solde comptable de chaque 521xxx, 552xxx = solde du relevé, compte par compte, à chaque fin de mois.

### 5.4 Devises

- Devise fixée sur le journal ; le compte la reprend. Odoo refuse de changer la devise d'un compte mouvementé dans une autre devise (`addons/account/models/account_account.py:1080-1084`).
- Écarts de change réalisés : tous en 676/776 par défaut (`addons/account/models/company.py:133-139`). Le SYSCOHADA révisé distingue 656/756 (créances et dettes commerciales) de 676/776 (financiers). Choix et éventuel reclassement : à valider.
- Clôture : réévaluation des banques en devises ; écarts latents sur créances et dettes en 478/479 et provision pour perte de change selon la règle validée.
- EUR : taux fixe 655,957, aucune mise à jour automatique qui l'écraserait. USD : source (BEAC ou banque) à documenter.

### 5.5 Découverts et crédits

Un découvert est un compte 52 créditeur, reclassé en DR et signalé par BASCULES. Ne jamais utiliser 565 pour un découvert (escompte de crédits ordinaires). Crédit de trésorerie en 561. Dans le modèle d'Odoo, les comptes 561 à 566 sont typés `asset_current` et 564/565 ont le même libellé : types et libellés à corriger (à valider).

### 5.6 Relances

**EE** (`account_followup`, à confirmer sur la base) : trois niveaux alignés sur les conditions de paiement, par exemple J+7 (courriel), J+30 (courriel et appel), J+45 (lettre et blocage des nouvelles commandes). Balance âgée mensuelle. Clients publics : relance par la procédure de mandatement, hors Odoo.

### 5.7 Plan de trésorerie prévisionnel

Deux horizons : 13 semaines (pilotage) et 12 mois (budget).

| Flux | Source dans Odoo 19 | Règle |
| --- | --- | --- |
| Factures clients ouvertes | Échéances (`invoice_date_due`, `date_maturity`) | Échéance corrigée du retard moyen du client |
| Encaissement net | — | TTC − retenues subies (acompte sur CA, honoraires, TVA retenue) selon le client ; taux à valider |
| Commandes restant à facturer | `amount_to_invoice` (`addons/sale/models/sale_order.py:236`) | Selon jalons |
| Abonnements | Prochaine date de facture (EE, à confirmer) | Montant récurrent |
| Opportunités | `expected_revenue`, `probability`, `date_deadline` (`addons/crm/models/crm_lead.py:141-162`) | Pondérées par la probabilité |
| Factures fournisseurs, commandes d'achat | Échéances, `date_planned` | — |
| Salaires | Paie | Nets en fin de mois, impôts et cotisations le mois suivant |
| Impôts | Déclaration I/TVA-IR | Avant le 15 du mois suivant ; TVA calculée sur les encaissements prévus ; solde de l'IS à la DSF selon le centre |
| CNPS | — | Échéance à valider (source CNPS) |

Outil : tableur Odoo d'Enterprise (à confirmer sur la base) ou tableur Excel alimenté par les exports ; petit module AITE plus tard si le besoin se confirme.

### 5.8 Tableau des flux de trésorerie (TFT)

Utiliser le TFT SYSCOHADA du référentiel AITE (ZA à ZH ; contrôle ZH = BT − DT), pas le tableau des flux générique d'Enterprise, qui s'appuie sur des étiquettes que le plan `l10n_syscohada` ne pose pas. Limite connue : virements internes entre comptes d'immobilisations non neutralisés hors du moteur. Une trésorerie non rapprochée (585 non soldé, paiements en attente) fausse BT et DT sans que le contrôle TFT le voie : rapprocher avant d'éditer.

---

## 6. Fiscalité au quotidien

### 6.1 Sources et réserve générale

Règles retenues par le dépôt (skill `fiscalite-cameroun`, d'après les fiches TVA et IS et le formulaire I/TVA-IR de la DGI) :

- TVA 19,25 % (17,5 % + 10 % de CAC) ; exigible à la livraison pour les biens, à l'encaissement pour les services.
- Déclaration I/TVA-IR et paiement avant le 15 du mois suivant.
- Acompte d'IS : 2 % du chiffre d'affaires mensuel au réel (5 % au simplifié), plus CAC.
- IS : 30 %, ou 25 % si le chiffre d'affaires ne dépasse pas 3 milliards, plus 10 % de CAC.
- DSF et solde d'IS : 15 mars (DGE), 15 avril (CIME), 15 mai (CDI).

Changements signalés pour 2026 par des sources tierces, **non vérifiés** (impots.cm inaccessible pendant le relevé) : loi n° 2025/012 du 17/12/2025 (loi de finances 2026) ; circulaire n° 008/MINFI/DGI/LRI/L du 02/03/2026 ; arrêté MINFI du 05/01/2026 désignant les retenants de la TVA et de l'AIR ; retenue sur loyers ramenée de 15 % à 10 % ; TSR imputable ; TVA exigible à l'encaissement d'un acompte ; présence économique significative des entreprises numériques non résidentes. **Tous à valider par l'expert-comptable sur les textes avant paramétrage.**

### 6.2 TVA

| Opération | Taxe | Compte | Ligne | Statut |
| --- | --- | --- | --- | --- |
| Vente de services | S (encaissement) | 443800 puis 443200 | L10 | Socle, ou création manuelle |
| Vente de biens (matériel) | 19.25% | 443100 | L10 | Livrée par `l10n_cm` |
| Export de services ou de biens | 0% EX | — | L13 | Territorialité à valider |
| Achat de biens | 19.25% G | 445200 | L18 | Livrée |
| Achat de services | 19.25% S | 445200 (445400 avec le socle si la taxe n'a jamais servi) | L19 | Sur une base utilisée, créer une nouvelle taxe vers 445400 plutôt que modifier l'ancienne |
| Immobilisations | 19,25 % I | 445100 | L18 | Socle |
| TVA payée en douane (importations) | Taxe d'achat « 19,25 % importation », étiquettes +CM_20 et −CM_20, posée sur la facture du transitaire ou de la douane, base = valeur en douane | 445200 | L20 | À créer, assiette à valider |
| Services de fournisseurs étrangers | Autoliquidation | 445400 / 447161 | L21, L38 | À valider |
| TVA retenue par un client | Écart de règlement vers un compte dédié (à créer, à valider) | — | L24 | Saisie en attendant un calcul par compte |

Taxes déjà utilisées : suppression interdite, archivage seulement ; une modification des lignes de répartition ne vaut que pour l'avenir (`addons/account/models/account_tax.py:5153-5156, 403-430`). D'où la règle : nouvelles taxes à une date de coupure (01/01/2027), anciennes archivées.

Paiements en espèces de plus de 100 000 FCFA : TVA non déductible selon la fiche TVA de la DGI ; article du CGI, appréciation par facture ou par paiement, assimilation de la monnaie électronique : à valider. Le contrôle ESPECES du socle ne voit que les paiements fournisseurs des journaux Espèces.

### 6.3 Retenues

| Retenue | Sens | Compte | Ligne | Taux dans le dépôt | Statut |
| --- | --- | --- | --- | --- | --- |
| TSR (prestataires étrangers) | Opérée | 447120 | L0 | 15 % | À valider |
| Précompte sur loyers | Opérée | 447130 | L42 | 15 % | À valider (10 % signalé en 2026) |
| Retenue sur honoraires | Opérée | 447140 | L43 | 5 % | À valider |
| Acompte sur CA retenu par le client | Subie | 449220 | L45 | 2 % | À valider ; arrêté du 05/01/2026 à lire |
| Retenue sur honoraires subie | Subie | 449240 | L48 | 5 % | À valider |
| Précompte sur achats | Subi | 449210 | L46 | 2 % | À valider ; seulement si un fournisseur le facture |
| TVA retenue par un client public ou désigné | Subie | à créer | L24 | — | À valider |

Les retenues du socle sont des taxes négatives, **inactives** tant que leur taux n'est pas validé. Décalage : une taxe sur facture retient à la date de facture, le client retient au paiement. Pour les retenues subies, préférer l'écart de règlement au paiement, justifié par l'attestation de retenue (ARS). Un module de retenue au paiement d'Odoo existe peut-être (`l10n_account_withholding_tax`) : à confirmer sur la base.

### 6.4 Acompte et IS

- Acompte mensuel (L50) : base, CAC et imputation des retenues subies (L45 à L48) à valider. Écriture : débit 449250, crédit 441100 pour le montant de L54.
- IS annuel : taux selon le chiffre d'affaires, minimum de perception à valider ; écriture 891100 / 441000, imputation de 449250 et des 4492xx sur 441000 ; 441100 reste réservé aux acomptes mensuels (socle). Passage au résultat fiscal hors Odoo tant que le lot 3 n'est pas livré.
- IRCM sur dividendes : taux à valider.

### 6.5 Déclaration I/TVA-IR

| Partie | Outil cible |
| --- | --- |
| L10 à L35 (TVA) | Rapport « Déclaration TVA » d'Enterprise (définition `l10n_cm`, report L35 → L17 natif) ; saisies L11, L24 à L27, L34 en valeurs externes |
| L0 à L9, L36 à L80 | Module AITE porté en 19.0, limité à ces lignes ; sinon tableur du comptable, puis rapport `account.report` personnalisé (moteurs `account_codes`, `aggregation`, `external`, `addons/account/models/account_report.py:587-596`) à vérifier sur la base |
| Liquidation | Une seule chaîne (décision D5). Option conseillée : clôture de TVA d'Enterprise pour L10 à L35, écriture AITE limitée à l'acompte (L54). Avant toute clôture de TVA d'Enterprise, décocher « Écriture de clôture de taxe » (`use_in_tax_closing`, coché par défaut sur toute ligne « tax » portée par un compte de bilan, `addons/account/models/account_tax.py:5370-5390`) sur les lignes de répartition des taxes de retenue et de précompte, et sur la ligne 447161 de l'autoliquidation. Recette sur copie : après la clôture, 447xxx et 449xxx sont inchangés et 4441 = L32. Comportement exact de la clôture d'Enterprise : à vérifier sur la base. |
| Crédit de TVA | Les groupes de taxes de `l10n_cm` mettent la créance sur 4445 (remboursement) ; la convention AITE est 4449 (crédit à reporter). Passer le compte de créance des groupes à 4449 : à valider |

Défauts connus du module AITE à corriger lors du portage (dépôt `ROADMAP.md`, lot 2) : L17 non recalculé selon l'ordre de saisie ; extourne non déduite des lignes de retenue (lire le solde net du compte) ; liquidation refusée hors de la société de la déclaration.

### 6.6 Calendrier

| Échéance | Obligation | Source |
| --- | --- | --- |
| Avant le 15 du mois M+1 | Déclaration I/TVA-IR et paiement : TVA, acompte, retenues, impôts sur salaires | DGI (skill du dépôt) |
| 15 mars, 15 avril ou 15 mai | DSF et solde de l'IS selon le centre | DGI (skill du dépôt) ; centre d'AITE à confirmer |
| À valider | Patente, droits d'enregistrement, CNPS | Aucune source dans le dépôt |

Dans Odoo : activités planifiées récurrentes (rappel le 5, le 10 et le 14 de chaque mois) ; périodicité mensuelle de la déclaration de TVA d'Enterprise (à confirmer sur la base).

---

## 7. Reprise de l'existant

### 7.1 Faits qui cadrent les choix

- Le champ « Pack » est en lecture seule dès qu'une écriture existe ; seul « Recharger » reste visible (`addons/account/views/res_config_settings_views.xml:33-38`, `addons/account/models/company.py:992-996`). Charger un autre plan par le code empile les deux plans (`addons/account/models/chart_template.py:232-257`) : à proscrire.
- Le socle AITE ne s'applique qu'aux sociétés au plan « cm » (taxes) ou SYSCOHADA (comptes) (dépôt `res_company.py:119-132`).
- Sur une base utilisée, le socle réécrit 45 libellés sans condition, change des types de comptes quand Odoo le permet, crée 32 sous-comptes et des taxes, mais ne reclasse aucune écriture passée.
- Une écriture datée dans une période verrouillée est **reportée** à une date ultérieure, pas refusée (`addons/account/models/company.py:76-102`) : passer les reclassements avant de verrouiller.
- Une société créée comme succursale (`parent_id`) partage le plan de sa mère (`addons/account/models/chart_template.py:247-251`) : une nouvelle société doit être sans société mère.
- Au chargement du plan dans une nouvelle société, Odoo pose « 19.25% » et « 19.25% G » sur les articles partagés (`addons/account/models/chart_template.py:761-781`) : à reprendre article par article.

### 7.2 Scénarios comparés

| Critère | A. Correction en place | B. Nouvelle société au 01/01/2027 | C1. Correction en place avec coupure au 01/01/2027 | C2. Nouvelle société + ancienne en extinction |
| --- | --- | --- | --- | --- |
| Condition | Pack « cm » (ou « syscohada » rechargeable en « cm » sur copie) | Licence multi-société (à vérifier) | Pack « cm » | Licence multi-société |
| Historique | Continu | Ancienne société en lecture | Continu | Ancienne société en lecture |
| Taxes mouvementées | Gardent leurs anciens comptes | Neuves (« 19.25% S » en 445400) | Nouvelles taxes au 01/01, anciennes archivées | Neuves |
| Reclassements | Nombreux, sur l'exercice ouvert | Aucun : ouverture par soldes | Limités aux OD d'inventaire 2026 | Aucun |
| Reprise des tiers, articles, abonnements, stocks | Aucune | Complète | Aucune | Soldes seulement ; créances 2026 encaissées dans l'ancienne |
| TVA en attente des services non encaissés | Sans objet | Factures 2026 ouvertes reprises en solde TTC sur 411, sans taxe. Ne mettre en 443800 que la TVA qui n'a encore jamais été déclarée | Factures 2026 restent sous l'ancien régime ; règle de bascule à valider | Réglée (encaissement dans l'ancienne) |
| Déclaration I/TVA-IR | Une société | Une société | Une société | Deux sociétés à additionner à la main pendant l'extinction (un seul NIU) |
| Risque principal | Exercice 2026 mélangé | Volume de reprise, erreurs de société | Coexistence de deux jeux de taxes en 2026-2027 | Double tenue |

### 7.3 Recommandation

1. **Pack « cm »** : C1. Coupure au 01/01/2027, nouvelles taxes et catégories pour 2027, OD d'inventaire 2026 validées par l'expert-comptable, pas de retouche de la saisie 2026.
2. **Pack « syscohada »** : tester sur une copie le rechargement en « cm » (même parent, même fichier de comptes) ; s'il est propre, C1 ; sinon B.
3. **Autre plan (générique ou autre pays)** : B, ou C2 si les créances de services ouvertes au 31/12/2026 sont nombreuses.

Le choix final dépend des exports 3, 5, 6 et 19 et de la licence (D2, D3).

Les exercices clos ne sont pas retraités dans Odoo ; seuls l'exercice 2026 (OD d'inventaire) et la coupure 2027 sont traités (décision D6).

### 7.4 Étapes (C1, la plus probable si le Pack est « cm »)

1. Sauvegarde complète (base et filestore) ; copie de test neutralisée (courriels sortants et paiements coupés) ; `ANALYZE` après copie (piège des statistiques PostgreSQL, dépôt `CLAUDE.md`).
2. Portage 19.0 et suite de tests verte sur une base Enterprise 19 de test.
3. Export du plan comptable (sauvegarde des libellés personnalisés que le socle réécrira).
4. Installation du socle sur la copie ; lecture du journal (« AITE SYSCOHADA : … non modifié »).
5. Imports des modèles (README) ; nouvelles taxes au 01/01/2027 ; archivage des anciennes à la date de coupure.
6. Table des OD de clôture 2026 validée par l'expert-comptable (services passés en 701, 477, 476, stock 382 vers 311 ; aucune OD sur la TVA des factures 2026 déjà déclarées. Régularisation éventuelle (L24 ou L27) seulement selon la règle de bascule validée par écrit (question 21)).
7. Contrôles avant/après (section 7.6).
8. Répétition complète sur une nouvelle copie avec les données au 30/11.
9. Production un week-end ; verrouillage des ventes et des achats au 31/12/2026 une fois les factures de décembre passées.
10. Verrouillage global après l'arrêté, verrouillage définitif après le dépôt de la DSF.

### 7.5 Étapes (B)

0. Sauvegarde complète (base et filestore) ; copie neutralisée ; `ANALYZE` après copie.
1. Contrat renouvelé et multi-société vérifiés avant le 25/12/2026.
2. Table de correspondance des comptes (ancien plan vers « cm ») validée.
3. Répétition sur copie avec les données au 30/11.
4. Gel des devis et commandes au 31/12.
5. Création de la société sans société mère, pays Cameroun, plan « cm », socle AITE.
6. Journaux, banques, catégories, articles (comptes et taxes par société), analytique.
7. Ouverture provisoire au 01/01/2027 : tiers par pièce (factures 2026 ouvertes reprises en solde TTC sur 411, sans taxe ; ne mettre en 443800 que la TVA qui n'a encore jamais été déclarée), trésorerie, stocks au coût unitaire de l'inventaire, 477. Journal « À nouveaux » ; contrôle : 999999 à zéro (compte d'équilibrage créé par Odoo, `addons/account/models/company.py:864-940`).
8. Abonnements recréés avec une prochaine facture postérieure à la dernière période facturée.
9. Ouverture complémentaire après validation de la balance 2026 (immobilisations, provisions, capitaux propres, résultat en instance d'affectation).
10. Verrouillage définitif de l'ancienne société au 31/12/2026 après la DSF.

### 7.6 Contrôles avant et après

| Contrôle | Méthode | Tolérance |
| --- | --- | --- |
| Balance générale par compte | Export avant / après, différence par compte | Nulle, ou justifiée par une OD documentée |
| Clients et fournisseurs | Balance âgée = soldes 411 et 401 ; total des factures ouvertes reprises = solde | Nulle |
| Trésorerie | Solde de chaque banque et portefeuille = relevé | Nulle |
| Stock | Valeur du rapport de valorisation = solde 31 | Nulle |
| Immobilisations | Valeur nette du registre = 2x − 28x − 29x | Nulle |
| TVA | Rapport de TVA du dernier mois avant / après | Nulle |
| Intangibilité | Bilan d'ouverture 2027 = bilan de clôture 2026 | Nulle |
| Contrôles AITE | 9 contrôles ; invariants BZ = DZ, XI = CJ, ZH = BT − DT | Aucun « Bloquant » |
| Recette | États 2025 comparés aux états validés ; trois déclarations déposées reproduites | Écart nul ou expliqué |

---

## 8. Organisation et contrôles mensuels

### 8.1 Clôture mensuelle (avant le 10 du mois suivant)

1. Toutes les factures du mois validées ; aucun brouillon (contrôle BROUILLONS).
2. Relevés de toutes les banques et de tous les portefeuilles importés et rapprochés ; solde comptable = relevé.
3. Procès-verbal de comptage de chaque caisse ; écart passé en 658800 ou 758800.
4. Comptes 585 et d'attente bancaire soldés ; comptes de paiements en attente justifiés ; 471 justifié ligne à ligne.
5. Lettrage 411, 401, 481, 4191.
6. Balance âgée ; relances.
7. Attestations de retenue reçues rapprochées des règlements ; retenues subies comptabilisées.
8. Écritures de paie (si hors Odoo) et de charges sociales.
9. Contrôles AITE : aucun « Bloquant » accepté (CAISSE, EQUILIBRE…), « Alertes » justifiées (ATTENTE, ESPECES, BASCULES).
10. Déclaration I/TVA-IR : calculer, comparer au grand livre, liquider, valider, payer avant le 15.
11. Date de verrouillage des déclarations fiscales posée sur le mois déclaré.
12. Plan de trésorerie à 13 semaines mis à jour ; marge par ligne de métier.

### 8.2 Droits

Groupes d'Odoo 19 Community (`addons/account/security/account_security.xml:50-80`). Seuls Facturation et Administrateur sont proposés comme rôles ; Lecture seule et Fonctions comptables complètes sont des cases techniques (mode développeur ou Paramètres > Groupes), et l'Administrateur ne les reçoit pas automatiquement en Community. Profils Lecture seule et Comptable disponibles comme rôles seulement avec l'application Comptabilité (`accountant`) ; sans elle, Facturation ou Administrateur. Les rôles ajoutés par l'application Comptabilité d'Enterprise sont à vérifier sur la base.

| Profil | Groupe | Qui |
| --- | --- | --- |
| Facturation | Facturation (`group_account_invoice`) | Commerciaux, chefs de projet |
| Basique | Basique (`group_account_basic`, implique Facturation ; case technique en Community) | Selon besoin (rapprochement simple) |
| Lecture comptable | Lecture seule (`group_account_readonly`) | DG, DT |
| Comptable | Fonctions comptables complètes (`group_account_user`) | Comptable |
| Administrateur comptable | Administrateur (`group_account_manager`) | Comptable principal, DT (dépannage) |
| Expert-comptable | Utilisateur dédié (« Conseiller ») ou lecture seule ; rôle exact sur Enterprise à confirmer sur la base | Cabinet |

Séparation : qui saisit un paiement ne valide pas le rapprochement ; qui valide la déclaration n'est pas seul à la payer. Pas d'utilisateur partagé.

### 8.3 Verrouillage des périodes

Champs de la société (`addons/account/models/company.py:58-112`) : verrouillage global, des déclarations fiscales (posé aussi par la clôture de TVA d'Enterprise), des ventes, des achats, et verrouillage définitif irréversible. Exceptions tracées possibles (`addons/account/models/account_lock_exception.py`), sauf sur le verrouillage définitif. Écran de saisie : Enterprise, à confirmer sur la base.

| Moment | Verrou |
| --- | --- |
| Après la déclaration du mois M | Déclarations fiscales au dernier jour de M |
| Après la clôture mensuelle | Ventes et achats au dernier jour de M |
| Après l'arrêté annuel | Global au 31/12 |
| Après le dépôt de la DSF | Définitif au 31/12 |

Hachage des pièces (journaux de ventes) : `restrict_mode_hash_table` (`addons/account/models/account_journal.py:145`) ; à activer à la coupure, il empêche ensuite certaines fusions de comptes.

### 8.4 Revue trimestrielle avec l'expert-comptable

Balance, états SYSCOHADA intermédiaires, contrôles, écarts de TVA, retenues, produits et charges constatés d'avance, immobilisations, stock.

---

## 9. Feuille de route

| Semaine | Travaux | Livrable | Responsable |
| --- | --- | --- | --- |
| S47 (16-22/11) | Envoi du présent plan ; réponses aux questions 1 à 6 de la section 10 | Hébergement et contrat confirmés | DG, DT |
| S48 (23-29/11) | Exports 1 à 26, pièces hors Odoo ; sauvegarde et première copie neutralisée | Dossier d'exports, copie de test | Comptable, DT |
| S49 (30/11-06/12) | Diagnostic : plan réel, taxes utilisées, montants mal classés sur 4 ans, trésorerie non rapprochée | Note de diagnostic chiffrée | AITE (équipe projet) |
| S49-S51 | Portage du socle, extraction de la déclaration, correction des défauts du lot 2, tests (13 à 21 jours-homme : deux développeurs ou trois semaines) | Modules 19.0, suite verte | DT + un développeur nommé |
| S50 (07-13/12) | Décisions D3 à D5 ; table de correspondance ; natures fiscales | Procès-verbal de décisions | DG, expert-comptable |
| S51 (14-20/12) | Paramétrage sur copie : imports, taxes, analytique, journaux, modèles de rapprochement | Copie paramétrée | Comptable, DT |
| S51 | Renouvellement du contrat Enterprise | Contrat | DG |
| S52 (21-27/12) | Répétition générale de la bascule sur copie ; formation des utilisateurs | Rapport de répétition, contrôles avant/après | DT, comptable |
| S52 | Recette du lot 2 sur la copie : les trois dernières déclarations déposées (pièces hors Odoo n° 1) reproduites ligne par ligne par le module porté ; écarts expliqués | Procès-verbal de recette | Comptable, DT |
| S53-S1 (28/12-10/01) | Bascule au 01/01/2027 ; ouverture provisoire (B) ou coupure (C1) | Base de production 2027 | DT, comptable |
| S1-S2 (avant le 15/01/2027) | Déclaration de décembre 2026 selon la méthode actuelle du comptable, depuis les écritures 2026 (anciennes taxes) ; TVA des factures de services 2026 non encaissées traitée selon la règle de bascule validée (question 21) | Déclaration déposée | Comptable, expert-comptable |
| S2-S7 (janvier-février 2027) | Premier mois complet ; déclaration de janvier depuis Odoo, double calcul | Déclaration déposée avant le 15/02/2027 | Comptable, expert-comptable |
| Février-mai 2027 | Arrêté 2026, DSF, à-nouveaux définitifs, verrouillage | DSF déposée | Expert-comptable |
| Mars-juin 2027 | Rapports SYSCOHADA Enterprise comparés au moteur ; plan de trésorerie ; budget par ligne de métier | Recette du lot 1 (états) | DT |

### Risques

| Risque | Probabilité | Effet | Parade |
| --- | --- | --- | --- |
| Base sur Odoo Online | Inconnue jusqu'à D1 (le site public est probablement auto-hébergé, mais la base comptable peut être une autre instance) | Aucun module AITE | Aucun travail de portage engagé avant la confirmation écrite de D1 ; paramétrage manuel ; migration vers Odoo.sh ou serveur propre à chiffrer |
| Expiration du 25/12/2026 non traitée | Moyenne | Base bloquée en pleine bascule | Renouvellement constaté sur la base avant le 18/12 ; sinon report de la bascule au 01/02/2027 ; jours fériés du 25/12 et du 01/01 exclus du planning de bascule |
| Licence sans multi-société | À confirmer | Scénario B impossible | C1, ou avenant au contrat |
| Taux de retenues non validés | Élevée | Taxes inactives, saisies manuelles | Validation écrite de l'expert-comptable sur la loi de finances 2026 |
| Portage plus long que prévu | Élevée | Pas de déclaration AITE en janvier | Déclaration de janvier au tableur, module en février |
| Rapports Enterprise AITE jamais exécutés | Certaine | Écarts non mesurés | Comparaison au moteur sur chaque exercice clos |
| Analytique obligatoire trop tôt | Moyenne | Factures bloquées (boutique, abonnements) | Facultative un mois, modèles de distribution d'abord |
| Libellés personnalisés écrasés par le socle | Moyenne | Perte de libellés | Export du plan avant installation |
| Double liquidation de TVA | Moyenne | TVA comptée deux fois | Décision D5 |

---

## 10. Questions ouvertes à trancher

### Direction d'AITE

1. Hébergement exact de la base, URL, qui administre le serveur ? Le site et la base comptable sont-ils la même instance ?
2. Contrat Enterprise : formule, nombre d'utilisateurs, multi-société, modules personnalisés, renouvellement avant le 25/12/2026 ? AITE est-elle partenaire Odoo (licence interne) ? AITE a-t-elle un accès partenaire au code source d'Odoo Enterprise 19 ?
3. Applications installées : Ventes, Comptabilité, Abonnements, Projet (avec l'option Jalons), Feuilles de temps, Notes de frais, Paie, Site et boutique, Immobilisations, Relances ?
4. Préférence : garder l'historique dans la même société (C1) ou repartir au 01/01/2027 (B, C2) ?
5. Catalogue de référence : pourquoi AITE Courrier et AITE GMAO manquent à la boutique et AITE School, SUP, Facture avec IR, Point de Vente n'apparaissent pas dans le référentiel interne ? Les prix publiés sont-ils HT ou TTC, uniques ou périodiques ?
6. Lignes de métier à suivre et niveau de détail (projet, client, commercial) ?
7. Les consultants saisissent-ils des temps ? Les projets sont-ils facturés par jalons ?
8. Contrats d'infogérance et de licences : mensuels ou annuels d'avance ? Combien en cours ?
9. Matériel : stock physique ou achat à la commande ? Importations ? Fournisseur des kits et abonnements Starlink ?
10. Banques, devises, cartes, portefeuilles Orange Money et MTN MoMo marchands, caisses ?
11. Outil de paie actuel (AITE SI RH ou autre), version d'Odoo, nombre de salariés ?

### Comptable d'AITE

12. Plan comptable actuel (Pack) et version de départ de la base ; comptes ou taxes créés à la main ?
13. Comment sont aujourd'hui comptabilisés : TVA des prestations (facture ou encaissement), retenues subies et opérées, acomptes clients, frais bancaires, paiements en devises, écarts de change ?
14. Relevés importés et rapprochés depuis 4 ans ? Soldes non justifiés sur 585, 471, 521xxx d'attente, 999 ?
15. Factures émises depuis Odoo ou depuis la plateforme de facturation de la DGI ?
16. Paiements fournisseurs en espèces ou en monnaie électronique au-delà de 100 000 FCFA ?
17. Exercices clos et DSF déposées ; dates de verrouillage déjà posées ; journaux scellés ?

### Expert-comptable

18. Nature des licences revendues : marchandises (601/701), services (605700 ou 632700 puis 706) ou commission (707200) ?
19. Produits packagés AITE : 706 ou 707600 ? Coûts de développement immobilisables ?
20. Pose : 705 ou 706 ? Ventilation d'un prix global matériel et pose ?
21. TVA des services à l'encaissement : article du CGI, traitement des acomptes (loi de finances 2026), règle de bascule pour les factures ouvertes au 31/12/2026 ?
22. Autoliquidation et TSR sur Microsoft, Odoo SA, nuage : applicables ? Taux, assiette, convention fiscale, paiement brut ou net ?
23. Taux 2026 des retenues : loyers (15 % ou 10 %), honoraires, acompte sur CA, TVA retenue par les clients publics et désignés (arrêté du 05/01/2026) ?
24. Base et CAC de l'acompte d'IS ; imputation des retenues subies ; taux d'IS applicable et minimum de perception ?
25. Compte de créance de TVA des groupes de taxes : 4449 (crédit à reporter) au lieu de 4445 ?
26. Écarts de change : 656/756 pour les créances et dettes, 676/776 pour la trésorerie ? Écarts de conversion 478/479 ?
27. Comptes de stock du matériel : 311/6011/6031 au lieu de 382/6021/6032 ? Valorisation périodique ou permanente, méthode de coût ?
28. Compte de personnel « à payer » pour les notes de frais ; frais refacturés en débours ou en 707800 ?
29. Compte d'attente réel dans 471 (pour limiter le contrôle ATTENTE) ; subdivision des 52 ; types des 561 à 566 ?
30. Durées d'amortissement et seuil d'immobilisation ; traitement de la dette d'immobilisation (481) ?
31. Territorialité des prestations aux clients étrangers ; régime de TVA des organismes internationaux (CAFRAD) ?
32. Patente, droits d'enregistrement, échéance CNPS : textes et calendrier ?

---

## Annexe — Sources du constat de la synthèse

| Point | Sources |
| --- | --- |
| Hébergement | Site aite-consulting.com : Odoo `19.0+e-20260924`, nginx 1.24 sous Ubuntu, adresse 51.68.227.125 |
| Comptes par défaut | `addons/l10n_syscohada/models/template_syscohada.py:29-30` |
| Taxe de vente par défaut | `addons/l10n_cm/data/template/account.tax-cm.csv:2-5` |
| Fournisseurs étrangers | `addons/l10n_cm/data/template/account.fiscal.position-cm.csv:3` |
| Stock | `addons/l10n_cm/models/template_cm.py:23-36` |
| Application | `addons/account/security/account_security.xml:5-37` (Facturation, `account_accountant`, `accountant`) |

---

*Sources principales : relevé du 16/11/2026 des sources d'Odoo 19 Community (`/home/user/work/odoo19`) et du dépôt AITE SYSCOHADA (guide, ROADMAP, skills `fiscalite-cameroun` et `dsf-classeur`) ; site public aite-consulting.com. Les sources d'Odoo Enterprise et la documentation officielle n'étaient pas consultables pendant le relevé : chaque fonction Enterprise est à confirmer sur la base.*
