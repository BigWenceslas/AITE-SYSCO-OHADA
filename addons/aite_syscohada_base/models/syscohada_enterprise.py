# -*- coding: utf-8 -*-
"""Génération des rapports Odoo Enterprise (account.report) depuis le référentiel SYSCOHADA.

Le fichier XML produit est livré dans le module aite_syscohada_reports (dépend d'account_reports).
Il ne référence aucun identifiant Enterprise : il se charge aussi dans une base Community,
ce qui permet de le valider (schéma, champs, domaines) et d'en émuler le calcul dans les tests.
"""
from lxml import etree

from odoo import api, models

REPORTS = {
    "actif": ("SYSCOHADA – Bilan actif", False, [("brut", "Brut"), ("amort", "Amort. et dépréc."), ("net", "Net")]),
    "passif": ("SYSCOHADA – Bilan passif", False, [("balance", "Net")]),
    "resultat": ("SYSCOHADA – Compte de résultat", True, [("balance", "Net")]),
    "flux": ("SYSCOHADA – Tableau des flux de trésorerie", True, [("balance", "Montant")]),
}
LEVELS = {"total": 0, "subtotal": 1, "detail": 3}
DATE_SCOPE = {"end": "from_beginning", "start": "to_beginning_of_period", "period": "strict_range"}


def term_to_str(term, sign=1):
    s = term.sign * sign
    excl = f"\\({','.join(term.excluded)})" if term.excluded else ""
    return f"{'-' if s < 0 else '+'}{term.prefix}{excl}{term.balance_character}"


class AiteSyscohadaEnterprise(models.AbstractModel):
    _name = "aite.syscohada.enterprise"
    _description = "Générateur des rapports Enterprise SYSCOHADA"

    # ------------------------------------------------------------------ formules
    @api.model
    def _flatten(self, statement, code, sign=1):
        """Termes de comptes (avec signe) d'une rubrique, totaux développés ; actif = net."""
        engine = self.env["aite.syscohada.engine"]
        rub = self.env["aite.syscohada.rubrique"].search([("statement", "=", statement), ("code", "=", code)], limit=1)
        if not rub:
            raise ValueError(f"rubrique {statement}/{code} introuvable")
        if rub.line_type != "detail":
            out = []
            for sub_sign, sub in engine._parse_aggregation(rub.aggregation):
                out += self._flatten(statement, sub, sign * sub_sign)
            return out
        formulas = [rub.formula_brut, rub.formula_amort] if statement == "actif" else [rub.formula]
        out = []
        for formula in filter(None, formulas):
            out += [term_to_str(t, sign) for t in engine._parse_account_formula(formula)]
        return out

    @api.model
    def _bilan_statement(self, code):
        return "actif" if self.env["aite.syscohada.rubrique"].search_count(
            [("statement", "=", "actif"), ("code", "=", code)]) else "passif"

    @api.model
    def _domain(self, account_terms, side):
        clauses = []
        for term in account_terms:
            if term.sign < 0:
                raise ValueError("terme négatif interdit dans un argument D: ou C:")
            clause = [f"('account_id.code', '=like', '{term.prefix}%')"]
            clause += [f"'!', ('account_id.code', '=like', '{e}%')" for e in term.excluded]
            clauses.append(clause)
        parts = []
        for i, clause in enumerate(clauses):
            if i < len(clauses) - 1:
                parts.append("'|'")
            parts.append("'&', " * (len(clause) - 1) + ", ".join(clause) if len(clause) > 1 else clause[0])
        amount = "('debit', '>', 0)" if side == "D" else "('credit', '>', 0)"
        return "[" + ", ".join(parts + [amount]) + "]"

    @api.model
    def _flow_expressions(self, code, formula):
        """Expressions d'une ligne de flux et formule d'agrégation de sa valeur."""
        engine = self.env["aite.syscohada.engine"]
        expressions, combo = [], []

        def add(label, engine_name, expr_formula, date_scope, subformula=None, sign=1):
            expressions.append({"label": label, "engine": engine_name, "formula": expr_formula,
                                "date_scope": date_scope, "subformula": subformula})
            combo.append(f"{'-' if sign < 0 else '+'}{code}.{label}")

        for i, (sign, kind, arg, terms) in enumerate(engine._parse_flow_formula(formula), 1):
            label = f"t{i}"
            if kind == "R":
                add(label, "account_codes", "".join(self._flatten("resultat", arg)), DATE_SCOPE["period"], sign=sign)
            elif kind in ("B", "B0"):
                st = self._bilan_statement(arg)
                add(label, "account_codes", "".join(self._flatten(st, arg)),
                    DATE_SCOPE["end" if kind == "B" else "start"], sign=sign)
            elif kind == "V":
                st = self._bilan_statement(arg)
                flat = "".join(self._flatten(st, arg))
                add(label + "e", "account_codes", flat, DATE_SCOPE["end"], sign=sign)
                add(label + "s", "account_codes", flat, DATE_SCOPE["start"], sign=-sign)
            elif kind in ("P", "E", "S"):
                scope = {"P": "period", "E": "end", "S": "start"}[kind]
                add(label, "account_codes", "".join(term_to_str(t) for t in terms), DATE_SCOPE[scope], sign=sign)
            else:  # D, DX, C, CX : domaine sur les lignes (les virements internes ne sont pas neutralisés)
                side = "D" if kind in ("D", "DX") else "C"
                add(label, "domain", self._domain(terms, side), DATE_SCOPE["period"],
                    subformula="sum" if side == "D" else "-sum", sign=sign)
        aggregation = "".join(combo).lstrip("+")
        return expressions, aggregation

    # ------------------------------------------------------------------ XML
    @api.model
    def generate_xml(self):
        engine = self.env["aite.syscohada.engine"]
        root = etree.Element("odoo")
        def field(parent, name, text=None, **attrs):
            el = etree.SubElement(parent, "field", name=name, **attrs)
            if text is not None:
                el.text = text
            return el
        for statement, (title, date_range, columns) in REPORTS.items():
            rid = f"report_{statement}"
            rec = etree.SubElement(root, "record", id=rid, model="account.report")
            field(rec, "name", title)
            field(rec, "availability_condition", "always")
            field(rec, "filter_date_range", eval=str(date_range))
            field(rec, "filter_period_comparison", eval="True")
            field(rec, "filter_unfold_all", eval="False")
            field(rec, "default_opening_date_filter", "this_year")
            cols = field(rec, "column_ids")
            for seq, (label, name) in enumerate(columns, 1):
                col = etree.SubElement(cols, "record", id=f"{rid}_col_{label}", model="account.report.column")
                field(col, "name", name)
                field(col, "expression_label", label)
                field(col, "sequence", str(seq))
            lines = field(rec, "line_ids")
            for rub in self.env["aite.syscohada.rubrique"].search([("statement", "=", statement)]):
                line = etree.SubElement(lines, "record", id=f"{rid}_line_{rub.code}", model="account.report.line")
                field(line, "name", f"{rub.code} – {rub.name}")
                field(line, "code", rub.code)
                field(line, "sequence", str(rub.sequence))
                field(line, "hierarchy_level", str(LEVELS[rub.line_type]))
                exprs = field(line, "expression_ids")
                specs = []
                if rub.line_type != "detail":
                    terms = engine._parse_aggregation(rub.aggregation)
                    for label, _name in columns:
                        formula = "".join(f"{'-' if s < 0 else '+'}{c}.{label}" for s, c in terms).lstrip("+")
                        specs.append({"label": label, "engine": "aggregation", "formula": formula, "date_scope": None, "subformula": None})
                elif statement == "actif":
                    brut = engine._parse_account_formula(rub.formula_brut)
                    amort = engine._parse_account_formula(rub.formula_amort) if rub.formula_amort else []
                    end = DATE_SCOPE["end"]
                    specs.append({"label": "brut", "engine": "account_codes", "formula": "".join(term_to_str(t) for t in brut).lstrip("+"), "date_scope": end, "subformula": None})
                    if amort:
                        specs.append({"label": "amort", "engine": "account_codes", "formula": "".join(term_to_str(t, -1) for t in amort).lstrip("+"), "date_scope": end, "subformula": None})
                    else:
                        specs.append({"label": "amort", "engine": "aggregation", "formula": "0", "date_scope": None, "subformula": None})
                    specs.append({"label": "net", "engine": "account_codes", "formula": "".join(term_to_str(t) for t in brut + amort).lstrip("+"), "date_scope": end, "subformula": None})
                elif statement == "flux":
                    flow, aggregation = self._flow_expressions(rub.code, rub.formula)
                    specs += flow
                    specs.append({"label": "balance", "engine": "aggregation", "formula": aggregation, "date_scope": None, "subformula": None})
                else:
                    scope = DATE_SCOPE["period" if statement == "resultat" else "end"]
                    specs.append({"label": "balance", "engine": "account_codes", "formula": rub.formula, "date_scope": scope, "subformula": None})
                for spec in specs:
                    ex = etree.SubElement(exprs, "record", id=f"{rid}_line_{rub.code}_{spec['label']}", model="account.report.expression")
                    field(ex, "label", spec["label"])
                    field(ex, "engine", spec["engine"])
                    field(ex, "formula", spec["formula"])
                    if spec["subformula"]:
                        field(ex, "subformula", spec["subformula"])
                    if spec["date_scope"]:
                        field(ex, "date_scope", spec["date_scope"])
            action = etree.SubElement(root, "record", id=f"action_{rid}", model="ir.actions.client")
            field(action, "name", title)
            field(action, "tag", "account_report")
            field(action, "context", eval=f"{{'report_id': ref('{rid}')}}")
            etree.SubElement(root, "menuitem", id=f"menu_{rid}", name=title, action=f"action_{rid}",
                             parent="l10n_syscohada.account_reports_syscohada_statements_menu",
                             sequence=str(10 + list(REPORTS).index(statement)))
        return etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True).decode()
