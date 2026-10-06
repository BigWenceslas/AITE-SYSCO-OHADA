# -*- coding: utf-8 -*-
"""À exécuter sur une base Odoo 18 Enterprise : compare le moteur de rapports Enterprise
au moteur de référence du module de base, sur le scénario chiffré à la main.
    odoo-bin -d <base> -i aite_syscohada_reports --test-enable --test-tags aite_syscohada_enterprise --stop-after-init
"""
from odoo.tests import tagged

from odoo.addons.aite_syscohada_base.tests.common import SyscohadaCommon


@tagged("post_install", "-at_install", "aite_syscohada_enterprise")
class TestEnterpriseReports(SyscohadaCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_reference_scenario()

    def report_values(self, statement, date_from, date_to):
        report = self.env.ref(f"aite_syscohada_reports.report_{statement}").with_company(self.company)
        if statement in ("actif", "passif"):
            date = {"date_to": date_to, "mode": "single", "filter": "custom"}
        else:
            date = {"date_from": date_from, "date_to": date_to, "mode": "range", "filter": "custom"}
        options = report.get_options({"date": date, "unfold_all": False})
        values = {}
        for line in report._get_lines(options):
            model, res_id = report._get_model_info_from_id(line["id"])
            if model != "account.report.line":
                continue
            code = self.env["account.report.line"].browse(res_id).code
            values[code] = {col["expression_label"]: col.get("no_format") or 0.0 for col in line["columns"]}
        return values

    def check_period(self, date_from, date_to):
        expected = self.compute(date_from, date_to)
        for statement in ("actif", "passif", "resultat", "flux"):
            got = self.report_values(statement, date_from, date_to)
            for code, value in expected[statement].items():
                if statement == "actif":
                    for label in ("brut", "amort", "net"):
                        self.assertAlmostEqual(got[code][label], value[label], places=0, msg=f"{statement} {code} {label}")
                else:
                    self.assertAlmostEqual(got[code]["balance"], value, places=0, msg=f"{statement} {code}")

    def test_n1(self):
        self.check_period("2025-01-01", "2025-12-31")

    def test_n(self):
        self.check_period("2026-01-01", "2026-12-31")
