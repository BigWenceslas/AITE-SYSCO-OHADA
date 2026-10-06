# -*- coding: utf-8 -*-
{
    "name": "SYSCOHADA révisé – rapports Enterprise",
    "summary": "Bilan, compte de résultat et tableau des flux SYSCOHADA dans le moteur de rapports d'Odoo Enterprise, "
               "générés depuis le référentiel des rubriques AITE.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations/Reporting",
    "author": "AITE Consulting",
    "website": "https://aite-consulting.com",
    "license": "OEEL-1",
    "depends": ["aite_syscohada_base", "account_reports"],
    "data": ["data/syscohada_reports.xml"],
    "installable": True,
    "auto_install": True,
}
