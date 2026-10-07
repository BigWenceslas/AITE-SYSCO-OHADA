# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from ..models.syscohada_rubrique import STATEMENTS


class AiteSyscohadaStatementWizard(models.TransientModel):
    _name = "aite.syscohada.statement.wizard"
    _description = "États SYSCOHADA et contrôles"

    company_id = fields.Many2one("res.company", string="Société", required=True, default=lambda self: self.env.company)
    date_from = fields.Date("Du", required=True, default=lambda self: fields.Date.today().replace(month=1, day=1))
    date_to = fields.Date("Au", required=True, default=lambda self: fields.Date.today().replace(month=12, day=31))
    compare = fields.Boolean("Exercice N-1", default=True)
    line_ids = fields.One2many("aite.syscohada.statement.line", "wizard_id", string="Lignes")
    actif_line_ids = fields.One2many("aite.syscohada.statement.line", "wizard_id", domain=[("statement", "=", "actif")])
    passif_line_ids = fields.One2many("aite.syscohada.statement.line", "wizard_id", domain=[("statement", "=", "passif")])
    resultat_line_ids = fields.One2many("aite.syscohada.statement.line", "wizard_id", domain=[("statement", "=", "resultat")])
    flux_line_ids = fields.One2many("aite.syscohada.statement.line", "wizard_id", domain=[("statement", "=", "flux")])
    check_ids = fields.One2many("aite.syscohada.check.line", "wizard_id", string="Contrôles")
    computed = fields.Boolean(readonly=True)

    def _compute_display_name(self):
        for wizard in self:
            wizard.display_name = _("États et contrôles")

    def action_compute(self):
        self.ensure_one()
        engine = self.env["aite.syscohada.engine"]
        self.line_ids.unlink()
        self.check_ids.unlink()
        current = engine.compute(self.company_id, self.date_from, self.date_to)
        previous = {}
        if self.compare:
            previous = engine.compute(self.company_id, self.date_from - relativedelta(years=1),
                                      self.date_to - relativedelta(years=1))
        lines = []
        for rub in self.env["aite.syscohada.rubrique"].search([]):
            cur = current.get(rub.statement, {}).get(rub.code)
            prev = previous.get(rub.statement, {}).get(rub.code)
            vals = {"wizard_id": self.id, "statement": rub.statement, "sequence": rub.sequence, "code": rub.code,
                    "dsf_code": rub.dsf_code, "name": rub.name, "line_type": rub.line_type}
            if rub.statement == "actif":
                vals.update(brut=cur["brut"], amort=cur["amort"], net=cur["net"], net_n1=prev["net"] if prev else 0.0)
            else:
                vals.update(net=cur, net_n1=prev or 0.0)
            lines.append(vals)
        self.env["aite.syscohada.statement.line"].create(lines)
        checks = self.env["aite.syscohada.check"].run(self.company_id, self.date_from, self.date_to, results=current)
        self.env["aite.syscohada.check.line"].create([dict(c, wizard_id=self.id) for c in checks])
        self.computed = True
        return {"type": "ir.actions.act_window", "res_model": self._name, "res_id": self.id,
                "view_mode": "form", "target": "current", "context": self.env.context}


class AiteSyscohadaStatementLine(models.TransientModel):
    _name = "aite.syscohada.statement.line"
    _description = "Ligne d'état SYSCOHADA"
    _order = "sequence, id"

    wizard_id = fields.Many2one("aite.syscohada.statement.wizard", required=True, ondelete="cascade")
    statement = fields.Selection(STATEMENTS, required=True)
    sequence = fields.Integer()
    code = fields.Char("Réf")
    dsf_code = fields.Char("Réf DGI")
    name = fields.Char("Rubrique")
    line_type = fields.Selection([("detail", "Détail"), ("subtotal", "Sous-total"), ("total", "Total")])
    currency_id = fields.Many2one(related="wizard_id.company_id.currency_id")
    brut = fields.Monetary("Brut")
    amort = fields.Monetary("Amort. et dépréc.")
    net = fields.Monetary("Exercice N")
    net_n1 = fields.Monetary("Exercice N-1")


class AiteSyscohadaCheckLine(models.TransientModel):
    _name = "aite.syscohada.check.line"
    _description = "Résultat de contrôle SYSCOHADA"

    wizard_id = fields.Many2one("aite.syscohada.statement.wizard", required=True, ondelete="cascade")
    code = fields.Char("Contrôle")
    name = fields.Char("Libellé")
    level = fields.Selection([("ok", "Conforme"), ("info", "Information"), ("warning", "Alerte"), ("error", "Bloquant")],
                             string="Résultat")
    message = fields.Text("Détail")
