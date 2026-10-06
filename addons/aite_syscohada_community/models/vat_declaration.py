# -*- coding: utf-8 -*-
"""Déclaration mensuelle de TVA (Cameroun, formulaire I/TVA-IR, lignes L10 à L35) pour Odoo Community.

Le calcul lit la définition officielle du rapport de TVA du module l10n_cm (présente dans Community) :
    tax_tags    : montants des lignes d'écritures exigibles portant les étiquettes de taxe
    external    : saisies du déclarant (accises L11, régularisations L24 à L27, remboursement L34)
                  et crédit antérieur L17 (reprise de la ligne L35 de la déclaration précédente)
    aggregation : formules de la DGI, avec plancher à zéro (if_above)
L'écriture de liquidation reproduit la « clôture de TVA » d'Enterprise.
"""
import re
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

AGG_TERM = re.compile(r"([+-]?)\s*([A-Z0-9_]+)\.(\w+)")
IF_ABOVE = re.compile(r"^if_above\(\w+\((-?[\d.]+)\)\)$")
MANUAL = {
    ("CM_EXCISE", "base"): "excise_base", ("CM_EXCISE", "tax"): "excise_tax",
    ("CM_ADJUSTMENT_DEDUCTIBLE", "tax"): "adj_deductible", ("CM_ADJUSTMENT_STATE", "tax"): "adj_state",
    ("CM_ADJUSTMENT_FIXED", "tax"): "adj_fixed", ("CM_ADJUSTMENT_OTHER", "tax"): "adj_other",
    ("CM_REIMBURSEMENT", "tax"): "reimbursement",
    ("CM_CREDIT_REPORTED", "_applied_carryover_tax"): "credit_previous",
}


class AiteCmVatDeclaration(models.Model):
    _name = "aite.cm.vat.declaration"
    _description = "Déclaration mensuelle de TVA (Cameroun)"
    _order = "date_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    date_from = fields.Date("Du", required=True,
                            default=lambda self: fields.Date.today().replace(day=1) - relativedelta(months=1))
    date_to = fields.Date("Au", required=True,
                          default=lambda self: fields.Date.today().replace(day=1) - relativedelta(days=1))
    state = fields.Selection([("draft", "Brouillon"), ("done", "Validée")], default="draft", required=True)
    line_ids = fields.One2many("aite.cm.vat.declaration.line", "declaration_id", string="Lignes")
    # saisies du déclarant (lignes « external » du rapport l10n_cm)
    excise_base = fields.Monetary("L11 – Droits d'accises (base)")
    excise_tax = fields.Monetary("L11 – Droits d'accises (taxe)")
    adj_deductible = fields.Monetary("L24 – Régularisation de TVA déductible ou retenue à la source")
    adj_state = fields.Monetary("L25 – Régularisation de TVA prise en charge par l'État")
    adj_fixed = fields.Monetary("L26 – Régularisation sur cession d'immobilisations")
    adj_other = fields.Monetary("L27 – Régularisation de TVA à reverser et autres")
    reimbursement = fields.Monetary("L34 – Remboursement demandé")
    credit_previous = fields.Monetary("L17 – Crédit antérieur", compute="_compute_credit_previous", store=True,
                                      readonly=False, help="Repris de la ligne L35 de la déclaration validée précédente.")
    adjustment_account_id = fields.Many2one("account.account", string="Compte de contrepartie des régularisations",
                                            check_company=True)
    # résultats
    vat_collected = fields.Monetary("L28 – TVA collectée", readonly=True)
    vat_deductible = fields.Monetary("L29 – TVA déductible", readonly=True)
    vat_to_pay = fields.Monetary("L32 – TVA à payer", readonly=True)
    vat_credit = fields.Monetary("L33 – Crédit de TVA", readonly=True)
    credit_to_report = fields.Monetary("L35 – Crédit à reporter", readonly=True)
    move_id = fields.Many2one("account.move", string="Écriture de liquidation", readonly=True, copy=False)

    _sql_constraints = [("period_uniq", "unique(company_id, date_from, date_to)",
                         "Une déclaration existe déjà pour cette période.")]

    @api.depends("date_from", "date_to")
    def _compute_name(self):
        for rec in self:
            rec.name = _("TVA %(start)s – %(end)s", start=rec.date_from, end=rec.date_to) if rec.date_from else "/"

    @api.depends("company_id", "date_from")
    def _compute_credit_previous(self):
        for rec in self:
            previous = self.search([("company_id", "=", rec.company_id.id), ("state", "=", "done"),
                                    ("date_to", "<", rec.date_from or fields.Date.today())], order="date_to desc", limit=1)
            rec.credit_previous = previous.credit_to_report if previous else 0.0

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(_("La date de début doit précéder la date de fin."))

    # ------------------------------------------------------------------ calcul
    def _tag_amounts(self):
        """Montants par étiquette (sans signe) sur les lignes exigibles de la période."""
        self.ensure_one()
        AML = self.env["account.move.line"]
        domain = [("company_id", "=", self.company_id.id), ("parent_state", "=", "posted"),
                  ("date", ">=", self.date_from), ("date", "<=", self.date_to), ("tax_tag_ids", "!=", False)]
        domain += AML._get_tax_exigible_domain()
        amounts = defaultdict(float)
        for line in AML.search(domain):
            for tag in line.tax_tag_ids:
                sign = (-1 if tag.tax_negate else 1) * (-1 if line.tax_tag_invert else 1)
                amounts[tag.name.lstrip("+-")] += sign * line.balance
        return amounts

    def _evaluate(self):
        self.ensure_one()
        report = self.env.ref("l10n_cm.account_tax_report_cm")
        tags = self._tag_amounts()
        lines = {line.code: line for line in report.line_ids if line.code}
        cache = {}

        def value(code, label, stack=()):
            key = (code, label)
            if key in cache:
                return cache[key]
            if key in stack:
                raise UserError(_("Formule circulaire dans le rapport de TVA : %s", key))
            expr = lines[code].expression_ids.filtered(lambda e: e.label == label) if code in lines else None
            if not expr:
                result = 0.0
            elif expr.engine == "tax_tags":
                result = tags.get(expr.formula, 0.0)
            elif expr.engine == "external":
                field = MANUAL.get(key)
                result = self[field] if field else 0.0
            elif expr.engine == "aggregation":
                result = sum((-1 if sign == "-" else 1) * value(c, l, stack + (key,))
                             for sign, c, l in AGG_TERM.findall(expr.formula))
                bound = IF_ABOVE.match(expr.subformula or "")
                if bound and result <= float(bound.group(1)):
                    result = 0.0
            else:
                raise UserError(_("Moteur de calcul non géré : %s", expr.engine))
            result = self.currency_id.round(result)
            cache[key] = result
            return result

        rows = []
        for line in report.line_ids.sorted(lambda l: (l.sequence, l.id)):
            labels = set(line.expression_ids.mapped("label"))
            rows.append({
                "sequence": line.sequence, "code": line.code, "name": line.name, "level": line.hierarchy_level,
                "base": value(line.code, "base") if "base" in labels else 0.0,
                "tax": value(line.code, "tax") if "tax" in labels else 0.0,
                "has_base": "base" in labels, "has_tax": "tax" in labels,
            })
        return rows, value

    def action_compute(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("Déclaration validée : remettez-la en brouillon pour la recalculer."))
            rows, value = rec._evaluate()
            rec.line_ids.unlink()
            rec.line_ids = [Command.create({k: v for k, v in row.items()}) for row in rows]
            rec.write({
                "vat_collected": value("CM_COLLECTED", "tax"), "vat_deductible": value("CM_DEDUCTIBLE_VAT_29", "tax"),
                "vat_to_pay": value("CM_VAT_TO_PAY", "tax"), "vat_credit": value("CM_CREDIT", "tax"),
                "credit_to_report": value("CM_CREDIT_REPORT", "tax"),
            })
            rec._itvair_compute(value)
        return True

    # ------------------------------------------------------------------ liquidation
    def _closing_balances(self):
        """Soldes de la période par compte de TVA (lignes de taxe exigibles sur les comptes 443 et 445)."""
        self.ensure_one()
        AML = self.env["account.move.line"]
        transition = self.env["account.tax"].with_context(active_test=False).search(
            [("company_id", "=", self.company_id.id)]).cash_basis_transition_account_id
        domain = [("company_id", "=", self.company_id.id), ("parent_state", "=", "posted"),
                  ("date", ">=", self.date_from), ("date", "<=", self.date_to),
                  ("tax_line_id", "!=", False), ("account_id", "not in", transition.ids), "|",
                  ("account_id.code", "=like", "443%"), ("account_id.code", "=like", "445%")]
        domain += AML._get_tax_exigible_domain()
        balances = defaultdict(float)
        for account, balance in AML._read_group(domain, ["account_id"], ["balance:sum"]):
            balances[account] += balance
        return balances

    def action_create_closing_entry(self):
        self.ensure_one()
        if self.move_id:
            raise UserError(_("L'écriture de liquidation existe déjà."))
        self.action_compute()
        company = self.company_id
        acc = company._aite_account
        due, credit_acc, refund = acc("4441"), acc("4449"), acc("4445")
        if not (due and credit_acc and refund):
            raise UserError(_("Comptes 4441, 4449 ou 4445 introuvables."))
        lines = []

        def add(account, amount, label):
            if not float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                lines.append({"account_id": account.id, "name": label,
                              "debit": amount if amount > 0 else 0.0, "credit": -amount if amount < 0 else 0.0})

        for account, balance in self._closing_balances().items():
            add(account, -balance, _("Liquidation de la TVA"))
        add(credit_acc, -self.credit_previous, _("L17 – Crédit antérieur imputé"))
        add(due, -self.vat_to_pay, _("L32 – TVA à payer"))
        add(credit_acc, self.credit_to_report, _("L35 – Crédit à reporter"))
        add(refund, self.reimbursement, _("L34 – Remboursement demandé"))
        imbalance = sum(l["debit"] - l["credit"] for l in lines)
        manual = self.excise_tax + self.adj_fixed + self.adj_other - self.adj_deductible - self.adj_state
        # sans régularisation manuelle, le grand livre doit coïncider exactement avec la déclaration
        if float_compare(imbalance, -manual, precision_rounding=self.currency_id.rounding) != 0:
            raise UserError(_("Écart de %(gap)s entre le grand livre et la déclaration : vérifiez les étiquettes de taxe.",
                              gap=imbalance + manual))
        if not float_is_zero(imbalance, precision_rounding=self.currency_id.rounding):
            if not self.adjustment_account_id:
                raise UserError(_("Renseignez le compte de contrepartie des régularisations (L11, L24 à L27)."))
            add(self.adjustment_account_id, -imbalance, _("Régularisations de la déclaration"))
        if not float_is_zero(self.acompte_to_pay, precision_rounding=self.currency_id.rounding):
            advance, payable = acc("449250"), acc("441100")
            if not (advance and payable):
                raise UserError(_("Comptes 449250 ou 441100 introuvables : appliquez le paramétrage SYSCOHADA."))
            add(advance, self.acompte_to_pay, _("L54 – Acompte d'impôt sur le résultat"))
            add(payable, -self.acompte_to_pay, _("L54 – Acompte d'impôt sur le résultat à payer"))
        if not lines:
            raise UserError(_("Rien à liquider pour cette période."))
        journal = self.env["account.journal"].search([("company_id", "=", company.id), ("type", "=", "general")], limit=1)
        move = self.env["account.move"].create({
            "move_type": "entry", "journal_id": journal.id, "date": self.date_to, "company_id": company.id,
            "ref": self.name, "line_ids": [Command.create(l) for l in lines]})
        move.action_post()
        self.move_id = move
        return move

    def action_done(self):
        for rec in self:
            if not rec.line_ids:
                rec.action_compute()
            rec.state = "done"

    def action_draft(self):
        for rec in self:
            later = self.search([("company_id", "=", rec.company_id.id), ("state", "=", "done"), ("date_from", ">", rec.date_to)], limit=1)
            if later:
                raise UserError(_("Une déclaration ultérieure est validée : son crédit antérieur dépend de celle-ci."))
            rec.state = "draft"

    def action_open_move(self):
        self.ensure_one()
        return {"type": "ir.actions.act_window", "res_model": "account.move", "res_id": self.move_id.id, "view_mode": "form"}


class AiteCmVatDeclarationLine(models.Model):
    _name = "aite.cm.vat.declaration.line"
    _description = "Ligne de déclaration de TVA (Cameroun)"
    _order = "sequence, id"

    declaration_id = fields.Many2one("aite.cm.vat.declaration", required=True, ondelete="cascade")
    currency_id = fields.Many2one(related="declaration_id.currency_id")
    sequence = fields.Integer()
    code = fields.Char()
    name = fields.Char("Ligne")
    level = fields.Integer()
    base = fields.Monetary("Base")
    tax = fields.Monetary("Taxe")
    has_base = fields.Boolean()
    has_tax = fields.Boolean()
