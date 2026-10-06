# -*- coding: utf-8 -*-
"""Test avancé : cycle de vie de la déclaration mensuelle et de son écriture de liquidation.

Tous les montants attendus sont calculés à la main (règle 2 de CLAUDE.md). TVA 19,25 % = 77/400 : chaque base est un
multiple de 400, les taxes sont donc des entiers en XAF.

Scénario de référence, juillet 2026 (``july_documents``) :
    vente de biens  2 000 000 HT (tva_sale_19_25)          → TVA 2 000 000 × 19,25 % = 385 000 au crédit de 4431
    achat de biens    800 000 HT (tva_purchase_good_19_25)  → TVA   800 000 × 19,25 % = 154 000 au débit de 4452
    L28 = 385 000 ; L29 = L17 (0) + 154 000 = 154 000 ; L32 = 385 000 − 154 000 = 231 000 ; L33 = L35 = 0
    L50 = 2 000 000 × 2 % = 40 000, CAC 10 % = 4 000, total 44 000 ; L52 = L53 = 0 → L54 = 44 000
    Écriture de liquidation au 31/07/2026, journal des opérations diverses :
        4431   D 385 000  (solde de la TVA collectée)
        4452   C 154 000  (solde de la TVA récupérable)
        4441   C 231 000  (L32, TVA due)
        449250 D  44 000  (L54, acompte d'impôt sur le résultat)
        441100 C  44 000  (L54, acompte à payer)
    Total des débits = total des crédits = 385 000 + 44 000 = 429 000.
"""
import datetime

from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_vat_declaration import VatDeclarationCommon

# lignes attendues de l'écriture de juillet : (préfixe de compte, débit, crédit)
JULY_CLOSING = [
    ("4431", 385000, 0),      # 2 000 000 × 19,25 %
    ("4452", 0, 154000),      # 800 000 × 19,25 %
    ("4441", 0, 231000),      # L32 = 385 000 − 154 000
    ("449250", 44000, 0),     # L54 = 2 000 000 × 2 % = 40 000, + 10 % de CAC = 4 000
    ("441100", 0, 44000),
]


@tagged("post_install", "-at_install", "aite_syscohada", "aite_syscohada_advanced")
class TestAdvClosingLifecycle(VatDeclarationCommon):
    """Écriture de liquidation, états de la déclaration, échéance, contraintes et saisies du déclarant."""

    # ------------------------------------------------------------------ outils
    def july_documents(self):
        """Vente de biens 2 000 000 et achat de biens 800 000, juillet 2026."""
        self.doc("out_invoice", "2026-07-06", 2000000, self.t_sale)          # TVA 385 000 → 4431
        self.doc("in_invoice", "2026-07-13", 800000, self.t_buy, "6011")     # TVA 154 000 → 4452

    def closing_lines(self, move):
        """Lignes de l'écriture triées : [(compte, débit, crédit)]."""
        return sorted((l.account_id.id, l.debit, l.credit) for l in move.line_ids)

    def expected_lines(self, rows):
        """Lignes attendues à partir de (préfixe, débit, crédit) ; 449250 et 441100 sont des sous-comptes du socle."""
        return sorted((self.acc(prefix).id, debit, credit) for prefix, debit, credit in rows)

    def totals(self, decl):
        """L28, L29, L32, L33, L35, L54 et total à payer."""
        return (decl.vat_collected, decl.vat_deductible, decl.vat_to_pay, decl.vat_credit, decl.credit_to_report,
                decl.acompte_to_pay, decl.total_to_pay)

    def assertUserError(self, message, func, *args):
        """``func`` lève une UserError dont le message est exactement ``message``."""
        with self.assertRaises(UserError) as cm:
            func(*args)
        self.assertEqual(cm.exception.args[0], message)

    # ------------------------------------------------------------------ écriture de liquidation
    def test_closing_entry_exact_lines(self):
        """Juillet 2026 : écriture validée, datée du 31/07, journal général, cinq lignes exactes ; une seule écriture."""
        self.july_documents()
        decl = self.declare("2026-07-01", "2026-07-31")
        # L32 = 231 000 ; L54 = 44 000 ; total à payer = L39 (= L32) + L54 = 231 000 + 44 000 = 275 000
        self.assertEqual(self.totals(decl), (385000, 154000, 231000, 0, 0, 44000, 275000), "juillet : L28 à L54 et total")
        move = decl.action_create_closing_entry()
        self.assertEqual(decl.move_id, move)
        self.assertEqual(move.state, "posted")
        self.assertEqual(move.date, datetime.date(2026, 7, 31), "écriture datée du dernier jour de la période")
        self.assertEqual(move.journal_id.type, "general")
        self.assertEqual(move.company_id, self.company)
        self.assertEqual(self.closing_lines(move), self.expected_lines(JULY_CLOSING), "lignes de l'écriture")
        self.assertEqual((sum(move.line_ids.mapped("debit")), sum(move.line_ids.mapped("credit"))), (429000, 429000),
                         "385 000 + 44 000 de chaque côté")
        # soldes après liquidation : 4431 et 4452 soldés ; 4441 = −231 000 ; 449250 = +44 000 ; 441100 = −44 000
        self.assertEqual([self.balance(p) for p in ("4431", "4452", "4441", "449250", "441100")],
                         [0, 0, -231000, 44000, -44000])
        # seconde demande : refusée, aucune nouvelle écriture
        moves_before = self.env["account.move"].search_count([("company_id", "=", self.company.id)])
        self.assertUserError("L'écriture de liquidation existe déjà.", decl.action_create_closing_entry)
        self.assertEqual(self.env["account.move"].search_count([("company_id", "=", self.company.id)]), moves_before)
        self.assertEqual(decl.move_id, move)

    def test_done_draft_and_recompute_keep_move(self):
        """Validée puis remise en brouillon ; recalcul refusé si validée ; après brouillon, move_id et totaux inchangés."""
        self.july_documents()
        decl = self.declare("2026-07-01", "2026-07-31")
        move = decl.action_create_closing_entry()
        decl.action_done()
        self.assertEqual(decl.state, "done")
        self.assertUserError("Déclaration validée : remettez-la en brouillon pour la recalculer.", decl.action_compute)
        decl.action_draft()
        self.assertEqual(decl.state, "draft")
        decl.action_compute()
        # l'écriture de liquidation ne porte aucune étiquette de taxe et ne touche aucun compte de retenue (L40 à L49) :
        # le recalcul retrouve L28 = 385 000, L29 = 154 000, L32 = 231 000, L54 = 44 000, total 275 000
        self.assertEqual(decl.move_id, move, "le recalcul garde l'écriture de liquidation")
        self.assertEqual(move.state, "posted")
        self.assertEqual(self.totals(decl), (385000, 154000, 231000, 0, 0, 44000, 275000), "totaux inchangés")
        self.assertEqual((self.line(decl, "CM_NORMAL").base, self.line(decl, "CM_NORMAL").tax), (2000000, 385000))
        self.assertEqual(self.line(decl, "CM_LOCAL_PURCHASE").tax, 154000)
        # validée à nouveau : toujours une seule écriture de liquidation
        decl.action_done()
        self.assertUserError("L'écriture de liquidation existe déjà.", decl.action_create_closing_entry)

    def test_nothing_to_close(self):
        """Mois sans écriture : toutes les lignes à zéro, aucun acompte, liquidation refusée."""
        decl = self.declare("2026-08-01", "2026-08-31")
        self.assertEqual(self.totals(decl), (0, 0, 0, 0, 0, 0, 0))
        self.assertUserError("Rien à liquider pour cette période.", decl.action_create_closing_entry)
        self.assertFalse(decl.move_id)

    # ------------------------------------------------------------------ échéance et contraintes
    def test_date_due(self):
        """Dépôt et paiement avant le 15 du mois suivant, y compris en fin d'année."""
        feb = self.Decl.create({"company_id": self.company.id, "date_from": "2026-02-01", "date_to": "2026-02-28"})
        dec = self.Decl.create({"company_id": self.company.id, "date_from": "2026-12-01", "date_to": "2026-12-31"})
        # 28/02/2026 → mois suivant mars 2026, le 15 ; 31/12/2026 → mois suivant janvier 2027, le 15
        self.assertEqual(feb.date_due, datetime.date(2026, 3, 15))
        self.assertEqual(dec.date_due, datetime.date(2027, 1, 15))

    def test_period_unique_and_dates_ordered(self):
        """Une seule déclaration par société et période ; date de début postérieure à la date de fin refusée."""
        self.Decl.create({"company_id": self.company.id, "date_from": "2026-07-01", "date_to": "2026-07-31"})
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.Decl.create({"company_id": self.company.id, "date_from": "2026-07-01", "date_to": "2026-07-31"})
        # une autre période reste possible
        self.assertTrue(self.Decl.create({"company_id": self.company.id, "date_from": "2026-08-01", "date_to": "2026-08-31"}))
        with self.assertRaises(ValidationError) as cm:
            self.Decl.create({"company_id": self.company.id, "date_from": "2026-09-30", "date_to": "2026-09-01"})
        self.assertEqual(cm.exception.args[0], "La date de début doit précéder la date de fin.")

    # ------------------------------------------------------------------ saisies du déclarant
    def test_manual_credit_previous(self):
        """L17 saisi à la main (10 000) avant le calcul : ligne CM_CREDIT_REPORTED, effet sur L32 puis sur L35."""
        # --- juillet : L32 diminué du crédit antérieur
        self.july_documents()
        jul = self.declare("2026-07-01", "2026-07-31", credit_previous=10000)
        self.assertEqual(jul.credit_previous, 10000, "la saisie n'est pas écrasée par le calcul")
        self.assertEqual(self.line(jul, "CM_CREDIT_REPORTED").tax, 10000, "L17")
        # L29 = 10 000 + 154 000 = 164 000 ; L32 = 385 000 − 164 000 = 221 000 ; L33 = L35 = 0 ; L54 = 44 000
        self.assertEqual(self.totals(jul)[:6], (385000, 164000, 221000, 0, 0, 44000))
        move = jul.action_create_closing_entry()
        # 4431 D 385 000 ; 4452 C 154 000 ; 4449 C 10 000 (L17 imputé) ; 4441 C 221 000 ; acompte 44 000
        # débits 385 000 + 44 000 = 429 000 ; crédits 154 000 + 10 000 + 221 000 + 44 000 = 429 000
        self.assertEqual(self.closing_lines(move), self.expected_lines([
            ("4431", 385000, 0), ("4452", 0, 154000), ("4449", 0, 10000), ("4441", 0, 221000),
            ("449250", 44000, 0), ("441100", 0, 44000)]))
        # --- septembre : achats seuls, le crédit antérieur s'ajoute au crédit à reporter
        self.doc("in_invoice", "2026-09-10", 400000, self.t_buy, "6011")   # TVA 400 000 × 19,25 % = 77 000 → 4452
        sep = self.declare("2026-09-01", "2026-09-30", credit_previous=10000)
        self.assertEqual(self.line(sep, "CM_CREDIT_REPORTED").tax, 10000, "L17")
        # L28 = 0 ; L29 = 10 000 + 77 000 = 87 000 ; L32 = 0 ; L33 = 87 000 ; L35 = 87 000 − L34 (0) = 87 000 ; L54 = 0
        self.assertEqual(self.totals(sep)[:6], (0, 87000, 0, 87000, 87000, 0))
        self.assertEqual(self.line(sep, "CM_CREDIT_REPORT").tax, 87000, "L35 (ligne)")
        move = sep.action_create_closing_entry()
        # 4452 C 77 000 ; 4449 C 10 000 (L17 imputé) ; 4449 D 87 000 (L35) → 87 000 de chaque côté
        self.assertEqual(self.closing_lines(move), self.expected_lines([
            ("4452", 0, 77000), ("4449", 0, 10000), ("4449", 87000, 0)]))
        # 4449 cumulé : −10 000 (juillet) − 10 000 + 87 000 (septembre) = 67 000
        self.assertEqual(self.balance("4449"), 67000)

    def test_adjustment_l27_counterpart(self):
        """L27 (adj_other) sans compte de contrepartie : refus exact ; avec 4711 : écriture équilibrée, 4711 soldé à +5 000."""
        self.doc("out_invoice", "2026-10-05", 400000, self.t_sale)   # TVA 400 000 × 19,25 % = 77 000 → 4431
        decl = self.declare("2026-10-01", "2026-10-31", adj_other=5000)
        self.assertEqual(self.line(decl, "CM_ADJUSTMENT_OTHER").tax, 5000, "L27")
        self.assertEqual(self.line(decl, "CM_ADJUSTMENT_TO_PAY").tax, 5000, "L31 = L26 + L27 = 0 + 5 000")
        # L32 = L28 − L29 − L30 + L31 = 77 000 − 0 − 0 + 5 000 = 82 000 ; L54 = 400 000 × 2 % = 8 000 + 800 = 8 800
        self.assertEqual(self.totals(decl)[:6], (77000, 0, 82000, 0, 0, 8800))
        self.assertUserError("Renseignez le compte de contrepartie des régularisations (L11, L24 à L27).",
                             decl.action_create_closing_entry)
        self.assertFalse(decl.move_id)
        decl.adjustment_account_id = self.acc("4711")
        move = decl.action_create_closing_entry()
        # 4431 D 77 000 ; 4441 C 82 000 ; 4711 D 5 000 (contrepartie de L27) ; 449250 D 8 800 ; 441100 C 8 800
        # débits 77 000 + 5 000 + 8 800 = 90 800 = crédits 82 000 + 8 800
        self.assertEqual(self.closing_lines(move), self.expected_lines([
            ("4431", 77000, 0), ("4441", 0, 82000), ("4711", 5000, 0), ("449250", 8800, 0), ("441100", 0, 8800)]))
        self.assertEqual((sum(move.line_ids.mapped("debit")), sum(move.line_ids.mapped("credit"))), (90800, 90800))
        self.assertEqual((self.balance("4711"), self.balance("4441"), self.balance("4431")), (5000, -82000, 0))

    def test_closing_never_touches_waiting_account(self):
        """Prestation sur encaissement impayée : 443800 garde sa TVA en attente, l'écriture de liquidation l'ignore."""
        self.july_documents()
        # prestation 1 000 000 HT impayée : TVA 1 000 000 × 19,25 % = 192 500 au crédit de 443800, non exigible
        self.doc("out_invoice", "2026-07-20", 1000000, self.t_services, "7061")
        waiting = self.t_services.cash_basis_transition_account_id
        self.assertEqual(waiting.code, "443800")
        decl = self.declare("2026-07-01", "2026-07-31")
        # la prestation non encaissée n'entre ni dans L10, ni dans L15 (base de l'acompte) : mêmes totaux que juillet seul
        self.assertEqual(self.line(decl, "CM_GLOBAL").base, 2000000, "L15 sans la prestation impayée")
        self.assertEqual(self.totals(decl), (385000, 154000, 231000, 0, 0, 44000, 275000))
        move = decl.action_create_closing_entry()
        self.assertFalse(move.line_ids.filtered(lambda l: l.account_id == waiting), "aucune ligne sur 443800")
        self.assertEqual(self.closing_lines(move), self.expected_lines(JULY_CLOSING))
        self.assertEqual(self.balance("4438"), -192500, "TVA de la prestation toujours en attente")
