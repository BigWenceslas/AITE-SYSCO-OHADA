# -*- coding: utf-8 -*-
from odoo import Command, fields
from odoo.tests import tagged

from .common import SyscohadaCommon


@tagged("post_install", "-at_install", "aite_syscohada")
class TestInvoiceTaxes(SyscohadaCommon):
    """Lot 0 : les factures de test sont correctement taxées (critère de sortie du lot)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client test", "company_id": False})
        chart = cls.env["account.chart.template"].with_company(cls.company)
        cls.tax_goods = chart.ref("tva_sale_19_25")
        cls.tax_services_purchase = chart.ref("tva_purchase_services_19_25")
        cls.tax_services_cash = cls.company._aite_tax_ref("tva_prestations_encaissement")
        cls.tax_assets = cls.company._aite_tax_ref("tva_immobilisations")

    def balance(self, code):
        account = self.company._aite_account(code)
        lines = self.env["account.move.line"].search([("account_id", "=", account.id), ("parent_state", "=", "posted"),
                                                      ("company_id", "=", self.company.id)])
        return sum(lines.mapped("balance"))

    def invoice(self, move_type, price, tax, account=None, partner=None):
        line = {"name": "ligne", "quantity": 1, "price_unit": price, "tax_ids": [Command.set(tax.ids)]}
        if account:
            line["account_id"] = account.id
        move = self.env["account.move"].create({
            "move_type": move_type, "partner_id": (partner or self.partner).id, "invoice_date": "2026-03-10",
            "date": "2026-03-10", "company_id": self.company.id, "invoice_line_ids": [Command.create(line)]})
        move.action_post()
        return move

    def pay(self, move, amount=None):
        wizard = self.env["account.payment.register"].with_context(active_model="account.move", active_ids=move.ids).create({
            "payment_date": "2026-04-10", "journal_id": self.journal_bank.id, **({"amount": amount} if amount else {})})
        return wizard._create_payments()

    def lines_by_code(self, move):
        result = {}
        for line in move.line_ids:
            code = line.account_id.with_company(self.company).code
            result[code] = result.get(code, 0.0) + line.balance
        return result

    def test_sale_goods(self):
        move = self.invoice("out_invoice", 100000, self.tax_goods)
        lines = self.lines_by_code(move)
        self.assertEqual(lines["701100"], -100000)
        self.assertEqual(lines["443100"], -19250)
        self.assertEqual(move.amount_total, 119250)

    def test_sale_services_cash_basis_full_payment(self):
        move = self.invoice("out_invoice", 100000, self.tax_services_cash, account=self.acc("7061"))
        self.assertEqual(self.lines_by_code(move)["443800"], -19250, "TVA d'abord en compte d'attente")
        self.assertEqual(self.balance("4432"), 0)
        self.pay(move)
        self.assertEqual(self.balance("4438"), 0, "le compte d'attente est soldé au paiement")
        self.assertEqual(self.balance("4432"), -19250, "la TVA devient exigible en 4432")

    def test_sale_services_cash_basis_partial_payment(self):
        move = self.invoice("out_invoice", 100000, self.tax_services_cash, account=self.acc("7061"))
        self.pay(move, amount=59625)
        self.assertEqual(self.balance("4432"), -9625, "exigible au prorata de l'encaissement")
        self.assertEqual(self.balance("4438"), -9625)

    def test_purchase_services(self):
        move = self.invoice("in_invoice", 10000, self.tax_services_purchase, account=self.acc("6311") if self.company._aite_account("6311") else self.acc("63"))
        lines = self.lines_by_code(move)
        self.assertEqual(lines.get("445400"), 1925)
        self.assertNotIn("445200", lines)

    def test_purchase_fixed_asset_from_investment_supplier(self):
        supplier = self.env["res.partner"].create({"name": "Fournisseur de chambre froide", "company_id": False})
        supplier.with_company(self.company).property_account_payable_id = self.company._aite_account("4812")
        move = self.invoice("in_invoice", 2400000, self.tax_assets, account=self.acc("2411"), partner=supplier)
        lines = self.lines_by_code(move)
        self.assertEqual(lines["241100"], 2400000)
        self.assertEqual(lines["445100"], 462000)
        self.assertEqual(lines["481200"], -2862000, "dette fournisseur d'investissement (rubrique DH)")
        result = self.compute("2026-01-01", "2026-12-31", ("actif", "passif"))
        self.assertEqual(result["passif"]["DH"], 2862000)
        self.assertEqual(result["actif"]["AM"]["brut"], 2400000)
