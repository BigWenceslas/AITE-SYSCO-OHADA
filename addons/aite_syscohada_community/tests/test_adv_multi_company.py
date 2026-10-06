# -*- coding: utf-8 -*-
"""Test avancé : multi-sociétés et robustesse du rattachement des comptes.

Trois sociétés cohabitent dans la même base :
    A  : la société camerounaise de ``SyscohadaCommon`` (plan « cm », XAF) ;
    B  : une deuxième société camerounaise, plan « cm » chargé par ``try_loading`` ;
    BE : une société belge (pays BE, EUR) sur le plan générique d'Odoo, hors SYSCOHADA.
Le paramétrage AITE doit s'appliquer à A et B indépendamment, jamais à BE ; les écritures,
les états et la déclaration de TVA de chaque société doivent rester étanches.

Convention des montants (XAF, sans décimale) :
    TVA 19,25 % = 17,5 % + 10 % de CAC.
    Vente dans A  : 1 000 000 HT, TVA 1 000 000 × 19,25 % = 192 500, TTC 1 192 500.
    Achat dans B  :   500 000 HT, TVA   500 000 × 19,25 % =  96 250, TTC   596 250.
"""
import logging
import unittest

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.aite_syscohada_base.tests.common import SyscohadaCommon

_logger = logging.getLogger(__name__)

# Clés enregistrées dans ir.model.data par res_company.py pour une société « cm » :
# 4 taxes nommées (prestations encaissement, immobilisations, taxe de séjour, précompte),
# 8 retenues à la source (WITHHOLDING_TAXES), l'autoliquidation et le groupe de taxes « autres ».
EXPECTED_KEYS = {
    "tva_prestations_encaissement", "tva_immobilisations", "taxe_sejour", "precompte_achats",
    "retenue_loyers", "retenue_honoraires", "retenue_tsr", "retenue_tva", "retenue_acompte_ca",
    "subie_acompte_ca", "subie_loyers", "subie_honoraires",
    "autoliquidation_services", "tax_group_other",
}


@tagged("post_install", "-at_install", "aite_syscohada", "aite_syscohada_advanced")
class TestAdvMultiCompany(SyscohadaCommon):
    """Deux sociétés camerounaises et une société belge : paramétrage, isolation, couverture."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.company
        xaf = cls.env.ref("base.XAF")
        # ---- société B : deuxième société camerounaise, même plan « cm »
        company_b = cls.env["res.company"].create({
            "name": "Test SYSCOHADA AITE — société B", "country_id": cls.env.ref("base.cm").id, "currency_id": xaf.id})
        cls.env.user.company_ids |= company_b
        cls.company_b = cls.env["res.company"].browse(company_b.id)
        cls.env["account.chart.template"].try_loading("cm", company=cls.company_b, install_demo=False)
        # ---- société BE : belge, euro, plan générique d'Odoo (hors SYSCOHADA)
        eur = cls.env.ref("base.EUR")
        eur.active = True
        company_be = cls.env["res.company"].create({
            "name": "Société belge test", "country_id": cls.env.ref("base.be").id, "currency_id": eur.id})
        cls.env.user.company_ids |= company_be
        cls.company_be = cls.env["res.company"].browse(company_be.id)
        cls.env["account.chart.template"].try_loading("generic_coa", company=cls.company_be, install_demo=False)
        # ---- taxes du plan « cm » propres à chaque société
        cls.t_sale_a = cls.env["account.chart.template"].with_company(cls.company_a).ref("tva_sale_19_25")
        cls.t_buy_b = cls.env["account.chart.template"].with_company(cls.company_b).ref("tva_purchase_good_19_25")
        cls.partner = cls.env["res.partner"].create({"name": "Partenaire multi-sociétés"})

    # ------------------------------------------------------------------ outils multi-sociétés
    def _callTestMethod(self, method):
        """Honore ``unittest.expectedFailure`` sous Odoo 18 (mécanisme repris de test_adv_declaration_sequence.py).

        Le lanceur d'Odoo (``odoo.tests.case.TestCase.run`` et ``OdooTestResult``) ignore l'attribut posé par le
        décorateur : un défaut connu serait compté comme un échec ordinaire. Pour cette classe seulement, une méthode
        décorée dont une assertion échoue est journalisée comme échec attendu et n'est pas comptée ; si elle réussit,
        le défaut est corrigé et le test échoue explicitement pour que le décorateur soit retiré (sémantique d'unittest).
        """
        if not getattr(method, "__unittest_expecting_failure__", False):
            return super()._callTestMethod(method)
        try:
            method()
        except self.failureException as exc:
            _logger.info("échec attendu (défaut connu) dans %s : %s", self._testMethodName, exc)
            return
        self.fail("succès inattendu : le défaut connu paraît corrigé, retirez @unittest.expectedFailure")

    def acc_in(self, company, prefix):
        """Premier compte de ``company`` dont le code commence par ``prefix`` (lu dans le contexte de la société)."""
        account = self.env["account.account"].with_company(company).search(
            [("code", "=like", f"{prefix}%"), ("company_ids", "in", company.id)], order="code", limit=1)
        self.assertTrue(account, f"aucun compte {prefix} dans {company.name}")
        return account

    def invoice(self, company, move_type, day, price, tax, account_prefix):
        """Facture validée dans ``company`` : une ligne HT ``price`` sur le compte ``account_prefix`` avec ``tax``."""
        move = self.env["account.move"].with_company(company).create({
            "move_type": move_type, "partner_id": self.partner.id, "invoice_date": day, "date": day,
            "company_id": company.id,
            "invoice_line_ids": [Command.create({
                "name": "ligne", "quantity": 1, "price_unit": price,
                "account_id": self.acc_in(company, account_prefix).id, "tax_ids": [Command.set(tax.ids)]})],
        })
        move.action_post()
        return move

    def post_march_documents(self):
        """Vente de biens dans A et achat de biens dans B, mars 2026.

        A : 4111 débit 1 192 500 ; 7011 crédit 1 000 000 ; 4431 crédit 192 500 (= 1 000 000 × 19,25 %).
        B : 6011 débit 500 000 ; 4452 débit 96 250 (= 500 000 × 19,25 %) ; 4011 crédit 596 250.
        """
        self.sale_a = self.invoice(self.company_a, "out_invoice", "2026-03-05", 1000000, self.t_sale_a, "7011")
        self.purchase_b = self.invoice(self.company_b, "in_invoice", "2026-03-10", 500000, self.t_buy_b, "6011")

    def balance(self, company, prefix):
        """Solde (débit − crédit) des lignes validées du premier compte ``prefix`` de ``company``."""
        account = self.acc_in(company, prefix)
        return sum(self.env["account.move.line"].search(
            [("account_id", "=", account.id), ("company_id", "=", company.id), ("parent_state", "=", "posted")]
        ).mapped("balance"))

    def declare(self, company, date_from, date_to):
        """Déclaration de TVA calculée dans le contexte de ``company``."""
        decl = self.env["aite.cm.vat.declaration"].with_company(company).create(
            {"company_id": company.id, "date_from": date_from, "date_to": date_to})
        decl.action_compute()
        return decl

    def line(self, decl, code):
        return decl.line_ids.filtered(lambda l: l.code == code)

    def checks(self, company, date_from="2026-01-01", date_to="2026-12-31"):
        return {c["code"]: c for c in self.checker.run(company, date_from, date_to)}

    def coverage_codes(self, company):
        return [p["code"] for p in self.checker.coverage(company)]

    def create_account(self, company, code, name, account_type, **extra):
        return self.env["account.account"].with_company(company).create(dict({
            "code": code, "name": name, "account_type": account_type,
            "company_ids": [Command.set(company.ids)]}, **extra))

    # ------------------------------------------------------------------ (1) paramétrage par société
    def test_setup_applied_to_each_cm_company_only(self):
        """Le paramétrage AITE est appliqué aux deux sociétés « cm », jamais à la société belge."""
        self.assertTrue(self.company_a.aite_syscohada_setup_date, "société A : paramétrage non appliqué")
        self.assertTrue(self.company_b.aite_syscohada_setup_date, "société B : paramétrage non appliqué")
        self.assertTrue(self.company_a._aite_is_syscohada() and self.company_b._aite_is_syscohada())
        self.assertTrue(self.company_a.tax_exigibility and self.company_b.tax_exigibility,
                        "TVA sur encaissements activée dans chaque société camerounaise")
        # société belge : ni par le crochet de chargement du plan, ni par un appel explicite
        self.assertEqual(self.company_be.chart_template, "generic_coa")
        self.assertFalse(self.company_be._aite_is_syscohada())
        self.assertFalse(self.company_be.aite_syscohada_setup_date, "société belge : le crochet ne doit rien appliquer")
        self.company_be._aite_syscohada_setup()
        self.assertFalse(self.company_be.aite_syscohada_setup_date, "société belge : l'appel explicite ne doit rien appliquer")
        self.assertFalse(self.company_be._aite_tax_ref("tva_prestations_encaissement"))
        self.assertFalse(self.company_be._aite_account("552100"), "aucun sous-compte SYSCOHADA créé chez la belge")

    def test_tax_refs_are_distinct_per_company(self):
        """_aite_tax_ref retourne, par société, une taxe distincte rattachée à cette société."""
        tax_a = self.company_a._aite_tax_ref("tva_prestations_encaissement")
        tax_b = self.company_b._aite_tax_ref("tva_prestations_encaissement")
        self.assertTrue(tax_a and tax_b, "taxe « prestations encaissement » absente dans A ou B")
        self.assertNotEqual(tax_a.id, tax_b.id, "A et B doivent avoir chacune leur enregistrement de taxe")
        self.assertEqual(tax_a.company_id, self.company_a)
        self.assertEqual(tax_b.company_id, self.company_b)
        for tax, company in ((tax_a, self.company_a), (tax_b, self.company_b)):
            self.assertEqual((tax.type_tax_use, tax.amount, tax.tax_exigibility), ("sale", 19.25, "on_payment"), company.name)
            transition = tax.cash_basis_transition_account_id
            self.assertEqual(transition.with_company(company).code, "443800", company.name)
            self.assertEqual(transition.company_ids, company, "le compte d'attente 443800 appartient à sa seule société")
            tax_line = tax.repartition_line_ids.filtered(lambda l: l.repartition_type == "tax" and l.document_type == "invoice")
            self.assertEqual(tax_line.account_id.with_company(company).code, "443200", company.name)
            self.assertEqual(tax_line.account_id.company_ids, company)
        # toutes les clés du socle existent dans chaque société et désignent des taxes de cette société
        for key in EXPECTED_KEYS - {"tax_group_other"}:
            ref_a, ref_b = self.company_a._aite_tax_ref(key), self.company_b._aite_tax_ref(key)
            self.assertTrue(ref_a and ref_b, key)
            self.assertNotEqual(ref_a, ref_b, key)
            self.assertEqual((ref_a.company_id, ref_b.company_id), (self.company_a, self.company_b), key)

    def test_subaccounts_exist_in_each_cm_company(self):
        """Les sous-comptes 552100, 447210 et 449250 existent dans A et dans B, chacun propre à sa société."""
        for code in ("552100", "447210", "449250"):
            acc_a = self.company_a._aite_account(code)
            acc_b = self.company_b._aite_account(code)
            self.assertTrue(acc_a, f"{code} absent de A")
            self.assertTrue(acc_b, f"{code} absent de B")
            self.assertNotEqual(acc_a.id, acc_b.id, f"{code} : A et B doivent avoir des comptes distincts")
            self.assertEqual(acc_a.with_company(self.company_a).code, code)
            self.assertEqual(acc_b.with_company(self.company_b).code, code)
            self.assertEqual(acc_a.company_ids, self.company_a, code)
            self.assertEqual(acc_b.company_ids, self.company_b, code)
            self.assertEqual(acc_a.account_type, acc_b.account_type, f"{code} : même type dans A et B")
        self.assertEqual(self.company_b._aite_account("552100").account_type, "asset_cash")
        self.assertEqual(self.company_b._aite_account("447210").account_type, "liability_current")
        self.assertEqual(self.company_b._aite_account("449250").account_type, "asset_current")
        self.assertFalse(self.company_be._aite_account("447210"), "la société belge n'a pas de 447210")

    def test_ir_model_data_named_by_company(self):
        """Les objets du paramétrage sont enregistrés sous aite_syscohada_base.<id société>_<clé>.

        Par société « cm » : 13 taxes + 1 groupe de taxes = 14 enregistrements (EXPECTED_KEYS).
        Société belge : aucun.
        """
        records = self.env["ir.model.data"].search([("module", "=", "aite_syscohada_base")])

        def keys_of(company):
            prefix = f"{company.id}_"
            return {r.name[len(prefix):]: r for r in records if r.name.startswith(prefix)}

        for company in (self.company_a, self.company_b):
            keys = keys_of(company)
            self.assertEqual(set(keys), EXPECTED_KEYS, f"{company.name} : clés enregistrées")
            self.assertEqual(len(keys), 14, company.name)
            tax = company._aite_tax_ref("tva_prestations_encaissement")
            data = keys["tva_prestations_encaissement"]
            self.assertEqual((data.model, data.res_id, data.noupdate), ("account.tax", tax.id, True), company.name)
            self.assertEqual(self.env.ref(f"aite_syscohada_base.{company.id}_tva_prestations_encaissement"), tax)
            group = keys["tax_group_other"]
            self.assertEqual(group.model, "account.tax.group")
            self.assertEqual(self.env["account.tax.group"].browse(group.res_id).company_id, company)
        self.assertEqual(keys_of(self.company_be), {}, "aucun objet enregistré pour la société belge")

    # ------------------------------------------------------------------ (2) isolation des données
    def test_engine_sees_only_its_company(self):
        """engine.compute(A) ne voit que les écritures de A, compute(B) que celles de B.

        A : TA = −solde(701) = 1 000 000 ; RA = 0 ; XI = 1 000 000 ;
            BI = 4111 débiteur 1 192 500 ; DK = 4431 créditeur 192 500 ; CJ = 1 000 000 ;
            BZ = 1 192 500 = DZ (1 000 000 + 192 500).
        B : TA = 0 ; RA = −solde(601) = −500 000 ; XI = −500 000 ;
            BJ = 4452 débiteur 96 250 ; DJ = 4011 créditeur 596 250 ; CJ = −500 000 ;
            BZ = 96 250 = DZ (−500 000 + 596 250).
        """
        self.post_march_documents()
        self.assertEqual((self.sale_a.company_id, self.purchase_b.company_id), (self.company_a, self.company_b))
        res_a = self.engine.compute(self.company_a, "2026-01-01", "2026-12-31")
        res_b = self.engine.compute(self.company_b, "2026-01-01", "2026-12-31")
        ra, aa, pa = res_a["resultat"], res_a["actif"], res_a["passif"]
        self.assertEqual((ra["TA"], ra["RA"], ra["XI"]), (1000000, 0, 1000000), "A : vente seule, aucun achat")
        self.assertEqual((aa["BI"]["net"], aa["BJ"]["net"]), (1192500, 0), "A : client TTC, aucune TVA déductible")
        self.assertEqual((pa["DK"], pa["DJ"], pa["CJ"]), (192500, 0, 1000000), "A : TVA facturée, aucun fournisseur")
        self.assertEqual((aa["BZ"]["net"], pa["DZ"]), (1192500, 1192500), "A : bilan équilibré")
        rb, ab, pb = res_b["resultat"], res_b["actif"], res_b["passif"]
        self.assertEqual((rb["TA"], rb["RA"], rb["XI"]), (0, -500000, -500000), "B : achat seul, aucune vente")
        self.assertEqual((ab["BI"]["net"], ab["BJ"]["net"]), (0, 96250), "B : aucun client, TVA déductible")
        self.assertEqual((pb["DK"], pb["DJ"], pb["CJ"]), (0, 596250, -500000), "B : fournisseur TTC, aucune TVA facturée")
        self.assertEqual((ab["BZ"]["net"], pb["DZ"]), (96250, 96250), "B : bilan équilibré")
        # les soldes bruts du moteur n'empruntent rien à l'autre société
        self.assertEqual(self.engine._balances(self.company_a).get("601100", 0), 0, "A ne voit pas l'achat de B")
        self.assertEqual(self.engine._balances(self.company_b).get("701100", 0), 0, "B ne voit pas la vente de A")
        self.assertEqual(self.balance(self.company_a, "4431"), -192500)
        self.assertEqual(self.balance(self.company_b, "4452"), 96250)
        self.assertEqual((self.balance(self.company_a, "4452"), self.balance(self.company_b, "4431")), (0, 0))

    def test_vat_declaration_reads_only_its_company_tags(self):
        """La déclaration de A ne lit que les étiquettes de A ; celle de B que les étiquettes de B.

        A : L10 (CM_NORMAL) base 1 000 000, taxe 192 500 ; L15 (CM_GLOBAL) 1 000 000 ; L18 (CM_LOCAL_PURCHASE) 0 ;
            TVA collectée 192 500, déductible 0, à payer 192 500, crédit 0 ;
            acompte L50 = 1 000 000 × 2 % = 20 000, CAC 10 % = 2 000, L54 = 22 000.
        B : L10 base 0 ; L18 taxe 96 250 ; collectée 0, déductible 96 250, à payer 0, crédit 96 250 à reporter ;
            acompte 0 (chiffre d'affaires nul).
        Liquidation A : 4431 débit 192 500, 4441 crédit 192 500, 449250 débit 22 000, 441100 crédit 22 000 (débits 214 500).
        Liquidation B : 4452 crédit 96 250, 4449 débit 96 250 (débits 96 250).
        """
        self.post_march_documents()
        decl_a = self.declare(self.company_a, "2026-03-01", "2026-03-31")
        decl_b = self.declare(self.company_b, "2026-03-01", "2026-03-31")
        self.assertEqual((decl_a.company_id, decl_b.company_id), (self.company_a, self.company_b))
        self.assertEqual((self.line(decl_a, "CM_NORMAL").base, self.line(decl_a, "CM_NORMAL").tax), (1000000, 192500))
        self.assertEqual(self.line(decl_a, "CM_GLOBAL").base, 1000000)
        self.assertEqual(self.line(decl_a, "CM_LOCAL_PURCHASE").tax, 0, "A : l'achat de B ne doit pas apparaître")
        self.assertEqual((decl_a.vat_collected, decl_a.vat_deductible, decl_a.vat_to_pay, decl_a.vat_credit),
                         (192500, 0, 192500, 0))
        self.assertEqual(decl_a.acompte_to_pay, 22000, "acompte : 2 % de 1 000 000 + 10 % de CAC")
        self.assertEqual((self.line(decl_b, "CM_NORMAL").base, self.line(decl_b, "CM_NORMAL").tax), (0, 0),
                         "B : la vente de A ne doit pas apparaître")
        self.assertEqual(self.line(decl_b, "CM_LOCAL_PURCHASE").tax, 96250)
        self.assertEqual((decl_b.vat_collected, decl_b.vat_deductible, decl_b.vat_to_pay, decl_b.vat_credit,
                          decl_b.credit_to_report), (0, 96250, 0, 96250, 96250))
        self.assertEqual(decl_b.acompte_to_pay, 0)
        # liquidation dans chaque société, sans fuite vers l'autre
        move_a = decl_a.action_create_closing_entry()
        move_b = decl_b.action_create_closing_entry()
        self.assertEqual((move_a.company_id, move_b.company_id), (self.company_a, self.company_b))
        self.assertEqual(sum(move_a.line_ids.mapped("debit")), 214500, "A : TVA 192 500 + acompte 22 000")
        self.assertEqual(sum(move_b.line_ids.mapped("debit")), 96250, "B : crédit de TVA porté en 4449")
        self.assertEqual((self.balance(self.company_a, "4431"), self.balance(self.company_a, "4441")), (0, -192500))
        self.assertEqual((self.balance(self.company_a, "449250"), self.balance(self.company_a, "441100")), (22000, -22000))
        self.assertEqual((self.balance(self.company_b, "4452"), self.balance(self.company_b, "4449")), (0, 96250))
        self.assertEqual((self.balance(self.company_b, "4441"), self.balance(self.company_b, "449250")), (0, 0),
                         "B : rien à payer, pas d'acompte")
        self.assertEqual((self.balance(self.company_a, "4449"), self.balance(self.company_a, "4452")), (0, 0),
                         "A : aucun crédit, aucune TVA déductible")

    # Défaut connu : vat_declaration.py, _closing_balances() (ligne 169) filtre les lignes de taxe avec
    # ("account_id.code", "=like", "443%") et "445%". En Odoo 18 le code d'un compte (code_store) dépend de la
    # société de l'environnement, pas de celle de la déclaration : depuis le contexte de A, les comptes de B
    # n'ont aucun code, le domaine ne trouve rien, et action_create_closing_entry() lève
    # « Écart de 96250.0 entre le grand livre et la déclaration ». Correction attendue : évaluer le domaine
    # dans with_company(self.company_id) ou filtrer sur self.company_id._aite_accounts_prefix("443"/"445").
    @unittest.expectedFailure
    def test_closing_entry_of_b_from_company_a_context(self):
        """La liquidation de B donne le même résultat lorsque la société courante de l'utilisateur est A.

        Cas réel : utilisateur multi-sociétés, A sélectionnée, qui liquide la déclaration de B.
        Attendu : écriture dans B, 4452 crédit 96 250 et 4449 débit 96 250, comme depuis le contexte de B.
        """
        self.post_march_documents()
        decl_b = self.declare(self.company_b, "2026-03-01", "2026-03-31")
        decl_b_from_a = self.env["aite.cm.vat.declaration"].with_company(self.company_a).browse(decl_b.id)
        self.assertEqual(decl_b_from_a.env.company, self.company_a, "le contexte courant est bien A")
        try:
            move = decl_b_from_a.action_create_closing_entry()
        except UserError as exc:
            # le refus est le symptôme du défaut : il est converti en échec d'assertion (échec attendu)
            self.fail(f"liquidation de B refusée depuis le contexte de A : {exc}")
        self.assertEqual(move.company_id, self.company_b)
        self.assertEqual(move.state, "posted")
        self.assertEqual(sum(move.line_ids.mapped("debit")), 96250)
        self.assertEqual((self.balance(self.company_b, "4452"), self.balance(self.company_b, "4449")), (0, 96250))

    # ------------------------------------------------------------------ (3) couverture : sous-comptes à 7 chiffres
    def test_coverage_accepts_custom_seven_digit_subaccounts(self):
        """Des sous-comptes à 7 chiffres sont captés par leur préfixe : 55 → BS/DR, 44 → BJ/DK ; aucune anomalie."""
        wave = self.create_account(self.company_a, "5521001", "Monnaie électronique, Wave", "asset_cash")
        irpp = self.create_account(self.company_a, "4471001", "État, IRPP retenu sur salaires, agence 1", "liability_current")
        self.assertEqual((wave.with_company(self.company_a).code, irpp.with_company(self.company_a).code), ("5521001", "4471001"))
        problems = {p["code"]: p["message"] for p in self.checker.coverage(self.company_a)}
        self.assertNotIn("5521001", problems, problems.get("5521001"))
        self.assertNotIn("4471001", problems, problems.get("4471001"))
        self.assertEqual(problems, {}, "le plan de A reste intégralement couvert")
        # rattachement exact : une rubrique au débit, une au crédit
        bilan, resultat = self.checker._mapping_terms()

        def hits(code, side):
            return sorted({rub for rub, t in bilan if t.matches(code) and t.balance_character in ("", side)})

        self.assertEqual((hits("5521001", "D"), hits("5521001", "C")), (["BS"], ["DR"]))
        self.assertEqual((hits("4471001", "D"), hits("4471001", "C")), (["BJ"], ["DK"]))
        self.assertEqual([rub for rub, t in resultat if t.matches("5521001") or t.matches("4471001")], [],
                         "comptes de bilan : jamais captés par le compte de résultat")
        # _aite_account rend toujours le compte à 6 chiffres, pas le sous-compte à 7
        six = self.company_a._aite_account("552100")
        self.assertEqual(six.with_company(self.company_a).code, "552100")
        self.assertNotEqual(six, wave)
        self.assertEqual(self.company_a._aite_account("5521001"), wave, "le code complet à 7 chiffres reste accessible")
        # les deux sous-comptes sont bien pris dans les états : 50 000 virés de la banque vers Wave, seule écriture de A.
        # Solde 5521001 = +50 000 (débiteur → BS) ; banque = −50 000 (créditrice → DR, découvert) ;
        # BS = 50 000 et DR = 50 000 : la trésorerie nette reste nulle, mais chaque solde est rangé selon son sens.
        self.entry("2026-04-01", [(wave, 50000, 0), (self.bank, 0, 50000)], "approvisionnement Wave")
        res = self.compute("2026-01-01", "2026-12-31")
        self.assertEqual(res["actif"]["BS"]["net"], 50000, "Wave débiteur 50 000 en BS")
        self.assertEqual(res["passif"]["DR"], 50000, "banque créditrice 50 000 en DR")
        self.assertEqual(self.checks(self.company_a)["RATTACHEMENT"]["level"], "ok", "sous-compte mouvementé et rattaché")

    def test_coverage_reports_account_outside_chart(self):
        """Un compte hors plan « 905000 » est signalé : capté 0 fois au débit et au crédit."""
        rogue = self.create_account(self.company_a, "905000", "Compte hors plan", "expense")
        problems = {p["code"]: p["message"] for p in self.checker.coverage(self.company_a)}
        self.assertIn("905000", problems)
        self.assertIn("capté 0 fois", problems["905000"])
        self.assertEqual(list(problems), ["905000"], "seul le compte hors plan est en anomalie")
        self.assertNotIn("905000", self.coverage_codes(self.company_b), "B n'est pas affectée par le compte de A")
        # sans écriture : avertissement ; après écriture : erreur bloquante
        before = self.checks(self.company_a)["RATTACHEMENT"]
        self.assertEqual(before["level"], "warning", before["message"])
        self.assertIn("905000", before["message"])
        self.entry("2026-05-01", [(rogue, 1000, 0), (self.bank, 0, 1000)], "écriture hors plan")
        after = self.checks(self.company_a)["RATTACHEMENT"]
        self.assertEqual(after["level"], "error", after["message"])
        self.assertIn("905000", after["message"])
        self.assertEqual(self.checks(self.company_b)["RATTACHEMENT"]["level"], "ok", "B reste intacte")

    # ------------------------------------------------------------------ (4) comptes dépréciés
    def test_coverage_ignores_deprecated_account_without_lines(self):
        """Un compte hors plan déprécié et jamais mouvementé n'est pas signalé ; mouvementé, il le reste."""
        self.create_account(self.company_a, "906000", "Compte hors plan déprécié", "expense", deprecated=True)
        self.assertEqual(self.coverage_codes(self.company_a), [], "compte déprécié sans écriture : ignoré")
        self.assertEqual(self.checks(self.company_a)["RATTACHEMENT"]["level"], "ok")
        # les comptes techniques 999001 et 999002, dépréciés par le paramétrage, ne sont pas signalés non plus
        for code in ("999001", "999002"):
            for company in (self.company_a, self.company_b):
                account = company._aite_account(code)
                self.assertTrue(account and account.deprecated, f"{code} déprécié dans {company.name}")
        self.assertEqual(self.coverage_codes(self.company_b), [])
        # contre-épreuve : un compte mouvementé puis déprécié reste signalé (l'écriture existe au grand livre)
        moved = self.create_account(self.company_a, "907000", "Compte hors plan mouvementé", "expense")
        self.entry("2026-06-01", [(moved, 1000, 0), (self.bank, 0, 1000)], "écriture puis dépréciation")
        moved.deprecated = True
        self.assertEqual(self.coverage_codes(self.company_a), ["907000"])
        self.assertEqual(self.checks(self.company_a)["RATTACHEMENT"]["level"], "error")

    # ------------------------------------------------------------------ (5) contrôles avant toute écriture
    def test_checks_rattachement_never_error_before_entries(self):
        """RATTACHEMENT est « ok » (ou au pire « warning ») sur A et B tant qu'aucun compte nouveau n'est mouvementé."""
        for company in (self.company_a, self.company_b):
            check = self.checks(company)["RATTACHEMENT"]
            self.assertEqual(check["level"], "ok", f"{company.name} : {check['message']}")
        # comptes nouveaux captés par préfixe dans A, comptes nouveaux hors plan dans B : jamais « error »
        self.create_account(self.company_a, "5521002", "Monnaie électronique, Wave agence 2", "asset_cash")
        self.create_account(self.company_a, "4471002", "État, IRPP retenu, agence 2", "liability_current")
        self.create_account(self.company_b, "905000", "Compte hors plan B", "expense")
        check_a = self.checks(self.company_a)["RATTACHEMENT"]
        check_b = self.checks(self.company_b)["RATTACHEMENT"]
        self.assertEqual(check_a["level"], "ok", check_a["message"])
        self.assertEqual(check_b["level"], "warning", check_b["message"])
        self.assertIn("905000", check_b["message"])
        for check in (check_a, check_b):
            self.assertIn(check["level"], ("ok", "warning"), "jamais d'erreur avant la première écriture")
        # les autres contrôles restent verts sur des sociétés sans écriture
        for company in (self.company_a, self.company_b):
            levels = {code: c["level"] for code, c in self.checks(company).items()}
            for code in ("BROUILLONS", "EQUILIBRE", "RESULTAT", "ATTENTE", "CAISSE", "TFT", "ESPECES", "BASCULES"):
                self.assertEqual(levels[code], "ok", f"{company.name} {code}")
