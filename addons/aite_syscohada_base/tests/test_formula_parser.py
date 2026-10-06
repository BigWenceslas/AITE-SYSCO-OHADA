# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from ..models.syscohada_engine import _split_top_level


@tagged("post_install", "-at_install", "aite_syscohada")
class TestFormulaParser(TransactionCase):
    """Syntaxe des formules : alignée sur le moteur « account_codes » d'Odoo Enterprise."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.engine = cls.env["aite.syscohada.engine"]

    def parse(self, formula):
        return [(t.sign, t.prefix, t.excluded, t.balance_character) for t in self.engine._parse_account_formula(formula)]

    def test_simple_terms(self):
        self.assertEqual(self.parse("211+2181+2191"), [(1, "211", (), ""), (1, "2181", (), ""), (1, "2191", (), "")])
        self.assertEqual(self.parse("-101-102"), [(-1, "101", (), ""), (-1, "102", (), "")])
        self.assertEqual(self.parse(" -13 - 6 "), [(-1, "13", (), ""), (-1, "6", (), "")])

    def test_exclusions_and_balance_character(self):
        self.assertEqual(self.parse("24\\(245,2495)"), [(1, "24", ("245", "2495"), "")])
        self.assertEqual(self.parse("-47\\(478,479)C"), [(-1, "47", ("478", "479"), "C")])
        self.assertEqual(self.parse("52D+58D"), [(1, "52", (), "D"), (1, "58", (), "D")])
        self.assertEqual(self.parse("101\\(1011)"), [(1, "101", ("1011",), "")])

    def test_invalid_formulas(self):
        for bad in ("", "  ", "21+", "2A1-", "21--3", "24\\(345)", "4D\\(41)", "tag(l10n.tag)", "24\\(245"):
            with self.assertRaises(ValueError, msg=bad):
                self.engine._parse_account_formula(bad)

    def test_evaluation_debit_credit_split(self):
        balances = {"401100": -500.0, "401200": 120.0, "409100": 80.0, "411100": 1000.0, "411200": -30.0}
        ev = lambda f: self.engine._eval_account_terms(self.engine._parse_account_formula(f), balances)
        self.assertEqual(ev("40D"), 200.0)          # 401200 + 409100
        self.assertEqual(ev("-40C"), 500.0)         # fournisseurs créditeurs, en positif
        self.assertEqual(ev("40"), -300.0)
        self.assertEqual(ev("40D") - ev("-40C"), ev("40"))
        self.assertEqual(ev("41D"), 1000.0)
        self.assertEqual(ev("-41C"), 30.0)
        self.assertEqual(ev("40\\(409)"), -380.0)
        self.assertEqual(ev("4\\(41,409)D"), 120.0)

    def test_aggregation(self):
        self.assertEqual(self.engine._parse_aggregation("AE+AF-AG"), [(1, "AE"), (1, "AF"), (-1, "AG")])
        with self.assertRaises(ValueError):
            self.engine._parse_aggregation("AE+12")
        with self.assertRaises(ValueError):
            self.engine._parse_aggregation("")

    def test_flow_formulas(self):
        terms = self.engine._parse_flow_formula("-DX:(21+251)-E:4811+S:4811+R:XI-V:BB")
        self.assertEqual([(s, k, a) for s, k, a, _t in terms],
                         [(-1, "DX", "21+251"), (-1, "E", "4811"), (1, "S", "4811"), (1, "R", "XI"), (-1, "V", "BB")])
        self.assertEqual(len(terms[0][3]), 2)
        self.assertEqual(self.engine._parse_flow_formula("C:(17\\(176)+181)")[0][3][0].excluded, ("176",))
        for bad in ("X:12", "R:12", "B:", "D:21C", "DX:(21+251", "P:"):
            with self.assertRaises(ValueError, msg=bad):
                self.engine._parse_flow_formula(bad)

    def test_split_top_level(self):
        self.assertEqual(_split_top_level("-DX:(21+251)-E:481\\(4811)+S:4811"),
                         ["-DX:(21+251)", "-E:481\\(4811)", "+S:4811"])
        with self.assertRaises(ValueError):
            _split_top_level("A:(1+2")
        with self.assertRaises(ValueError):
            _split_top_level("A:1)+2")
