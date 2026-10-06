# -*- coding: utf-8 -*-
from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.aite_syscohada_base.tests.common import SyscohadaCommon


class VatDeclarationCommon(SyscohadaCommon):
    """Données et outils communs aux tests de la déclaration mensuelle."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chart = cls.env["account.chart.template"].with_company(cls.company)
        cls.t_sale = chart.ref("tva_sale_19_25")
        cls.t_export = chart.ref("tva_export_0")
        cls.t_exempt = chart.ref("tva_exempt_0")
        cls.t_buy = chart.ref("tva_purchase_good_19_25")
        cls.t_buy_services = chart.ref("tva_purchase_services_19_25")
        cls.t_services = cls.company._aite_tax_ref("tva_prestations_encaissement")
        cls.t_assets = cls.company._aite_tax_ref("tva_immobilisations")
        cls.partner = cls.env["res.partner"].create({"name": "Partenaire test"})
        cls.Decl = cls.env["aite.cm.vat.declaration"]

    @classmethod
    def doc(cls, move_type, day, price, tax, account=None):  # tax : une ou plusieurs taxes
        line = {"name": "ligne", "quantity": 1, "price_unit": price, "tax_ids": [Command.set(tax.ids)]}
        if account:
            line["account_id"] = cls.acc(account).id
        move = cls.env["account.move"].create({
            "move_type": move_type, "partner_id": cls.partner.id, "invoice_date": day, "date": day,
            "company_id": cls.company.id, "invoice_line_ids": [Command.create(line)]})
        move.action_post()
        return move

    @classmethod
    def pay(cls, move, day):
        cls.env["account.payment.register"].with_context(active_model="account.move", active_ids=move.ids).create(
            {"payment_date": day, "journal_id": cls.journal_bank.id})._create_payments()

    def declare(self, date_from, date_to, **manual):
        decl = self.Decl.create(dict({"company_id": self.company.id, "date_from": date_from, "date_to": date_to}, **manual))
        decl.action_compute()
        return decl

    def line(self, decl, code):
        return decl.line_ids.filtered(lambda l: l.code == code)

    def balance(self, prefix):
        account = self.acc(prefix)
        return sum(self.env["account.move.line"].search(
            [("account_id", "=", account.id), ("parent_state", "=", "posted")]).mapped("balance"))



@tagged("post_install", "-at_install", "aite_syscohada")
class TestVatDeclaration(VatDeclarationCommon):
    """Déclaration mensuelle de TVA sous Community : montants attendus calculés à la main."""

    def march(self):
        self.doc("out_invoice", "2026-03-05", 1000000, self.t_sale)
        self.unpaid = self.doc("out_invoice", "2026-03-10", 400000, self.t_services, "7061")
        paid = self.doc("out_invoice", "2026-03-12", 200000, self.t_services, "7061")
        self.pay(paid, "2026-03-20")
        self.doc("out_invoice", "2026-03-14", 300000, self.t_export)
        self.doc("out_invoice", "2026-03-15", 100000, self.t_exempt)
        self.doc("in_invoice", "2026-03-16", 600000, self.t_buy, "6011")
        self.doc("in_invoice", "2026-03-17", 100000, self.t_buy_services, "6324")
        self.doc("in_invoice", "2026-03-18", 1000000, self.t_assets, "2441")

    def test_march_credit_then_april_payable(self):
        self.march()
        decl = self.declare("2026-03-01", "2026-03-31")
        self.assertEqual((self.line(decl, "CM_NORMAL").base, self.line(decl, "CM_NORMAL").tax), (1200000, 231000),
                         "L10 : ventes de biens + prestations encaissées seulement")
        self.assertEqual(self.line(decl, "CM_EXPORT").base, 300000)
        self.assertEqual(self.line(decl, "CM_EXEMPT").base, 100000)
        self.assertEqual(self.line(decl, "CM_GLOBAL").base, 1600000)
        self.assertEqual(self.line(decl, "CM_LOCAL_PURCHASE").tax, 308000, "L18 : biens et immobilisations")
        self.assertEqual(self.line(decl, "CM_LOCAL_SERVICE").tax, 19250, "L19 : services (compte 4454)")
        self.assertEqual(self.line(decl, "CM_DEDUCTIBLE_VAT").tax, 327250)
        self.assertEqual((decl.vat_collected, decl.vat_deductible, decl.vat_to_pay, decl.vat_credit, decl.credit_to_report),
                         (231000, 327250, 0, 96250, 96250))
        move = decl.action_create_closing_entry()
        self.assertEqual(move.state, "posted")
        self.assertEqual(decl.acompte_to_pay, 35200, "acompte : 2 % de 1 600 000 et 10 % de CAC")
        self.assertEqual(sum(move.line_ids.mapped("debit")), 327250 + 35200, "TVA et acompte liquidés ensemble")
        for prefix in ("4431", "4432", "4451", "4452", "4454"):
            self.assertEqual(self.balance(prefix), 0, prefix)
        self.assertEqual(self.balance("4449"), 96250, "crédit à reporter")
        self.assertEqual(self.balance("4438"), -77000, "prestation impayée : TVA encore en attente")
        decl.action_done()

        # Avril : crédit antérieur repris, prestation de mars encaissée
        self.doc("out_invoice", "2026-04-05", 2000000, self.t_sale)
        self.doc("in_invoice", "2026-04-06", 500000, self.t_buy, "6011")
        self.pay(self.unpaid, "2026-04-15")
        april = self.declare("2026-04-01", "2026-04-30")
        self.assertEqual(april.credit_previous, 96250)
        self.assertEqual(self.line(april, "CM_CREDIT_REPORTED").tax, 96250)
        self.assertEqual((self.line(april, "CM_NORMAL").base, self.line(april, "CM_NORMAL").tax), (2400000, 462000))
        self.assertEqual((april.vat_collected, april.vat_deductible, april.vat_to_pay, april.credit_to_report),
                         (462000, 192500, 269500, 0))
        april.action_create_closing_entry()
        self.assertEqual(self.balance("4441"), -269500)
        self.assertEqual(self.balance("4449"), 0, "crédit consommé")
        self.assertEqual(self.balance("4438"), 0)
        for prefix in ("4431", "4432", "4452"):
            self.assertEqual(self.balance(prefix), 0, prefix)
        april.action_done()
        with self.assertRaises(UserError):
            decl.action_draft()  # avril validé dépend de mars

    def test_refund_creates_credit(self):
        refund = self.doc("out_refund", "2026-05-10", 100000, self.t_sale)
        decl = self.declare("2026-05-01", "2026-05-31")
        self.assertEqual((self.line(decl, "CM_NORMAL").base, self.line(decl, "CM_NORMAL").tax), (-100000, -19250))
        self.assertEqual((decl.vat_to_pay, decl.vat_credit), (0, 19250))
        self.assertEqual((decl.acompte_to_pay, decl.is_credit_to_report), (0, 0), "pas d'acompte négatif")
        decl.action_create_closing_entry()
        self.assertEqual(self.balance("4449"), 19250)
        self.assertTrue(refund)

    def test_manual_adjustment_requires_counterpart(self):
        self.doc("out_invoice", "2026-06-05", 100000, self.t_sale)
        decl = self.declare("2026-06-01", "2026-06-30", adj_deductible=5000)
        self.assertEqual(self.line(decl, "CM_ADJUSTMENT_TO_DEDUCT").tax, 5000)
        self.assertEqual(decl.vat_to_pay, 14250)
        with self.assertRaises(UserError):
            decl.action_create_closing_entry()
        decl.adjustment_account_id = self.acc("4711")
        move = decl.action_create_closing_entry()
        self.assertEqual(sum(move.line_ids.mapped("debit")), sum(move.line_ids.mapped("credit")))
        self.assertEqual(self.balance("4441"), -14250)
        self.assertEqual(self.balance("4711"), -5000)

    def test_reimbursement(self):
        self.doc("in_invoice", "2026-07-05", 1000000, self.t_buy, "6011")
        decl = self.declare("2026-07-01", "2026-07-31", reimbursement=50000)
        self.assertEqual((decl.vat_credit, decl.credit_to_report), (192500, 142500))
        decl.action_create_closing_entry()
        self.assertEqual(self.balance("4445"), 50000)
        self.assertEqual(self.balance("4449"), 142500)

    def test_constraints(self):
        self.declare("2026-08-01", "2026-08-31")
        with mute_logger("odoo.sql_db"), self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.declare("2026-08-01", "2026-08-31")
        with self.assertRaises(ValidationError):
            self.Decl.create({"company_id": self.company.id, "date_from": "2026-09-30", "date_to": "2026-09-01"})
        decl = self.declare("2026-10-01", "2026-10-31")
        decl.action_done()
        with self.assertRaises(UserError):
            decl.action_compute()
