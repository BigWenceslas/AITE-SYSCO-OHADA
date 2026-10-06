# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

STATEMENTS = [
    ("actif", "Bilan actif"),
    ("passif", "Bilan passif"),
    ("resultat", "Compte de résultat"),
    ("flux", "Tableau des flux de trésorerie"),
]


class AiteSyscohadaRubrique(models.Model):
    """Rubrique d'un état SYSCOHADA : la seule source des correspondances comptes → états."""

    _name = "aite.syscohada.rubrique"
    _description = "Rubrique des états financiers SYSCOHADA"
    _order = "sequence, id"

    statement = fields.Selection(STATEMENTS, string="État", required=True, index=True)
    code = fields.Char(required=True, index=True)
    name = fields.Char(string="Libellé", required=True)
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(
        [("detail", "Détail"), ("subtotal", "Sous-total"), ("total", "Total")],
        string="Type de ligne", default="detail", required=True)
    formula = fields.Char(
        string="Formule",
        help="Passif et compte de résultat : formule de comptes au format « account_codes » d'Odoo Enterprise "
             "(ex. -40C, 24\\(245,2495)). Flux : formule du moteur (R:, B:, V:, P:, E:, S:, D:, C:, DX:, CX:).")
    formula_brut = fields.Char(string="Formule brut", help="Actif : comptes du montant brut.")
    formula_amort = fields.Char(string="Formule amortissements et dépréciations", help="Actif : comptes soustraits du brut.")
    aggregation = fields.Char(string="Agrégation", help="Somme de rubriques du même état, ex. AE+AF+AG+AH.")
    note = fields.Char(string="Note DSF")
    dsf_code = fields.Char(string="Code du classeur DGI")
    dsf_sheet = fields.Char(string="Onglet DSF")
    dsf_cell_brut = fields.Char(string="Cellule brut")
    dsf_cell_amort = fields.Char(string="Cellule amortissements")
    dsf_cell = fields.Char(string="Cellule N")
    dsf_cell_n1 = fields.Char(string="Cellule N-1")
    dsf_sign = fields.Integer(string="Signe DSF", default=1,
                              help="-1 lorsque le classeur DGI attend une charge en valeur positive.")

    _sql_constraints = [
        ("statement_code_uniq", "unique(statement, code)", "Le code d'une rubrique doit être unique dans son état."),
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code} – {rec.name}" if rec.code else rec.name

    @api.constrains("formula", "formula_brut", "formula_amort", "aggregation", "statement", "line_type")
    def _check_formulas(self):
        engine = self.env["aite.syscohada.engine"]
        for rec in self:
            if rec.line_type == "detail" and not (rec.formula or rec.formula_brut or rec.formula_amort):
                raise ValidationError(_("La rubrique %s n'a pas de formule.", rec.code))
            if rec.line_type != "detail" and not rec.aggregation:
                raise ValidationError(_("Le total %s n'a pas d'agrégation.", rec.code))
            try:
                if rec.statement in ("actif", "passif", "resultat"):
                    for f in (rec.formula, rec.formula_brut, rec.formula_amort):
                        if f:
                            engine._parse_account_formula(f)
                elif rec.formula:
                    engine._parse_flow_formula(rec.formula)
                if rec.aggregation:
                    engine._parse_aggregation(rec.aggregation)
            except ValueError as e:
                raise ValidationError(_("Formule invalide pour %(code)s : %(err)s", code=rec.code, err=e)) from e
