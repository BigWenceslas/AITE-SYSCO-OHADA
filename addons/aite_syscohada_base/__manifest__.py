# -*- coding: utf-8 -*-
{
    "name": "SYSCOHADA révisé – socle AITE (Cameroun)",
    "summary": "Rubriques des états SYSCOHADA, moteur de calcul indépendant de l'édition, "
               "corrections du plan comptable, taxes camerounaises complémentaires et contrôles.",
    "version": "18.0.1.2.0",
    "category": "Accounting/Localizations",
    "author": "AITE Consulting",
    "website": "https://aite-consulting.com",
    "license": "LGPL-3",
    "depends": ["account", "l10n_cm"],
    "data": [
        "security/ir.model.access.csv",
        "data/aite.syscohada.rubrique.csv",
        "views/syscohada_rubrique_views.xml",
        "wizard/syscohada_statement_wizard_views.xml",
        "views/menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
