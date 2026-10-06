# -*- coding: utf-8 -*-
"""Formulaire I/TVA-IR complet (lot 2) : sections 0, 1 et 6 à 14, plus le récapitulatif.

Natures de ligne :
    credit / debit : mouvements de la période sur le compte de retenue dédié (créé par le socle)
    manual         : base × taux saisis ; manual_unit : base × tarif unitaire ; manual_amount : montant saisi
    acompte        : chiffre d'affaires déclaré (ligne L15) × taux de l'acompte
    vat            : TVA à payer de la déclaration (L32) ; carry : crédit L55 de la déclaration précédente
    formula        : combinaison des totaux des lignes précédentes
"""
from collections import defaultdict

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

S = lambda *codes: (lambda t: sum(t[c] for c in codes))  # noqa: E731

LINES = [
    # code, section, libellé, nature, compte, compte CAC, taux, CAC, formule
    ("L0", "0", "TSR sur rémunérations versées à l'étranger", "credit", "447120", None, None, False, None),
    ("L1", "1", "Chiffre d'affaires taxable au taux général des accises", "manual", None, None, 25.0, False, None),
    ("L2", "1", "Chiffre d'affaires taxable au taux réduit des accises", "manual", None, None, 12.5, False, None),
    ("L3", "1", "Droits d'accises ad valorem (L1 + L2)", "formula", None, None, None, False, S("L1", "L2")),
    ("L4", "1", "Droits d'accises spécifiques", "manual_amount", None, None, None, False, None),
    ("L5", "1", "Droits d'accises à reverser (L3 + L4)", "formula", None, None, None, False, S("L3", "L4")),
    ("L6", "1", "Droits d'accises payés à l'importation", "manual_amount", None, None, None, False, None),
    ("L8", "1", "Total des droits d'accises à payer (L5 − L6)", "formula", None, None, None, False,
     lambda t: max(t["L5"] - t["L6"], 0.0)),
    ("L36", "6", "TVA à payer (L32)", "vat", None, None, None, False, None),
    ("L37", "6", "TVA retenue à la source (entreprise habilitée)", "credit", "447160", None, None, False, None),
    ("L38", "6", "TVA retenue sur rémunérations versées à l'étranger", "credit", "447161", None, None, False, None),
    ("L39", "6", "Montant de TVA à payer (L36 + L37 + L38)", "formula", None, None, None, False, S("L36", "L37", "L38")),
    ("L40", "7", "Acompte sur chiffre d'affaires retenu à la source", "credit", "447170", None, None, False, None),
    ("L41", "7", "Précomptes sur achats retenus", "credit", "447180", None, None, False, None),
    ("L42", "7", "Précomptes sur loyers (15 %)", "credit", "447130", None, None, False, None),
    ("L43", "7", "Précomptes sur rémunérations et honoraires (5 %)", "credit", "447140", None, None, False, None),
    ("L44", "7", "Total des acomptes et précomptes à reverser", "formula", None, None, None, False, S("L40", "L41", "L42", "L43")),
    ("L45", "8", "Acompte sur chiffre d'affaires retenu à la source (subi)", "debit", "449220", None, None, False, None),
    ("L46", "8", "Précomptes sur achats (subis)", "debit", "449210", None, None, False, None),
    ("L47", "8", "Précomptes de 15 % sur loyers (subis)", "debit", "449230", None, None, False, None),
    ("L48", "8", "Précomptes sur rémunérations et honoraires (subis)", "debit", "449240", None, None, False, None),
    ("L49", "8", "Total des acomptes et précomptes à déduire", "formula", None, None, None, False, S("L45", "L46", "L47", "L48")),
    ("L50", "9", "Acompte sur chiffre d'affaires déclaré", "acompte", None, None, None, True, None),
    ("L51", "9", "Acompte de 15 % sur loyers perçus", "manual", None, None, 15.0, True, None),
    ("L52", "9", "Déductions à opérer (L49)", "formula", None, None, None, False, S("L49")),
    ("L53", "9", "Crédit antérieur (L55 de la déclaration précédente)", "carry", None, None, None, False, None),
    ("L54", "9", "Acompte à payer", "formula", None, None, None, False,
     lambda t: max(t["L50"] + t["L51"] - t["L52"] - t["L53"], 0.0)),
    ("L55", "9", "Crédit d'impôt à reporter", "formula", None, None, None, False,
     lambda t: max(t["L52"] + t["L53"] - t["L50"] - t["L51"], 0.0)),
    ("L56", "10", "Revenus des obligations", "manual", None, None, 15.0, True, None),
    ("L57", "10", "Revenus des actions, parts sociales et assimilés", "manual", None, None, 15.0, True, None),
    ("L58", "10", "Revenus des créances, dépôts et cautionnements", "manual", None, None, 15.0, True, None),
    ("L59", "10", "Gains sur cessions d'actions et d'obligations", "manual", None, None, 15.0, True, None),
    ("L60", "10", "Dividendes payés hors du Cameroun", "manual", None, None, 15.0, True, None),
    ("L61", "10", "Rémunérations des dirigeants et jetons de présence", "manual", None, None, 15.0, True, None),
    ("L62", "10", "Total de l'IRCM", "formula", None, None, None, False, S("L56", "L57", "L58", "L59", "L60", "L61")),
    ("L63", "11", "Rémunérations des sessions des conseils d'administration", "manual", None, None, 15.0, True, None),
    ("L64", "11", "Primes, indemnités et perdiem des commissions et comités", "manual", None, None, 15.0, True, None),
    ("L65", "11", "Rémunérations des artistes et sportifs", "manual", None, None, 15.0, True, None),
    ("L66", "11", "Total de l'IRNC", "formula", None, None, None, False, S("L63", "L64", "L65")),
    ("L67", "12", "IRPP sur traitements et salaires", "credit", "447210", "447215", None, False, None),
    ("L68", "12", "Crédit foncier du Cameroun, part salariale", "credit", "447220", None, None, False, None),
    ("L69", "12", "Crédit foncier du Cameroun, part patronale", "credit", "447230", None, None, False, None),
    ("L70", "12", "Fonds national de l'emploi", "credit", "447240", None, None, False, None),
    ("L71", "12", "Redevance audiovisuelle", "credit", "447250", None, None, False, None),
    ("L72", "12", "Taxe de développement local", "credit", "447260", None, None, False, None),
    ("L73", "12", "Total des impôts retenus sur salaires", "formula", None, None, None, False,
     S("L67", "L68", "L69", "L70", "L71", "L72")),
    ("L74", "13", "Plus-value immobilière des particuliers", "manual", None, None, 0.0, False, None),
    ("L75", "13", "Plus-value de cession de titres négociables", "manual", None, None, 0.0, False, None),
    ("L76", "13", "Plus-value de cession d'immobilisations", "manual", None, None, 0.0, False, None),
    ("L77", "13", "Total des impôts sur les plus-values", "formula", None, None, None, False, S("L74", "L75", "L76")),
    ("L78", "14", "Droit de timbre d'aéroport, vols internationaux (passagers × tarif)", "manual_unit", None, None, 10000.0, False, None),
    ("L79", "14", "Droit de timbre d'aéroport, vols nationaux (passagers × tarif)", "manual_unit", None, None, 1000.0, False, None),
    ("L80", "14", "Total du droit de timbre d'aéroport", "formula", None, None, None, False, S("L78", "L79")),
    ("TOTAL", "R", "Total à payer", "formula", None, None, None, False,
     S("L0", "L8", "L39", "L44", "L54", "L62", "L66", "L73", "L77", "L80")),
]
DEF = {l[0]: l for l in LINES}
SECTIONS = [
    ("0", "Taxe spéciale sur le revenu"), ("1", "Droits d'accises"), ("6", "TVA à payer"),
    ("7", "Acomptes et précomptes à reverser"), ("8", "Acomptes et précomptes à déduire"),
    ("9", "Liquidation des acomptes d'impôt sur le revenu"), ("10", "IRCM retenu à la source"),
    ("11", "IRNC retenu à la source"), ("12", "Impôts retenus sur salaires"), ("13", "Impôts sur les plus-values"),
    ("14", "Droit de timbre d'aéroport"), ("R", "Récapitulatif"),
]
EDITABLE = {"manual": ("base_input", "rate_input"), "manual_unit": ("base_input", "rate_input"),
            "manual_amount": ("amount_input",), "acompte": ("base_input",), "carry": ("amount_input",)}


class AiteCmItvairLine(models.Model):
    _name = "aite.cm.itvair.line"
    _description = "Ligne du formulaire I/TVA-IR (hors TVA)"
    _order = "sequence, id"

    declaration_id = fields.Many2one("aite.cm.vat.declaration", required=True, ondelete="cascade")
    currency_id = fields.Many2one(related="declaration_id.currency_id")
    sequence = fields.Integer()
    code = fields.Char("Ligne", readonly=True)
    section = fields.Selection(SECTIONS, readonly=True)
    name = fields.Char("Libellé", readonly=True)
    kind = fields.Char(readonly=True)
    base_input = fields.Monetary("Base saisie", help="Pour un acompte : laisser à zéro pour reprendre la ligne L15.")
    rate_input = fields.Float("Taux ou tarif", digits=(16, 4))
    amount_input = fields.Monetary("Montant saisi")
    penalty = fields.Monetary("Pénalités")
    base = fields.Monetary(readonly=True)
    rate = fields.Float(readonly=True, digits=(16, 4))
    principal = fields.Monetary(readonly=True)
    cac = fields.Monetary("CAC", readonly=True)
    total = fields.Monetary(readonly=True)
    editable = fields.Boolean(compute="_compute_editable")

    @api.depends("kind", "declaration_id.state")
    def _compute_editable(self):
        for line in self:
            line.editable = line.kind in EDITABLE and line.declaration_id.state == "draft"


class AiteCmVatDeclaration(models.Model):
    _inherit = "aite.cm.vat.declaration"

    itvair_line_ids = fields.One2many("aite.cm.itvair.line", "declaration_id", string="Formulaire I/TVA-IR")
    acompte_rate = fields.Float("Taux de l'acompte sur CA (%)", default=2.0, digits=(16, 4))
    cac_rate = fields.Float("Centimes additionnels communaux (%)", default=10.0, digits=(16, 4))
    date_due = fields.Date("Date limite de dépôt et de paiement", compute="_compute_date_due", store=True)
    acompte_to_pay = fields.Monetary("L54 – Acompte à payer", readonly=True)
    is_credit_to_report = fields.Monetary("L55 – Crédit d'acompte à reporter", readonly=True)
    total_to_pay = fields.Monetary("Total à payer", readonly=True)

    @api.depends("date_to")
    def _compute_date_due(self):
        for rec in self:
            rec.date_due = rec.date_to + relativedelta(months=1, day=15) if rec.date_to else False

    def _itvair_sync_lines(self):
        self.ensure_one()
        existing = {l.code for l in self.itvair_line_ids}
        values = [{"declaration_id": self.id, "sequence": i, "code": code, "section": section, "name": name, "kind": kind,
                   "rate_input": rate or 0.0}
                  for i, (code, section, name, kind, _a, _c, rate, _cac, _f) in enumerate(LINES) if code not in existing]
        if values:
            self.env["aite.cm.itvair.line"].create(values)

    def _itvair_ledger(self):
        """Débits, crédits et bases de taxe de la période sur les comptes de retenue."""
        codes = {c for l in LINES for c in (l[4], l[5]) if c}
        accounts = {code: self.company_id._aite_account(code) for code in codes}
        ids = [a.id for a in accounts.values() if a]
        AML = self.env["account.move.line"]
        domain = [("company_id", "=", self.company_id.id), ("parent_state", "=", "posted"),
                  ("date", ">=", self.date_from), ("date", "<=", self.date_to), ("account_id", "in", ids)]
        moves = {a.id: (d, c) for a, d, c in AML._read_group(domain, ["account_id"], ["debit:sum", "credit:sum"])}
        bases = defaultdict(float)
        for account, base in AML._read_group(domain + [("tax_line_id", "!=", False)], ["account_id"], ["tax_base_amount:sum"]):
            bases[account.id] += abs(base)
        return accounts, moves, bases

    def _itvair_compute(self, vat_value):
        self.ensure_one()
        self._itvair_sync_lines()
        accounts, moves, bases = self._itvair_ledger()
        lines = {l.code: l for l in self.itvair_line_ids}
        previous = self.search([("company_id", "=", self.company_id.id), ("state", "=", "done"),
                                ("date_to", "<", self.date_from), ("id", "!=", self.id)], order="date_to desc", limit=1)
        rnd = self.currency_id.round
        totals = {}
        for code, _section, _name, kind, acc_code, cac_code, _rate, with_cac, formula in LINES:
            line = lines[code]
            base, rate, principal, cac = 0.0, 0.0, 0.0, 0.0
            if kind in ("credit", "debit"):
                account = accounts.get(acc_code)
                debit, credit = moves.get(account.id, (0.0, 0.0)) if account else (0.0, 0.0)
                principal = credit if kind == "credit" else debit
                base = bases.get(account.id, 0.0) if account else 0.0
                if cac_code and accounts.get(cac_code):
                    cac = moves.get(accounts[cac_code].id, (0.0, 0.0))[1]
            elif kind in ("manual", "manual_unit"):
                base, rate = line.base_input, line.rate_input
                principal = base * rate / 100.0 if kind == "manual" else base * rate
            elif kind == "manual_amount":
                principal = line.amount_input
            elif kind == "acompte":
                base = max(line.base_input or vat_value("CM_GLOBAL", "base"), 0.0)  # un mois d'avoirs ne crée pas de crédit
                rate = self.acompte_rate
                principal = base * rate / 100.0
            elif kind == "vat":
                principal = self.vat_to_pay
            elif kind == "carry":
                carried = previous.itvair_line_ids.filtered(lambda l: l.code == "L55").total if previous else 0.0
                principal = line.amount_input or carried
            elif kind == "formula":
                principal = formula(totals)
            principal = rnd(principal)
            if with_cac:
                cac = rnd(principal * self.cac_rate / 100.0)
            total = rnd(principal + cac + line.penalty)
            totals[code] = total
            line.write({"base": rnd(base), "rate": rate, "principal": principal, "cac": cac, "total": total})
        self.write({"acompte_to_pay": totals["L54"], "is_credit_to_report": totals["L55"], "total_to_pay": totals["TOTAL"]})
        return totals

    def _itvair_lines_by_section(self):
        """Pour l'impression : [(libellé de section, lignes)]."""
        self.ensure_one()
        return [(label, self.itvair_line_ids.filtered(lambda l, s=section: l.section == s)) for section, label in SECTIONS]
