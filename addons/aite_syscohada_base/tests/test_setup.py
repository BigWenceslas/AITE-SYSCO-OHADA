# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import SyscohadaCommon


@tagged("post_install", "-at_install", "aite_syscohada")
class TestSetup(SyscohadaCommon):
    """Lot 0 : plan comptable corrigé, sous-comptes, écarts de caisse, taxes camerounaises."""

    def account(self, code):
        account = self.company._aite_account(code)
        self.assertTrue(account, f"compte {code} absent")
        return account.with_company(self.company)

    def test_setup_flag(self):
        self.assertTrue(self.company.aite_syscohada_setup_date)
        self.assertTrue(self.company.tax_exigibility, "la TVA sur encaissements doit être activée")

    def test_labels(self):
        self.assertEqual(self.account("121").name, "Report à nouveau créditeur")
        self.assertEqual(self.account("131").name, "Résultat net : bénéfice")
        self.assertEqual(self.account("477").name, "Produits constatés d'avance")
        self.assertEqual(self.account("6613").name, "Congés payés")
        self.assertEqual(self.account("465").name, "Associés, dividendes à payer")

    def test_account_types(self):
        for code in ("4451", "4452", "4454", "4455", "4492"):
            self.assertEqual(self.account(code).account_type, "asset_current", code)
        self.assertEqual(self.account("162").account_type, "liability_non_current")
        self.assertEqual(self.account("1662").account_type, "liability_current", "les intérêts courus restent courants")
        for code in ("4811", "4812"):
            account = self.account(code)
            self.assertEqual(account.account_type, "liability_payable", code)
            self.assertTrue(account.reconcile, code)

    def test_subaccounts(self):
        expected = {"281810": "asset_fixed", "291910": "asset_fixed", "293910": "asset_fixed",
                    "294950": "asset_fixed", "443800": "liability_current", "552100": "asset_cash", "552200": "asset_cash"}
        for code, account_type in expected.items():
            self.assertEqual(self.account(code).code, code)
            self.assertEqual(self.account(code).account_type, account_type, code)
        self.assertTrue(self.account("443800").reconcile)

    def test_cash_difference_accounts(self):
        company = self.company.with_company(self.company)
        self.assertEqual(company.default_cash_difference_expense_account_id.code, "658800")
        self.assertEqual(company.default_cash_difference_income_account_id.code, "758800")
        for journal in self.env["account.journal"].search([("company_id", "=", self.company.id), ("type", "in", ("cash", "bank"))]):
            if journal.loss_account_id:
                self.assertTrue(journal.loss_account_id.with_company(self.company).code.startswith("6"), journal.name)
            if journal.profit_account_id:
                self.assertTrue(journal.profit_account_id.with_company(self.company).code.startswith("7"), journal.name)
        self.assertTrue(self.company._aite_account("999001").deprecated)
        self.assertTrue(self.company._aite_account("999002").deprecated)

    def tax_line(self, tax, document_type="invoice"):
        return tax.repartition_line_ids.filtered(lambda l: l.repartition_type == "tax" and l.document_type == document_type)

    def test_tax_services_cash_basis(self):
        tax = self.company._aite_tax_ref("tva_prestations_encaissement")
        self.assertTrue(tax)
        self.assertEqual((tax.type_tax_use, tax.amount, tax.tax_exigibility), ("sale", 19.25, "on_payment"))
        self.assertEqual(tax.cash_basis_transition_account_id.with_company(self.company).code, "443800")
        line = self.tax_line(tax)
        self.assertEqual(line.account_id.with_company(self.company).code, "443200")
        self.assertEqual(line.tag_ids.mapped("name"), ["+CM_10_tax"])
        refund = self.tax_line(tax, "refund")
        self.assertEqual(refund.tag_ids.mapped("name"), ["-CM_10_tax"])

    def test_tax_assets_and_services(self):
        tax = self.company._aite_tax_ref("tva_immobilisations")
        self.assertEqual(self.tax_line(tax).account_id.with_company(self.company).code, "445100")
        self.assertEqual(self.tax_line(tax).tag_ids.mapped("name"), ["+CM_18"])
        services = self.env["account.chart.template"].with_company(self.company).ref("tva_purchase_services_19_25")
        self.assertEqual(self.tax_line(services).account_id.with_company(self.company).code, "445400")

    def test_inactive_taxes_to_configure(self):
        for key, account in (("taxe_sejour", "442200"), ("precompte_achats", "449210")):
            tax = self.company._aite_tax_ref(key)
            self.assertTrue(tax, key)
            self.assertFalse(tax.active, f"{key} doit rester inactive tant que le taux n'est pas validé")
            self.assertEqual(self.tax_line(tax).account_id.with_company(self.company).code, account)

    def test_setup_is_idempotent(self):
        Tax = self.env["account.tax"].with_context(active_test=False)
        Account = self.env["account.account"]
        taxes_before = Tax.search_count([("company_id", "=", self.company.id)])
        accounts_before = Account.search_count([("company_ids", "in", self.company.id)])
        self.company._aite_syscohada_setup()
        self.company._aite_syscohada_setup()
        self.assertEqual(Tax.search_count([("company_id", "=", self.company.id)]), taxes_before)
        self.assertEqual(Account.search_count([("company_ids", "in", self.company.id)]), accounts_before)

    def test_non_syscohada_company_untouched(self):
        other = self.env["res.company"].create({"name": "Société non OHADA", "country_id": self.env.ref("base.be").id})
        self.assertFalse(other._aite_is_syscohada())
        other._aite_syscohada_setup()
        self.assertFalse(other.aite_syscohada_setup_date)

    def test_lot2_accounts_and_withholding_taxes(self):
        for code in ("441100", "447110", "447120", "447130", "447140", "447150", "447160", "447161", "447170",
                     "447180", "447210", "447215", "447220", "447230", "447240", "447250", "447260",
                     "449210", "449220", "449230", "449240", "449250"):
            self.assertEqual(self.account(code).code, code)
        self.assertEqual(self.account("449210").account_type, "asset_current")
        other = self.company._aite_other_tax_group()
        expected = {"retenue_loyers": ("purchase", -15.0, "447130"), "retenue_honoraires": ("purchase", -5.0, "447140"),
                    "retenue_tsr": ("purchase", -15.0, "447120"), "retenue_tva": ("purchase", -19.25, "447160"),
                    "retenue_acompte_ca": ("purchase", -2.0, "447170"), "subie_acompte_ca": ("sale", -2.0, "449220"),
                    "subie_loyers": ("sale", -15.0, "449230"), "subie_honoraires": ("sale", -5.0, "449240")}
        for key, (use, amount, code) in expected.items():
            tax = self.company._aite_tax_ref(key)
            self.assertEqual((tax.type_tax_use, tax.amount, tax.active, tax.tax_group_id), (use, amount, False, other), key)
            self.assertEqual(self.tax_line(tax).account_id.with_company(self.company).code, code, key)
        precompte = self.company._aite_tax_ref("precompte_achats")
        self.assertEqual(self.tax_line(precompte).account_id.with_company(self.company).code, "449210")
        self.assertEqual(precompte.tax_group_id, other)
        auto = self.company._aite_tax_ref("autoliquidation_services")
        lines = self.tax_line(auto)
        self.assertEqual(sorted((l.account_id.with_company(self.company).code, l.factor_percent) for l in lines),
                         [("445400", 100.0), ("447161", -100.0)])
