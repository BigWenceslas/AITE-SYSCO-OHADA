# -*- coding: utf-8 -*-
"""Générateur des données de démonstration : société « Bar-Hôtel Démo AITE », de janvier 2025 à septembre 2026.

Le scénario (montants, calendrier, calculs à la main) est décrit dans ``demo_scenario.py``. Les pièces passent par
les mécanismes standard d'Odoo (factures et taxes, paiements lettrés avec leur facture, TVA sur encaissements) et
par la déclaration mensuelle du module ``aite_syscohada_community`` (calcul, liquidation, validation) : la
démonstration montre ce que l'utilisateur obtiendrait en saisissant lui-même ces opérations.

Chaque mois est créé par lots (écritures de début de mois, factures, règlements, écritures de fin de mois), puis
déclaré : un lot de pièces est trois à cinq fois plus rapide que des pièces créées une à une.
"""
import calendar
import logging
import time
from collections import defaultdict
from datetime import date, timedelta

import psycopg2

from odoo import Command, _, api, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.aite_syscohada_community.models.itvair import DEF as ITVAIR_LINES

from . import demo_scenario as S

_logger = logging.getLogger(__name__)

COMPANY_XMLID = "demo_company"
TERM_TYPES = ("asset_receivable", "liability_payable")
ANALYZED_TABLES = "account_move, account_move_line, account_partial_reconcile, account_payment"


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
        return _DemoBuilder(self.env).run()


class _DemoBuilder:
    """Construit la société de démonstration, puis ses pièces mois par mois."""

    def __init__(self, env):
        self.root_env = env
        self.pending = []           # règlements prévus un mois ultérieur : (date, facture, journal, montant)
        self.count = 0              # pièces comptables créées (hors écritures de TVA sur encaissements)
        self.loan = 0               # capital restant dû sur l'emprunt
        self.result_previous = 0    # résultat de l'exercice précédent
        self.income_tax = None      # (impôt, {compte : acompte imputé})
        self.dividends = 0
        self._accounts, self._taxes = {}, {}

    # ------------------------------------------------------------------ déroulé
    def run(self):
        start = time.time()
        self._create_company()
        self._configure()
        months = S.months()
        for year, month in months:
            self._month(year, month, last=(year, month) == months[-1])
        _logger.info("Démonstration SYSCOHADA : société « %s », %s pièces générées en %.0f s.",
                     self.company.name, self.count, time.time() - start)
        return self.company

    def _create_company(self):
        env = self.root_env
        xaf = env.ref("base.XAF")
        if not xaf.active:
            xaf.active = True
        # chart_template_load : pas de chargement automatique du plan en fin de transaction, il est chargé ci-dessous
        company = env["res.company"].with_context(chart_template_load=True).create(
            dict(S.COMPANY, country_id=env.ref("base.cm").id, currency_id=xaf.id))
        env["ir.model.data"].create({"module": "aite_syscohada_demo", "name": COMPANY_XMLID, "model": "res.company",
                                     "res_id": company.id, "noupdate": True})
        users = env.ref("base.user_root") | env.user
        admin = env.ref("base.user_admin", raise_if_not_found=False)
        if admin:
            users |= admin
        users.write({"company_ids": [Command.link(company.id)]})
        self.env = env(context=dict(env.context, allowed_company_ids=[company.id], lang="en_US",
                                    tracking_disable=True, mail_create_nolog=True, mail_notrack=True))
        self.company = self.env["res.company"].browse(company.id)
        self.env["account.chart.template"]._load("cm", self.company, install_demo=False)
        if not self.company.aite_syscohada_setup_date:
            raise UserError(_("Le paramétrage SYSCOHADA n'a pas été appliqué à la société de démonstration."))
        try:  # le module base_vat, s'il est installé, contrôle le format du numéro
            with self.env.cr.savepoint():
                self.company.vat = S.NIU
        except ValidationError:
            _logger.info("Démonstration SYSCOHADA : NIU fictif refusé par le contrôle de format, laissé vide.")
        self.round = self.company.currency_id.round
        self.engine = self.env["aite.syscohada.engine"]

    def _configure(self):
        company, Journal = self.company, self.env["account.journal"]

        def journal(journal_type):
            found = Journal.search([("company_id", "=", company.id), ("type", "=", journal_type)], limit=1)
            if not found:
                raise UserError(_("Journal de type %s introuvable dans la société de démonstration.", journal_type))
            return found

        self.j_sale, self.j_purchase = journal("sale"), journal("purchase")
        self.j_bank, self.j_cash, self.j_misc = journal("bank"), journal("cash"), journal("general")
        generals = Journal.search([("company_id", "=", company.id), ("type", "=", "general")])
        # la liquidation de la TVA passe par le premier journal d'opérations diverses : la paie vient après lui
        self.j_paie = Journal.create({"name": "Paie", "code": "PAIE", "type": "general", "company_id": company.id,
                                      "sequence": max(generals.mapped("sequence")) + 1})
        self.j_om = Journal.create({"name": "Orange Money", "code": "OM", "type": "bank", "company_id": company.id,
                                    "default_account_id": self.acc("552100").id})
        self.j_mtn = Journal.create({"name": "MTN Mobile Money", "code": "MOMO", "type": "bank",
                                     "company_id": company.id, "default_account_id": self.acc("552200").id})
        # sans relevés bancaires dans la démonstration, les règlements sont passés directement en trésorerie
        for treasury in self.j_bank | self.j_cash | self.j_om | self.j_mtn:
            methods = treasury.inbound_payment_method_line_ids | treasury.outbound_payment_method_line_ids
            methods.payment_account_id = treasury.default_account_id
        self.bank, self.cash = self.j_bank.default_account_id, self.j_cash.default_account_id
        self.om, self.mtn = self.j_om.default_account_id, self.j_mtn.default_account_id
        self.transfer = company.transfer_account_id or self.acc("585")
        for key in S.TAXES_ACTIVEES:
            self.tax(key).active = True
        self.p = {}
        for key, values in S.PARTNERS.items():
            partner = self.env["res.partner"].create({
                "name": values["name"], "is_company": values.get("is_company", False), "company_id": company.id,
                "country_id": self.env.ref(values.get("country", "base.cm")).id, "city": values.get("city", "Douala")})
            if values.get("investissement"):
                partner.with_company(company).property_account_payable_id = self.acc("4812")
            self.p[key] = partner

    # ------------------------------------------------------------------ un mois
    def _month(self, year, month, last):
        p, coef, params = self.p, S.COEF_DIXIEMES[month - 1], S.YEARS[year]
        first, end = date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
        previous_end = first - timedelta(days=1)

        def d(day):
            return date(year, month, day)

        def next_month(day):
            return date(year + month // 12, month % 12 + 1, day)

        mm, mm_prev, tag = f"{month:02d}/{year}", f"{previous_end:%m/%Y}", f"{year}-{month:02d}"
        opening = (year, month) == S.START
        sales = params["ventes"] * coef // 10
        lodging = params["hebergement"] * coef // 10
        self._refresh_statistics()

        # ---- 1. début de mois : ouverture, virements de fonds, État et CNPS, emprunt, résultat de N-1
        entries = []
        if opening:
            entries.append((self.j_bank, S.CAPITAL[0], "Apport en capital, libéré intégralement",
                            [(self.bank, S.CAPITAL[1], 0), ("1013", 0, S.CAPITAL[1])]))
        else:
            if month == 1:
                entries += self._opening_entries(year, first)
            entries += self._sweep_entries(previous_end, mm_prev, d(1), d(2), d(3))
            entries += self._state_payment_entries(previous_end, mm_prev, d(15))
        entries += self._loan_entries(d(15), mm)
        if month == 2:
            entries.append((self.j_bank, d(28), f"Patente {year}",
                            [("6412", params["patente"], 0), (self.bank, 0, params["patente"])]))
        if first <= S.IMPUTATION_IS <= end:
            entries.append(self._income_tax_imputation(S.IMPUTATION_IS))
        if first <= S.AFFECTATION <= end:
            entries += self._allocation_entries(S.AFFECTATION)
        if first <= S.DIVIDENDES <= end:
            entries += self._dividend_entries(S.DIVIDENDES)
        self.post_entries(entries)

        # ---- 2. factures du mois
        docs = {
            "rent": ("in_invoice", p["bailleur"], d(1), f"LOY-{tag}",
                     [(f"Loyer du mois {mm}", "6222", S.LOYER, ["retenue_loyers"])]),
            "beer": ("in_invoice", p["brasseries"], d(5), f"BRA-{tag}",
                     [("Bières et boissons gazeuses", "6011", sales * S.ACHAT_BRASSERIES // 100,
                       ["tva_purchase_good_19_25", "precompte_achats"])]),
            "wine": ("in_invoice", p["vins"], d(8), f"VIN-{tag}",
                     [("Vins et spiritueux", "6011", sales * S.ACHAT_VINS // 100, ["tva_purchase_good_19_25"])]),
            "power": ("in_invoice", p["energie"], d(12), f"ELE-{tag}",
                      [(f"Électricité {mm}", "6052", params["electricite"], ["tva_purchase_good_19_25"])]),
            "phone": ("in_invoice", p["telecom"], d(14), f"TEL-{tag}",
                      [(f"Internet et téléphone {mm}", "6281", S.TELEPHONE, ["tva_purchase_services_19_25"])]),
            "bar": ("out_invoice", p["comptoir"], end, f"BAR-{tag}",
                    [(f"{label}, ventes du mois {mm}", "7011", sales * share // 100, ["tva_sale_19_25"])
                     for label, share in S.VENTES_LIGNES]),
            "rooms": ("out_invoice", p["hebergement"], end, f"HEB-{tag}",
                      [(f"Nuitées du mois {mm}", "7061", lodging, ["tva_prestations_encaissement"])]),
            "charges": ("in_invoice", p["banque"], end, f"FRB-{tag}",
                        [("Frais de tenue de compte et commissions", "6318", S.FRAIS_BANCAIRES,
                          ["tva_purchase_services_19_25"])]),
        }
        if month in S.LOGICIEL_MOIS:
            docs["software"] = ("in_invoice", p["logiciel"], d(15), f"LOG-{tag}",
                                [("Licence du logiciel de gestion hôtelière, trimestre", "6343", S.LOGICIEL,
                                  ["autoliquidation_services", "retenue_tsr"])])
        if month in S.HONORAIRES_MOIS:
            docs["fees"] = ("in_invoice", p["cabinet"], d(28), f"HON-{tag}",
                            [("Honoraires de tenue comptable et fiscale, trimestre", "6324", S.HONORAIRES,
                              ["tva_purchase_services_19_25", "retenue_honoraires"])])
        if month in S.SEMINAIRE_AGENCE_MOIS.get(year, ()):
            docs["seminar"] = ("out_invoice", p["agence"], d(20), f"SEM-{tag}",
                               [("Séminaire résidentiel, forfait", "7061", S.SEMINAIRE_AGENCE,
                                 ["tva_prestations_encaissement"])])
        if (year, month) in S.SEMINAIRE_PETROLIER_MOIS:
            docs["oil"] = ("out_invoice", p["petrolier"], d(12), f"PET-{tag}",
                           [("Séminaire et hébergement des équipes", "7061", S.SEMINAIRE_PETROLIER,
                             ["tva_prestations_encaissement", "subie_acompte_ca"])])
        assets = {asset[0]: asset for asset in S.IMMOBILISATIONS}
        investments = [(f"asset{i}", when, payments) for i, (when, _supplier, _keys, payments)
                       in enumerate(S.INVESTISSEMENTS) if first <= when <= end]
        for i, (when, supplier, keys, _payments) in enumerate(S.INVESTISSEMENTS):
            if first <= when <= end:
                docs[f"asset{i}"] = ("in_invoice", p[supplier], when, f"IMMO-{when:%Y-%m-%d}",
                                     [(assets[key][1], assets[key][2], assets[key][4], ["tva_immobilisations"])
                                      for key in keys])
        moves = self.post_invoices(docs)

        # ---- 3. règlements : échéances des mois précédents, puis celles du mois (les autres attendent leur mois)
        payments = [item for item in self.pending if item[0] <= end]
        self.pending = [item for item in self.pending if item[0] > end]

        def settle(move, day, journal, amount=None):
            (payments if day <= end else self.pending).append((day, move, journal, amount))

        bank = self.j_bank
        settle(moves["rent"], d(5), bank)
        settle(moves["beer"], next_month(5), bank)
        settle(moves["wine"], d(25), bank)
        settle(moves["power"], d(20), bank)
        settle(moves["phone"], d(22), bank)
        settle(moves["charges"], end, bank)
        for key in ("software", "fees", "seminar"):
            if key in moves:
                settle(moves[key], next_month(10), bank)
        if "oil" in moves:
            settle(moves["oil"], d(28), bank)
        for key, _when, schedule in investments:
            for day, share in schedule:
                settle(moves[key], day, bank, self.round(moves[key].amount_total * share / 100) if share else None)
        bar, rooms = moves["bar"], moves["rooms"]
        settle(bar, end, self.j_om, self.round(bar.amount_total * S.ENCAISSEMENT_ORANGE_MONEY / 100))
        settle(bar, end, self.j_mtn, self.round(bar.amount_total * S.ENCAISSEMENT_MTN / 100))
        settle(bar, end, self.j_cash)
        settle(rooms, end, bank, self.round(rooms.amount_total * S.HEBERGEMENT_ENCAISSE / 100))
        settle(rooms, next_month(10), bank)
        self.post_payments(payments)

        # ---- 4. fin de mois : paie, amortissements, ristourne, inventaire
        entries = self._payroll_entries(S.PAIE[year], end, mm) + self._depreciation_entries(year, month, end, mm)
        if end == S.RISTOURNE["constatee"]:
            amount = S.RISTOURNE["montant"]
            entries.append((self.j_misc, end, f"Ristourne {year} à obtenir des brasseries",
                            [("4098", amount, 0), ("6019", 0, amount)]))
        if end in S.INVENTAIRES:
            stock = S.INVENTAIRES[end]
            entries.append((self.j_misc, end, f"Stock de marchandises au {end:%d/%m/%Y}",
                            [("3111", stock, 0), ("6031", 0, stock)]))
        rebate = first <= S.RISTOURNE["imputee"] <= end
        if rebate:  # avoir de ristourne imputé sur la facture des brasseries du mois
            amount = S.RISTOURNE["montant"]
            entries.append((self.j_misc, S.RISTOURNE["imputee"], "Avoir de ristourne des brasseries, imputé",
                            [("4011", amount, 0, moves["beer"].partner_id), ("4098", 0, amount)]))
        posted = self.post_entries(entries)
        if rebate:
            payable = self.acc("4011")
            (posted[-1].line_ids | moves["beer"].line_ids).filtered(lambda l: l.account_id == payable).reconcile()

        # ---- 5. déclaration du mois ; 6. impôt sur le résultat en fin d'exercice
        self._declare(year, month, end, last)
        if month == 12:
            self._income_tax(year, end)

    # ------------------------------------------------------------------ opérations
    def _sweep_entries(self, period_end, label, day_out, day_in, day_mobile):
        """Espèces et monnaie électronique du mois précédent virées en banque par le compte 585."""
        balances = self.balances([self.cash, self.om, self.mtn], period_end)
        entries, mobile = [], 0
        cash = balances[self.cash]
        if cash > 0:
            entries += [(self.j_cash, day_out, f"Versement en banque des espèces de {label}",
                         [(self.transfer, cash, 0), (self.cash, 0, cash)]),
                        (self.j_bank, day_in, f"Versement en banque des espèces de {label}",
                         [(self.bank, cash, 0), (self.transfer, 0, cash)])]
        for journal, account in ((self.j_om, self.om), (self.j_mtn, self.mtn)):
            amount = balances[account]
            if amount > 0:
                entries.append((journal, day_mobile, f"Virement vers la banque, {journal.name}, {label}",
                                [(self.transfer, amount, 0), (account, 0, amount)]))
                mobile += amount
        if mobile:
            entries.append((self.j_bank, day_mobile, f"Réception des virements de monnaie électronique de {label}",
                            [(self.bank, mobile, 0), (self.transfer, 0, mobile)]))
        return entries

    def _state_payment_entries(self, period_end, label, day):
        """Paiement des soldes créditeurs du mois précédent : déclaration I/TVA-IR, puis CNPS."""
        entries = []
        for codes, ref in ((S.COMPTES_DECLARATION, f"Paiement I/TVA-IR {label}"),
                           (S.COMPTES_CNPS, f"Cotisations CNPS {label}")):
            lines = [(code, -balance, 0) for code, balance in self.balances(codes, period_end).items() if balance < 0]
            total = sum(line[1] for line in lines)
            if total:
                entries.append((self.j_bank, day, ref, lines + [(self.bank, 0, total)]))
        return entries

    def _loan_entries(self, day, label):
        loan = S.EMPRUNT
        if day == loan["date"]:
            self.loan = loan["montant"]
            return [(self.j_bank, day, "Emprunt bancaire, mise à disposition des fonds",
                     [(self.bank, loan["montant"], 0), ("162", 0, loan["montant"])])]
        if not (self.loan and day > loan["date"]):
            return []
        capital = min(loan["capital_mensuel"], self.loan)
        interest = self.round(self.loan * loan["taux_mensuel_pour_cent"] / 100)
        self.loan -= capital
        return [(self.j_bank, day, f"Échéance d'emprunt {label}",
                 [("162", capital, 0), ("6712", interest, 0), (self.bank, 0, capital + interest)])]

    def _payroll_entries(self, pay, day, label):
        net = pay["brut"] - sum(pay[k] for k in ("cnps_salariale", "irpp", "cac", "cfc_salariale", "rav", "tdl"))
        employer = pay["cnps_pf"] + pay["cnps_at"] + pay["cnps_pension"]
        taxes = pay["cfc_patronale"] + pay["fne"]
        return [
            (self.j_paie, day, f"Paie {label}", [
                ("6611", pay["brut"], 0), ("4313", 0, pay["cnps_salariale"]), ("447210", 0, pay["irpp"]),
                ("447215", 0, pay["cac"]), ("447220", 0, pay["cfc_salariale"]), ("447250", 0, pay["rav"]),
                ("447260", 0, pay["tdl"]), ("422", 0, net),
                ("6641", employer, 0), ("4311", 0, pay["cnps_pf"]), ("4312", 0, pay["cnps_at"]),
                ("4313", 0, pay["cnps_pension"]),
                ("6413", taxes, 0), ("447230", 0, pay["cfc_patronale"]), ("447240", 0, pay["fne"])]),
            (self.j_bank, day, f"Virement des salaires nets {label}", [("422", net, 0), (self.bank, 0, net)]),
        ]

    def _depreciation_entries(self, year, month, day, label):
        lines = [(amort, 0, amount // duration) for _key, _name, _code, amort, amount, start, duration
                 in S.IMMOBILISATIONS if (year, month) >= start]
        total = sum(line[2] for line in lines)
        return [(self.j_misc, day, f"Dotations aux amortissements {label}", [("6813", total, 0)] + lines)] if total else []

    def _declare(self, year, month, day, last):
        """Déclaration I/TVA-IR du mois : calculée, liquidée et validée ; la dernière reste en brouillon."""
        declaration = self.env["aite.cm.vat.declaration"].create(
            {"company_id": self.company.id, "date_from": date(year, month, 1), "date_to": day})
        if self.dividends and (S.DIVIDENDES.year, S.DIVIDENDES.month) == (year, month):
            declaration.action_compute()  # crée les lignes du formulaire
            declaration.itvair_line_ids.filtered(lambda l: l.code == "L57").base_input = self.dividends
        if last:
            declaration.action_compute()
            return declaration
        declaration.action_create_closing_entry()
        declaration.action_done()
        self.count += 1
        return declaration

    def _opening_entries(self, year, day):
        """1er janvier : résultat de l'exercice précédent en instance d'affectation et reprise du stock initial."""
        result = self.engine.compute(self.company, date(year - 1, 1, 1), date(year - 1, 12, 31), ("resultat",))
        self.result_previous = int(self.round(result["resultat"]["XI"]))
        label, entries = f"Résultat {year - 1} en instance d'affectation", []
        if self.result_previous > 0:
            entries.append((self.j_misc, day, label, [("999999", self.result_previous, 0),
                                                      ("131", 0, self.result_previous)]))
        elif self.result_previous < 0:
            entries.append((self.j_misc, day, label, [("139", -self.result_previous, 0),
                                                      ("999999", 0, -self.result_previous)]))
        stock = self.balances(["3111"], day - timedelta(days=1))["3111"]
        if stock:
            entries.append((self.j_misc, day, f"Reprise du stock initial {year}", [("6031", stock, 0),
                                                                                  ("3111", 0, stock)]))
        return entries

    def _income_tax(self, year, day):
        """Impôt illustratif : 33 % du résultat avant impôt, au minimum les acomptes et précomptes de l'exercice."""
        result = self.engine.compute(self.company, date(year, 1, 1), day, ("resultat",))["resultat"]
        before_tax = result["XG"] + result.get("XH", 0.0)
        advances = {code: amount for code, amount in self.balances(S.COMPTES_ACOMPTES_IS, day).items() if amount > 0}
        tax = max(self.round(max(before_tax, 0.0) * S.TAUX_IS_ILLUSTRATIF), sum(advances.values()))
        self.post_entries([(self.j_misc, day, f"Impôt sur le résultat {year} (montant illustratif)",
                            [("8911", tax, 0), ("441", 0, tax)])])
        self.income_tax = (tax, advances)

    def _income_tax_imputation(self, day):
        tax, advances = self.income_tax
        rest = tax - sum(advances.values())
        lines = [("441", tax, 0)] + [(code, 0, amount) for code, amount in advances.items()]
        journal = self.j_misc
        if rest > 0:
            lines.append((self.bank, 0, rest))
            journal = self.j_bank
        return (journal, day, f"Impôt sur le résultat {day.year - 1} : imputation des acomptes et précomptes", lines)

    def _allocation_entries(self, day):
        """Affectation : réserve légale 10 %, dividendes (moitié arrondie à 10 000 près), report à nouveau."""
        result = self.result_previous
        if result <= 0:
            return []
        reserve = result // 10
        self.dividends = result // 2 // 10_000 * 10_000
        retained = result - reserve - self.dividends
        return [(self.j_misc, day, f"Affectation du résultat {day.year - 1} (assemblée générale du {day:%d/%m/%Y})",
                 [("131", result, 0), ("111", 0, reserve), ("465", 0, self.dividends), ("121", 0, retained)])]

    def _dividend_entries(self, day):
        """Dividendes versés, IRCM retenu au taux par défaut de la ligne L57 et centimes additionnels communaux."""
        if not self.dividends:
            return []
        rate = ITVAIR_LINES["L57"][6]
        cac_rate = self.env["aite.cm.vat.declaration"].default_get(["cac_rate"])["cac_rate"]
        principal = self.round(self.dividends * rate / 100)
        ircm = principal + self.round(principal * cac_rate / 100)
        return [(self.j_bank, day, "Dividendes versés, IRCM retenu à la source",
                 [("465", self.dividends, 0), ("447110", 0, ircm), (self.bank, 0, self.dividends - ircm)])]

    # ------------------------------------------------------------------ outils
    def _refresh_statistics(self):
        """Toute la génération tient en une transaction : sans statistiques à jour, PostgreSQL choisit de mauvais
        plans d'exécution dès que les tables comptables grossissent (jusqu'à dix fois plus lent)."""
        self.env.flush_all()
        try:
            with self.env.cr.savepoint(flush=False):
                self.env.cr.execute(f"ANALYZE {ANALYZED_TABLES}")
        except psycopg2.Error:
            _logger.debug("Démonstration SYSCOHADA : ANALYZE refusé, génération poursuivie sans.")

    def acc(self, code):
        if code not in self._accounts:
            account = self.company._aite_account(code)
            if not account:
                raise UserError(_("Compte %s introuvable dans la société de démonstration.", code))
            self._accounts[code] = account
        return self._accounts[code]

    def tax(self, key):
        if key not in self._taxes:
            tax = self.company._aite_tax_ref(key) or self.env["account.chart.template"].with_company(
                self.company).ref(key, raise_if_not_found=False)
            if not tax:
                raise UserError(_("Taxe %s introuvable dans la société de démonstration.", key))
            self._taxes[key] = tax
        return self._taxes[key]

    def balances(self, keys, date_to):
        """Soldes (débit − crédit) cumulés au ``date_to`` inclus, pour des codes ou des comptes : {clé: solde}."""
        accounts = {key: self.acc(key) if isinstance(key, str) else key for key in keys}
        groups = self.env["account.move.line"]._read_group(
            [("company_id", "=", self.company.id), ("parent_state", "=", "posted"), ("date", "<=", date_to),
             ("account_id", "in", [account.id for account in accounts.values()])], ["account_id"], ["balance:sum"])
        found = {account.id: balance for account, balance in groups}
        return {key: self.round(found.get(account.id, 0.0)) for key, account in accounts.items()}

    def post_invoices(self, documents):
        """Factures validées en lot ; documents = {clé: (type, partenaire, date, référence, lignes)},
        lignes = [(libellé, code de compte, montant hors taxes, clés de taxes)]. Retourne {clé: facture}."""
        keys = sorted(documents, key=lambda key: documents[key][2])
        moves = self.env["account.move"].create([{
            "move_type": move_type, "partner_id": partner.id, "invoice_date": day, "date": day, "ref": ref,
            "journal_id": (self.j_sale if move_type.startswith("out_") else self.j_purchase).id,
            "invoice_line_ids": [Command.create({
                "name": label, "account_id": self.acc(code).id, "quantity": 1, "price_unit": amount,
                "tax_ids": [Command.set([self.tax(tax).id for tax in taxes])]}) for label, code, amount, taxes in lines],
        } for move_type, partner, day, ref, lines in (documents[key] for key in keys)])
        moves.action_post()
        self.count += len(moves)
        return dict(zip(keys, moves))

    def post_payments(self, requests):
        """Règlements en lot, comme l'assistant de paiement d'Odoo : paiements créés et validés, puis lettrés avec
        leur facture. requests = [(date, facture, journal, montant ou None pour le solde restant dû)]."""
        if not requests:
            return
        requests = sorted(requests, key=lambda request: request[0])
        explicit = defaultdict(float)
        for _day, move, _journal, amount in requests:
            explicit[move] += amount or 0.0
        values = []
        for day, move, journal, amount in requests:
            inbound = move.is_inbound()
            methods = journal.inbound_payment_method_line_ids if inbound else journal.outbound_payment_method_line_ids
            term = move.line_ids.filtered(lambda line: line.account_type in TERM_TYPES)
            values.append({
                "date": day, "amount": amount if amount is not None else move.amount_residual - explicit[move],
                "payment_type": "inbound" if inbound else "outbound",
                "partner_type": "customer" if move.is_sale_document(True) else "supplier",
                "memo": move.name, "journal_id": journal.id, "company_id": self.company.id,
                "currency_id": self.company.currency_id.id, "partner_id": move.commercial_partner_id.id,
                "payment_method_line_id": methods[:1].id, "destination_account_id": term.account_id.id,
                "invoice_ids": [Command.link(move.id)]})
        payments = self.env["account.payment"].with_context(skip_invoice_sync=True).create(values)
        payments.action_post()
        to_match = defaultdict(lambda: self.env["account.move.line"])
        for payment, (_day, move, _journal, _amount) in zip(payments, requests):
            to_match[move] |= payment.move_id.line_ids
        self.env["account.move.line"]._reconcile_plan([
            (lines | move.line_ids).filtered(lambda line: line.account_type in TERM_TYPES and not line.reconciled)
            for move, lines in to_match.items()])
        self.count += len(payments)

    def post_entries(self, entries):
        """Écritures validées en lot ; entries = [(journal, date, référence, lignes)],
        lignes = [(code ou compte, débit, crédit[, partenaire])]. Retourne les écritures dans le même ordre."""
        if not entries:
            return []
        order = sorted(range(len(entries)), key=lambda i: entries[i][1])
        moves = self.env["account.move"].create([{
            "move_type": "entry", "journal_id": journal.id, "date": day, "ref": ref,
            "line_ids": [Command.create({
                "account_id": (self.acc(line[0]) if isinstance(line[0], str) else line[0]).id, "name": ref,
                "debit": line[1], "credit": line[2], "partner_id": line[3].id if len(line) > 3 else False,
            }) for line in lines if line[1] or line[2]],
        } for journal, day, ref, lines in (entries[i] for i in order)])
        moves.action_post()
        self.count += len(moves)
        result = [None] * len(entries)
        for i, move in zip(order, moves):
            result[i] = move
        return result
