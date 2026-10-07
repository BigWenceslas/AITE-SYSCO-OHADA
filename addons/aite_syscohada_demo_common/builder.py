# -*- coding: utf-8 -*-
"""Moteur commun des sociétés de démonstration SYSCOHADA.

Une société de démonstration est décrite par un module de paramètres (le « scénario ») et une sous-classe de
``DemoBuilder`` qui fournit, pour chaque mois, ses factures et leurs règlements. Le moteur se charge du reste :
création de la société et chargement du plan « cm » (le paramétrage AITE suit), journaux, partenaires, taxes,
pièces créées par lots (écritures de début de mois, factures, règlements, écritures de fin de mois), paie,
amortissements, inventaires, déclaration I/TVA-IR du mois (calculée, liquidée, payée le 15 du mois suivant et
validée ; la dernière reste en brouillon), impôt sur le résultat, affectation du résultat et dividendes.

Toutes les pièces passent par les mécanismes standard d'Odoo (factures et taxes, paiements lettrés avec leur
facture, TVA sur encaissements) : la démonstration montre ce qu'obtiendrait un utilisateur en saisissant
lui-même ces opérations. Un lot de pièces est trois à cinq fois plus rapide que des pièces créées une à une.

Paramètres lus dans le scénario (module Python) :
    START, END                      premier et dernier mois (année, mois)
    COMPANY, NIU                    coordonnées fictives de la société, numéro d'identifiant unique fictif
    PARTNERS                        {clé: {"name", "is_company", "country", "city", "investissement", "compte"}} ;
                                    compte fournisseur : « compte » s'il est donné, sinon 4812 pour un fournisseur
                                    d'investissement (4811 pour les immobilisations incorporelles)
    TAXES_ACTIVEES                  clés des taxes du socle à activer dans la société de démonstration
    YEARS[année]["patente"]         patente payée le 28 février
    PAIE[année]                     paie globale du mois (brut, retenues salariales, charges patronales)
    CAPITAL                         (date, montant) de l'apport en capital
    IMMOBILISATIONS                 [(clé, libellé, compte, compte d'amortissement, montant, (année, mois), durée)]
    INVESTISSEMENTS                 [(date, fournisseur, clés d'immobilisations, [(date, % du TTC ou None)])]
    INVENTAIRES                     {date: stock de marchandises (compte 3111)}, un dernier jour de mois, un seul
                                    par exercice (le stock précédent n'est repris qu'au 1er janvier)
    TAUX_IS_ILLUSTRATIF, IMPUTATION_IS, AFFECTATION, DIVIDENDES
    EMPRUNT (facultatif)            {"date", "montant", "capital_mensuel", "taux_mensuel_pour_cent"}, date un 15
                                    (échéances le 15 de chaque mois)
Un paramètre que le moteur ne sait pas traiter est refusé à l'exécution, jamais ignoré.
"""
import base64
import calendar
import logging
import time
from collections import defaultdict
from datetime import date, timedelta

import psycopg2

from odoo import Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import file_open

from odoo.addons.aite_syscohada_community.models.itvair import DEF as ITVAIR_LINES

_logger = logging.getLogger(__name__)

# Comptes réglés le 15 du mois suivant avec la déclaration I/TVA-IR (soldes créditeurs en fin de mois)
COMPTES_DECLARATION = ("444100", "441100", "447110", "447120", "447130", "447140", "447150", "447160", "447161",
                       "447170", "447180", "447210", "447215", "447220", "447230", "447240", "447250", "447260")
COMPTES_CNPS = ("431100", "431200", "431300")
# Acomptes et précomptes imputables sur l'impôt sur le résultat
COMPTES_ACOMPTES_IS = ("449210", "449220", "449230", "449240", "449250")
TERM_TYPES = ("asset_receivable", "liability_payable")
ANALYZED_TABLES = "account_move, account_move_line, account_partial_reconcile, account_payment"


def months(start, end):
    """Mois de ``start`` à ``end`` inclus : [(année, mois), ...]."""
    year, month = start
    result = []
    while (year, month) <= end:
        result.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result


class Month:
    """Repères d'un mois du scénario : dates, libellés, mois d'ouverture et dernier mois."""

    def __init__(self, year, month, opening, last):
        self.year, self.month, self.opening, self.last = year, month, opening, last
        self.first = date(year, month, 1)
        self.end = date(year, month, calendar.monthrange(year, month)[1])
        self.previous_end = self.first - timedelta(days=1)
        self.label = f"{month:02d}/{year}"
        self.previous_label = f"{self.previous_end:%m/%Y}"
        self.tag = f"{year}-{month:02d}"

    def day(self, day):
        return date(self.year, self.month, day)

    def next_month(self, day):
        return date(self.year + self.month // 12, self.month % 12 + 1, day)

    def contains(self, day):
        return self.first <= day <= self.end


class DemoBuilder:
    """Construit une société de démonstration, puis ses pièces mois par mois (voir la docstring du module)."""

    scenario = None          # module de paramètres
    xmlid = None             # (module, nom) de l'identifiant externe de la société
    mobile_money = False     # journaux Orange Money et MTN Mobile Money

    def __init__(self, env):
        self.S = self.scenario
        self.root_env = env
        self.pending = []           # règlements prévus un mois ultérieur : (date, facture, journal, montant)
        self.count = 0              # pièces comptables créées (hors écritures de TVA sur encaissements)
        self.loan = 0               # capital restant dû sur l'emprunt
        self.result_previous = 0    # résultat de l'exercice précédent
        self.income_tax = None      # (impôt, {compte : acompte imputé})
        self.dividends = 0
        self._accounts, self._taxes = {}, {}

    # ------------------------------------------------------------------ à fournir par le scénario
    def documents(self, m):
        """Factures du mois : {clé: (type, partenaire, date, référence, lignes)}."""
        raise NotImplementedError

    def settlements(self, m, moves):
        """Règlements des factures du mois : [(facture, date, journal, montant ou None pour le solde)]."""
        raise NotImplementedError

    def extra_start_entries(self, m):
        """Écritures propres au scénario en début de mois : [(journal, date, référence, lignes)]."""
        return []

    def extra_end_entries(self, m, moves):
        """Écritures propres au scénario en fin de mois : [((journal, date, référence, lignes), rappel ou None)] ;
        le rappel reçoit l'écriture validée."""
        return []

    # ------------------------------------------------------------------ déroulé
    def run(self):
        start = time.time()
        self._check_scenario()
        self._create_company()
        self._configure()
        period = months(self.S.START, self.S.END)
        for year, month in period:
            self._month(Month(year, month, (year, month) == self.S.START, (year, month) == period[-1]))
        _logger.info("Démonstration SYSCOHADA : société « %s », %s pièces générées en %.0f s.",
                     self.company.name, self.count, time.time() - start)
        return self.company

    def _check_scenario(self):
        """Refuse les paramètres que le moteur ne sait pas traiter, plutôt que de les ignorer en silence."""
        loan = getattr(self.S, "EMPRUNT", None)
        if loan and loan["date"].day != 15:
            raise UserError(_("EMPRUNT : la mise à disposition doit tomber un 15, jour des échéances (%s).",
                              loan["date"]))
        for day in self.S.INVENTAIRES:
            if day.day != calendar.monthrange(day.year, day.month)[1]:
                raise UserError(_("INVENTAIRES : le %s n'est pas un dernier jour de mois.", day))
        years = [day.year for day in self.S.INVENTAIRES]
        if len(years) != len(set(years)):
            raise UserError(_("INVENTAIRES : un seul inventaire par exercice, le stock n'étant repris qu'au 1er "
                              "janvier."))

    def _month(self, m):
        self._refresh_statistics()
        # 1. début de mois : ouverture, apport, virements de fonds, État et CNPS, emprunt, patente, résultat de N-1
        self.post_entries(self.start_entries(m))
        # 2. factures du mois
        documents = self.documents(m)
        documents.update(self.investment_documents(m))
        moves = self.post_invoices(documents)
        # 3. règlements : échéances des mois précédents, puis celles du mois (les autres attendent leur mois)
        payments = [item for item in self.pending if item[0] <= m.end]
        self.pending = [item for item in self.pending if item[0] > m.end]
        for move, day, journal, amount in self.settlements(m, moves) + self.investment_settlements(m, moves):
            (payments if day <= m.end else self.pending).append((day, move, journal, amount))
        self.post_payments(payments)
        # 4. fin de mois : paie, amortissements, inventaire, écritures propres au scénario
        entries = (self.payroll_entries(self.S.PAIE[m.year], m.end, m.label)
                   + self.depreciation_entries(m) + self.inventory_entries(m))
        extra = self.extra_end_entries(m, moves)
        posted = self.post_entries(entries + [entry for entry, _callback in extra])
        for move, (_entry, callback) in zip(posted[len(entries):], extra):
            if callback:
                callback(move)
        # 5. déclaration du mois ; 6. impôt sur le résultat en fin d'exercice
        self.declare(m)
        if m.month == 12:
            self.post_income_tax(m.year, m.end)

    def start_entries(self, m):
        entries = []
        if m.opening:
            day, amount = self.S.CAPITAL
            entries.append((self.j_bank, day, "Apport en capital, libéré intégralement",
                            [(self.bank, amount, 0), ("1013", 0, amount)]))
        else:
            if m.month == 1:
                entries += self.opening_entries(m.year, m.first)
            entries += self.sweep_entries(m.previous_end, m.previous_label, m.day(1), m.day(2), m.day(3))
            entries += self.state_payment_entries(m.previous_end, m.previous_label, m.day(15))
        entries += self.loan_entries(m.day(15), m.label)
        if m.month == 2:
            patente = self.S.YEARS[m.year]["patente"]
            entries.append((self.j_bank, m.day(28), f"Patente {m.year}",
                            [("6412", patente, 0), (self.bank, 0, patente)]))
        if m.contains(self.S.IMPUTATION_IS) and self.income_tax:
            entries.append(self.income_tax_imputation(self.S.IMPUTATION_IS))
        if m.contains(self.S.AFFECTATION):
            entries += self.allocation_entries(self.S.AFFECTATION)
        if m.contains(self.S.DIVIDENDES):
            entries += self.dividend_entries(self.S.DIVIDENDES)
        return entries + self.extra_start_entries(m)

    # ------------------------------------------------------------------ société
    def _create_company(self):
        env = self.root_env
        xaf = env.ref("base.XAF")
        if not xaf.active:
            xaf.active = True
        # chart_template_load : pas de chargement automatique du plan en fin de transaction, il est chargé ci-dessous
        module, name = self.xmlid
        # logo de la société (en-tête des documents imprimés) : l'icône du module de démonstration
        with file_open(f"{module}/static/description/icon.png", "rb") as icon:
            logo = base64.b64encode(icon.read())
        company = env["res.company"].with_context(chart_template_load=True).create(
            dict(self.S.COMPANY, country_id=env.ref("base.cm").id, currency_id=xaf.id, logo=logo))
        env["ir.model.data"].create({"module": module, "name": name, "model": "res.company",
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
                self.company.vat = self.S.NIU
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
        treasuries = self.j_bank | self.j_cash
        self.j_om = self.j_mtn = Journal
        if self.mobile_money:
            self.j_om = Journal.create({"name": "Orange Money", "code": "OM", "type": "bank",
                                        "company_id": company.id, "default_account_id": self.acc("552100").id})
            self.j_mtn = Journal.create({"name": "MTN Mobile Money", "code": "MOMO", "type": "bank",
                                         "company_id": company.id, "default_account_id": self.acc("552200").id})
            treasuries |= self.j_om | self.j_mtn
        # sans relevés bancaires dans la démonstration, les règlements sont passés directement en trésorerie
        for treasury in treasuries:
            methods = treasury.inbound_payment_method_line_ids | treasury.outbound_payment_method_line_ids
            methods.payment_account_id = treasury.default_account_id
        self.bank, self.cash = self.j_bank.default_account_id, self.j_cash.default_account_id
        self.om, self.mtn = self.j_om.default_account_id, self.j_mtn.default_account_id
        self.transfer = company.transfer_account_id or self.acc("585")
        for key in self.S.TAXES_ACTIVEES:
            self.tax(key).active = True
        self.p = {}
        for key, values in self.S.PARTNERS.items():
            partner = self.env["res.partner"].create({
                "name": values["name"], "is_company": values.get("is_company", False), "company_id": company.id,
                "country_id": self.env.ref(values.get("country", "base.cm")).id, "city": values.get("city", "Douala")})
            payable = values.get("compte") or ("4812" if values.get("investissement") else None)
            if payable:
                partner.with_company(company).property_account_payable_id = self.acc(payable)
            self.p[key] = partner

    # ------------------------------------------------------------------ opérations communes
    def investment_documents(self, m):
        assets = {asset[0]: asset for asset in self.S.IMMOBILISATIONS}
        return {f"asset{i}": ("in_invoice", self.p[supplier], when, f"IMMO-{when:%Y-%m-%d}",
                              [(assets[key][1], assets[key][2], assets[key][4], ["tva_immobilisations"])
                               for key in keys])
                for i, (when, supplier, keys, _payments) in enumerate(self.S.INVESTISSEMENTS) if m.contains(when)}

    def investment_settlements(self, m, moves):
        result = []
        for i, (when, _supplier, _keys, payments) in enumerate(self.S.INVESTISSEMENTS):
            if m.contains(when):
                move = moves[f"asset{i}"]
                result += [(move, day, self.j_bank, self.round(move.amount_total * share / 100) if share else None)
                           for day, share in payments]
        return result

    def sweep_entries(self, period_end, label, day_out, day_in, day_mobile):
        """Espèces et monnaie électronique du mois précédent virées en banque par le compte 585."""
        accounts = [self.cash] + ([self.om, self.mtn] if self.mobile_money else [])
        balances = self.balances(accounts, period_end)
        entries, mobile = [], 0
        cash = balances[self.cash]
        if cash > 0:
            entries += [(self.j_cash, day_out, f"Versement en banque des espèces de {label}",
                         [(self.transfer, cash, 0), (self.cash, 0, cash)]),
                        (self.j_bank, day_in, f"Versement en banque des espèces de {label}",
                         [(self.bank, cash, 0), (self.transfer, 0, cash)])]
        if self.mobile_money:
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

    def state_payment_entries(self, period_end, label, day):
        """Paiement des soldes créditeurs du mois précédent : déclaration I/TVA-IR, puis CNPS."""
        entries = []
        for codes, ref in ((COMPTES_DECLARATION, f"Paiement I/TVA-IR {label}"),
                           (COMPTES_CNPS, f"Cotisations CNPS {label}")):
            lines = [(code, -balance, 0) for code, balance in self.balances(codes, period_end).items() if balance < 0]
            total = sum(line[1] for line in lines)
            if total:
                entries.append((self.j_bank, day, ref, lines + [(self.bank, 0, total)]))
        return entries

    def loan_entries(self, day, label):
        loan = getattr(self.S, "EMPRUNT", None)
        if not loan:
            return []
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

    def payroll_entries(self, pay, day, label):
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

    def depreciation_entries(self, m):
        """Dotations du mois : 6812 pour les immobilisations incorporelles (amortissements 281), 6813 sinon."""
        lines = [(amort, 0, amount // duration) for _key, _name, _code, amort, amount, start, duration
                 in self.S.IMMOBILISATIONS if (m.year, m.month) >= start]
        charges = defaultdict(int)
        for amort, _debit, amount in lines:
            charges["6812" if amort.startswith("281") else "6813"] += amount
        debits = [(account, amount, 0) for account, amount in sorted(charges.items())]
        return [(self.j_misc, m.end, f"Dotations aux amortissements {m.label}", debits + lines)] if lines else []

    def inventory_entries(self, m):
        stock = self.S.INVENTAIRES.get(m.end)
        if not stock:
            return []
        return [(self.j_misc, m.end, f"Stock de marchandises au {m.end:%d/%m/%Y}",
                 [("3111", stock, 0), ("6031", 0, stock)])]

    def declare(self, m):
        """Déclaration I/TVA-IR du mois : calculée, liquidée et validée ; la dernière reste en brouillon."""
        # libellés des lignes L10 à L35 (l10n_cm) en français si la langue est installée ; le reste de la génération
        # écrit en anglais, langue source des champs traduisibles
        lang = "fr_FR" if self.env["res.lang"]._get_data(code="fr_FR") else "en_US"
        declaration = self.env["aite.cm.vat.declaration"].with_context(lang=lang).create(
            {"company_id": self.company.id, "date_from": m.first, "date_to": m.end})
        if self.dividends and m.contains(self.S.DIVIDENDES):
            declaration.action_compute()  # crée les lignes du formulaire
            declaration.itvair_line_ids.filtered(lambda l: l.code == "L57").base_input = self.dividends
        if m.last:
            declaration.action_compute()
            return declaration
        declaration.action_create_closing_entry()
        declaration.action_done()
        self.count += 1
        return declaration

    def opening_entries(self, year, day):
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

    def post_income_tax(self, year, day):
        """Impôt illustratif : TAUX_IS_ILLUSTRATIF du résultat avant impôt, au minimum les acomptes et précomptes de
        l'exercice."""
        result = self.engine.compute(self.company, date(year, 1, 1), day, ("resultat",))["resultat"]
        before_tax = result["XG"] + result.get("XH", 0.0)
        advances = {code: amount for code, amount in self.balances(COMPTES_ACOMPTES_IS, day).items() if amount > 0}
        tax = max(self.round(max(before_tax, 0.0) * self.S.TAUX_IS_ILLUSTRATIF), sum(advances.values()))
        self.post_entries([(self.j_misc, day, f"Impôt sur le résultat {year} (montant illustratif)",
                            [("8911", tax, 0), ("441", 0, tax)])])
        self.income_tax = (tax, advances)

    def income_tax_imputation(self, day):
        tax, advances = self.income_tax
        rest = tax - sum(advances.values())
        lines = [("441", tax, 0)] + [(code, 0, amount) for code, amount in advances.items()]
        journal = self.j_misc
        if rest > 0:
            lines.append((self.bank, 0, rest))
            journal = self.j_bank
        return (journal, day, f"Impôt sur le résultat {day.year - 1} : imputation des acomptes et précomptes", lines)

    def allocation_entries(self, day):
        """Affectation : réserve légale 10 %, dividendes (moitié arrondie à 10 000 près), report à nouveau."""
        result = self.result_previous
        if result <= 0:
            return []
        reserve = result // 10
        self.dividends = result // 2 // 10_000 * 10_000
        retained = result - reserve - self.dividends
        return [(self.j_misc, day, f"Affectation du résultat {day.year - 1} (assemblée générale du {day:%d/%m/%Y})",
                 [("131", result, 0), ("111", 0, reserve), ("465", 0, self.dividends), ("121", 0, retained)])]

    def dividend_entries(self, day):
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
