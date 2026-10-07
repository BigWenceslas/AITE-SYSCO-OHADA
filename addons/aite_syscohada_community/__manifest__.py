# -*- coding: utf-8 -*-
{
    "name": "SYSCOHADA révisé – adaptation Odoo Community (Cameroun)",
    "summary": "États SYSCOHADA en un clic (MIS Builder, exercices N et N-1), déclaration mensuelle "
               "I/TVA-IR complète (TVA, retenues, acomptes, IRCM, salaires) et écritures de liquidation, sans Odoo Enterprise.",
    "version": "18.0.1.2.0",
    "category": "Accounting/Localizations",
    "author": "AITE Consulting",
    "website": "https://aite-consulting.com",
    "license": "AGPL-3",
    "depends": ["aite_syscohada_mis", "l10n_cm"],
    "data": [
        "security/ir.model.access.csv",
        "views/vat_declaration_views.xml",
        "views/menus.xml",
        "report/itvair_report.xml",
    ],
    "application": True,
    "installable": True,
}
