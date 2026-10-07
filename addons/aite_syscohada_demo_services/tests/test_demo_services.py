# -*- coding: utf-8 -*-
"""Recette des données de démonstration de la société « Services Informatiques Démo AITE ».

Montants attendus calculés à la main (règle 2 de CLAUDE.md) à partir du scénario (models/scenario.py) ;
TVA 19,25 % ; acompte 2 % + 10 % de CAC = 2,2 % du chiffre d'affaires déclaré (L15).

CHIFFRE D'AFFAIRES DÉCLARÉ (L15 : services comptés à l'encaissement, matériel à la facture)
    Infogérance encaissée le 25 du mois ; régie du mois m encaissée le 20 de m+1 ; projets encaissés le 15 du mois
    suivant leur facture ; formations et matériel encaissés dans le mois ; support annuel encaissé en octobre 2025.
    2025 : jan. 3 000 000 + 1 200 000 = 4 200 000 ; fév. 3 000 000 + régie de janvier 1 600 000 + 1 200 000
    = 5 800 000 ; mars 3 000 000 + 1 600 000 + projet 4 000 000 + formation 1 200 000 + 1 600 000 = 11 400 000 ;
    avr. et mai 3 000 000 + 1 920 000 + 1 600 000 = 6 520 000 ; juin 3 000 000 + 1 920 000 + 4 000 000 + 1 200 000
    + 2 000 000 = 12 120 000 ; juil. 3 000 000 + 1 600 000 + 1 200 000 = 5 800 000 ; août 3 000 000 + 1 280 000
    + 800 000 = 5 080 000 ; sept. 3 000 000 + 960 000 + 4 000 000 + 2 400 000 = 10 360 000 ; oct. 3 000 000
    + 1 920 000 + 1 200 000 + support 6 000 000 + 1 600 000 = 13 720 000 ; nov. 6 520 000 ; déc. 3 000 000
    + 1 920 000 + 4 000 000 + 2 800 000 = 11 720 000. Total 99 760 000 (= 101 360 000 facturés − régie de décembre
    1 600 000 encaissée en janvier 2026).
    2026 : jan. 3 200 000 + régie de décembre 1 600 000 + 1 600 000 = 6 400 000 ; fév. 3 200 000 + 1 760 000
    + 1 600 000 = 6 560 000 ; mars 3 200 000 + 2 112 000 + 4 000 000 + 1 200 000 + 2 000 000 = 12 512 000 ; avr.
    3 200 000 + 2 112 000 + 2 000 000 = 7 312 000 ; mai 3 200 000 + 2 464 000 + 2 400 000 = 8 064 000 ; juin
    3 200 000 + 2 464 000 + 4 000 000 + 1 200 000 + 2 400 000 = 13 264 000 ; juil. 3 200 000 + 2 112 000
    + 1 600 000 = 6 912 000 ; août 3 200 000 + 1 408 000 + 1 200 000 = 5 808 000 (total janvier à août 66 832 000) ;
    sept. 3 200 000 + 1 056 000 + 4 000 000 + 2 800 000 = 11 056 000.

ACOMPTES (L50 = 2,2 % × L15 ; L52 = L45 acompte retenu par la banque, 2 % de l'infogérance, + L48 retenue de 5 %
sur les projets ; L54 = L50 − L52 − L53 s'il est positif, sinon crédit L55 reporté en L53 le mois suivant)
    Janvier 2025 : L50 92 400, L52 60 000, L54 32 400. Février : L50 127 600, L52 60 000 + 200 000 = 260 000,
    L54 0, L55 132 400. Mars : L50 250 800, L53 132 400, L54 250 800 − 60 000 − 132 400 = 58 400.
    2025 sans crédit en fin d'année : acomptes versés = 2,2 % × 99 760 000 − 12 × 60 000 − 4 × 200 000
    = 2 194 720 − 720 000 − 800 000 = 674 720 (449250) ; acomptes et précomptes imputables 2 194 720.
    Août 2026 : L50 127 776, L52 64 000 + 200 000, L55 136 224 ; septembre : L53 136 224.
    Janvier à août 2026 : 2,2 % × 66 832 000 − 8 × 64 000 − 3 × 200 000 + crédit d'août 136 224 = 494 528 (449250).

COMPTE DE RÉSULTAT 2025
    TA matériel 19 600 000 ; TC infogérance 12 × 3 000 000 + régie 126 jours × 160 000 + projets 4 × 4 000 000
    + formations 3 × 1 200 000 + support 6 000 000 − produits constatés d'avance 4 500 000
    = 36 000 000 + 20 160 000 + 16 000 000 + 3 600 000 + 1 500 000 = 77 260 000 ; XB 96 860 000 ;
    RA −75 % × 19 600 000 = −14 700 000 ; RB +1 800 000 ; XA 6 700 000 ; RE −12 × 200 000 = −2 400 000 ;
    RH −(loyer 12 × 600 000 + nuage 12 × 500 000 + sous-traitance 4 × 1 200 000 + internet 12 × 200 000
    + frais bancaires 12 × 24 000) = −20 688 000 ; RI −(patente 600 000 + 12 × 75 000) = −1 500 000 ;
    XC 59 372 000 ; RK −12 × (3 000 000 + 388 500) = −40 662 000 ; XD 18 710 000 ;
    RL −(12 × 300 000 + 10 × 200 000) = −5 600 000 ; XE = XG 13 110 000.
    Impôt : maximum (27,5 % × 13 110 000 = 3 605 250 ; acomptes 2 194 720) = 3 605 250 ; XI 9 504 750.
    Imputation du 15/03/2026 : 720 000 + 800 000 + 674 720 imputés, solde 3 605 250 − 2 194 720 = 1 410 530 payé
    par la banque.

COMPTE DE RÉSULTAT 2026, JANVIER À SEPTEMBRE
    TA 17 600 000 ; TC 9 × 3 200 000 + 102 jours × 176 000 + 3 × 4 000 000 + 2 × 1 200 000 + reprise des produits
    constatés d'avance 4 500 000 = 28 800 000 + 17 952 000 + 12 000 000 + 2 400 000 + 4 500 000 = 65 652 000 ;
    XB 83 252 000 ; RA −75 % × 17 600 000 = −13 200 000 ; RB −1 800 000 + 2 100 000 = +300 000 ;
    RE −9 × 220 000 = −1 980 000 ; RH −(5 400 000 + 9 × 600 000 + 3 × 1 200 000 + 9 × 200 000 + 9 × 24 000)
    = −16 416 000 ; RI −(650 000 + 9 × 82 500) = −1 392 500 ; XC 50 563 500 ; RK −9 × (3 300 000 + 427 350)
    = −33 546 150 ; XD 17 017 350 ; RL −(9 × 300 000 + 9 × 200 000 + 6 × 150 000) = −5 400 000 ;
    XG = XI 11 617 350.

AFFECTATION ET DIVIDENDES
    Réserve légale 9 504 750 // 10 = 950 475 ; dividendes 9 504 750 // 2 = 4 752 375 arrondi à 10 000 près
    = 4 750 000 ; report à nouveau 9 504 750 − 950 475 − 4 750 000 = 3 804 275. IRCM 15 % × 4 750 000 = 712 500
    + CAC 71 250 = 783 750 (L62 de juillet 2026) ; net versé 4 750 000 − 783 750 = 3 966 250.

BILAN AU 30/09/2026
    AF progiciel brut 7 200 000, amortissements 19 × 200 000 = 3 800 000 ; AM brut 10 800 000 + 5 400 000
    = 16 200 000, amortissements 21 × 300 000 + 6 × 150 000 = 7 200 000 ; AZ 12 400 000 ; BB 2 100 000.
    BI 411100 : régie de septembre 14 × 176 000 = 2 464 000 × 1,1925 = 2 938 320.
    BJ : TVA déductible de septembre non liquidée 446 600 (4452) + 158 620 (4454 : internet 38 500, frais 4 620,
    nuage 115 500) + acomptes 2026 576 000 (449220) + 600 000 (449240) + 494 528 (449250) = 2 275 748.
    BT : banque 521001 = 29 261 832 (détail ci-dessous). BZ = 12 400 000 + 2 100 000 + 2 938 320 + 2 275 748
    + 29 261 832 = 48 975 900.
    CA 25 000 000 ; CF 950 475 ; CH 3 804 275 ; CJ 11 617 350 ; DJ 401100 : matériel de septembre 2 100 000
    × 1,1925 = 2 504 250 + sous-traitance de septembre 1 140 000 = 3 644 250 ; DK : CNPS 565 950 + impôts sur
    salaires 435 500 + TSR 90 000 + précompte sur loyer 90 000 + retenue sur honoraires 60 000 + TVA autoliquidée
    115 500 + TVA collectée de septembre 539 000 (4431) + 1 589 280 (4432) + TVA en attente 474 320 (443800,
    régie de septembre) = 3 959 550 ; DZ = 41 372 100 + 3 644 250 + 3 959 550 = 48 975 900 = BZ.
    Banque, entrées : capital 25 000 000 ; infogérance 12 × 3 517 500 + 9 × 3 752 000 = 75 978 000 ; régie
    20 160 000 × 1,1925 + 15 488 000 × 1,1925 = 42 510 240 ; projets 7 × (4 770 000 − 200 000) = 31 990 000 ;
    formations 5 × 1 431 000 = 7 155 000 ; support 7 155 000 ; matériel 37 200 000 × 1,1925 = 44 361 000 ;
    total 234 149 240. Sorties : loyers 21 × 510 000 = 10 710 000 ; nuage 12 × 425 000 + 9 × 510 000
    = 9 690 000 ; matériel 17 529 750 + 13 236 750 = 30 766 500 ; électricité 12 × 238 500 + 9 × 262 350
    = 5 223 150 ; internet 21 × 238 500 = 5 008 500 ; frais 21 × 28 620 = 601 020 ; sous-traitance 6 × 1 140 000
    = 6 840 000 ; immobilisations 12 879 000 + 8 586 000 + 6 439 500 = 27 904 500 ; patentes 1 250 000 ; salaires
    nets 12 × 2 557 000 + 9 × 2 808 400 = 55 959 600 ; CNPS 12 × 514 500 + 8 × 565 950 = 10 701 600 ; solde
    d'impôt 1 410 530 ; dividendes nets 3 966 250 ; déclarations de janvier 2025 à août 2026 34 855 758 ;
    total 204 887 408. Solde 234 149 240 − 204 887 408 = 29 261 832.
    Déclarations payées : TSR 12 × 75 000 + 8 × 90 000 = 1 620 000 ; TVA autoliquidée 12 × 96 250 + 8 × 115 500
    = 2 079 000 ; précomptes sur loyers 20 × 90 000 + retenues sur honoraires 6 × 60 000 = 2 160 000 ; acomptes
    674 720 + 494 528 = 1 169 248 ; IRCM 783 750 ; impôts sur salaires 12 × 392 000 + 8 × 435 500 = 8 188 000 ;
    TVA à payer = 19,25 % × (99 760 000 + 66 832 000) − 19,25 % × (biens et immobilisations 53 360 000
    + services 4 480 000 + nuage 10 800 000) = 32 068 960 − 13 213 200 = 18 855 760 ; total 34 855 758.

TABLEAU DES FLUX : 2025 FF progiciel −7 200 000, FG ordinateurs −10 800 000, FK 25 000 000 ; 2026 FG serveurs
    −5 400 000, FN dividendes −4 750 000, FK 0 ; ZH = BT − DT (aucun découvert).
    Le progiciel (2131) est amorti par 6812 et son fournisseur suit 4811 (immobilisations incorporelles), les
    ordinateurs et serveurs (2442) par 6813 avec un fournisseur en 4812 : 2025 6812 −10 × 200 000 = 2 000 000,
    6813 12 × 300 000 = 3 600 000.

DÉCLARATION DE JANVIER 2025
    L10 4 200 000, TVA 808 500 ; L18 matériel 900 000 → 173 250, électricité 38 500, ordinateurs 10 800 000
    → 2 079 000 : 2 290 750 ; L19 38 500 + 4 620 = 43 120 ; L21 nuage 96 250 ; L22 2 430 120 ;
    L35 = 2 430 120 − 808 500 = 1 621 620, repris en L17 de février. L0 TSR 75 000 ; L38 96 250 ; L42 90 000 ;
    L44 90 000 ; L45 60 000 ; L50 92 400 ; L54 32 400 ; L73 240 000 + 24 000 + 30 000 + 45 000 + 30 000 + 13 000
    + 10 000 = 392 000. Total 75 000 + 96 250 + 90 000 + 32 400 + 392 000 = 685 650.

DÉCLARATION DE SEPTEMBRE 2026 (brouillon)
    L10 11 056 000, TVA 2 128 280 ; L18 2 100 000 → 404 250 + électricité 42 350 = 446 600 ; L19 43 120 ;
    L21 115 500 ; L32 = 2 128 280 − 446 600 − 43 120 − 115 500 = 1 523 060. L0 90 000 ; L38 115 500 ; L42 90 000 ;
    L43 60 000 ; L44 150 000 ; L45 64 000 ; L50 243 232 ; L53 136 224 ; L54 243 232 − 64 000 − 136 224 = 43 008 ;
    L73 270 000 + 27 000 + 33 000 + 49 500 + 33 000 + 13 000 + 10 000 = 435 500.
    Total 90 000 + 1 523 060 + 115 500 + 150 000 + 43 008 + 435 500 = 2 357 068, à payer le 15/10/2026.
"""
import calendar
from datetime import date
from types import SimpleNamespace

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

from odoo.addons.aite_syscohada_demo_services.models.generator import ServicesBuilder


@tagged("post_install", "-at_install", "aite_syscohada_demo")
class TestDemoServices(TransactionCase):
    """Société de services informatiques : états, déclarations et soldes comparés aux calculs à la main."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.ref("aite_syscohada_demo_services.demo_company")
        cls.env = cls.env(context=dict(cls.env.context, allowed_company_ids=[company.id], lang="en_US"))
        cls.company = cls.env["res.company"].browse(company.id)
        engine = cls.env["aite.syscohada.engine"]
        cls.y2025 = engine.compute(cls.company, date(2025, 1, 1), date(2025, 12, 31))
        cls.y2026 = engine.compute(cls.company, date(2026, 1, 1), date(2026, 9, 30))
        cls.declarations = cls.env["aite.cm.vat.declaration"].search(
            [("company_id", "=", cls.company.id)], order="date_from")

    # ------------------------------------------------------------------ outils
    def balance(self, code, date_to=date(2026, 9, 30)):
        account = self.company._aite_account(code)
        self.assertTrue(account, f"compte {code} absent")
        return self.env["account.move.line"]._read_group(
            [("account_id", "=", account.id), ("parent_state", "=", "posted"), ("date", "<=", date_to)],
            [], ["balance:sum"])[0][0] or 0.0

    def declaration(self, year, month):
        found = self.declarations.filtered(lambda d: d.date_from == date(year, month, 1))
        self.assertEqual(len(found), 1, f"déclaration {month:02d}/{year}")
        return found

    def vat(self, declaration, code):
        line = declaration.line_ids.filtered(lambda l: l.code == code)
        return line.base, line.tax

    def form(self, declaration, *codes):
        lines = {l.code: l.total for l in declaration.itvair_line_ids}
        return {code: lines[code] for code in codes}

    def move(self, ref):
        found = self.env["account.move"].search([("company_id", "=", self.company.id), ("ref", "=", ref)])
        self.assertEqual(len(found), 1, ref)
        return found

    def assertAmounts(self, actual, expected):
        self.assertEqual({key: actual[key] for key in expected}, expected)

    # ------------------------------------------------------------------ société
    def test_company(self):
        company = self.company
        self.assertEqual((company.currency_id, company.chart_template), (self.env.ref("base.XAF"), "cm"))
        self.assertTrue(company.aite_syscohada_setup_date)
        self.assertIn(company, self.env.ref("base.user_admin").company_ids)
        codes = set(self.env["account.journal"].search([("company_id", "=", company.id)]).mapped("code"))
        self.assertIn("PAIE", codes)
        self.assertFalse({"OM", "MOMO"} & codes, "pas de monnaie électronique pour cette société")
        self.assertEqual(self.env["res.partner"].search_count([("company_id", "=", company.id)]), 15)
        payable = {name: self.env["res.partner"].search([("company_id", "=", company.id), ("name", "=", name)])
                   .property_account_payable_id.code for name in ("Éditeur Logiciel Démo SARL",
                                                                  "Intégrateur Matériel Démo SA")}
        self.assertEqual(payable, {"Éditeur Logiciel Démo SARL": "481100", "Intégrateur Matériel Démo SA": "481200"},
                         "fournisseurs d'immobilisations incorporelles en 4811, corporelles en 4812")

    def test_scenario_checks(self):
        """Paramètres que le moteur ne sait pas traiter : refusés à l'exécution, jamais ignorés en silence."""
        cases = [
            {"EMPRUNT": {"date": date(2026, 1, 10)}, "INVENTAIRES": {}},             # échéances le 15
            {"INVENTAIRES": {date(2026, 6, 15): 1_000_000}},                         # pas une fin de mois
            {"INVENTAIRES": {date(2026, 6, 30): 1_000_000, date(2026, 9, 30): 2_000_000}},  # deux dans l'exercice
        ]
        for params in cases:
            builder = type("Builder", (ServicesBuilder,), {"scenario": SimpleNamespace(**params)})(self.env)
            with self.assertRaises(UserError):
                builder._check_scenario()
        ServicesBuilder(self.env)._check_scenario()  # le scénario livré est accepté

    def test_regeneration_is_idempotent(self):
        moves = self.env["account.move"].search_count([("company_id", "=", self.company.id)])
        self.assertEqual(self.env["aite.syscohada.demo.services"]._aite_generate(), self.company)
        self.assertEqual(self.env["account.move"].search_count([("company_id", "=", self.company.id)]), moves)

    # ------------------------------------------------------------------ états
    def test_income_statement_2025(self):
        self.assertAmounts(self.y2025["resultat"], {
            "TA": 19600000, "TC": 77260000, "XB": 96860000, "RA": -14700000, "RB": 1800000, "XA": 6700000,
            "RE": -2400000, "RH": -20688000, "RI": -1500000, "XC": 59372000, "RK": -40662000, "XD": 18710000,
            "RL": -5600000, "RM": 0, "XG": 13110000, "RS": -3605250, "XI": 9504750})
        self.assertEqual((self.balance("6812", date(2025, 12, 31)), self.balance("6813", date(2025, 12, 31))),
                         (2000000, 3600000), "dotations : incorporelles en 6812, corporelles en 6813")

    def test_income_tax_2025(self):
        """Impôt supérieur aux acomptes : acomptes imputés le 15/03/2026, solde payé par la banque."""
        end = date(2025, 12, 31)
        self.assertEqual({code: self.balance(code, end) for code in ("449220", "449240", "449250", "441")},
                         {"449220": 720000, "449240": 800000, "449250": 674720, "441": -3605250})
        imputation = self.move("Impôt sur le résultat 2025 : imputation des acomptes et précomptes")
        self.assertEqual((imputation.date, imputation.journal_id.type), (date(2026, 3, 15), "bank"))
        bank = self.company._aite_account("521001")
        self.assertEqual(sum(imputation.line_ids.filtered(lambda l: l.account_id == bank).mapped("credit")), 1410530)
        self.assertEqual(self.balance("441", date(2026, 3, 15)), 0)

    def test_income_statement_2026(self):
        self.assertAmounts(self.y2026["resultat"], {
            "TA": 17600000, "TC": 65652000, "XB": 83252000, "RA": -13200000, "RB": 300000, "RE": -1980000,
            "RH": -16416000, "RI": -1392500, "XC": 50563500, "RK": -33546150, "XD": 17017350, "RL": -5400000,
            "XG": 11617350, "RS": 0, "XI": 11617350})

    def test_prepaid_revenue(self):
        """Support annuel facturé en octobre 2025 : 9 mois sur 12 en produits constatés d'avance, repris en 2026."""
        self.assertEqual(self.balance("477", date(2025, 12, 31)), -4500000)
        self.assertEqual(self.balance("477"), 0)
        self.assertEqual(self.y2025["passif"]["DM"], 4500000, "produits constatés d'avance en autres dettes")

    def test_balance_sheet_2026(self):
        passif, actif = self.y2026["passif"], self.y2026["actif"]
        self.assertAmounts(passif, {"CA": 25000000, "CF": 950475, "CH": 3804275, "CJ": 11617350, "DA": 0,
                                    "DJ": 3644250, "DK": 3959550})
        self.assertEqual((actif["AF"]["brut"], actif["AF"]["amort"]), (7200000, 3800000))
        self.assertEqual((actif["AM"]["brut"], actif["AM"]["amort"]), (16200000, 7200000))
        self.assertEqual({key: actif[key]["net"] for key in ("BB", "BI", "BJ", "BT")},
                         {"BB": 2100000, "BI": 2938320, "BJ": 2275748, "BT": 29261832})
        self.assertEqual((actif["BZ"]["net"], passif["DZ"]), (48975900, 48975900))
        self.assertEqual({code: self.balance(code) for code in (
            "521001", "411100", "443800", "401100", "481100", "481200", "3111", "465", "441", "449220", "449240",
            "449250")}, {
            "521001": 29261832, "411100": 2938320, "443800": -474320, "401100": -3644250, "481100": 0, "481200": 0,
            "3111": 2100000, "465": 0, "441": 0, "449220": 576000, "449240": 600000, "449250": 494528})

    def test_cash_flow(self):
        self.assertAmounts(self.y2025["flux"], {"FF": -7200000, "FG": -10800000, "FK": 25000000, "FN": 0})
        self.assertAmounts(self.y2026["flux"], {"FF": 0, "FG": -5400000, "FK": 0, "FN": -4750000, "FO": 0,
                                                "ZH": 29261832})
        self.assertEqual(self.y2025["flux"]["ZH"], self.y2025["actif"]["BT"]["net"] - self.y2025["passif"]["DT"])

    def test_checks(self):
        checker = self.env["aite.syscohada.check"]
        for date_from, date_to in ((date(2025, 1, 1), date(2025, 12, 31)), (date(2026, 1, 1), date(2026, 9, 30))):
            problems = [(c["code"], c["level"], c["message"]) for c in checker.run(self.company, date_from, date_to)
                        if c["level"] in ("error", "warning")]
            self.assertEqual(problems, [], f"contrôles du {date_from} au {date_to}")

    def test_bank_never_overdrawn(self):
        for year, month in [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 10)]:
            end = date(year, month, calendar.monthrange(year, month)[1])
            self.assertGreaterEqual(self.balance("521001", end), 0, f"banque au {end}")

    # ------------------------------------------------------------------ déclarations
    def test_declarations_sequence(self):
        self.assertEqual(len(self.declarations), 21)
        done, draft = self.declarations[:-1], self.declarations[-1]
        self.assertEqual(set(done.mapped("state")), {"done"})
        self.assertTrue(all(d.move_id.state == "posted" for d in done))
        self.assertEqual((draft.date_from, draft.state, bool(draft.move_id)), (date(2026, 9, 1), "draft", False))
        self.assertEqual(self.declaration(2025, 2).credit_previous, 1621620, "L17 de février = L35 de janvier")

    def test_january_2025(self):
        decl = self.declaration(2025, 1)
        self.assertEqual(self.vat(decl, "CM_NORMAL"), (4200000, 808500))
        self.assertEqual({code: self.vat(decl, code)[1] for code in (
            "CM_LOCAL_PURCHASE", "CM_LOCAL_SERVICE", "CM_FOREIGN_SERVICE", "CM_DEDUCTIBLE_VAT")},
            {"CM_LOCAL_PURCHASE": 2290750, "CM_LOCAL_SERVICE": 43120, "CM_FOREIGN_SERVICE": 96250,
             "CM_DEDUCTIBLE_VAT": 2430120})
        self.assertEqual((decl.vat_to_pay, decl.credit_to_report), (0, 1621620))
        self.assertEqual(self.form(decl, "L0", "L38", "L42", "L44", "L45", "L50", "L54", "L73"),
                         {"L0": 75000, "L38": 96250, "L42": 90000, "L44": 90000, "L45": 60000, "L50": 92400,
                          "L54": 32400, "L73": 392000})
        self.assertEqual((decl.total_to_pay, decl.date_due), (685650, date(2025, 2, 15)))

    def test_acompte_credit_carry(self):
        """Retenue de 5 % sur un projet : crédit d'acompte en février, imputé en mars (L55 vers L53)."""
        february, march = self.declaration(2025, 2), self.declaration(2025, 3)
        self.assertEqual(self.form(february, "L48", "L50", "L52", "L54", "L55"),
                         {"L48": 200000, "L50": 127600, "L52": 260000, "L54": 0, "L55": 132400})
        self.assertEqual(self.form(march, "L50", "L53", "L54", "L55"),
                         {"L50": 250800, "L53": 132400, "L54": 58400, "L55": 0})
        self.assertEqual(self.form(self.declaration(2026, 8), "L55")["L55"], 136224)

    def test_july_2026_ircm(self):
        self.assertEqual(self.form(self.declaration(2026, 7), "L62")["L62"], 783750)
        dividends = self.move("Dividendes versés, IRCM retenu à la source")
        self.assertEqual((dividends.date, sum(dividends.line_ids.mapped("debit"))), (date(2026, 7, 20), 4750000))
        self.assertEqual(sum(dividends.line_ids.filtered(lambda l: l.account_id.code == "447110").mapped("credit")),
                         783750)

    def test_september_2026_draft(self):
        decl = self.declaration(2026, 9)
        self.assertEqual(self.vat(decl, "CM_NORMAL"), (11056000, 2128280))
        self.assertEqual(decl.vat_to_pay, 1523060)
        self.assertEqual(self.form(decl, "L0", "L38", "L42", "L43", "L44", "L45", "L50", "L53", "L54", "L73"),
                         {"L0": 90000, "L38": 115500, "L42": 90000, "L43": 60000, "L44": 150000, "L45": 64000,
                          "L50": 243232, "L53": 136224, "L54": 43008, "L73": 435500})
        self.assertEqual((decl.total_to_pay, decl.date_due), (2357068, date(2026, 10, 15)))

    def test_payments_match_declarations(self):
        """Chaque paiement du 15 (soldes du grand livre) égale le total à payer de la déclaration validée."""
        bank = self.company._aite_account("521001")
        for decl in self.declarations.filtered(lambda d: d.state == "done"):
            payment = self.move(f"Paiement I/TVA-IR {decl.date_to:%m/%Y}")
            self.assertEqual(payment.date, decl.date_due, decl.name)
            self.assertEqual(sum(payment.line_ids.filtered(lambda l: l.account_id == bank).mapped("credit")),
                             decl.total_to_pay, decl.name)

    # ------------------------------------------------------------------ tiers
    def test_withholdings_suffered(self):
        """Infogérance : la banque retient 2 % du hors taxes ; projet : l'assureur retient 5 %."""
        maintenance, project = self.move("INF-2025-01"), self.move("PRJ-2025-02")
        self.assertEqual((maintenance.amount_total, maintenance.payment_state), (3517500, "paid"),
                         "3 000 000 + 577 500 de TVA − 60 000 retenus")
        self.assertEqual((project.amount_total, project.payment_state), (4570000, "paid"),
                         "4 000 000 + 770 000 de TVA − 200 000 retenus")

    def test_open_items_at_end(self):
        open_moves = self.env["account.move"].search([
            ("company_id", "=", self.company.id), ("move_type", "in", ("out_invoice", "in_invoice")),
            ("payment_state", "!=", "paid")])
        self.assertEqual({m.ref: m.amount_residual for m in open_moves},
                         {"REG-2026-09": 2938320, "MAT-2026-09": 2504250, "SST-2026-09": 1140000})
