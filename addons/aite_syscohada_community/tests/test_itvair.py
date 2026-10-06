# -*- coding: utf-8 -*-
from datetime import date

from odoo import Command
from odoo.tests import tagged

from .test_vat_declaration import VatDeclarationCommon


@tagged("post_install", "-at_install", "aite_syscohada")
class TestItvairForm(VatDeclarationCommon):
    """Formulaire I/TVA-IR complet : retenues, acomptes, IRCM, salaires ; montants calculés à la main."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ref = cls.company._aite_tax_ref
        cls.w_rent, cls.w_fees, cls.w_client, cls.precompte, cls.auto = (
            ref("retenue_loyers"), ref("retenue_honoraires"), ref("subie_acompte_ca"),
            ref("precompte_achats"), ref("autoliquidation_services"))
        (cls.w_rent | cls.w_fees | cls.w_client | cls.precompte | cls.auto).active = True

    def entry(self, day, *lines):
        move = self.env["account.move"].create({
            "move_type": "entry", "date": day, "company_id": self.company.id,
            "line_ids": [Command.create({"account_id": self.acc(code).id, "name": "paie",
                                         "debit": max(amount, 0), "credit": max(-amount, 0)}) for code, amount in lines]})
        move.action_post()
        return move

    def it(self, decl, code):
        return decl.itvair_line_ids.filtered(lambda l: l.code == code)

    def amounts(self, decl, code):
        line = self.it(decl, code)
        return line.base, line.principal, line.cac, line.total

    def test_march_full_form(self):
        self.doc("out_invoice", "2026-03-05", 2000000, self.t_sale)
        self.doc("out_invoice", "2026-03-06", 1000000, self.t_sale | self.w_client)
        self.doc("in_invoice", "2026-03-07", 500000, self.w_rent, "6222")
        self.doc("in_invoice", "2026-03-08", 200000, self.w_fees, "6324")
        self.doc("in_invoice", "2026-03-09", 1000000, self.t_buy | self.precompte, "6011")
        self.entry("2026-03-31", ("6611", 1000000), ("447210", -100000), ("447215", -10000), ("447220", -10000),
                   ("447250", -2000), ("447260", -1000), ("422", -877000))
        self.entry("2026-03-31", ("6413", 25000), ("447230", -15000), ("447240", -10000))
        decl = self.declare("2026-03-01", "2026-03-31")
        self.assertEqual(len(decl.itvair_line_ids), 54)
        self.it(decl, "L57").base_input = 1000000  # dividendes distribués, saisis par le déclarant
        decl.action_compute()
        self.assertEqual(self.it(decl, "L57").base_input, 1000000, "saisie conservée au recalcul")
        self.assertEqual(decl.date_due, date(2026, 4, 15))
        self.assertEqual(decl.vat_to_pay, 385000)
        self.assertEqual(self.amounts(decl, "L39"), (0, 385000, 0, 385000))
        self.assertEqual(self.amounts(decl, "L42"), (500000, 75000, 0, 75000))
        self.assertEqual(self.amounts(decl, "L43"), (200000, 10000, 0, 10000))
        self.assertEqual(self.it(decl, "L44").total, 85000)
        self.assertEqual(self.amounts(decl, "L45"), (1000000, 20000, 0, 20000))
        self.assertEqual(self.amounts(decl, "L46"), (1000000, 20000, 0, 20000))
        self.assertEqual(self.it(decl, "L49").total, 40000)
        self.assertEqual(self.amounts(decl, "L50"), (3000000, 60000, 6000, 66000), "2 % du CA déclaré + 10 % de CAC")
        self.assertEqual((self.it(decl, "L52").total, self.it(decl, "L54").total, self.it(decl, "L55").total), (40000, 26000, 0))
        self.assertEqual(self.amounts(decl, "L57"), (1000000, 150000, 15000, 165000))
        self.assertEqual(self.amounts(decl, "L67"), (0, 100000, 10000, 110000))
        self.assertEqual([self.it(decl, c).total for c in ("L68", "L69", "L70", "L71", "L72", "L73")],
                         [10000, 15000, 10000, 2000, 1000, 148000])
        self.assertEqual(decl.total_to_pay, 809000)
        self.assertEqual(self.it(decl, "TOTAL").total, 809000)

        decl.action_create_closing_entry()
        self.assertEqual((self.balance("4441"), self.balance("441100"), self.balance("449250")), (-385000, -26000, 26000))
        self.assertEqual((self.balance("447130"), self.balance("449220"), self.balance("449210")), (-75000, 20000, 20000),
                         "les retenues restent hors de la liquidation de TVA")
        html = self.env["ir.actions.report"]._render_qweb_html("aite_syscohada_community.report_itvair", decl.ids)[0].decode()
        for text in ("I/TVA-IR", "Acompte à payer", "Impôts retenus sur salaires", "TOTAL À PAYER"):
            self.assertIn(text, html)
        decl.action_done()
        self.assertFalse(self.it(decl, "L57").editable)

    def test_acompte_credit_carried_forward(self):
        self.doc("in_invoice", "2026-04-05", 1000000, self.t_buy | self.precompte, "6011")
        self.doc("out_invoice", "2026-04-06", 100000, self.t_sale)
        april = self.declare("2026-04-01", "2026-04-30")
        self.assertEqual(self.amounts(april, "L50"), (100000, 2000, 200, 2200))
        self.assertEqual((april.acompte_to_pay, april.is_credit_to_report), (0, 17800))
        april.action_done()
        self.doc("out_invoice", "2026-05-05", 2000000, self.t_sale)
        may = self.declare("2026-05-01", "2026-05-31")
        self.assertEqual(self.it(may, "L53").total, 17800, "crédit d'avril repris")
        self.assertEqual((may.acompte_to_pay, may.is_credit_to_report), (26200, 0))

    def test_reverse_charge_foreign_services(self):
        self.doc("in_invoice", "2026-06-05", 1000000, self.auto, "6324")
        decl = self.declare("2026-06-01", "2026-06-30")
        self.assertEqual(self.line(decl, "CM_FOREIGN_SERVICE").tax, 192500, "L21 : TVA autoliquidée déductible")
        self.assertEqual(self.it(decl, "L38").total, 192500, "L38 : TVA autoliquidée à reverser")
        self.assertEqual((decl.vat_to_pay, decl.vat_credit, self.it(decl, "L39").total), (0, 192500, 192500))
        decl.action_create_closing_entry()
        self.assertEqual((self.balance("4454"), self.balance("4449"), self.balance("447161")), (0, 192500, -192500))
