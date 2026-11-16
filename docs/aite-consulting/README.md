# Modèles d'import pour la base Odoo 19 d'AITE Consulting

Ces fichiers accompagnent le plan `structuration-comptable-tresorerie.md`. Ce sont des **modèles** : codes, libellés et choix de comptes sont à relire avec l'expert-comptable avant tout import. Ils ne remplacent pas le paramétrage du socle AITE (taxes, sous-comptes, contrôles), qui demande des modules Python portés en 19.0.

## Prérequis

1. **Copie de test d'abord.** Jamais d'import direct en production. Sauvegarde (base et filestore) avant chaque import.
2. **Une seule société active** dans le sélecteur de sociétés. Les comptes des catégories, l'applicabilité par défaut des plans analytiques et les comptes de trésorerie dépendent de la société : l'import les écrit pour la société active.
3. **Plan « cm » chargé** (Pack « SYSCOHADA pour Sociétés »). Les codes utilisés (706100, 621000, 311100…) sont ceux du modèle `l10n_syscohada` d'Odoo 19, complétés à six chiffres au chargement (`addons/account/models/chart_template.py:542-546`). Sur une base de 4 ans, vérifier chaque code dans l'export du plan comptable avant l'import : à confirmer sur la base.
4. **Devises EUR et USD actives** (Comptabilité > Configuration > Devises) avant `comptes_tresorerie.csv`. Taux EUR fixe : 655,957 XAF.
5. **Application Inventaire installée** pour les colonnes de stock de `categories_produits.csv` (`property_valuation`, `property_cost_method`, `property_stock_valuation_account_id`, `account_stock_variation_id` viennent de `stock_account`, `addons/stock_account/models/product.py:720-766`). Sans elle, supprimer ces quatre colonnes.
6. **Ventes et Achats installés** pour les lignes `sale_order` et `purchase_order` de `plans_analytiques.csv`. Sinon, supprimer ces lignes. Si l'application Notes de frais est installée, ajouter une ligne `expense`.
7. **Socle AITE installé ou non** : s'il l'est, 552100 et 552200 existent déjà ; retirer ces deux lignes de `comptes_tresorerie.csv`.
8. **Fichiers en UTF-8, séparateur virgule, guillemets doubles.** À l'écran d'import, cocher « Utiliser la première ligne comme en-tête ».
9. **Comptabilité analytique activée** : Comptabilité > Configuration > Paramètres > Analytique, cocher « Comptabilité analytique » (groupe `analytic.group_analytic_accounting`, `addons/analytic/models/res_config_settings.py:10`), sinon les menus des imports 4 et 5 sont masqués (`addons/account/views/account_menuitem.xml:65-68`).
10. **Droits de l'utilisateur qui importe** : sans l'application Comptabilité (`accountant`), lui donner en mode développeur le groupe « Afficher les fonctionnalités de comptabilité - Lecture seule » (Paramètres > Utilisateurs & Sociétés > Groupes), sinon le menu Plan comptable est masqué (`addons/account/views/account_menuitem.xml:46-51`).

## Ordre d'import

| Ordre | Fichier | Modèle Odoo | Écran (vue liste, menu engrenage > Importer des enregistrements) |
| --- | --- | --- | --- |
| 1 | `comptes_tresorerie.csv` | `account.account` | Comptabilité > Configuration > Comptabilité > Plan comptable |
| 2 | `journaux_tresorerie.csv` | `account.journal` | Comptabilité > Configuration > Comptabilité > Journaux |
| 3 | `categories_produits.csv` | `product.category` | Comptabilité > Configuration > Facturation > Catégories de produits (ou Inventaire > Configuration) |
| 4 | `plans_analytiques.csv` | `account.analytic.plan` | Comptabilité > Configuration > Comptabilité analytique > Dimensions analytiques |
| 5 | `comptes_analytiques.csv` | `account.analytic.account` | Comptabilité > Configuration > Comptabilité analytique > Comptes analytiques |

Les libellés de menus sont ceux de la version française ; ils sont à confirmer sur la base (sur une base sans l'application Comptabilité, le menu racine s'appelle Facturation). Ce sont les menus d'Odoo 19 Community ; réorganisation éventuelle par `accountant` à vérifier sur la base.

## Syntaxe des colonnes

- **Comptes par code** (`property_account_income_categ_id`, `default_account_id`, `profit_account_id`…) : la cellule contient le code seul, par exemple `706100`. L'import cherche la valeur par `name_search(name=valeur, operator='=')` (`odoo/addons/base/models/ir_fields.py:556`), et la recherche d'un compte retient `code =like '706100%'` ou le nom exact (`addons/account/models/account_account.py:864-876`). Le nom affiché « 706100 Services vendus dans la région » marche aussi : seul le premier mot sert de code. Toujours écrire les six chiffres : « 7061 » trouverait plusieurs comptes.
- **Identifiants externes** (`id`, `parent_id/id`, `plan_id/id`) : écrits en entier, `__import__.aite_…`. Le préfixe `__import__` est celui que l'import donne aux identifiants sans module ; l'écrire évite toute ambiguïté. Un second import du même fichier **met à jour** les enregistrements au lieu d'en créer de nouveaux. Exception : les lignes d'applicabilité (`applicability_ids/...`) sont recréées à chaque import (`odoo/addons/base/models/ir_fields.py:730-749`). Ne pas réimporter `plans_analytiques.csv` ; pour le rejouer, supprimer d'abord les règles du plan à l'écran, ou ajouter une colonne `applicability_ids/id` avec un identifiant par règle (par exemple `__import__.aite_appl_metier_invoice`) et vérifier sur la copie de test que la mise à jour fonctionne.
- **Listes de choix** (`account_type`, `type`, `property_valuation`, `default_applicability`, `business_domain`…) : valeur technique (`asset_cash`, `bank`, `periodic`, `optional`, `invoice`). L'import accepte la valeur technique ou le libellé (`odoo/addons/base/models/ir_fields.py:458-475`).
- **Lignes d'applicabilité** (`applicability_ids/...`) : une ligne par règle, les colonnes du plan laissées vides sous la première ligne du plan.
- **Devises** (`currency_id`) : code ISO (`EUR`, `USD`) ; vide = XAF, devise de la société.

## Après l'import (à la main)

1. **Journaux** : saisir le numéro de compte bancaire (RIB) dans chaque journal de banque. Dans l'onglet des paiements entrants et sortants des journaux Orange Money, MTN Mobile Money et Caisse, mettre le compte du journal comme compte de paiements en attente (sans relevé, les paiements restent sinon sur un compte d'attente). Vérifier que le journal de banque créé par le plan (BNK1) n'est pas un doublon : le renommer plutôt que d'en garder deux.
2. **Compte 311100** : son libellé du modèle est « Biens A1 » ; le renommer « Marchandises, matériel informatique » (libellé à valider par l'expert-comptable).
3. **Modèles de répartition analytique** (Comptabilité > Configuration > Comptabilité analytique > Modèles de répartition analytique) : un modèle par catégorie de produits vers son compte « LM-… ». La distribution est un champ JSON qui ne s'importe pas proprement par CSV : la saisir à l'écran.
4. **Applicabilité** : passer `invoice` (préfixe 70) puis `bill` (préfixe 6) à « Obligatoire » seulement quand les modèles de distribution remplissent tout seuls la ligne de métier, après un mois de test. Ne pas rendre obligatoire `sale_order` : une commande de la boutique en ligne ou d'un abonnement serait bloquée à l'envoi et à la confirmation.
5. **Comptes analytiques partagés** : en cas de nouvelle société au 1er janvier (scénario B), vider le champ Société des comptes analytiques pour les partager.

## Limites

- Les sources du cœur de l'ORM et des modules `product` et `stock` ne sont pas dans la copie d'Odoo 19 consultée : la gestion des identifiants `__import__` et le champ `parent_id` des catégories (utilisé par `addons/account/models/product.py:82-93`) suivent le comportement standard d'Odoo, à vérifier sur la copie de test.
- Choix de comptes non tranchés (voir le plan, section 3) : licences revendues (706100/605700 par défaut ici, 701100/601100 ou 707200 possibles), produits packagés (706100 ou 707600), installation (706100 ou 705100), frais refacturés (707800 ou débours), sous-traitance (621000 ou 632700). Tous **à valider**.
