# -*- coding: utf-8 -*-
import ast
import os
import random
import re
import tempfile
from datetime import date, timedelta

from odoo import fields
from odoo.modules.module import get_module_path
from odoo.tests import tagged
from odoo.tools.convert import convert_xml_import

from .common import SyscohadaCommon
from .test_tft_properties import TEMPLATES

AGG_TERM = re.compile(r"([+-]?)([A-Z][A-Z0-9]*)\.(\w+)")


@tagged("post_install", "-at_install", "aite_syscohada")
class TestEnterpriseReportsXml(SyscohadaCommon):
    """Lot 1 Enterprise : le XML généré se charge avec le chargeur d'Odoo (schéma, champs, domaines)
    et, émulé ici, donne les montants du moteur de référence."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.xml = cls.env["aite.syscohada.enterprise"].generate_xml()
        with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as handle:
            handle.write(cls.xml)
            path = handle.name
        try:
            convert_xml_import(cls.env, "aite_syscohada_reports", path, idref={}, mode="init")
        finally:
            os.unlink(path)
        cls.reports = {s: cls.env.ref(f"aite_syscohada_reports.report_{s}") for s in ("actif", "passif", "resultat", "flux")}

    # ------------------------------------------------------------------ émulation des moteurs Enterprise
    def emulate(self, statement, date_from, date_to):
        engine = self.engine
        date_from, date_to = fields.Date.to_date(date_from), fields.Date.to_date(date_to)
        codes = engine._account_codes(self.company)
        balances = {
            "from_beginning": engine._balances(self.company, date_to=date_to, codes=codes),
            "to_beginning_of_period": engine._balances(self.company, date_to=date_from - timedelta(days=1), codes=codes),
            "strict_range": engine._balances(self.company, date_to=date_to, date_from=date_from, codes=codes),
        }
        report = self.reports[statement]
        values = {}

        def leaf(expr):
            if expr.engine == "account_codes":
                return engine._eval_account_terms(engine._parse_account_formula(expr.formula), balances[expr.date_scope])
            if expr.engine == "domain":
                domain = ast.literal_eval(expr.formula) + engine._aml_domain(self.company, date_to, date_from)
                total = self.env["account.move.line"]._read_group(domain, [], ["balance:sum"])[0][0]
                return -total if expr.subformula == "-sum" else total
            raise AssertionError(f"moteur inattendu {expr.engine}")

        def value(code, label, stack=()):
            key = (code, label)
            if key in values:
                return values[key]
            self.assertNotIn(key, stack, f"cycle {key}")
            line = report.line_ids.filtered(lambda l: l.code == code)
            self.assertTrue(line, f"ligne {code} absente de {report.name}")
            expr = line.expression_ids.filtered(lambda e: e.label == label)
            self.assertEqual(len(expr), 1, f"{code}.{label}")
            if expr.engine == "aggregation":
                if expr.formula.strip() == "0":
                    result = 0.0
                else:
                    terms = AGG_TERM.findall(expr.formula.replace(" ", ""))
                    self.assertEqual("".join(f"{s}{c}.{l}" for s, c, l in terms), expr.formula.replace(" ", ""))
                    result = sum((-1 if s == "-" else 1) * value(c, l, stack + (key,)) for s, c, l in terms)
            else:
                result = leaf(expr)
            values[key] = result
            return result

        labels = report.column_ids.mapped("expression_label")
        return {line.code: {label: round(value(line.code, label), 2) for label in labels} for line in report.line_ids}

    def compare(self, date_from, date_to, statements=("actif", "passif", "resultat", "flux")):
        expected = self.compute(date_from, date_to)
        for statement in statements:
            got = self.emulate(statement, date_from, date_to)
            for code, val in expected[statement].items():
                if statement == "actif":
                    self.assertEqual(got[code], {"brut": val["brut"], "amort": val["amort"], "net": val["net"]}, f"{date_to} {code}")
                else:
                    self.assertEqual(got[code]["balance"], val, f"{date_to} {statement} {code}")

    # ------------------------------------------------------------------ tests
    def test_structure(self):
        Rub = self.env["aite.syscohada.rubrique"]
        for statement, report in self.reports.items():
            self.assertEqual(len(report.line_ids), Rub.search_count([("statement", "=", statement)]), statement)
            for expr in report.line_ids.expression_ids:
                self.assertIn(expr.engine, ("account_codes", "domain", "aggregation"))
                if expr.engine == "account_codes":
                    self.engine._parse_account_formula(expr.formula)  # syntaxe du moteur Enterprise
                    self.assertIn(expr.date_scope, ("from_beginning", "to_beginning_of_period", "strict_range"))
        self.assertEqual(self.reports["actif"].column_ids.mapped("expression_label"), ["brut", "amort", "net"])
        self.assertFalse(self.reports["actif"].filter_date_range)
        self.assertTrue(self.reports["resultat"].filter_date_range)
        cj = self.reports["passif"].line_ids.filtered(lambda l: l.code == "CJ").expression_ids
        self.assertEqual((cj.formula, cj.date_scope), ("-13-6-7-8-999999", "from_beginning"))
        action = self.env.ref("aite_syscohada_reports.action_report_actif")
        self.assertEqual(action.tag, "account_report")
        self.assertIn(str(self.reports["actif"].id), action.context)

    def test_reference_scenario(self):
        self.create_reference_scenario()
        self.compare("2025-01-01", "2025-12-31")
        self.compare("2026-01-01", "2026-12-31")
        self.compare("2026-04-01", "2026-09-30")

    def test_random_ledger(self):
        rng = random.Random(1789)
        names = sorted(n for n in TEMPLATES if n != "mise_en_service")
        for year in (2025, 2026):
            for _i in range(50):
                name = rng.choice(names)
                day = date(year, 1, 1) + timedelta(days=rng.randrange(0, 365))
                self.entry(day, TEMPLATES[name](rng.randrange(1000, 2000000, 500), self.bank), name)
        self.compare("2025-01-01", "2025-12-31")
        self.compare("2026-01-01", "2026-12-31")

    def test_shipped_file_is_up_to_date(self):
        path = get_module_path("aite_syscohada_reports", display_warning=False)
        if not path:
            self.skipTest("module aite_syscohada_reports absent : installation Community seule")
        with open(os.path.join(path, "data", "syscohada_reports.xml"), encoding="utf-8") as handle:
            self.assertEqual(handle.read(), self.xml, "régénérer le XML : tools/generate_enterprise_xml.py")
