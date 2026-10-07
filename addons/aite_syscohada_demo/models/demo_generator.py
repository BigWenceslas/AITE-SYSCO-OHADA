# -*- coding: utf-8 -*-
"""Générateur des données de démonstration : société « Bar-Hôtel Démo AITE », de janvier 2025 à septembre 2026.

Le scénario (montants, calendrier, calculs à la main) est décrit dans ``demo_scenario.py`` ; le moteur commun
(``aite_syscohada_demo_common``) crée la société, les pièces par lots, la paie, les amortissements, les
déclarations et la clôture. Cette classe ne fournit que ce qui est propre au bar-hôtel : factures du mois et leurs
règlements, ristourne des brasseries.
"""
import logging

from odoo import api, models

from odoo.addons.aite_syscohada_demo_common.builder import DemoBuilder

from . import demo_scenario as S

_logger = logging.getLogger(__name__)

COMPANY_XMLID = "demo_company"


class AiteSyscohadaDemo(models.AbstractModel):
    _name = "aite.syscohada.demo"
    _description = "Données de démonstration SYSCOHADA (bar-hôtel)"

    @api.model
    def _aite_demo_company(self):
        """Société de démonstration, si elle a déjà été générée."""
        return self.env.ref(f"aite_syscohada_demo.{COMPANY_XMLID}", raise_if_not_found=False)

    @api.model
    def _aite_generate(self):
        """Crée la société de démonstration et ses pièces ; sans effet si elle existe déjà."""
        company = self._aite_demo_company()
        if company:
            _logger.info("Démonstration SYSCOHADA : la société « %s » existe déjà, rien à générer.", company.name)
            return company
        return BarHotelBuilder(self.env).run()


class BarHotelBuilder(DemoBuilder):
    """Bar-hôtel : ventes du bar encaissées en espèces et monnaie électronique, nuitées et séminaires, achats."""

    scenario = S
    xmlid = ("aite_syscohada_demo", COMPANY_XMLID)
    mobile_money = True

    def documents(self, m):
        p, coef, params = self.p, S.COEF_DIXIEMES[m.month - 1], S.YEARS[m.year]
        sales = params["ventes"] * coef // 10
        lodging = params["hebergement"] * coef // 10
        mm, tag = m.label, m.tag
        docs = {
            "rent": ("in_invoice", p["bailleur"], m.day(1), f"LOY-{tag}",
                     [(f"Loyer du mois {mm}", "6222", S.LOYER, ["retenue_loyers"])]),
            "beer": ("in_invoice", p["brasseries"], m.day(5), f"BRA-{tag}",
                     [("Bières et boissons gazeuses", "6011", sales * S.ACHAT_BRASSERIES // 100,
                       ["tva_purchase_good_19_25", "precompte_achats"])]),
            "wine": ("in_invoice", p["vins"], m.day(8), f"VIN-{tag}",
                     [("Vins et spiritueux", "6011", sales * S.ACHAT_VINS // 100, ["tva_purchase_good_19_25"])]),
            "power": ("in_invoice", p["energie"], m.day(12), f"ELE-{tag}",
                      [(f"Électricité {mm}", "6052", params["electricite"], ["tva_purchase_good_19_25"])]),
            "phone": ("in_invoice", p["telecom"], m.day(14), f"TEL-{tag}",
                      [(f"Internet et téléphone {mm}", "6281", S.TELEPHONE, ["tva_purchase_services_19_25"])]),
            "bar": ("out_invoice", p["comptoir"], m.end, f"BAR-{tag}",
                    [(f"{label}, ventes du mois {mm}", "7011", sales * share // 100, ["tva_sale_19_25"])
                     for label, share in S.VENTES_LIGNES]),
            "rooms": ("out_invoice", p["hebergement"], m.end, f"HEB-{tag}",
                      [(f"Nuitées du mois {mm}", "7061", lodging, ["tva_prestations_encaissement"])]),
            "charges": ("in_invoice", p["banque"], m.end, f"FRB-{tag}",
                        [("Frais de tenue de compte et commissions", "6318", S.FRAIS_BANCAIRES,
                          ["tva_purchase_services_19_25"])]),
        }
        if m.month in S.LOGICIEL_MOIS:
            docs["software"] = ("in_invoice", p["logiciel"], m.day(15), f"LOG-{tag}",
                                [("Licence du logiciel de gestion hôtelière, trimestre", "6343", S.LOGICIEL,
                                  ["autoliquidation_services", "retenue_tsr"])])
        if m.month in S.HONORAIRES_MOIS:
            docs["fees"] = ("in_invoice", p["cabinet"], m.day(28), f"HON-{tag}",
                            [("Honoraires de tenue comptable et fiscale, trimestre", "6324", S.HONORAIRES,
                              ["tva_purchase_services_19_25", "retenue_honoraires"])])
        if m.month in S.SEMINAIRE_AGENCE_MOIS.get(m.year, ()):
            docs["seminar"] = ("out_invoice", p["agence"], m.day(20), f"SEM-{tag}",
                               [("Séminaire résidentiel, forfait", "7061", S.SEMINAIRE_AGENCE,
                                 ["tva_prestations_encaissement"])])
        if (m.year, m.month) in S.SEMINAIRE_PETROLIER_MOIS:
            docs["oil"] = ("out_invoice", p["petrolier"], m.day(12), f"PET-{tag}",
                           [("Séminaire et hébergement des équipes", "7061", S.SEMINAIRE_PETROLIER,
                             ["tva_prestations_encaissement", "subie_acompte_ca"])])
        return docs

    def settlements(self, m, moves):
        bank, end = self.j_bank, m.end
        result = [
            (moves["rent"], m.day(5), bank, None),
            (moves["beer"], m.next_month(5), bank, None),
            (moves["wine"], m.day(25), bank, None),
            (moves["power"], m.day(20), bank, None),
            (moves["phone"], m.day(22), bank, None),
            (moves["charges"], end, bank, None),
        ]
        result += [(moves[key], m.next_month(10), bank, None) for key in ("software", "fees", "seminar") if key in moves]
        if "oil" in moves:
            result.append((moves["oil"], m.day(28), bank, None))
        bar, rooms = moves["bar"], moves["rooms"]
        result += [
            (bar, end, self.j_om, self.round(bar.amount_total * S.ENCAISSEMENT_ORANGE_MONEY / 100)),
            (bar, end, self.j_mtn, self.round(bar.amount_total * S.ENCAISSEMENT_MTN / 100)),
            (bar, end, self.j_cash, None),
            (rooms, end, bank, self.round(rooms.amount_total * S.HEBERGEMENT_ENCAISSE / 100)),
            (rooms, m.next_month(10), bank, None),
        ]
        return result

    def extra_end_entries(self, m, moves):
        amount, entries = S.RISTOURNE["montant"], []
        if m.end == S.RISTOURNE["constatee"]:
            entries.append(((self.j_misc, m.end, f"Ristourne {m.year} à obtenir des brasseries",
                             [("4098", amount, 0), ("6019", 0, amount)]), None))
        if m.contains(S.RISTOURNE["imputee"]):  # avoir imputé sur la facture des brasseries du mois
            beer = moves["beer"]
            payable = self.acc("4011")

            def reconcile(move):
                (move.line_ids | beer.line_ids).filtered(lambda l: l.account_id == payable).reconcile()

            entries.append(((self.j_misc, S.RISTOURNE["imputee"], "Avoir de ristourne des brasseries, imputé",
                             [("4011", amount, 0, beer.partner_id), ("4098", 0, amount)]), reconcile))
        return entries
