# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import SyscohadaCommon


@tagged("post_install", "-at_install", "aite_syscohada")
class TestCoverage(SyscohadaCommon):
    """Chaque compte du plan est rattaché à une rubrique et une seule, quel que soit le sens de son solde."""

    def capture(self, code, side):
        bilan, resultat = self.checker._mapping_terms()
        if side == "R":
            return sorted({rub for rub, t in resultat if t.matches(code)})
        chars = ("", side)
        return sorted({rub for rub, t in bilan if t.matches(code) and t.balance_character in chars})

    def test_whole_chart_covered_exactly_once(self):
        problems = self.checker.coverage(self.company)
        self.assertEqual([(p["code"], p["message"]) for p in problems], [])

    def test_chart_size(self):
        accounts = self.env["account.account"].with_company(self.company).search(
            [("company_ids", "in", self.company.id), ("account_type", "!=", "off_balance"), ("deprecated", "=", False)])
        self.assertGreater(len(accounts), 1000)

    def test_key_accounts(self):
        cases = {
            # compte : (rubrique si solde débiteur, si solde créditeur)
            "401100": (["BH"], ["DJ"]), "409100": (["BH"], ["DJ"]),
            "411100": (["BI"], ["DI"]), "419100": (["BI"], ["DI"]),
            "445200": (["BJ"], ["DK"]), "443100": (["BJ"], ["DK"]), "441000": (["BJ"], ["DK"]),
            "465000": (["BJ"], ["DM"]), "476000": (["BJ"], ["DM"]), "477000": (["BJ"], ["DM"]),
            "478110": (["BU"], ["BU"]), "481200": (["BA"], ["DH"]), "485100": (["BA"], ["DH"]),
            "521001": (["BS"], ["DR"]), "552100": (["BS"], ["DR"]), "571001": (["BS"], ["DR"]),
            "585001": (["BS"], ["DR"]), "564000": (["DQ"], ["DQ"]),
            "281810": (["AE"], ["AE"]), "281800": (["AH"], ["AH"]), "291930": (["AF"], ["AF"]),
            "293910": (["AK"], ["AK"]), "293900": (["AL"], ["AL"]), "294950": (["AN"], ["AN"]),
            "294900": (["AM"], ["AM"]), "245100": (["AN"], ["AN"]), "241100": (["AM"], ["AM"]),
            "131000": (["CJ"], ["CJ"]), "999999": (["CJ"], ["CJ"]), "701100": (["CJ"], ["CJ"]),
            "162000": (["DA"], ["DA"]), "499800": (["DH"], ["DH"]), "499100": (["DN"], ["DN"]),
        }
        for code, (debit, credit) in cases.items():
            account = self.company._aite_account(code)
            if not account:
                self.fail(f"compte {code} absent du plan")
            self.assertEqual(self.capture(code, "D"), debit, f"{code} débiteur")
            self.assertEqual(self.capture(code, "C"), credit, f"{code} créditeur")

    def test_key_pl_accounts(self):
        cases = {"701100": "TA", "601100": "RA", "601900": "RA", "603100": "RB", "706100": "TC", "658800": "RJ",
                 "659100": "RJ", "758800": "TH", "754100": "TH", "661100": "RK", "671200": "RM", "676000": "RM",
                 "776000": "TK", "681300": "RL", "691100": "RL", "697100": "RN", "791100": "TJ", "798000": "TJ",
                 "799000": "TJ", "797100": "TL", "787000": "TM", "781000": "TI", "812000": "RO", "822000": "TN",
                 "831000": "RP", "851000": "RP", "841000": "TO", "861000": "TO", "871000": "RQ", "891100": "RS"}
        for code, rub in cases.items():
            self.assertTrue(self.company._aite_account(code), f"compte {code} absent du plan")
            self.assertEqual(self.capture(code, "R"), [rub], code)

    def test_unmapped_account_detected(self):
        Account = self.env["account.account"].with_company(self.company)
        rogue = Account.create({"code": "900500", "name": "Compte hors plan", "account_type": "expense",
                                "company_ids": [(6, 0, self.company.ids)]})
        codes = [p["code"] for p in self.checker.coverage(self.company)]
        self.assertIn(rogue.code, codes)
