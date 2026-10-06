# -*- coding: utf-8 -*-
import re

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "aite_syscohada")
class TestReferential(TransactionCase):
    """Cohérence du référentiel des rubriques (structure, formules, cellules DSF)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rub = cls.env["aite.syscohada.rubrique"]
        cls.engine = cls.env["aite.syscohada.engine"]

    def codes(self, statement):
        return self.Rub.search([("statement", "=", statement)]).mapped("code")

    def test_counts(self):
        self.assertEqual(len(self.codes("actif")), 29)
        self.assertEqual(len(self.codes("passif")), 28)
        self.assertEqual(len(self.codes("resultat")), 42)
        self.assertEqual(len(self.codes("flux")), 25)

    def test_codes_unique_across_bilan(self):
        actif, passif = set(self.codes("actif")), set(self.codes("passif"))
        self.assertFalse(actif & passif, "un code ne peut être à la fois à l'actif et au passif")

    def test_formulas_and_aggregations(self):
        for statement in ("actif", "passif", "resultat", "flux"):
            rubriques = self.Rub.search([("statement", "=", statement)])
            codes = set(rubriques.mapped("code"))
            for rub in rubriques:
                if rub.line_type == "detail":
                    self.assertFalse(rub.aggregation, rub.code)
                    if statement == "actif":
                        self.assertTrue(rub.formula_brut, rub.code)
                        self.assertFalse(rub.formula, rub.code)
                    else:
                        self.assertTrue(rub.formula, rub.code)
                else:
                    self.assertFalse(rub.formula or rub.formula_brut or rub.formula_amort, rub.code)
                    for _sign, code in self.engine._parse_aggregation(rub.aggregation):
                        self.assertIn(code, codes, f"{rub.code} référence {code} absent de l'état {statement}")
            # pas de cycle : l'agrégation sur des zéros doit aboutir
            zeros = {r.code: (dict(brut=0.0, amort=0.0, net=0.0) if statement == "actif" else 0.0)
                     for r in rubriques if r.line_type == "detail"}
            values = self.engine._aggregate(rubriques, zeros, ("brut", "amort", "net") if statement == "actif" else None)
            self.assertEqual(set(values), codes)

    def test_key_totals(self):
        agg = {r.code: r.aggregation for r in self.Rub.search([("line_type", "!=", "detail")])}
        self.assertEqual(agg["BZ"], "AZ+BK+BT+BU")
        self.assertEqual(agg["DZ"], "DF+DP+DT+DV")
        self.assertEqual(agg["XI"], "XG+XH+RQ+RS")
        self.assertEqual(agg["ZH"], "ZA+ZG")

    def test_dsf_cells(self):
        seen = {}
        for rub in self.Rub.search([]):
            for field in ("dsf_cell", "dsf_cell_n1", "dsf_cell_brut", "dsf_cell_amort"):
                cell = rub[field]
                if not cell:
                    continue
                self.assertRegex(cell, r"^[A-Z]{1,2}\d{1,3}$")
                key = (rub.dsf_sheet, cell)
                self.assertNotIn(key, seen, f"cellule {key} utilisée par {seen.get(key)} et {rub.code}")
                seen[key] = rub.code
        bilan = self.Rub.search([("code", "=", "BG")])
        self.assertEqual(bilan.dsf_code, "BC")
        self.assertEqual(self.Rub.search([("code", "=", "DV")]).dsf_code, "DY")
        self.assertEqual(self.Rub.search([("code", "=", "XI")]).dsf_cell, "E52")

    def test_constraint_rejects_bad_formula(self):
        rub = self.Rub.search([("statement", "=", "passif"), ("code", "=", "CA")])
        with self.assertRaises(Exception):
            rub.formula = "-101\\(201)"
