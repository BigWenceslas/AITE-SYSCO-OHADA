# -*- coding: utf-8 -*-
import random
from datetime import date, timedelta

from odoo import Command
from odoo.tests import tagged

from odoo.addons.aite_syscohada_base.tests.common import SyscohadaCommon
from odoo.addons.aite_syscohada_base.tests.test_tft_properties import TEMPLATES
from odoo.addons.aite_syscohada_mis.models.mis_report import kpi_name
from odoo.addons.mis_builder.models.accounting_none import AccountingNone


@tagged("post_install", "-at_install", "aite_syscohada")
class TestMisTemplates(SyscohadaCommon):
    """Lot 1 Community : les modèles MIS donnent exactement les montants du moteur de référence."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reports = {s: cls.env.ref(f"aite_syscohada_mis.report_{s}") for s in ("actif", "passif", "resultat", "flux")}

    def mis_values(self, statement, date_from, date_to):
        instance = self.env["mis.report.instance"].create({
            "name": f"test {statement}", "report_id": self.reports[statement].id, "company_id": self.company.id,
            "period_ids": [Command.create({"name": "P", "mode": "fix", "manual_date_from": date_from,
                                           "manual_date_to": date_to})]})
        matrix = instance._compute_matrix()
        values = {}
        for row in matrix.iter_rows():
            if row.account_id:
                continue
            cells = {}
            for cell in row.iter_cells():
                if cell is None:
                    continue
                val = 0.0 if cell.val is AccountingNone or cell.val is None else cell.val
                self.assertIsInstance(val, (int, float), f"{row.kpi.name} : {val!r}")
                cells[cell.subcol.subkpi.name if cell.subcol.subkpi else "value"] = round(val, 2)
            values[row.kpi.name] = cells
        return values

    def compare(self, date_from, date_to, statements=("actif", "passif", "resultat", "flux")):
        expected = self.compute(date_from, date_to)
        for statement in statements:
            mis = self.mis_values(statement, date_from, date_to)
            for code, value in expected[statement].items():
                got = mis[kpi_name(statement, code)]
                if statement == "actif":
                    self.assertEqual(got, {"brut": value["brut"], "amort": value["amort"], "net": value["net"]},
                                     f"{date_to} {statement} {code}")
                else:
                    self.assertEqual(got.get("value", 0.0), value, f"{date_to} {statement} {code}")

    def test_templates_structure(self):
        Rub = self.env["aite.syscohada.rubrique"]
        for statement, report in self.reports.items():
            self.assertEqual(len(report.kpi_ids), Rub.search_count([("statement", "=", statement)]), statement)
        self.assertEqual(self.reports["actif"].subkpi_ids.mapped("name"), ["brut", "amort", "net"])
        kpi = self.reports["passif"].kpi_ids.filtered(lambda k: k.name == "p_cj")
        self.assertIn("balu[6%]", kpi.expression, "les résultats antérieurs non affectés restent dans CJ")
        kpi = self.reports["actif"].kpi_ids.filtered(lambda k: k.name == "a_am")
        self.assertIn("'!', ('code', '=like', '245%')", kpi.expression, "exclusions traduites en domaine")
        kpi = self.reports["passif"].kpi_ids.filtered(lambda k: k.name == "p_dj")
        self.assertEqual(kpi.expression, "(-nbale[40%])")

    def test_reference_scenario_matches_engine(self):
        self.create_reference_scenario()
        self.compare("2025-01-01", "2025-12-31")
        self.compare("2026-01-01", "2026-12-31")
        self.compare("2026-04-01", "2026-09-30")

    def test_random_ledger_matches_engine(self):
        """Bilan et résultat sur un grand livre aléatoire ; le TFT hors virements internes d'immobilisations."""
        rng = random.Random(42)
        names = sorted(n for n in TEMPLATES if n != "mise_en_service")
        for year in (2025, 2026):
            for _i in range(50):
                name = rng.choice(names)
                day = date(year, 1, 1) + timedelta(days=rng.randrange(0, 365))
                self.entry(day, TEMPLATES[name](rng.randrange(1000, 2000000, 500), self.bank), name)
        self.compare("2025-01-01", "2025-12-31")
        self.compare("2026-01-01", "2026-12-31")

    def test_rebuild_is_idempotent(self):
        before = {s: r.id for s, r in self.reports.items()}
        self.env["mis.report"]._aite_syscohada_build()
        after = {s: self.env.ref(f"aite_syscohada_mis.report_{s}").id for s in self.reports}
        self.assertEqual(before, after)
        self.assertEqual(len(self.reports["flux"].kpi_ids), 25)
