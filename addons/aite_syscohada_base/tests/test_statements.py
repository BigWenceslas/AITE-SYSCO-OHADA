# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import SyscohadaCommon


@tagged("post_install", "-at_install", "aite_syscohada")
class TestStatementsScenario(SyscohadaCommon):
    """Scénario chiffré sur deux exercices : chaque montant attendu est calculé à la main."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_reference_scenario()
        cls.n1 = cls.engine.compute(cls.company, "2025-01-01", "2025-12-31")
        cls.n = cls.engine.compute(cls.company, "2026-01-01", "2026-12-31")

    def test_n1_statements(self):
        r, a, p, f = self.n1["resultat"], self.n1["actif"], self.n1["passif"], self.n1["flux"]
        self.assertEqual((r["TA"], r["RA"], r["RB"], r["XA"], r["RS"], r["XI"]),
                         (5000000, -3000000, 500000, 2500000, -300000, 2200000))
        self.assertEqual(a["BB"]["net"], 500000)
        self.assertEqual(a["BJ"]["net"], 577500)
        self.assertEqual(a["BS"]["net"], 12385000)
        self.assertEqual(a["BZ"]["net"], 13462500)
        self.assertEqual((p["CA"], p["CJ"], p["DK"], p["DZ"]), (10000000, 2200000, 1262500, 13462500))
        self.assertEqual((f["ZA"], f["FA"], f["FC"], f["FD"], f["FE"], f["ZB"]), (0, 2200000, -500000, -577500, 1262500, 2385000))
        self.assertEqual((f["FK"], f["ZD"], f["ZF"], f["ZG"], f["ZH"]), (10000000, 10000000, 10000000, 12385000, 12385000))

    def test_n_resultat(self):
        r = self.n["resultat"]
        expected = {"TA": 0, "RA": -800000, "RB": 200000, "XA": -600000, "TC": 1000000, "XB": 1000000,
                    "XC": 400000, "RK": -560000, "XD": -160000, "RL": -480000, "XE": -640000, "RM": -120000,
                    "XF": -120000, "XG": -760000, "XH": 0, "RS": -100000, "XI": -860000}
        self.assertEqual({k: r[k] for k in expected}, expected)

    def test_n_bilan(self):
        a, p = self.n["actif"], self.n["passif"]
        self.assertEqual(a["AM"], {"brut": 2400000, "amort": 480000, "net": 1920000})
        self.assertEqual(a["AZ"]["net"], 1920000)
        self.assertEqual(a["BB"]["net"], 700000)
        self.assertEqual(a["BJ"]["net"], 616000)
        self.assertEqual(a["BS"]["net"], 11980500)
        self.assertEqual(a["BZ"]["net"], 15216500)
        expected = {"CA": 10000000, "CF": 220000, "CH": 980000, "CJ": -860000, "CP": 10340000, "DA": 3200000,
                    "DD": 3200000, "DH": 0, "DJ": 954000, "DK": 722500, "DM": 0, "DP": 1676500, "DZ": 15216500}
        self.assertEqual({k: p[k] for k in expected}, expected)

    def test_n_flux(self):
        f = self.n["flux"]
        expected = {"ZA": 12385000, "FA": -380000, "FB": 0, "FC": -200000, "FD": -38500, "FE": 414000,
                    "ZB": -204500, "FF": 0, "FG": -2400000, "FH": 0, "FI": 0, "FJ": 0, "ZC": -2400000,
                    "FK": 0, "FL": 0, "FM": 0, "FN": -1000000, "ZD": -1000000, "FO": 4000000, "FP": 0,
                    "FQ": -800000, "ZE": 3200000, "ZF": 2200000, "ZG": -404500, "ZH": 11980500}
        self.assertEqual({k: f[k] for k in expected}, expected)

    def test_checks_all_green(self):
        for date_from, date_to in (("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-12-31")):
            checks = {c["code"]: c for c in self.checker.run(self.company, date_from, date_to)}
            for code in ("RATTACHEMENT", "BROUILLONS", "EQUILIBRE", "RESULTAT", "ATTENTE", "CAISSE", "TFT", "ESPECES"):
                self.assertEqual(checks[code]["level"], "ok", f"{date_to} {code} : {checks[code]['message']}")

    def test_unallocated_result_is_reported(self):
        """Sans écriture d'affectation, le résultat N-1 reste en CJ : le contrôle le signale sans bloquer."""
        self.entry("2027-01-01", [("131", 0, 1), ("999999", 1, 0)], "résultat en instance")  # mouvement neutre
        self.entry("2027-03-01", [("7011", 0, 100000), (self.bank, 100000, 0)], "vente comptant")
        checks = {c["code"]: c for c in self.checker.run(self.company, "2027-01-01", "2027-12-31")}
        self.assertEqual(checks["RESULTAT"]["level"], "ok", checks["RESULTAT"]["message"])
        self.assertEqual(checks["AFFECTATION"]["level"], "warning")

    def test_reclassifications_by_balance_sign(self):
        """Fournisseur débiteur, client créditeur et banque à découvert changent de rubrique."""
        b = self.bank
        self.entry("2027-02-01", [("4011", 1000000, 0), (b, 0, 1000000)], "trop-payé fournisseur")
        self.entry("2027-02-02", [(b, 50000, 0), ("4111", 0, 50000)], "avance client")
        self.entry("2027-02-03", [("6011", 20000000, 0), (b, 0, 20000000)], "gros achat")
        res = self.compute("2027-01-01", "2027-12-31")
        a, p, f = res["actif"], res["passif"], res["flux"]
        self.assertEqual(a["BH"]["net"], 46000)
        self.assertEqual(p["DJ"], 0)
        self.assertEqual(p["DI"], 50000)
        self.assertEqual(a["BI"]["net"], 0)
        bank_balance = 10788000 - 1000000 + 50000 - 20000000
        self.assertEqual(p["DR"], -bank_balance)
        self.assertEqual(a["BZ"]["net"], p["DZ"])
        self.assertEqual(f["ZH"], a["BT"]["net"] - p["DT"])
        checks = {c["code"]: c for c in self.checker.run(self.company, "2027-01-01", "2027-12-31", results=res)}
        self.assertEqual(checks["BASCULES"]["level"], "info")
        self.assertIn("débiteur", checks["BASCULES"]["message"])

    def test_wizard(self):
        wizard = self.env["aite.syscohada.statement.wizard"].create({
            "company_id": self.company.id, "date_from": "2026-01-01", "date_to": "2026-12-31", "compare": True})
        wizard.action_compute()
        self.assertTrue(wizard.computed)
        self.assertEqual(len(wizard.line_ids), self.env["aite.syscohada.rubrique"].search_count([]))
        bz = wizard.actif_line_ids.filtered(lambda l: l.code == "BZ")
        self.assertEqual((bz.net, bz.net_n1), (15216500, 13462500))
        xi = wizard.resultat_line_ids.filtered(lambda l: l.code == "XI")
        self.assertEqual((xi.net, xi.net_n1), (-860000, 2200000))
        self.assertEqual(wizard.flux_line_ids.filtered(lambda l: l.code == "ZH").net, 11980500)
        levels = set(wizard.check_ids.mapped("level"))
        self.assertNotIn("error", levels, wizard.check_ids.filtered(lambda c: c.level == "error").mapped("message"))
