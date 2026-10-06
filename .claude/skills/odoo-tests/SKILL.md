---
name: odoo-tests
description: Lance les tests automatiques des modules AITE SYSCOHADA sur une base Odoo 18 et analyse les échecs. À utiliser après toute modification de code, de données, de vues ou du référentiel, et avant de déclarer une tâche terminée.
---

# Lancer et lire les tests

1. Vérifier que PostgreSQL tourne (`pg_isready`) et que `odoo.conf` existe à la racine (sinon `scripts/setup_dev.sh`).
2. Base de développement : `aite_dev`. Si elle n'existe pas, la créer :
   `../venv/bin/python ../odoo18/odoo-bin -c odoo.conf -d aite_dev -i aite_syscohada_community --stop-after-init`
3. Lancer les tests des modules touchés ; mettre à jour le socle relance aussi les modules qui en dépendent :
   `scripts/run_tests.sh aite_dev <modules séparés par des virgules> [étiquettes]`
   - Suite complète : `scripts/run_tests.sh aite_dev aite_syscohada_base,aite_syscohada_mis,aite_syscohada_community`
   - Un test : étiquette `/module:Classe.methode`
   - Tests Enterprise (instance Enterprise seulement) : module `aite_syscohada_reports`, étiquette `aite_syscohada_enterprise`
4. Lire le résumé affiché, puis le journal indiqué. Pour un échec : `grep -n -A30 "FAIL:" <journal>` donne l'assertion et la ligne.

## Règles

- Résultat de référence : 62 tests, 0 échec (un test ignoré sans `aite_syscohada_reports`).
- Ne jamais corriger un montant attendu pour faire passer un test sans refaire le calcul à la main et l'écrire en commentaire.
- Après une correction : relancer le test isolé, puis toute la suite.
- Un nouveau comportement s'accompagne d'un nouveau test, avec l'étiquette `aite_syscohada` et les classes `post_install`, `-at_install`.
- Les tests de société partent de `SyscohadaCommon` (`aite_syscohada_base/tests/common.py`) ; ceux de la déclaration de `VatDeclarationCommon` (`aite_syscohada_community/tests/test_vat_declaration.py`).
