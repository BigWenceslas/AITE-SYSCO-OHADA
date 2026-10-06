# -*- coding: utf-8 -*-
"""Traduction du référentiel SYSCOHADA en modèles MIS Builder.

Formule de comptes (syntaxe account_codes) -> expression MIS :
    terme sans D/C -> bal, D -> pbal (soldes positifs, compte par compte), C -> nbal
    mode e (fin de période) pour le bilan, p (période) pour le résultat, i (début) pour les ouvertures
    exclusions -> sélecteur sous forme de domaine sur account.account
    comptes de gestion (classes 6, 7, 8) en mode e ou i : on ajoute le mode u (résultats antérieurs
    non affectés) pour retrouver tout l'historique, comme le moteur du module de base.
Limite assumée : les virements internes au groupe (DX, CX) ne sont pas neutralisés par MIS.
"""
from odoo import Command, api, models

STATEMENT_NAMES = {
    "actif": "SYSCOHADA – Bilan actif",
    "passif": "SYSCOHADA – Bilan passif",
    "resultat": "SYSCOHADA – Compte de résultat",
    "flux": "SYSCOHADA – Tableau des flux de trésorerie",
}
PL_CLASSES = ("6", "7", "8")
FIELD_BY_CHAR = {"": "bal", "D": "pbal", "C": "nbal"}


def kpi_name(statement, code):
    return f"{statement[0]}_{code.lower()}"


class MisReport(models.Model):
    _inherit = "mis.report"

    # ------------------------------------------------------------------ traduction des formules
    @api.model
    def _aite_selector(self, term):
        if not term.excluded:
            return f"[{term.prefix}%]"
        parts = [f"('code', '=like', '{term.prefix}%')"]
        parts += [f"'!', ('code', '=like', '{excluded}%')" for excluded in term.excluded]
        return "[" + ", ".join(parts) + "]"

    @api.model
    def _aite_account_expr(self, formula, mode, field=None):
        engine = self.env["aite.syscohada.engine"]
        pieces = []
        for term in engine._parse_account_formula(formula):
            sign = "-" if term.sign < 0 else "+"
            fld = field or FIELD_BY_CHAR[term.balance_character]
            selector = self._aite_selector(term)
            pieces.append(f"{sign}{fld}{mode}{selector}")
            if mode in ("e", "i") and fld == "bal" and term.prefix.startswith(PL_CLASSES):
                pieces.append(f"{sign}balu{selector}")
        return "(" + "".join(pieces).lstrip("+") + ")"

    @api.model
    def _aite_rubrique_expr(self, statement, code, mode):
        """Expression complète d'une rubrique (les totaux sont développés)."""
        engine = self.env["aite.syscohada.engine"]
        rub = self.env["aite.syscohada.rubrique"].search([("statement", "=", statement), ("code", "=", code)], limit=1)
        if not rub:
            raise ValueError(f"rubrique {statement}/{code} introuvable")
        if rub.line_type != "detail":
            parts = []
            for sign, sub in engine._parse_aggregation(rub.aggregation):
                parts.append(("-" if sign < 0 else "+") + self._aite_rubrique_expr(statement, sub, mode))
            return "(" + "".join(parts).lstrip("+") + ")"
        if statement == "actif":
            expr = self._aite_account_expr(rub.formula_brut, mode)
            if rub.formula_amort:
                expr = f"({expr}+{self._aite_account_expr(rub.formula_amort, mode)})"
            return expr
        return self._aite_account_expr(rub.formula, mode)

    @api.model
    def _aite_bilan_expr(self, code, mode):
        statement = "actif" if self.env["aite.syscohada.rubrique"].search_count(
            [("statement", "=", "actif"), ("code", "=", code)]) else "passif"
        return self._aite_rubrique_expr(statement, code, mode)

    @api.model
    def _aite_flow_expr(self, formula):
        engine = self.env["aite.syscohada.engine"]
        pieces = []
        for sign, kind, arg, _terms in engine._parse_flow_formula(formula):
            if kind == "R":
                expr = self._aite_rubrique_expr("resultat", arg, "p")
            elif kind == "B":
                expr = self._aite_bilan_expr(arg, "e")
            elif kind == "B0":
                expr = self._aite_bilan_expr(arg, "i")
            elif kind == "V":
                expr = f"({self._aite_bilan_expr(arg, 'e')}-{self._aite_bilan_expr(arg, 'i')})"
            elif kind == "P":
                expr = self._aite_account_expr(arg, "p")
            elif kind == "E":
                expr = self._aite_account_expr(arg, "e")
            elif kind == "S":
                expr = self._aite_account_expr(arg, "i")
            elif kind in ("D", "DX"):
                expr = self._aite_account_expr(arg, "p", field="deb")
            else:  # C, CX
                expr = self._aite_account_expr(arg, "p", field="crd")
            pieces.append(("-" if sign < 0 else "+") + expr)
        return "".join(pieces).lstrip("+")

    # ------------------------------------------------------------------ construction des modèles
    @api.model
    def _aite_total_style(self):
        style = self.env.ref("aite_syscohada_mis.style_total", raise_if_not_found=False)
        if not style:
            style = self.env["mis.report.style"].create({
                "name": "SYSCOHADA – total", "font_weight_inherit": False, "font_weight": "bold"})
            self.env["ir.model.data"].create({"module": "aite_syscohada_mis", "name": "style_total",
                                              "model": style._name, "res_id": style.id, "noupdate": True})
        return style

    @api.model
    def _aite_syscohada_build(self):
        style = self._aite_total_style()
        reports = self.browse()
        for statement in ("actif", "passif", "resultat", "flux"):
            reports |= self._aite_build_statement(statement, style)
        return reports

    @api.model
    def _aite_build_statement(self, statement, style):
        xmlid = f"aite_syscohada_mis.report_{statement}"
        report = self.env.ref(xmlid, raise_if_not_found=False)
        if not report:
            report = self.create({"name": STATEMENT_NAMES[statement], "description": "Généré depuis le référentiel AITE"})
            self.env["ir.model.data"].create({"module": "aite_syscohada_mis", "name": f"report_{statement}",
                                              "model": "mis.report", "res_id": report.id, "noupdate": True})
        report.kpi_ids.unlink()
        report.subkpi_ids.unlink()
        subkpis = {}
        if statement == "actif":
            for seq, (name, label) in enumerate((("brut", "Brut"), ("amort", "Amort. et dépréc."), ("net", "Net")), 1):
                subkpis[name] = self.env["mis.report.subkpi"].create(
                    {"report_id": report.id, "name": name, "description": label, "sequence": seq})
        accumulation = "none" if statement in ("actif", "passif") else "sum"
        engine = self.env["aite.syscohada.engine"]
        for rub in self.env["aite.syscohada.rubrique"].search([("statement", "=", statement)]):
            vals = {"report_id": report.id, "name": kpi_name(statement, rub.code),
                    "description": f"{rub.code} – {rub.name}", "sequence": rub.sequence,
                    "accumulation_method": accumulation, "compare_method": "diff",
                    "style_id": style.id if rub.line_type != "detail" else False}
            if rub.line_type != "detail":
                vals["expression"] = " + ".join(
                    ("-" if sign < 0 else "") + kpi_name(statement, sub) for sign, sub in engine._parse_aggregation(rub.aggregation)
                ).replace("+ -", "- ")
            elif statement == "actif":
                brut = self._aite_account_expr(rub.formula_brut, "e")
                amort = self._aite_account_expr(rub.formula_amort, "e") if rub.formula_amort else "0"
                vals["multi"] = True
                vals["expression_ids"] = [
                    Command.create({"subkpi_id": subkpis["brut"].id, "name": brut}),
                    Command.create({"subkpi_id": subkpis["amort"].id, "name": f"-{amort}"}),
                    Command.create({"subkpi_id": subkpis["net"].id, "name": f"{brut}+{amort}"}),
                ]
            elif statement == "flux":
                vals["expression"] = self._aite_flow_expr(rub.formula)
            else:
                vals["expression"] = self._aite_account_expr(rub.formula, "p" if statement == "resultat" else "e")
            self.env["mis.report.kpi"].create(vals)
        return report
