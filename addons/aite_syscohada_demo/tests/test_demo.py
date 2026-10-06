# -*- coding: utf-8 -*-
"""Recette des données de démonstration (société « Bar-Hôtel Démo AITE », générée à l'installation du module).

Montants attendus calculés à la main (règle 2 de CLAUDE.md) à partir du scénario (models/demo_scenario.py) ;
TVA 19,25 % ; coefficients mensuels en dixièmes 9, 9, 10, 10, 10, 11, 12, 12, 10, 10, 11, 16.

COMPTE DE RÉSULTAT 2025 (douze mois, somme des coefficients 13,0)
    TA 3 200 000 × 13,0 = 41 600 000 ; TC nuitées 1 800 000 × 13,0 + séminaires 4 × 1 200 000 + 2 000 000
    = 30 200 000 ; XB 71 800 000 ; RA −(48 % × 41 600 000 − ristourne 300 000) = −19 668 000 ; RB stock final
    +2 400 000 ; RE électricité −12 × 400 000 = −4 800 000 ; RH −(12 × 120 000 + 12 × 600 000 + 4 × 400 000
    + 4 × 300 000 + 12 × 16 000) = −11 632 000 ; RI −(patente 350 000 + 12 × 60 000) = −1 070 000 ; XC (valeur
    ajoutée) = 71 800 000 − 19 668 000 + 2 400 000 − 4 800 000 − 11 632 000 − 1 070 000 = 37 030 000 ;
    RK −12 × (2 400 000 + 310 800) = −32 529 600 ; RL −12 × 140 000 = −1 680 000 ; RM 0 ; XG 2 820 400.
    Impôt : maximum (33 % × 2 820 400 = 930 732 ; acomptes et précomptes de l'année = 2,2 % × L15 cumulé
    71 224 000 = 1 566 928) ; RS −1 566 928 ; XI 1 253 472.
    L15 cumulé 2025 = ventes 41 600 000 + nuitées 23 400 000 − solde de décembre encaissé en janvier 2026
    (1 800 000 × 1,6 × 20 % = 576 000) + séminaires 4 800 000 + 2 000 000 = 71 224 000.
    Acomptes au 31/12/2025 : 449210 précomptes subis 2 % × 36 % × 41 600 000 = 299 520 ; 449220 acompte retenu
    par la société pétrolière 2 % × 2 000 000 = 40 000 ; 449250 acomptes versés (L54) = 1 566 928 − 299 520
    − 40 000 = 1 227 408.

COMPTE DE RÉSULTAT 2026, JANVIER À SEPTEMBRE (somme des coefficients 9,3)
    TA 3 600 000 × 9,3 = 33 480 000 ; TC 2 200 000 × 9,3 + 3 × 1 200 000 + 2 000 000 = 26 060 000 ;
    XB 59 540 000 ; RA −48 % × 33 480 000 = −16 070 400 ; RB −2 400 000 (reprise) + 2 800 000 (stock au 30/09)
    = +400 000 ; RE −9 × 440 000 = −3 960 000 ; RH −(9 × 120 000 + 9 × 600 000 + 3 × 400 000 + 3 × 300 000
    + 9 × 16 000) = −8 724 000 ; RI −(380 000 + 9 × 62 500) = −942 500 ; XC 30 243 100 ;
    RK −9 × (2 500 000 + 323 750) = −25 413 750 ; RL −(9 × 140 000 + 7 × 100 000) = −1 960 000 ;
    RM −(120 000 + 115 000 + 110 000 + 105 000 + 100 000 + 95 000 + 90 000 + 85 000) = −820 000 ;
    XG = XI = 2 049 350 (pas d'impôt constaté en cours d'exercice).

BILAN AU 30/09/2026
    Capitaux : CA 30 000 000 ; CF réserve légale 1 253 472 // 10 = 125 347 ; dividendes 620 000 ; CH report à
    nouveau 1 253 472 − 125 347 − 620 000 = 508 125 ; CJ 2 049 350 ; DA emprunt 12 000 000 − 8 × 500 000 = 8 000 000.
    Immobilisations : AL 2351 brut 9 600 000, amortissements 21 × 80 000 = 1 680 000 ; AM brut 3 600 000 + 6 000 000
    = 9 600 000, amortissements 21 × 60 000 + 7 × 100 000 = 1 960 000 ; BB stock 2 800 000.
    Trésorerie : caisse 571 = 60 % des ventes TTC de septembre (3 600 000 × 1,1925 = 4 293 000) = 2 575 800 ;
    Orange Money 25 % = 1 073 250 ; MTN 15 % = 643 950 (versés en banque début octobre) ; 585 soldé.
    Banque 521, entrées : capital 30 000 000 + emprunt 12 000 000 + nuitées encaissées (43 860 000 × 1,1925
    − solde de septembre 524 700 = 51 778 350) + séminaires de l'agence (6 × 1 431 000 = 8 586 000) + séminaires
    pétroliers (2 × (2 385 000 − 40 000) = 4 690 000) + espèces et monnaie électronique versées (ventes TTC
    (41 600 000 + 33 480 000) × 1,1925 − septembre 4 293 000 = 85 239 900) = 192 294 250.
    Sorties : loyers 21 × 510 000 = 10 710 000 ; brasseries 2025 14 976 000 × 1,2125 = 18 158 400, janvier à
    août 2026 10 756 800 × 1,2125 = 13 042 620, moins la ristourne imputée 300 000 → 30 901 020 ; vins 9 009 600
    × 1,1925 = 10 743 948 ; électricité 12 × 477 000 + 9 × 524 700 = 10 446 300 ; téléphone 21 × 143 100
    = 3 005 100 ; logiciel 7 × 255 000 = 1 785 000 ; honoraires 6 × 457 000 = 2 742 000 ; frais bancaires
    21 × 19 080 = 400 680 ; immobilisations 15 741 000 + 7 155 000 = 22 896 000 ; patentes 730 000 ; salaires
    nets 12 × 2 126 700 + 9 × 2 215 250 = 45 457 650 ; CNPS 12 × 411 600 + 8 × 428 750 = 8 369 200 ; emprunt
    4 000 000 + 820 000 = 4 820 000 ; dividendes nets 517 700 ; déclarations de janvier 2025 à août 2026
    20 140 366 (détail ci-dessous) ; total 173 664 964. Solde 192 294 250 − 173 664 964 = 18 629 286.
    Déclarations payées (janvier 2025 à août 2026) : TSR 7 × 45 000 = 315 000 ; TVA autoliquidée 7 × 57 750
    = 404 250 ; précomptes sur loyers 20 × 90 000 + retenues sur honoraires 6 × 20 000 = 1 920 000 ; acomptes
    1 227 408 + 901 800 = 2 129 208 ; IRCM 102 300 ; impôts sur salaires 12 × 232 500 + 8 × 242 250 = 4 728 000 ;
    TVA à payer = collectée − déductible, le crédit étant entièrement consommé fin août : 19,25 % × (71 224 000
    + 52 588 000) − 19,25 % × (biens et immobilisations 61 830 400 + services 5 120 000 + logiciel 2 100 000)
    = 23 833 810 − 13 292 202 = 10 541 608 ; total 20 140 366.
    L15 cumulé de janvier à août 2026 = ventes 29 880 000 + nuitées (2 200 000 × 8,3 − solde d'août 528 000
    + solde de décembre 2025 576 000 = 18 308 000) + séminaires 2 400 000 + 2 000 000 = 52 588 000 ;
    acomptes versés 2,2 % × 52 588 000 − précomptes 2 % × 36 % × 29 880 000 − 40 000 = 1 156 936 − 215 136
    − 40 000 = 901 800 (449250 au 30/09/2026, celui de septembre n'étant pas encore liquidé).
    BT = 18 629 286 + 2 575 800 + 1 073 250 + 643 950 = 22 922 286.
    Créances : 411100 = solde des nuitées de septembre 2 623 500 × 20 % = 524 700 + séminaire de septembre
    1 431 000 = 1 955 700 ; TVA déductible de septembre non liquidée 417 340 + 103 180 = 520 520 ; acomptes
    901 800 + 241 056 + 40 000 = 1 182 856 ; BZ = AL 7 920 000 + AM 7 640 000 + BB 2 800 000 + 1 955 700
    + 520 520 + 1 182 856 + BT 22 922 286 = 44 941 362.
    Dettes : 401100 = brasseries de septembre 1 296 000 × 1,2125 = 1 571 400 + honoraires de septembre 400 000
    + 77 000 − 20 000 = 457 000, soit 2 028 400 ; sociales et fiscales de septembre : CNPS 428 750, impôts sur
    salaires 242 250, précompte sur loyer 90 000, retenue sur honoraires 20 000, TVA collectée non liquidée
    3 600 000 × 19,25 % = 693 000 et (1 760 000 + 528 000) × 19,25 % = 440 440, TVA en attente 443800 315 700
    (solde des nuitées 84 700 + séminaire 231 000) ; DZ = 30 000 000 + 125 347 + 508 125 + 2 049 350 + 8 000 000
    + 2 028 400 + 428 750 + 242 250 + 90 000 + 20 000 + 693 000 + 440 440 + 315 700 = 44 941 362 = BZ.

TABLEAU DES FLUX
    2026 : FO emprunt 12 000 000 ; FQ remboursements −4 000 000 ; FN dividendes −620 000 ; FG chambre froide
    −6 000 000 ; FK 0. 2025 : FK capital 30 000 000 ; FG aménagements et mobilier −13 200 000 ; FO = FQ = FN = 0.
    ZH = BT − DT (pas de découvert).

DÉCLARATION DE JANVIER 2025
    L10 ventes 3 200 000 × 0,9 = 2 880 000 + nuitées encaissées 80 % × 1 620 000 = 1 296 000 → base 4 176 000,
    TVA 803 880 ; L15 = 4 176 000.
    L18 brasseries 1 036 800 → 199 584, vins 345 600 → 66 528, électricité 400 000 → 77 000, aménagements et
    mobilier 13 200 000 → 2 541 000 : 2 884 112 ; L19 téléphone 23 100 + frais bancaires 3 080 = 26 180 ;
    L21 logiciel 300 000 → 57 750 ; L22 = 2 968 042 ; L33 = L35 = 2 968 042 − 803 880 = 2 164 162 ; L32 = 0.
    L0 TSR 15 % × 300 000 = 45 000 ; L38 TVA autoliquidée 57 750 ; L42 15 % × 600 000 = 90 000 ; L44 90 000 ;
    L50 2 % × 4 176 000 = 83 520 + CAC 8 352 = 91 872 ; L46 2 % × 1 036 800 = 20 736 ; L54 71 136 ;
    L73 120 000 + 12 000 + 24 000 + 36 000 + 24 000 + 9 000 + 7 500 = 232 500.
    Total 45 000 + 57 750 + 90 000 + 71 136 + 232 500 = 496 386, payé le 15/02/2025. Février reprend le crédit
    de 2 164 162 en L17.

DÉCLARATION D'AOÛT 2026
    L10 ventes 3 600 000 × 1,2 = 4 320 000 + nuitées 80 % × 2 640 000 = 2 112 000 + solde de juillet 528 000
    = 6 960 000 → 1 339 800 ; L18 1 555 200 → 299 376, 518 400 → 99 792, 440 000 → 84 700 : 483 868 ;
    L19 26 180 ; L32 = 1 339 800 − 483 868 − 26 180 = 829 752.

DÉCLARATION DE JUILLET 2026 : L57 dividendes 620 000 × 15 % = 93 000 + CAC 9 300 → L62 = 102 300.

DÉCLARATION DE SEPTEMBRE 2026 (brouillon, ni liquidée ni validée)
    L10 3 600 000 + 1 760 000 + solde d'août 528 000 = 5 888 000 → 1 133 440 ; L18 1 296 000 → 249 480, 432 000
    → 83 160, 440 000 → 84 700 : 417 340 ; L19 23 100 + 3 080 + honoraires 77 000 = 103 180 ; L32 = 612 920 ;
    L42 90 000 ; L43 20 000 ; L44 110 000 ; L50 2,2 % × 5 888 000 = 129 536 ; L46 25 920 ; L54 103 616 ;
    L73 125 000 + 12 500 + 25 000 + 37 500 + 25 000 + 9 750 + 7 500 = 242 250 ;
    total 612 920 + 110 000 + 103 616 + 242 250 = 1 068 786, à payer au plus tard le 15/10/2026.
"""
import calendar
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "aite_syscohada_demo")
class TestDemoData(TransactionCase):
    """Société de démonstration : états, déclarations et soldes comparés aux calculs à la main du module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.ref("aite_syscohada_demo.demo_company")
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

    def form(self, declaration, code):
        return declaration.itvair_line_ids.filtered(lambda l: l.code == code).total

    def assertAmounts(self, actual, expected):
        self.assertEqual({key: actual[key] for key in expected}, expected)

    # ------------------------------------------------------------------ société
    def test_company(self):
        company = self.company
        self.assertEqual(company.currency_id, self.env.ref("base.XAF"))
        self.assertEqual(company.chart_template, "cm")
        self.assertTrue(company.aite_syscohada_setup_date)
        self.assertIn(company, self.env.ref("base.user_admin").company_ids, "l'administrateur accède à la société")
        codes = set(self.env["account.journal"].search([("company_id", "=", company.id)]).mapped("code"))
        self.assertLessEqual({"OM", "MOMO", "PAIE"}, codes)
        self.assertEqual(self.env["res.partner"].search_count([("company_id", "=", company.id)]), 14)

    def test_regeneration_is_idempotent(self):
        moves = self.env["account.move"].search_count([("company_id", "=", self.company.id)])
        self.assertEqual(self.env["aite.syscohada.demo"]._aite_generate(), self.company)
        self.assertEqual(self.env["account.move"].search_count([("company_id", "=", self.company.id)]), moves)
        self.assertEqual(self.env["res.company"].search_count([("name", "=", self.company.name)]), 1)

    # ------------------------------------------------------------------ états
    def test_income_statement_2025(self):
        self.assertAmounts(self.y2025["resultat"], {
            "TA": 41600000, "TC": 30200000, "XB": 71800000, "RA": -19668000, "RB": 2400000, "RE": -4800000,
            "RH": -11632000, "RI": -1070000, "XC": 37030000, "RK": -32529600, "RL": -1680000, "RM": 0,
            "XG": 2820400, "RS": -1566928, "XI": 1253472})
        advances = {code: self.balance(code, date(2025, 12, 31)) for code in ("449210", "449220", "449250")}
        self.assertEqual(advances, {"449210": 299520, "449220": 40000, "449250": 1227408})
        self.assertEqual(self.balance("441", date(2025, 12, 31)), -1566928, "impôt 2025 constaté")
        self.assertEqual(self.balance("441", date(2026, 3, 15)), 0, "acomptes imputés le 15/03/2026")

    def test_income_statement_2026(self):
        self.assertAmounts(self.y2026["resultat"], {
            "TA": 33480000, "TC": 26060000, "XB": 59540000, "RA": -16070400, "RB": 400000, "RE": -3960000,
            "RH": -8724000, "RI": -942500, "XC": 30243100, "RK": -25413750, "RL": -1960000, "RM": -820000,
            "XG": 2049350, "RS": 0, "XI": 2049350})

    def test_balance_sheet_2026(self):
        passif, actif = self.y2026["passif"], self.y2026["actif"]
        self.assertAmounts(passif, {"CA": 30000000, "CF": 125347, "CH": 508125, "CJ": 2049350, "DA": 8000000})
        self.assertEqual((actif["AL"]["brut"], actif["AL"]["amort"]), (9600000, 1680000))
        self.assertEqual((actif["AM"]["brut"], actif["AM"]["amort"]), (9600000, 1960000))
        self.assertEqual(actif["BB"]["net"], 2800000)
        self.assertEqual(actif["BT"]["net"], 22922286)
        self.assertEqual((actif["BZ"]["net"], passif["DZ"]), (44941362, 44941362))
        self.assertEqual({code: self.balance(code) for code in (
            "521001", "571001", "552100", "552200", "585001", "411100", "443800", "401100", "481200", "162",
            "3111", "4098", "465", "441", "449250", "449210", "449220")}, {
            "521001": 18629286, "571001": 2575800, "552100": 1073250, "552200": 643950, "585001": 0,
            "411100": 1955700, "443800": -315700, "401100": -2028400, "481200": 0, "162": -8000000,
            "3111": 2800000, "4098": 0, "465": 0, "441": 0, "449250": 901800, "449210": 241056, "449220": 40000})

    def test_cash_flow(self):
        self.assertAmounts(self.y2026["flux"], {"FO": 12000000, "FQ": -4000000, "FN": -620000, "FG": -6000000,
                                                "FK": 0, "ZH": 22922286})
        self.assertAmounts(self.y2025["flux"], {"FO": 0, "FQ": 0, "FN": 0, "FG": -13200000, "FK": 30000000})
        self.assertEqual(self.y2025["flux"]["ZH"], self.y2025["actif"]["BT"]["net"] - self.y2025["passif"]["DT"])

    def test_checks(self):
        checker = self.env["aite.syscohada.check"]
        for date_from, date_to in ((date(2025, 1, 1), date(2025, 12, 31)), (date(2026, 1, 1), date(2026, 9, 30))):
            problems = [(c["code"], c["level"], c["message"]) for c in checker.run(self.company, date_from, date_to)
                        if c["level"] in ("error", "warning")]
            self.assertEqual(problems, [], f"contrôles du {date_from} au {date_to}")

    def test_cash_never_negative(self):
        """Aucun compte de trésorerie créditeur ou à découvert en fin de mois."""
        for year, month in [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 10)]:
            end = date(year, month, calendar.monthrange(year, month)[1])
            for code in ("521001", "571001", "552100", "552200"):
                self.assertGreaterEqual(self.balance(code, end), 0, f"{code} au {end}")

    # ------------------------------------------------------------------ déclarations
    def test_declarations_sequence(self):
        self.assertEqual(len(self.declarations), 21)
        done, draft = self.declarations[:-1], self.declarations[-1]
        self.assertEqual(set(done.mapped("state")), {"done"})
        self.assertTrue(all(d.move_id.state == "posted" for d in done), "chaque déclaration validée est liquidée")
        self.assertEqual((draft.date_from, draft.state, bool(draft.move_id)), (date(2026, 9, 1), "draft", False))
        self.assertEqual(self.declaration(2025, 2).credit_previous, 2164162, "L17 reprend la L35 de janvier")

    def test_january_2025(self):
        decl = self.declaration(2025, 1)
        self.assertEqual(self.vat(decl, "CM_NORMAL"), (4176000, 803880))
        self.assertEqual(self.vat(decl, "CM_GLOBAL")[0], 4176000)
        self.assertEqual(self.vat(decl, "CM_LOCAL_PURCHASE")[1], 2884112)
        self.assertEqual(self.vat(decl, "CM_LOCAL_SERVICE")[1], 26180)
        self.assertEqual(self.vat(decl, "CM_FOREIGN_SERVICE")[1], 57750)
        self.assertEqual((decl.vat_to_pay, decl.vat_credit, decl.credit_to_report), (0, 2164162, 2164162))
        self.assertEqual({code: self.form(decl, code) for code in ("L0", "L38", "L42", "L44", "L46", "L50", "L54",
                                                                    "L73")},
                         {"L0": 45000, "L38": 57750, "L42": 90000, "L44": 90000, "L46": 20736, "L50": 91872,
                          "L54": 71136, "L73": 232500})
        self.assertEqual((decl.total_to_pay, decl.date_due), (496386, date(2025, 2, 15)))

    def test_july_and_august_2026(self):
        july, august = self.declaration(2026, 7), self.declaration(2026, 8)
        self.assertEqual(self.form(july, "L62"), 102300, "IRCM sur 620 000 de dividendes")
        dividends = self.env["account.move"].search([("company_id", "=", self.company.id),
                                                     ("ref", "=", "Dividendes versés, IRCM retenu à la source")])
        self.assertEqual(dividends.date, date(2026, 7, 20))
        self.assertEqual(sum(dividends.line_ids.filtered(lambda l: l.account_id.code == "447110").mapped("credit")),
                         102300)
        self.assertEqual(sum(dividends.line_ids.filtered(lambda l: l.account_id.code == "521001").mapped("credit")),
                         517700)
        self.assertEqual(self.vat(august, "CM_NORMAL"), (6960000, 1339800))
        self.assertEqual(self.vat(august, "CM_LOCAL_PURCHASE")[1], 483868)
        self.assertEqual((august.credit_previous, august.vat_to_pay), (0, 829752))

    def test_september_2026_draft(self):
        decl = self.declaration(2026, 9)
        self.assertEqual(self.vat(decl, "CM_NORMAL"), (5888000, 1133440))
        self.assertEqual(self.vat(decl, "CM_LOCAL_PURCHASE")[1], 417340)
        self.assertEqual(self.vat(decl, "CM_LOCAL_SERVICE")[1], 103180)
        self.assertEqual(decl.vat_to_pay, 612920)
        self.assertEqual({code: self.form(decl, code) for code in ("L42", "L43", "L44", "L46", "L50", "L54", "L73")},
                         {"L42": 90000, "L43": 20000, "L44": 110000, "L46": 25920, "L50": 129536, "L54": 103616,
                          "L73": 242250})
        self.assertEqual((decl.total_to_pay, decl.date_due), (1068786, date(2026, 10, 15)))

    def test_payments_match_declarations(self):
        """Chaque paiement du 15 (soldes du grand livre) égale le total à payer de la déclaration validée."""
        bank = self.company._aite_account("521001")
        for decl in self.declarations.filtered(lambda d: d.state == "done"):
            payment = self.env["account.move"].search([("company_id", "=", self.company.id),
                                                       ("ref", "=", f"Paiement I/TVA-IR {decl.date_to:%m/%Y}")])
            self.assertEqual(payment.date, decl.date_due, decl.name)
            self.assertEqual(sum(payment.line_ids.filtered(lambda l: l.account_id == bank).mapped("credit")),
                             decl.total_to_pay, decl.name)
        first = self.env["account.move"].search([("company_id", "=", self.company.id),
                                                 ("ref", "=", "Paiement I/TVA-IR 01/2025")])
        self.assertEqual(sum(first.line_ids.mapped("debit")), 496386)

    # ------------------------------------------------------------------ tiers
    def test_open_items_at_end(self):
        """Pièces ouvertes au 30/09/2026 : celles de septembre réglées en octobre."""
        open_moves = self.env["account.move"].search([
            ("company_id", "=", self.company.id), ("move_type", "in", ("out_invoice", "in_invoice")),
            ("payment_state", "!=", "paid")])
        self.assertEqual({m.ref: m.amount_residual for m in open_moves}, {
            "HEB-2026-09": 524700, "SEM-2026-09": 1431000, "BRA-2026-09": 1571400, "HON-2026-09": 457000})

    def test_rebate_deducted_from_march_payment(self):
        """Brasseries de février 2026 : 3 600 000 × 0,9 × 36 % = 1 166 400 × 1,2125 = 1 414 260, moins l'avoir de
        ristourne de 300 000 imputé le 10/02 : 1 114 260 réglés le 05/03/2026."""
        invoice = self.env["account.move"].search([("company_id", "=", self.company.id), ("ref", "=", "BRA-2026-02")])
        self.assertEqual((invoice.amount_total, invoice.payment_state), (1414260, "paid"))
        payment = self.env["account.payment"].search([("company_id", "=", self.company.id),
                                                      ("memo", "=", invoice.name)])
        self.assertEqual((payment.date, payment.amount), (date(2026, 3, 5), 1114260))
