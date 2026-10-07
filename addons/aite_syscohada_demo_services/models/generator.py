# -*- coding: utf-8 -*-
"""Générateur des données de démonstration : société « Services Informatiques Démo AITE », de janvier 2025 à
septembre 2026.

Le scénario est décrit dans ``scenario.py`` ; le moteur commun (``aite_syscohada_demo_common``) crée la société,
les pièces par lots, la paie, les amortissements, les déclarations et la clôture. Cette classe ne fournit que ce
qui est propre à la société de services : factures du mois, règlements, produits constatés d'avance.
"""
import logging

from odoo import api, models

from odoo.addons.aite_syscohada_demo_common.builder import DemoBuilder

from . import scenario as S

_logger = logging.getLogger(__name__)

COMPANY_XMLID = "demo_company"


class AiteSyscohadaDemoServices(models.AbstractModel):
    _name = "aite.syscohada.demo.services"
    _description = "Données de démonstration SYSCOHADA (services informatiques)"

    @api.model
    def _aite_demo_company(self):
        """Société de démonstration, si elle a déjà été générée."""
        return self.env.ref(f"aite_syscohada_demo_services.{COMPANY_XMLID}", raise_if_not_found=False)

    @api.model
    def _aite_generate(self):
        """Crée la société de démonstration et ses pièces ; sans effet si elle existe déjà."""
        company = self._aite_demo_company()
        if company:
            _logger.info("Démonstration SYSCOHADA : la société « %s » existe déjà, rien à générer.", company.name)
            return company
        return ServicesBuilder(self.env).run()


class ServicesBuilder(DemoBuilder):
    """Société de services informatiques : infogérance, régie, projets, formations, support, revente de matériel."""

    scenario = S
    xmlid = ("aite_syscohada_demo_services", COMPANY_XMLID)

    def documents(self, m):
        p, params, index = self.p, S.YEARS[m.year], m.month - 1
        hardware, mm, tag = params["materiel"][index], m.label, m.tag
        days = params["jours"][index]
        docs = {
            "maintenance": ("out_invoice", p["banque_cliente"], m.day(1), f"INF-{tag}",
                            [(f"Infogérance du parc et des serveurs, {mm}", "7061", params["maintenance"],
                              ["tva_prestations_encaissement", "subie_acompte_ca"])]),
            "rent": ("in_invoice", p["bailleur"], m.day(1), f"LOY-{tag}",
                     [(f"Loyer des bureaux, {mm}", "6222", params["loyer"], ["retenue_loyers"])]),
            "cloud": ("in_invoice", p["cloud"], m.day(5), f"CLD-{tag}",
                      [(f"Services d'informatique en nuage et licences, {mm}", "6343", params["cloud"],
                        ["autoliquidation_services", "retenue_tsr"])]),
            "purchase": ("in_invoice", p["distributeur"], m.day(10), f"MAT-{tag}",
                         [("Ordinateurs, onduleurs et accessoires pour revente", "6011",
                           hardware * S.ACHAT_MATERIEL // 100, ["tva_purchase_good_19_25"])]),
            "power": ("in_invoice", p["energie"], m.day(12), f"ELE-{tag}",
                      [(f"Électricité, {mm}", "6052", params["electricite"], ["tva_purchase_good_19_25"])]),
            "internet": ("in_invoice", p["fai"], m.day(14), f"NET-{tag}",
                         [(f"Liaison internet fibre, {mm}", "6288", params["internet"],
                           ["tva_purchase_services_19_25"])]),
            "sale": ("out_invoice", p["pme"], m.day(20), f"VTE-{tag}",
                     [(f"Matériel informatique vendu, {mm}", "7011", hardware, ["tva_sale_19_25"])]),
            "consulting": ("out_invoice", p["industrie"], m.end, f"REG-{tag}",
                           [(f"Conseil en régie, {days} jours, {mm}", "7061", days * params["taux_jour"],
                             ["tva_prestations_encaissement"])]),
            "charges": ("in_invoice", p["banque"], m.end, f"FRB-{tag}",
                        [("Frais de tenue de compte et commissions", "6318", S.FRAIS_BANCAIRES,
                          ["tva_purchase_services_19_25"])]),
        }
        if m.month in S.PROJET_MOIS.get(m.year, ()):
            docs["project"] = ("out_invoice", p["assurances"], m.day(15), f"PRJ-{tag}",
                               [("Développement du portail clients, jalon livré", "7061", S.PROJET,
                                 ["tva_prestations_encaissement", "subie_honoraires"])])
        if m.month in S.FORMATION_MOIS.get(m.year, ()):
            docs["training"] = ("out_invoice", p["patronat"], m.day(25), f"FOR-{tag}",
                                [("Formation cybersécurité, session de deux jours", "7061", S.FORMATION,
                                  ["tva_prestations_encaissement"])])
        if m.month in S.SOUS_TRAITANCE_MOIS.get(m.year, ()):
            docs["subcontracting"] = ("in_invoice", p["freelance"], m.day(28), f"SST-{tag}",
                                      [("Développement sous-traité, forfait du mois", "621", S.SOUS_TRAITANCE,
                                        ["retenue_honoraires"])])
        if m.contains(S.SUPPORT["date"]):
            docs["support"] = ("out_invoice", p["operateur"], S.SUPPORT["date"], f"SUP-{tag}",
                               [("Contrat de support annuel, octobre 2025 à septembre 2026", "7061",
                                 S.SUPPORT["montant"], ["tva_prestations_encaissement"])])
        return docs

    def settlements(self, m, moves):
        bank = self.j_bank
        result = [
            (moves["maintenance"], m.day(25), bank, None),
            (moves["rent"], m.day(5), bank, None),
            (moves["cloud"], m.day(15), bank, None),
            (moves["purchase"], m.next_month(10), bank, None),
            (moves["power"], m.day(20), bank, None),
            (moves["internet"], m.day(22), bank, None),
            (moves["sale"], m.end, bank, None),
            (moves["consulting"], m.next_month(20), bank, None),
            (moves["charges"], m.end, bank, None),
        ]
        if "project" in moves:
            result.append((moves["project"], m.next_month(15), bank, None))
        if "training" in moves:
            result.append((moves["training"], m.day(25), bank, None))
        if "subcontracting" in moves:
            result.append((moves["subcontracting"], m.next_month(10), bank, None))
        if "support" in moves:
            result.append((moves["support"], S.SUPPORT["reglement"], bank, None))
        return result

    def extra_start_entries(self, m):
        if not m.contains(S.SUPPORT["reprise"]):
            return []
        amount = S.SUPPORT["pca_montant"]
        return [(self.j_misc, S.SUPPORT["reprise"], "Reprise des produits constatés d'avance (contrat de support)",
                 [("477", amount, 0), ("7061", 0, amount)])]

    def extra_end_entries(self, m, moves):
        if m.end != S.SUPPORT["pca"]:
            return []
        amount = S.SUPPORT["pca_montant"]
        return [((self.j_misc, m.end, "Produits constatés d'avance : support de janvier à septembre 2026",
                  [("7061", amount, 0), ("477", 0, amount)]), None)]
