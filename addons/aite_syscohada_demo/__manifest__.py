# -*- coding: utf-8 -*-
{
    "name": "SYSCOHADA révisé – données de démonstration (bar-hôtel, Cameroun)",
    "summary": "Société « Bar-Hôtel Démo AITE » avec 21 mois d'opérations (janvier 2025 à septembre 2026) : ventes, "
               "nuitées, achats, retenues, paie, immobilisations, emprunt, déclarations I/TVA-IR liquidées et "
               "états SYSCOHADA prêts à consulter. Pour les bases de test et de formation.",
    "version": "18.0.1.1.0",
    "category": "Accounting/Localizations",
    "author": "AITE Consulting",
    "website": "https://aite-consulting.com",
    "license": "AGPL-3",
    # aite_syscohada_community reste listé : sur une base installée en 18.0.1.0.0, la mise à jour de community
    # garde ce module chargé et installe le moteur commun
    "depends": ["aite_syscohada_community", "aite_syscohada_demo_common"],
    "data": [],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
