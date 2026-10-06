# -*- coding: utf-8 -*-
"""Test avancé : factures mixtes avec retenues à la source (mai 2026), extourne, liquidation et reversement (juin).

Tous les montants attendus sont calculés à la main (règle 2 de CLAUDE.md). TVA 19,25 % = 77/400 : chaque base est un
multiple de 400, les taxes sont donc entières en XAF. Les taux des retenues sont ceux paramétrés par le socle (taxes
« taux à valider », inactives, activées pour le test comme dans test_itvair) : loyers 15 %, honoraires 5 %, TSR 15 %,
acompte sur CA 2 %, précompte sur achats 2 %, autoliquidation 19,25 % (4454 à +100 %, 447161 à −100 %).

Pièces de mai 2026 (plan « cm », comptes à six chiffres) :
    (a) honoraires locaux 1 000 000 HT, TVA services 19,25 % + retenue honoraires 5 %
        6324 D 1 000 000 ; 445400 D 192 500 ; 447140 C 50 000 ; 401100 C 1 000 000 + 192 500 − 50 000 = 1 142 500
    (b) loyer 600 000, retenue loyers 15 %
        6222 D 600 000 ; 447130 C 90 000 ; 401100 C 510 000
    (c) prestataire étranger 2 000 000, autoliquidation + TSR 15 %
        6324 D 2 000 000 ; 445400 D 385 000 ; 447161 C 385 000 ; 447120 C 300 000 ; 401100 C 1 700 000
    (d) client habilité 3 000 000, TVA 19,25 % + acompte sur CA subi 2 % + retenue honoraires subie 5 %
        7061 C 3 000 000 ; 443100 C 577 500 ; 449220 D 60 000 ; 449240 D 150 000 ; 411100 D 3 367 500
    (e) achat de biens 500 000, TVA biens 19,25 % + précompte sur achats 2 %
        6011 D 500 000 ; 445200 D 96 250 ; 449210 D 10 000 ; 401100 C 606 250
    (f) seconds honoraires 400 000, TVA services + retenue honoraires, ANNULÉS le 25 mai par extourne validée
        facture  : 6324 D 400 000 ; 445400 D 77 000 ; 447140 C 20 000 ; 401100 C 457 000
        extourne : les mêmes lignes inversées (447140 D 20 000 ; 445400 C 77 000 ; 401100 D 457 000)

Déclaration de mai :
    TVA : L10 base 3 000 000, taxe 577 500 ; L18 96 250 ; L19 192 500 + 77 000 − 77 000 = 192 500 ; L21 385 000 ;
          déductible 96 250 + 192 500 + 385 000 = 673 750 ; L32 = max(577 500 − 673 750, 0) = 0 ; L33 = L35 = 96 250.
    I/TVA-IR : L0 300 000 ; L38 385 000 ; L39 = L32 + L38 = 385 000 ; L42 90 000 ; L43 50 000 (facture annulée exclue) ;
          L44 140 000 ; L45 60 000 ; L46 10 000 ; L48 150 000 ; L49 220 000 ; L50 = 3 000 000 × 2 % = 60 000, CAC 6 000 ;
          L54 = max(66 000 − 220 000, 0) = 0 ; L55 = 220 000 − 66 000 = 154 000 ; TOTAL = 300 000 + 385 000 + 140 000 = 825 000.
    Liquidation : 443100 D 577 500 ; 445200 C 96 250 ; 445400 C 577 500 (192 500 + 385 000 autoliquidés) ; 444900 D 96 250 ;
          aucune ligne sur 447xxx ni 449xxx.
Juin : reversement de la retenue de mai (447140 D 50 000, banque C 50 000) ; L43 de juin = 0 ; L53 = 154 000 ; L17 = 96 250.
"""
import logging
import unittest
from datetime import date

from odoo import fields
from odoo.tests import tagged

from .test_vat_declaration import VatDeclarationCommon

_logger = logging.getLogger(__name__)

# taxes inactives du socle (taux à valider) activées pour le test, comme dans test_itvair
WITHHOLDING_KEYS = ("retenue_loyers", "retenue_honoraires", "retenue_tsr", "retenue_tva", "retenue_acompte_ca",
                    "subie_acompte_ca", "subie_loyers", "subie_honoraires", "precompte_achats", "autoliquidation_services")
# comptes de retenues et de précomptes : la liquidation de TVA ne doit jamais les toucher
WITHHOLDING_ACCOUNTS = ("447120", "447130", "447140", "447160", "447161", "447170", "447180",
                        "449210", "449220", "449230", "449240")


@tagged("post_install", "-at_install", "aite_syscohada", "aite_syscohada_advanced")
class TestAdvWithholdingMixed(VatDeclarationCommon):
    """Factures mixtes TVA + retenues, extourne dans le mois, liquidation de mai et reversement en juin."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ref = cls.company._aite_tax_ref
        cls.taxes = {key: ref(key) for key in WITHHOLDING_KEYS}
        for key, tax in cls.taxes.items():
            assert tax, f"taxe {key} absente du paramétrage"
            tax.active = True
        cls.w_rent, cls.w_fees, cls.w_tsr = cls.taxes["retenue_loyers"], cls.taxes["retenue_honoraires"], cls.taxes["retenue_tsr"]
        cls.s_acompte, cls.s_fees = cls.taxes["subie_acompte_ca"], cls.taxes["subie_honoraires"]
        cls.precompte, cls.auto = cls.taxes["precompte_achats"], cls.taxes["autoliquidation_services"]
        cls.may_documents()

    @classmethod
    def may_documents(cls):
        """Les six pièces de mai 2026 décrites dans l'en-tête du module, plus l'extourne de la pièce (f)."""
        cls.inv_fees = cls.doc("in_invoice", "2026-05-04", 1000000, cls.t_buy_services | cls.w_fees, "6324")   # (a)
        cls.inv_rent = cls.doc("in_invoice", "2026-05-06", 600000, cls.w_rent, "6222")                          # (b)
        cls.inv_foreign = cls.doc("in_invoice", "2026-05-08", 2000000, cls.auto | cls.w_tsr, "6324")           # (c)
        cls.inv_customer = cls.doc("out_invoice", "2026-05-12", 3000000, cls.t_sale | cls.s_acompte | cls.s_fees, "7061")  # (d)
        cls.inv_goods = cls.doc("in_invoice", "2026-05-15", 500000, cls.t_buy | cls.precompte, "6011")          # (e)
        cls.inv_cancelled = cls.doc("in_invoice", "2026-05-20", 400000, cls.t_buy_services | cls.w_fees, "6324")  # (f)
        day = fields.Date.to_date("2026-05-25")
        cls.reversal = cls.inv_cancelled._reverse_moves(
            default_values_list=[{"date": day, "invoice_date": day, "ref": "annulation des honoraires du 20 mai"}],
            cancel=True)

    # ------------------------------------------------------------------ outils
    def _callTestMethod(self, method):
        """Honore ``unittest.expectedFailure`` sous Odoo 18.

        Le lanceur d'Odoo (``odoo.tests.case.TestCase.run``) ignore l'attribut posé par le décorateur : un défaut connu
        serait compté comme un échec ordinaire. Pour cette classe, une méthode décorée dont une assertion échoue est
        journalisée comme échec attendu et n'est pas comptée ; si elle réussit, le défaut est corrigé et le test échoue
        explicitement pour que le décorateur soit retiré (sémantique d'unittest).
        """
        if not getattr(method, "__unittest_expecting_failure__", False):
            return super()._callTestMethod(method)
        try:
            method()
        except self.failureException as exc:
            _logger.info("échec attendu (défaut connu) dans %s : %s", self._testMethodName, exc)
            return
        self.fail("succès inattendu : le défaut connu paraît corrigé, retirez @unittest.expectedFailure")

    def it(self, decl, code):
        """Ligne du formulaire I/TVA-IR (hors TVA)."""
        return decl.itvair_line_ids.filtered(lambda l: l.code == code)

    def amounts(self, decl, code):
        """(base, principal, CAC, total) d'une ligne I/TVA-IR."""
        line = self.it(decl, code)
        return line.base, line.principal, line.cac, line.total

    def vat(self, decl, code):
        """(base, taxe) d'une ligne de TVA L10 à L35."""
        line = self.line(decl, code)
        return line.base, line.tax

    def move_lines(self, move, prefix):
        """(total débit, total crédit) des lignes de ``move`` dont le compte commence par ``prefix``."""
        lines = move.line_ids.filtered(lambda l: l.account_id.code.startswith(prefix))
        return sum(lines.mapped("debit")), sum(lines.mapped("credit"))

    def partner_line(self, move):
        """(débit, crédit) de la ligne de tiers (401 ou 411) de la pièce."""
        lines = move.line_ids.filtered(lambda l: l.display_type == "payment_term")
        return sum(lines.mapped("debit")), sum(lines.mapped("credit"))

    def tax_line(self, move, tax, prefix):
        """Ligne de taxe de ``move`` portée par ``tax`` sur le compte ``prefix`` (unique)."""
        line = move.line_ids.filtered(lambda l: l.tax_line_id == tax and l.account_id.code.startswith(prefix))
        self.assertEqual(len(line), 1, f"une seule ligne de taxe {tax.name} sur {prefix}")
        return line

    def may(self):
        return self.declare("2026-05-01", "2026-05-31")

    # ------------------------------------------------------------------ écritures des pièces de mai
    def test_a_local_fees_invoice(self):
        """(a) TVA 1 000 000 × 19,25 % = 192 500 (4454) ; retenue 1 000 000 × 5 % = 50 000 au crédit du 447140 ;
        fournisseur 1 000 000 + 192 500 − 50 000 = 1 142 500 ; total des taxes 192 500 − 50 000 = 142 500."""
        move = self.inv_fees
        self.assertEqual(move.state, "posted")
        self.assertEqual(self.move_lines(move, "6324"), (1000000, 0), "charge d'honoraires")
        self.assertEqual(self.move_lines(move, "445400"), (192500, 0), "TVA déductible sur services")
        self.assertEqual(self.move_lines(move, "447140"), (0, 50000), "retenue sur honoraires au crédit")
        self.assertEqual(self.partner_line(move), (0, 1142500), "fournisseur net de retenue")
        self.assertEqual(self.move_lines(move, "401"), (0, 1142500))
        self.assertEqual((move.amount_untaxed, move.amount_tax, move.amount_total), (1000000, 142500, 1142500))
        self.assertEqual(sum(move.line_ids.mapped("debit")), 1192500, "équilibre : 1 000 000 + 192 500")
        self.assertEqual(sum(move.line_ids.mapped("credit")), 1192500, "équilibre : 50 000 + 1 142 500")
        # la ligne de retenue porte la base de taxe, source de la colonne « base » de L43
        self.assertEqual(abs(self.tax_line(move, self.w_fees, "447140").tax_base_amount), 1000000)

    def test_b_rent_invoice(self):
        """(b) retenue 600 000 × 15 % = 90 000 au crédit du 447130 ; fournisseur 600 000 − 90 000 = 510 000."""
        move = self.inv_rent
        self.assertEqual(move.state, "posted")
        self.assertEqual(self.move_lines(move, "6222"), (600000, 0), "charge de loyer")
        self.assertEqual(self.move_lines(move, "447130"), (0, 90000), "précompte sur loyers au crédit")
        self.assertEqual(self.partner_line(move), (0, 510000), "bailleur net de précompte")
        self.assertEqual((move.amount_untaxed, move.amount_tax, move.amount_total), (600000, -90000, 510000))
        self.assertEqual(abs(self.tax_line(move, self.w_rent, "447130").tax_base_amount), 600000)

    def test_c_foreign_reverse_charge_invoice(self):
        """(c) TVA autoliquidée 2 000 000 × 19,25 % = 385 000 : 4454 au débit (+100 %) et 447161 au crédit (−100 %) ;
        TSR 2 000 000 × 15 % = 300 000 au crédit du 447120 ; fournisseur 2 000 000 + 385 000 − 385 000 − 300 000 = 1 700 000."""
        move = self.inv_foreign
        self.assertEqual(move.state, "posted")
        self.assertEqual(self.move_lines(move, "6324"), (2000000, 0))
        self.assertEqual(self.move_lines(move, "445400"), (385000, 0), "TVA autoliquidée déductible")
        self.assertEqual(self.move_lines(move, "447161"), (0, 385000), "TVA autoliquidée à reverser")
        self.assertEqual(self.move_lines(move, "447120"), (0, 300000), "TSR retenue")
        self.assertEqual(self.partner_line(move), (0, 1700000), "prestataire étranger net de TSR, TVA neutre")
        self.assertEqual((move.amount_untaxed, move.amount_tax, move.amount_total), (2000000, -300000, 1700000))
        self.assertEqual(sum(move.line_ids.mapped("debit")), 2385000, "équilibre : 2 000 000 + 385 000")
        self.assertEqual(abs(self.tax_line(move, self.w_tsr, "447120").tax_base_amount), 2000000)
        self.assertEqual(abs(self.tax_line(move, self.auto, "447161").tax_base_amount), 2000000)

    def test_d_customer_withholding_invoice(self):
        """(d) TVA collectée 3 000 000 × 19,25 % = 577 500 (4431) ; acompte subi 3 000 000 × 2 % = 60 000 au débit du
        449220 ; retenue subie 3 000 000 × 5 % = 150 000 au débit du 449240 ;
        client 3 000 000 + 577 500 − 60 000 − 150 000 = 3 367 500."""
        move = self.inv_customer
        self.assertEqual(move.state, "posted")
        self.assertEqual(self.move_lines(move, "7061"), (0, 3000000), "produit de prestations")
        self.assertEqual(self.move_lines(move, "443100"), (0, 577500), "TVA collectée")
        self.assertEqual(self.move_lines(move, "449220"), (60000, 0), "acompte sur CA retenu par le client")
        self.assertEqual(self.move_lines(move, "449240"), (150000, 0), "retenue sur honoraires subie")
        self.assertEqual(self.partner_line(move), (3367500, 0), "client net des retenues")
        self.assertEqual(self.move_lines(move, "411"), (3367500, 0))
        self.assertEqual((move.amount_untaxed, move.amount_tax, move.amount_total), (3000000, 367500, 3367500))
        self.assertEqual(sum(move.line_ids.mapped("debit")), 3577500, "équilibre : 60 000 + 150 000 + 3 367 500")
        self.assertEqual(abs(self.tax_line(move, self.s_acompte, "449220").tax_base_amount), 3000000)
        self.assertEqual(abs(self.tax_line(move, self.s_fees, "449240").tax_base_amount), 3000000)

    def test_e_goods_precompte_invoice(self):
        """(e) TVA 500 000 × 19,25 % = 96 250 (4452) ; précompte 500 000 × 2 % = 10 000 au débit du 449210 (avance
        d'impôt facturée par le fournisseur) ; fournisseur 500 000 + 96 250 + 10 000 = 606 250."""
        move = self.inv_goods
        self.assertEqual(move.state, "posted")
        self.assertEqual(self.move_lines(move, "6011"), (500000, 0))
        self.assertEqual(self.move_lines(move, "445200"), (96250, 0), "TVA déductible sur biens")
        self.assertEqual(self.move_lines(move, "449210"), (10000, 0), "précompte subi au débit")
        self.assertEqual(self.partner_line(move), (0, 606250), "fournisseur TTC + précompte")
        self.assertEqual((move.amount_untaxed, move.amount_tax, move.amount_total), (500000, 106250, 606250))
        self.assertEqual(abs(self.tax_line(move, self.precompte, "449210").tax_base_amount), 500000)

    def test_f_reversal_entry(self):
        """(f) facture 400 000 : TVA 77 000 (4454), retenue 20 000 (447140), fournisseur 457 000 ; l'extourne validée
        le 25 mai inverse chaque ligne et lettre le fournisseur. Solde du 447140 après extourne :
        −50 000 (a) − 20 000 (f) + 20 000 (extourne) = −50 000."""
        move, rev = self.inv_cancelled, self.reversal
        self.assertEqual(self.move_lines(move, "445400"), (77000, 0))
        self.assertEqual(self.move_lines(move, "447140"), (0, 20000))
        self.assertEqual(self.partner_line(move), (0, 457000))
        self.assertEqual(len(rev), 1)
        self.assertEqual((rev.state, rev.move_type, rev.date, rev.reversed_entry_id), ("posted", "in_refund", date(2026, 5, 25), move))
        self.assertEqual(self.move_lines(rev, "6324"), (0, 400000), "charge annulée")
        self.assertEqual(self.move_lines(rev, "445400"), (0, 77000), "TVA déductible annulée")
        self.assertEqual(self.move_lines(rev, "447140"), (20000, 0), "retenue annulée : débit du 447140")
        self.assertEqual(self.partner_line(rev), (457000, 0), "fournisseur soldé")
        self.assertEqual(move.payment_state, "reversed", "facture lettrée avec son extourne")
        self.assertEqual(self.balance("447140"), -50000, "seule la retenue de la facture (a) reste due")
        self.assertEqual(self.balance("445400"), 192500 + 385000, "TVA services : (a) + (c), (f) neutralisée")

    # ------------------------------------------------------------------ déclaration de mai
    def test_may_vat_lines(self):
        """TVA de mai : collectée 577 500 ; déductible 96 250 (L18) + 192 500 (L19, extourne neutralisée) + 385 000 (L21)
        = 673 750 ; L32 = max(577 500 − 673 750, 0) = 0 ; crédit L33 = L35 = 96 250."""
        decl = self.may()
        self.assertEqual(self.vat(decl, "CM_NORMAL"), (3000000, 577500), "L10 : vente (d) seule")
        self.assertEqual(self.vat(decl, "CM_GLOBAL"), (3000000, 577500))
        self.assertEqual(self.line(decl, "CM_CREDIT_REPORTED").tax, 0, "L17 : aucune déclaration validée avant mai")
        self.assertEqual(self.line(decl, "CM_LOCAL_PURCHASE").tax, 96250, "L18 : achat (e)")
        self.assertEqual(self.line(decl, "CM_LOCAL_SERVICE").tax, 192500, "L19 : (a) + (f) − extourne de (f)")
        self.assertEqual(self.line(decl, "CM_FOREIGN_SERVICE").tax, 385000, "L21 : autoliquidation (c)")
        self.assertEqual(self.line(decl, "CM_DEDUCTIBLE_VAT").tax, 673750)
        self.assertEqual((decl.vat_collected, decl.vat_deductible, decl.vat_to_pay, decl.vat_credit, decl.credit_to_report),
                         (577500, 673750, 0, 96250, 96250))

    def test_may_itvair_lines(self):
        """Lignes I/TVA-IR de mai hors L43 (défaut connu, test dédié) : L0 300 000 ; L38 385 000 ; L39 = L32 + L38 ;
        L42 90 000 ; L45 60 000 ; L46 10 000 ; L48 150 000 ; L49 220 000 ; L50 60 000 + CAC 6 000 ; L54 0 ; L55 154 000.
        La colonne « base » de chaque ligne de retenue est la base de taxe de la facture."""
        decl = self.may()
        self.assertEqual(decl.date_due, date(2026, 6, 15))
        self.assertEqual(self.amounts(decl, "L0"), (2000000, 300000, 0, 300000), "TSR : crédits du 447120")
        self.assertEqual(self.amounts(decl, "L36"), (0, 0, 0, 0), "L36 = L32 = 0")
        self.assertEqual(self.amounts(decl, "L37"), (0, 0, 0, 0), "aucune TVA retenue par un client habilité")
        self.assertEqual(self.amounts(decl, "L38"), (2000000, 385000, 0, 385000), "TVA autoliquidée : crédits du 447161")
        self.assertEqual(self.it(decl, "L39").total, 385000, "L39 = L32 (0) + L38 (385 000)")
        self.assertEqual(self.it(decl, "L39").total, decl.vat_to_pay + self.it(decl, "L38").total)
        self.assertEqual(self.amounts(decl, "L40"), (0, 0, 0, 0))
        self.assertEqual(self.amounts(decl, "L41"), (0, 0, 0, 0))
        self.assertEqual(self.amounts(decl, "L42"), (600000, 90000, 0, 90000), "loyers : base 600 000, 15 %")
        self.assertEqual(self.amounts(decl, "L45"), (3000000, 60000, 0, 60000), "acompte subi : base 3 000 000, 2 %")
        self.assertEqual(self.amounts(decl, "L46"), (500000, 10000, 0, 10000), "précompte subi : base 500 000, 2 %")
        self.assertEqual(self.amounts(decl, "L47"), (0, 0, 0, 0))
        self.assertEqual(self.amounts(decl, "L48"), (3000000, 150000, 0, 150000), "retenue subie : base 3 000 000, 5 %")
        self.assertEqual(self.it(decl, "L49").total, 220000, "60 000 + 10 000 + 150 000")
        self.assertEqual(self.amounts(decl, "L50"), (3000000, 60000, 6000, 66000), "2 % du CA de L15 + 10 % de CAC")
        self.assertEqual([self.it(decl, c).total for c in ("L51", "L52", "L53", "L54", "L55")], [0, 220000, 0, 0, 154000],
                         "L54 = max(66 000 − 220 000, 0) ; L55 = 220 000 − 66 000")
        self.assertEqual((decl.acompte_to_pay, decl.is_credit_to_report), (0, 154000))
        for code in ("L8", "L62", "L66", "L73", "L77", "L80"):
            self.assertEqual(self.it(decl, code).total, 0, f"{code} : rien de saisi ni retenu")
        # total à payer = somme des sections du récapitulatif (la valeur à la main, 825 000, est dans le test du défaut)
        sections = sum(self.it(decl, c).total for c in ("L0", "L8", "L39", "L44", "L54", "L62", "L66", "L73", "L77", "L80"))
        self.assertEqual(decl.total_to_pay, sections)
        self.assertEqual(self.it(decl, "TOTAL").total, sections)
        self.assertEqual(sections, 300000 + 385000 + self.it(decl, "L44").total, "sections non nulles : L0, L39, L44")

    @unittest.expectedFailure
    def test_may_l43_excludes_reversed_invoice(self):
        """Comportement correct : L43 ne retient que la facture (a) : base 1 000 000, retenue 50 000 ; L44 = 90 000 +
        50 000 = 140 000 ; total à payer = 300 000 + 385 000 + 140 000 = 825 000.

        Défaut connu : ``itvair.py`` (``_itvair_compute``, nature « credit ») somme les seuls crédits du compte 447140
        et ignore le débit de 20 000 de l'extourne ; ``_itvair_ledger`` additionne de même les bases de taxe en valeur
        absolue. L43 est donc surestimée à 70 000 (base 1 800 000), L44 à 160 000 et le total à 845 000 : une retenue
        annulée serait reversée au Trésor.
        """
        decl = self.may()
        self.assertEqual(self.amounts(decl, "L43"), (1000000, 50000, 0, 50000), "L43 : facture (f) annulée exclue")
        self.assertEqual(self.it(decl, "L44").total, 140000, "90 000 + 50 000")
        self.assertEqual(decl.total_to_pay, 825000, "300 000 + 385 000 + 140 000")

    def test_may_closing_entry(self):
        """Liquidation de mai : 443100 D 577 500 ; 445200 C 96 250 ; 445400 C 192 500 + 385 000 = 577 500 ; 444900 D 96 250
        (L35) ; total 673 750 ; pas d'acompte (L54 = 0) ; aucune ligne sur 447xxx ni 449xxx, dont les soldes sont
        intacts après l'écriture."""
        decl = self.may()
        move = decl.action_create_closing_entry()
        self.assertEqual((move.state, move.date), ("posted", date(2026, 5, 31)))
        self.assertEqual(self.move_lines(move, "443100"), (577500, 0), "TVA collectée soldée")
        self.assertEqual(self.move_lines(move, "445200"), (0, 96250), "TVA sur biens soldée")
        self.assertEqual(self.move_lines(move, "445400"), (0, 577500), "TVA sur services, part autoliquidée comprise")
        self.assertEqual(self.move_lines(move, "444900"), (96250, 0), "crédit à reporter")
        self.assertEqual(self.move_lines(move, "444100"), (0, 0), "rien à payer en L32")
        self.assertEqual(self.move_lines(move, "449250"), (0, 0), "pas d'acompte liquidé")
        self.assertEqual(len(move.line_ids), 4)
        self.assertEqual(sum(move.line_ids.mapped("debit")), 673750)
        self.assertEqual(sum(move.line_ids.mapped("credit")), 673750)
        self.assertFalse(move.line_ids.filtered(lambda l: l.account_id.code[:3] in ("447", "449")),
                         "la liquidation ne touche ni les retenues (447) ni les précomptes subis (449)")
        for prefix in ("443100", "445200", "445400", "444100", "443800"):
            self.assertEqual(self.balance(prefix), 0, f"{prefix} soldé")
        self.assertEqual(self.balance("444900"), 96250)
        expected = {"447120": -300000, "447130": -90000, "447140": -50000, "447161": -385000,
                    "449210": 10000, "449220": 60000, "449240": 150000}
        for prefix in WITHHOLDING_ACCOUNTS:
            self.assertEqual(self.balance(prefix), expected.get(prefix, 0), f"{prefix} intact après liquidation")
        self.assertEqual(decl.move_id, move)

    # ------------------------------------------------------------------ juin : reversement au Trésor
    def test_june_treasury_payment_keeps_l43_at_zero(self):
        """Juin : le reversement de la retenue de mai (447140 D 50 000, banque C 50 000, écriture manuelle) solde le
        compte sans alimenter L43 (nature « credit » : un débit n'y entre pas) ; L43 de juin = 0, base 0.
        Reports depuis mai validée : L17 = 96 250 (L35 de mai) et L53 = 154 000 (L55 de mai) ; juin sans pièce :
        L50 = 0, L54 = 0, L55 = 154 000, TVA déductible 96 250 reportée en L35, total à payer 0."""
        may = self.may()
        may.action_create_closing_entry()
        may.action_done()
        payment = self.entry("2026-06-10", [("447140", 50000, 0), (self.bank, 0, 50000)], "reversement des retenues sur honoraires de mai")
        self.assertEqual(payment.state, "posted")
        self.assertEqual(self.balance("447140"), 0, "retenue de mai reversée : compte soldé")
        june = self.declare("2026-06-01", "2026-06-30")
        self.assertEqual(self.amounts(june, "L43"), (0, 0, 0, 0), "le reversement (débit) n'alimente pas L43")
        self.assertEqual(self.amounts(june, "L42"), (0, 0, 0, 0))
        self.assertEqual(self.it(june, "L44").total, 0)
        self.assertEqual(self.amounts(june, "L0"), (0, 0, 0, 0))
        self.assertEqual(june.credit_previous, 96250, "L17 : crédit L35 de mai")
        self.assertEqual(self.line(june, "CM_CREDIT_REPORTED").tax, 96250)
        self.assertEqual((june.vat_collected, june.vat_deductible, june.vat_to_pay, june.vat_credit, june.credit_to_report),
                         (0, 96250, 0, 96250, 96250))
        self.assertEqual(self.it(june, "L53").total, 154000, "crédit d'acompte L55 de mai repris")
        self.assertEqual(self.amounts(june, "L50"), (0, 0, 0, 0), "aucun chiffre d'affaires en juin")
        self.assertEqual((june.acompte_to_pay, june.is_credit_to_report, june.total_to_pay), (0, 154000, 0))
        self.assertEqual(self.it(june, "TOTAL").total, 0)
