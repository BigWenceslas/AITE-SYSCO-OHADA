# -*- coding: utf-8 -*-
from odoo import Command, fields
from odoo.tests import TransactionCase


class SyscohadaCommon(TransactionCase):
    """Société camerounaise de test, plan SYSCOHADA « cm » et paramétrage AITE appliqué."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True, lang="en_US"))
        xaf = cls.env.ref("base.XAF")
        xaf.active = True
        company = cls.env["res.company"].create({
            "name": "Test SYSCOHADA AITE", "country_id": cls.env.ref("base.cm").id, "currency_id": xaf.id})
        cls.env.user.company_ids |= company
        cls.env = cls.env(context=dict(cls.env.context, allowed_company_ids=[company.id]))
        cls.company = cls.env["res.company"].browse(company.id)
        cls.env["account.chart.template"].try_loading("cm", company=cls.company, install_demo=False)
        cls.engine = cls.env["aite.syscohada.engine"]
        cls.checker = cls.env["aite.syscohada.check"]
        cls.journal_misc = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "general")], limit=1)
        cls.journal_bank = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "bank")], limit=1)
        cls.journal_cash = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "cash")], limit=1)
        cls.bank = cls.journal_bank.default_account_id
        cls.cash = cls.journal_cash.default_account_id

    @classmethod
    def acc(cls, prefix):
        """Premier compte de la société dont le code commence par ``prefix``."""
        account = cls.env["account.account"].with_company(cls.company).search(
            [("code", "=like", f"{prefix}%"), ("company_ids", "in", cls.company.id)], order="code", limit=1)
        assert account, f"aucun compte {prefix}"
        return account

    @classmethod
    def entry(cls, date, lines, ref=None):
        """Écriture validée : lines = [(préfixe de compte, débit, crédit), ...]."""
        move = cls.env["account.move"].create({
            "move_type": "entry", "date": date, "journal_id": cls.journal_misc.id, "ref": ref or "test",
            "company_id": cls.company.id,
            "line_ids": [Command.create({"account_id": (p if not isinstance(p, str) else cls.acc(p)).id,
                                         "debit": d, "credit": c, "name": ref or "ligne"})
                         for p, d, c in lines],
        })
        move.action_post()
        return move

    @classmethod
    def create_reference_scenario(cls):
        """Scénario de référence sur 2025 (N-1) et 2026 (N), montants calculés à la main dans test_statements."""
        b, c = cls.bank, cls.cash
        E = cls.entry
        # ---- exercice N-1 (2025)
        E("2025-01-02", [(b, 10000000, 0), ("1013", 0, 10000000)], "apport en capital")
        E("2025-03-01", [("6011", 3000000, 0), ("4452", 577500, 0), ("4011", 0, 3577500)], "achat de boissons")
        E("2025-06-30", [("4111", 5962500, 0), ("7011", 0, 5000000), ("4431", 0, 962500)], "vente de boissons")
        E("2025-07-15", [(b, 5962500, 0), ("4111", 0, 5962500)], "encaissement client")
        E("2025-08-01", [("4011", 3577500, 0), (b, 0, 3577500)], "paiement fournisseur")
        E("2025-12-31", [("311", 500000, 0), ("6031", 0, 500000)], "stock final")
        E("2025-12-31", [("891", 300000, 0), ("441", 0, 300000)], "impôt sur le résultat")
        # ---- exercice N (2026)
        E("2026-01-01", [("6031", 500000, 0), ("311", 0, 500000)], "reprise du stock initial")
        E("2026-01-01", [("999999", 2200000, 0), ("131", 0, 2200000)], "résultat N-1 en instance d'affectation")
        E("2026-02-01", [(b, 4000000, 0), ("162", 0, 4000000)], "emprunt")
        E("2026-03-01", [("2411", 2400000, 0), ("4451", 462000, 0), ("4812", 0, 2862000)], "chambre froide")
        E("2026-04-01", [("4812", 2862000, 0), (b, 0, 2862000)], "paiement fournisseur d'investissement")
        E("2026-05-01", [("162", 800000, 0), ("6712", 120000, 0), (b, 0, 920000)], "échéance d'emprunt")
        E("2026-06-01", [(c, 1192500, 0), ("7061", 0, 1000000), ("4432", 0, 192500)], "séminaire payé comptant")
        E("2026-06-15", [("6011", 800000, 0), ("4452", 154000, 0), ("4011", 0, 954000)], "achat non réglé")
        E("2026-06-30", [("4431", 962500, 0), ("4452", 0, 577500), ("4441", 0, 385000)], "liquidation de TVA")
        E("2026-07-10", [("4441", 385000, 0), (b, 0, 385000)], "paiement de la TVA")
        E("2026-07-01", [("6611", 500000, 0), ("422", 0, 430000), ("431", 0, 21000), ("4472", 0, 49000)], "paie")
        E("2026-07-01", [("664", 60000, 0), ("431", 0, 60000)], "charges patronales")
        E("2026-07-05", [("422", 430000, 0), (b, 0, 430000)], "paiement des salaires")
        E("2026-07-15", [("131", 2200000, 0), ("111", 0, 220000), ("465", 0, 1000000), ("121", 0, 980000)], "affectation")
        E("2026-08-01", [("465", 1000000, 0), (b, 0, 1000000)], "dividendes payés")
        E("2026-12-31", [("6813", 480000, 0), ("2841", 0, 480000)], "amortissement")
        E("2026-12-31", [("311", 700000, 0), ("6031", 0, 700000)], "stock final")
        E("2026-12-31", [("891", 100000, 0), ("441", 0, 100000)], "impôt sur le résultat")

    def compute(self, date_from, date_to, statements=("actif", "passif", "resultat", "flux")):
        return self.engine.compute(self.company, fields.Date.to_date(date_from), fields.Date.to_date(date_to), statements)

    def assertAmount(self, value, expected, msg=None):
        self.assertAlmostEqual(value, expected, places=2, msg=msg)
