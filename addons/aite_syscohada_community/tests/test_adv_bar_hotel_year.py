# -*- coding: utf-8 -*-
"""Scénario de recette d'un bar-hôtel sur deux exercices, en écritures directes (helper ``entry``).

Tous les montants attendus sont calculés à la main ci-dessous (règle 2 de CLAUDE.md) ; aucune valeur
n'est recopiée depuis la sortie du code. TVA à 19,25 %. Banque = compte 521 du journal de banque,
caisse = compte 571 du journal de caisse ; 515 (cartes bancaires à encaisser) est créé s'il manque au plan.

EXERCICE N-1 (2025), RÉDUIT À L'OUVERTURE
    02/01 apport en capital                         D 521 20 000 000                      C 1013 20 000 000
    01/03 achat de boissons réglé (hors TVA)        D 6011 3 000 000                      C 521  3 000 000
    30/06 ventes comptoir encaissées (hors TVA)     D 521  4 500 000                      C 7011 4 500 000
    31/12 stock final                               D 311  1 500 000                      C 6031 1 500 000
    Compte de résultat : TA 4 500 000 ; RA −3 000 000 ; RB +1 500 000 ; XA (marge) 3 000 000 ; XB (chiffre
                        d'affaires) = TA = 4 500 000 ; XC = XB + RA + RB = 3 000 000 = XI (bénéfice)
    Bilan 31/12/2025  : BB 1 500 000 ; BS = 20 000 000 − 3 000 000 + 4 500 000 = 21 500 000 ; BT 21 500 000 ;
                        BZ 23 000 000 = CA 20 000 000 + CJ 3 000 000 = DZ
    TFT 2025          : ZA 0 ; FA 3 000 000 ; FC −1 500 000 ; ZB 1 500 000 ; FK 20 000 000 ; ZD = ZF 20 000 000 ;
                        ZG = ZH 21 500 000

EXERCICE N (2026)
    01/01 reprise du stock initial                  D 6031 1 500 000                      C 311  1 500 000
    01/01 résultat N-1 en instance d'affectation    D 999999 3 000 000                    C 131  3 000 000
    15/01 emprunt bancaire reçu                     D 521 10 000 000                      C 162 10 000 000
    01/02 chambre froide                            D 2411 6 000 000 ; D 4451 1 155 000  C 4812 7 155 000
    15/02 paiement du fournisseur d'immobilisation  D 4812 7 155 000                      C 521  7 155 000
    05/03 vente comptoir du jour                    D 571 4 000 000 ; D 552100 2 000 000 ; D 515 1 155 000
                                                                                          C 7011 6 000 000 ; C 4431 1 155 000
    10/03 virement caisse → banque (départ)         D 585 3 000 000                       C 571  3 000 000
    11/03 virement caisse → banque (arrivée)        D 521 3 000 000                       C 585  3 000 000
    31/03 écart de caisse                           D 658800 5 000                        C 571  5 000
    10/04 facture d'hébergement n° 1                D 4111 1 192 500                      C 7061 1 000 000 ; C 443800 192 500
    20/04 encaissement complet                      D 521 1 192 500                       C 4111 1 192 500
    20/04 TVA devenue exigible                      D 443800 192 500                      C 443200 192 500
    02/05 acompte client (200 000 HT + TVA)         D 521 238 500                         C 4191 238 500
    10/05 facture d'hébergement n° 2                D 4111 596 250                        C 7061 500 000 ; C 443800 96 250
    10/05 imputation de l'acompte                   D 4191 238 500                        C 4111 238 500
    10/05 TVA exigible sur l'acompte (200 000 × 19,25 %) D 443800 38 500                  C 443200 38 500
    01/06 emballages consignés par le fournisseur   D 4094 150 000                        C 4011 150 000
    05/06 achat de marchandises                     D 6011 4 000 000 ; D 4452 770 000    C 4011 4 770 000
    20/06 retour partiel des emballages             D 4011 100 000                        C 4094 100 000
    25/06 paiement partiel du fournisseur           D 4011 3 000 000                      C 521  3 000 000
    30/06 affectation du résultat N-1               D 131 3 000 000                       C 111 300 000 ; C 121 700 000 ; C 465 2 000 000
    01/07 honoraires de l'expert-comptable          D 6324 400 000 ; D 4454 77 000       C 4011 477 000
    10/07 dividendes payés                          D 465 2 000 000                       C 521  2 000 000
    31/07 paie                                      D 6611 2 000 000                      C 431 70 000 ; C 447210 150 000 ;
                                                        C 447215 15 000 ; C 447220 20 000 ; C 447250 5 000 ; C 447260 3 000 ; C 422 1 737 000
    31/07 charges sociales patronales               D 664 330 000                         C 431 330 000
    31/07 taxes patronales sur salaires             D 6413 50 000                         C 447230 30 000 ; C 447240 20 000
    05/08 paiement des salaires nets                D 422 1 737 000                       C 521  1 737 000
    01/10 échéance d'emprunt                        D 162 2 000 000 ; D 6712 500 000     C 521  2 500 000
    31/12 ristourne annuelle à obtenir              D 4098 100 000                        C 6019 100 000
    31/12 amortissement de la chambre froide        D 6813 600 000                        C 2841 600 000
    31/12 stock final                               D 311 2 000 000                       C 6031 2 000 000
    31/12 impôt sur le résultat                     D 891 65 000                          C 441 65 000

SOLDES AU 31/12/2026 UTILES AU BILAN
    521 : 21 500 000 + 10 000 000 − 7 155 000 + 3 000 000 + 1 192 500 + 238 500 − 3 000 000 − 1 737 000
          − 2 000 000 − 2 500 000 = 19 539 000
    571 : 4 000 000 − 3 000 000 − 5 000 = 995 000 ; 552100 : 2 000 000 ; 515 : 1 155 000 ; 585 : 0
    4111 : 1 192 500 + 596 250 − 1 192 500 − 238 500 = 357 750 (débiteur) ; 4191 : 0
    4094 : 150 000 − 100 000 = 50 000 (débiteur) ; 4098 : 100 000 (débiteur)
    4011 : 150 000 + 4 770 000 + 477 000 − 100 000 − 3 000 000 = 2 297 000 (créditeur)
    4451 1 155 000 ; 4452 770 000 ; 4454 77 000 (débiteurs) → 2 002 000
    431 : 70 000 + 330 000 = 400 000 ; 4431 1 155 000 ; 443200 192 500 + 38 500 = 231 000 ;
    443800 : 192 500 + 96 250 − 192 500 − 38 500 = 57 750 ; 447210 150 000 ; 447215 15 000 ; 447220 20 000 ;
    447230 30 000 ; 447240 20 000 ; 447250 5 000 ; 447260 3 000 ; 441 65 000 (tous créditeurs)
    162 : 10 000 000 − 2 000 000 = 8 000 000 ; 131 : 0 ; 999999 : 3 000 000 (débiteur) ; 465 : 0 ; 4812 : 0

COMPTE DE RÉSULTAT 2026
    TA  = 7011                                   = 6 000 000
    RA  = −(6011 4 000 000 − 6019 100 000)       = −3 900 000
    RB  = −6031 = −(1 500 000 − 2 000 000)       = +500 000
    XA  = TA + RA + RB                           = 2 600 000
    TC  = 7061 (1 000 000 + 500 000)             = 1 500 000
    XB  = TA + TB + TC + TD                      = 7 500 000
    RH  = −6324                                  = −400 000
    RI  = −6413                                  = −50 000
    RJ  = −658800                                = −5 000
    XC  = 7 500 000 − 3 900 000 + 500 000 − 400 000 − 50 000 − 5 000 = 3 645 000
    RK  = −(6611 2 000 000 + 664 330 000)        = −2 330 000
    XD  = 3 645 000 − 2 330 000                  = 1 315 000
    RL  = −6813                                  = −600 000
    XE  = 1 315 000 − 600 000                    = 715 000
    RM  = −6712                                  = −500 000
    XF  = −500 000
    XG  = 715 000 − 500 000                      = 215 000
    XH  = 0 ; RQ = 0
    RS  = −891                                   = −65 000
    XI  = 215 000 − 65 000                       = 150 000

BILAN AU 31/12/2026
    AM  : brut 2411 6 000 000 ; amort 2841 600 000 ; net 5 400 000 ; AI = AZ = 5 400 000
    BA 0 (4812 soldé) ; BB 311 2 000 000
    BH  = 4094 50 000 + 4098 100 000             = 150 000
    BI  = 4111                                   = 357 750
    BJ  = 4451 + 4452 + 4454                     = 2 002 000
    BG  = 150 000 + 357 750 + 2 002 000          = 2 509 750 ; BK = 0 + 2 000 000 + 2 509 750 = 4 509 750
    BR  = 515                                    = 1 155 000
    BS  = 521 19 539 000 + 571 995 000 + 552100 2 000 000 = 22 534 000
    BT  = 1 155 000 + 22 534 000                 = 23 689 000
    BZ  = 5 400 000 + 4 509 750 + 23 689 000     = 33 598 750
    CA 20 000 000 ; CF 111 300 000 ; CH 121 700 000
    CJ  = −(13 + 6 + 7 + 8 + 999999) cumulés = −(0 − 3 150 000 + 3 000 000) = 150 000 = XI
    CP  = 20 000 000 + 300 000 + 700 000 + 150 000 = 21 150 000
    DA  = 162 8 000 000 = DD ; DF = 29 150 000
    DH 0 ; DI 0 ; DJ = 4011 2 297 000
    DK  = 400 000 + 1 155 000 + 231 000 + 57 750 + 150 000 + 15 000 + 20 000 + 30 000 + 20 000 + 5 000 + 3 000 + 65 000
        = 2 151 750
    DM 0 (465 payé) ; DP = 2 297 000 + 2 151 750 = 4 448 750 ; DT 0
    DZ  = 29 150 000 + 4 448 750                 = 33 598 750 = BZ

TABLEAU DES FLUX DE TRÉSORERIE 2026
    ZA  = BT − DT au 31/12/2025                  = 21 500 000
    FA  = XI 150 000 + dotations 681 600 000     = 750 000
    FB  = 0 ; FC = −(BB 2 000 000 − 1 500 000)   = −500 000
    FD  = −(BG 2 509 750 − 0)                    = −2 509 750
    FE  = V:DJ 2 297 000 + V:DK 2 151 750 (4812 et 465 soldés aux deux bornes) = 4 448 750
    ZB  = 750 000 − 500 000 − 2 509 750 + 4 448 750 = 2 189 000
    FG  = −débits 24 (6 000 000) − 4812 fin (0) + 4812 début (0) = −6 000 000 ; FF = FH = FI = FJ = 0 ; ZC = −6 000 000
    FK  = V:CF 300 000 + V:CH 700 000 + V:CJ (150 000 − 3 000 000) − XI 150 000 + D:465 2 000 000 = 0
    FN  = −D:465                                 = −2 000 000 ; ZD = −2 000 000
    FO  = crédits 162                            = 10 000 000 ; FQ = −débits 162 = −2 000 000 ; ZE = 8 000 000
    ZF  = ZD + ZE                                = 6 000 000
    ZG  = 2 189 000 − 6 000 000 + 6 000 000      = 2 189 000 = BT fin − BT début
    ZH  = 21 500 000 + 2 189 000                 = 23 689 000 = BT − DT au 31/12/2026
"""
from datetime import date

from odoo import Command
from odoo.tests import tagged

from odoo.addons.aite_syscohada_mis.models.mis_report import kpi_name
from odoo.addons.mis_builder.models.accounting_none import AccountingNone

from .test_vat_declaration import VatDeclarationCommon

STATEMENTS = ("actif", "passif", "resultat", "flux")
CHECK_CODES = {"RATTACHEMENT", "BROUILLONS", "EQUILIBRE", "RESULTAT", "ATTENTE", "CAISSE", "TFT", "ESPECES", "BASCULES"}


@tagged("post_install", "-at_install", "aite_syscohada", "aite_syscohada_advanced")
class TestAdvBarHotelYear(VatDeclarationCommon):
    """Bar-hôtel sur deux exercices : états N et N-1 du moteur, contrôles et modèles MIS, chiffrés à la main."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Cartes bancaires à encaisser (515, rubrique BR) : absent du plan « cm » d'Odoo, créé pour le scénario
        if not cls.company._aite_accounts_prefix("515"):
            cls.env["account.account"].with_company(cls.company).create({
                "code": "515000", "name": "Cartes de crédit à encaisser", "account_type": "asset_cash",
                "reconcile": False, "company_ids": [Command.set(cls.company.ids)]})
        cls.create_bar_hotel_scenario()
        cls.n1 = cls.engine.compute(cls.company, "2025-01-01", "2025-12-31")
        cls.n = cls.engine.compute(cls.company, "2026-01-01", "2026-12-31")

    @classmethod
    def create_bar_hotel_scenario(cls):
        """Écritures des deux exercices (détail et calculs dans la docstring du module)."""
        b, c = cls.bank, cls.cash
        E = cls.entry
        # ---- exercice N-1 (2025), réduit à l'ouverture
        E("2025-01-02", [(b, 20000000, 0), ("1013", 0, 20000000)], "apport en capital")
        E("2025-03-01", [("6011", 3000000, 0), (b, 0, 3000000)], "achat de boissons réglé")
        E("2025-06-30", [(b, 4500000, 0), ("7011", 0, 4500000)], "ventes comptoir encaissées")
        E("2025-12-31", [("311", 1500000, 0), ("6031", 0, 1500000)], "stock final N-1")
        # ---- exercice N (2026) : ouverture
        E("2026-01-01", [("6031", 1500000, 0), ("311", 0, 1500000)], "reprise du stock initial")
        E("2026-01-01", [("999999", 3000000, 0), ("131", 0, 3000000)], "résultat N-1 en instance d'affectation")
        # ---- financement et investissement
        E("2026-01-15", [(b, 10000000, 0), ("162", 0, 10000000)], "emprunt bancaire reçu")
        E("2026-02-01", [("2411", 6000000, 0), ("4451", 1155000, 0), ("4812", 0, 7155000)], "chambre froide")
        E("2026-02-15", [("4812", 7155000, 0), (b, 0, 7155000)], "paiement du fournisseur d'immobilisation")
        # ---- bar : vente comptoir, virement de fonds, écart de caisse
        E("2026-03-05", [(c, 4000000, 0), ("552100", 2000000, 0), ("515", 1155000, 0),
                         ("7011", 0, 6000000), ("4431", 0, 1155000)], "vente comptoir du jour")
        E("2026-03-10", [("585", 3000000, 0), (c, 0, 3000000)], "virement caisse vers banque (départ)")
        E("2026-03-11", [(b, 3000000, 0), ("585", 0, 3000000)], "virement caisse vers banque (arrivée)")
        E("2026-03-31", [("658800", 5000, 0), (c, 0, 5000)], "écart de caisse")
        # ---- hôtel : hébergement facturé, TVA à l'encaissement, acompte
        E("2026-04-10", [("4111", 1192500, 0), ("7061", 0, 1000000), ("443800", 0, 192500)], "facture d'hébergement n° 1")
        E("2026-04-20", [(b, 1192500, 0), ("4111", 0, 1192500)], "encaissement complet")
        E("2026-04-20", [("443800", 192500, 0), ("443200", 0, 192500)], "TVA devenue exigible")
        E("2026-05-02", [(b, 238500, 0), ("4191", 0, 238500)], "acompte client")
        E("2026-05-10", [("4111", 596250, 0), ("7061", 0, 500000), ("443800", 0, 96250)], "facture d'hébergement n° 2")
        E("2026-05-10", [("4191", 238500, 0), ("4111", 0, 238500)], "imputation de l'acompte")
        E("2026-05-10", [("443800", 38500, 0), ("443200", 0, 38500)], "TVA exigible sur l'acompte encaissé")
        # ---- fournisseurs : consigne, achats, services, ristourne
        E("2026-06-01", [("4094", 150000, 0), ("4011", 0, 150000)], "emballages consignés")
        E("2026-06-05", [("6011", 4000000, 0), ("4452", 770000, 0), ("4011", 0, 4770000)], "achat de marchandises")
        E("2026-06-20", [("4011", 100000, 0), ("4094", 0, 100000)], "retour partiel des emballages")
        E("2026-06-25", [("4011", 3000000, 0), (b, 0, 3000000)], "paiement partiel du fournisseur")
        E("2026-07-01", [("6324", 400000, 0), ("4454", 77000, 0), ("4011", 0, 477000)], "honoraires")
        E("2026-12-31", [("4098", 100000, 0), ("6019", 0, 100000)], "ristourne annuelle à obtenir")
        # ---- affectation du résultat N-1 et dividendes
        E("2026-06-30", [("131", 3000000, 0), ("111", 0, 300000), ("121", 0, 700000), ("465", 0, 2000000)],
          "affectation du résultat N-1")
        E("2026-07-10", [("465", 2000000, 0), (b, 0, 2000000)], "dividendes payés")
        # ---- paie de juillet
        E("2026-07-31", [("6611", 2000000, 0), ("431", 0, 70000), ("447210", 0, 150000), ("447215", 0, 15000),
                         ("447220", 0, 20000), ("447250", 0, 5000), ("447260", 0, 3000), ("422", 0, 1737000)], "paie")
        E("2026-07-31", [("664", 330000, 0), ("431", 0, 330000)], "charges sociales patronales")
        E("2026-07-31", [("6413", 50000, 0), ("447230", 0, 30000), ("447240", 0, 20000)], "taxes patronales sur salaires")
        E("2026-08-05", [("422", 1737000, 0), (b, 0, 1737000)], "paiement des salaires nets")
        # ---- échéance d'emprunt et clôture
        E("2026-10-01", [("162", 2000000, 0), ("6712", 500000, 0), (b, 0, 2500000)], "échéance d'emprunt")
        E("2026-12-31", [("6813", 600000, 0), ("2841", 0, 600000)], "amortissement de la chambre froide")
        E("2026-12-31", [("311", 2000000, 0), ("6031", 0, 2000000)], "stock final N")
        E("2026-12-31", [("891", 65000, 0), ("441", 0, 65000)], "impôt sur le résultat")

    # ------------------------------------------------------------------ outils MIS
    def mis_values(self, matrix, col_key=None):
        """{nom du KPI : {sous-colonne : valeur}} lu dans une matrice MIS, limité à la colonne ``col_key`` si donnée."""
        values = {}
        for row in matrix.iter_rows():
            if row.account_id:
                continue
            cells = {}
            for cell in row.iter_cells():
                if cell is None or (col_key is not None and cell.subcol.col.key != col_key):
                    continue
                val = 0.0 if cell.val is AccountingNone or cell.val is None else cell.val
                self.assertIsInstance(val, (int, float), f"{row.kpi.name} : {val!r}")
                cells[cell.subcol.subkpi.name if cell.subcol.subkpi else "value"] = round(val, 2)
            values[row.kpi.name] = cells
        return values

    def assert_mis_matches_engine(self, statement, mis, expected, label):
        """Chaque rubrique du moteur a la même valeur dans le modèle MIS (brut, amortissements et net pour l'actif)."""
        for code, value in expected[statement].items():
            got = mis[kpi_name(statement, code)]
            if statement == "actif":
                self.assertEqual(got, {"brut": value["brut"], "amort": value["amort"], "net": value["net"]},
                                 f"{label} {statement} {code}")
            else:
                self.assertEqual(got.get("value", 0.0), value, f"{label} {statement} {code}")

    # ------------------------------------------------------------------ grand livre
    def test_ledger_balances(self):
        """Soldes de comptes au 31/12/2026, calculés dans la docstring du module."""
        # 585 : 3 000 000 − 3 000 000 ; 4812 : 7 155 000 − 7 155 000 ; 4191 : 238 500 − 238 500 ;
        # 465 : 2 000 000 − 2 000 000 ; 131 : 3 000 000 − 3 000 000 → tous soldés
        for prefix in ("585", "4812", "4191", "465", "131"):
            self.assertEqual(self.balance(prefix), 0, f"{prefix} doit être soldé")
        # 4111 : 1 192 500 + 596 250 − 1 192 500 − 238 500 = 357 750 (débiteur)
        self.assertEqual(self.balance("4111"), 357750, "solde client après acompte et encaissement")
        # 443800 : 192 500 + 96 250 − 192 500 − 38 500 = 57 750 (créditeur, donc solde négatif)
        self.assertEqual(self.balance("443800"), -57750, "TVA des prestations non encore encaissées")
        # 443200 : 192 500 + 38 500 = 231 000 (créditeur)
        self.assertEqual(self.balance("443200"), -231000, "TVA sur prestations devenue exigible")
        # 4011 : 150 000 + 4 770 000 + 477 000 − 100 000 − 3 000 000 = 2 297 000 (créditeur)
        self.assertEqual(self.balance("4011"), -2297000, "dette fournisseurs")
        # 4094 : 150 000 − 100 000 = 50 000 (emballages encore à rendre)
        self.assertEqual(self.balance("4094"), 50000, "emballages consignés non rendus")
        # caisse : 4 000 000 − 3 000 000 − 5 000 = 995 000
        self.assertEqual(self.balance(self.cash.code), 995000, "solde de caisse")
        # banque : voir docstring → 19 539 000
        self.assertEqual(self.balance(self.bank.code), 19539000, "solde de banque")

    # ------------------------------------------------------------------ exercice N-1
    def test_n1_statements(self):
        """N-1 : TA 4 500 000, RA −3 000 000, RB +1 500 000 → XI 3 000 000 ; BZ = DZ = 23 000 000 ; ZH 21 500 000."""
        r, a, p, f = self.n1["resultat"], self.n1["actif"], self.n1["passif"], self.n1["flux"]
        # XA = 4 500 000 − 3 000 000 + 1 500 000 = 3 000 000 ; XB = TA (seul produit de chiffre d'affaires) = 4 500 000 ;
        # XC = XB + RA + RB = 3 000 000 ; XI = 3 000 000
        self.assertEqual((r["TA"], r["RA"], r["RB"], r["XA"], r["XB"], r["XC"], r["XI"]),
                         (4500000, -3000000, 1500000, 3000000, 4500000, 3000000, 3000000))
        # BB 1 500 000 ; BS = 20 000 000 − 3 000 000 + 4 500 000 = 21 500 000 ; BZ = 23 000 000
        self.assertEqual((a["BB"]["net"], a["BS"]["net"], a["BT"]["net"], a["BZ"]["net"]),
                         (1500000, 21500000, 21500000, 23000000))
        self.assertEqual((p["CA"], p["CJ"], p["CP"], p["DP"], p["DZ"]), (20000000, 3000000, 23000000, 0, 23000000))
        # ZA 0 ; FA = XI 3 000 000 ; FC = −1 500 000 ; ZB 1 500 000 ; FK = V:CA 20 000 000 + V:CJ 3 000 000 − XI 3 000 000
        self.assertEqual((f["ZA"], f["FA"], f["FC"], f["FD"], f["FE"], f["ZB"]), (0, 3000000, -1500000, 0, 0, 1500000))
        self.assertEqual((f["ZC"], f["FK"], f["ZD"], f["ZE"], f["ZF"], f["ZG"], f["ZH"]),
                         (0, 20000000, 20000000, 0, 20000000, 21500000, 21500000))

    # ------------------------------------------------------------------ exercice N : compte de résultat
    def test_n_compte_de_resultat(self):
        """Compte de résultat 2026 (calcul détaillé dans la docstring du module)."""
        r = self.n["resultat"]
        expected = {
            "TA": 6000000,      # 7011
            "TC": 1500000,      # 7061 : 1 000 000 + 500 000
            "XB": 7500000,      # TA + TC
            "RA": -3900000,     # −(6011 4 000 000 − 6019 100 000)
            "RB": 500000,       # −(6031 : 1 500 000 débit − 2 000 000 crédit)
            "XA": 2600000,      # 6 000 000 − 3 900 000 + 500 000
            "RE": 0,            # pas de 604/605/608
            "RH": -400000,      # 6324
            "RI": -50000,       # 6413
            "RJ": -5000,        # 658800
            "XC": 3645000,      # 7 500 000 − 3 900 000 + 500 000 − 400 000 − 50 000 − 5 000
            "RK": -2330000,     # 6611 2 000 000 + 664 330 000
            "XD": 1315000,      # 3 645 000 − 2 330 000
            "RL": -600000,      # 6813
            "XE": 715000,       # 1 315 000 − 600 000
            "RM": -500000,      # 6712
            "XF": -500000,
            "XG": 215000,       # 715 000 − 500 000
            "XH": 0,
            "RS": -65000,       # 891
            "XI": 150000,       # 215 000 − 65 000
        }
        self.assertEqual({k: r[k] for k in expected}, expected)

    # ------------------------------------------------------------------ exercice N : bilan
    def test_n_bilan(self):
        """Bilan au 31/12/2026 : BZ = DZ = 33 598 750 (calcul détaillé dans la docstring du module)."""
        a, p = self.n["actif"], self.n["passif"]
        # AM : chambre froide 6 000 000, amortie de 600 000
        self.assertEqual(a["AM"], {"brut": 6000000, "amort": 600000, "net": 5400000})
        self.assertEqual((a["AI"]["net"], a["AZ"]["net"]), (5400000, 5400000))
        expected_actif = {
            "BA": 0,            # 4812 soldé
            "BB": 2000000,      # 311
            "BH": 150000,       # 4094 50 000 + 4098 100 000
            "BI": 357750,       # 4111
            "BJ": 2002000,      # 4451 1 155 000 + 4452 770 000 + 4454 77 000
            "BG": 2509750,      # BH + BI + BJ
            "BK": 4509750,      # BA + BB + BG
            "BR": 1155000,      # 515
            "BS": 22534000,     # 521 19 539 000 + 571 995 000 + 552100 2 000 000
            "BT": 23689000,     # BR + BS
            "BZ": 33598750,     # 5 400 000 + 4 509 750 + 23 689 000
        }
        self.assertEqual({k: a[k]["net"] for k in expected_actif}, expected_actif)
        expected_passif = {
            "CA": 20000000,     # 1013
            "CF": 300000,       # 111
            "CH": 700000,       # 121
            "CJ": 150000,       # = XI, le résultat N-1 ayant été affecté
            "CP": 21150000,     # 20 000 000 + 300 000 + 700 000 + 150 000
            "DA": 8000000,      # 162 : 10 000 000 − 2 000 000
            "DD": 8000000,
            "DF": 29150000,     # CP + DD
            "DH": 0,
            "DI": 0,            # 4191 soldé, 4111 débiteur
            "DJ": 2297000,      # 4011
            "DK": 2151750,      # 431 400 000 + 4431 1 155 000 + 443200 231 000 + 443800 57 750 + 447xxx 243 000 + 441 65 000
            "DM": 0,            # 465 payé
            "DP": 4448750,      # DJ + DK
            "DT": 0,
            "DZ": 33598750,     # 29 150 000 + 4 448 750
        }
        self.assertEqual({k: p[k] for k in expected_passif}, expected_passif)
        self.assertEqual(a["BZ"]["net"], p["DZ"], "équilibre du bilan")

    # ------------------------------------------------------------------ exercice N : TFT
    def test_n_tft(self):
        """TFT 2026 : ZH 23 689 000 = BT − DT (calcul détaillé dans la docstring du module)."""
        f = self.n["flux"]
        expected = {
            "ZA": 21500000,     # trésorerie nette au 31/12/2025
            "FA": 750000,       # XI 150 000 + dotation 6813 600 000
            "FB": 0,
            "FC": -500000,      # −(2 000 000 − 1 500 000)
            "FD": -2509750,     # −(BG 2 509 750 − 0)
            "FE": 4448750,      # V:DJ 2 297 000 + V:DK 2 151 750
            "ZB": 2189000,      # 750 000 − 500 000 − 2 509 750 + 4 448 750
            "FF": 0,
            "FG": -6000000,     # débits sur 2411, fournisseur d'immobilisation soldé
            "FH": 0, "FI": 0, "FJ": 0,
            "ZC": -6000000,
            "FK": 0,            # 300 000 + 700 000 + (150 000 − 3 000 000) − 150 000 + 2 000 000
            "FL": 0, "FM": 0,
            "FN": -2000000,     # dividendes versés (débits 465)
            "ZD": -2000000,
            "FO": 10000000,     # crédits 162
            "FP": 0,
            "FQ": -2000000,     # débits 162
            "ZE": 8000000,
            "ZF": 6000000,      # ZD + ZE
            "ZG": 2189000,      # ZB + ZC + ZF
            "ZH": 23689000,     # ZA + ZG
        }
        self.assertEqual({k: f[k] for k in expected}, expected)
        # ZG = variation de la trésorerie du bilan : 23 689 000 − 21 500 000
        self.assertEqual(f["ZG"], self.n["actif"]["BT"]["net"] - self.n1["actif"]["BT"]["net"])

    # ------------------------------------------------------------------ contrôles
    def test_checks_all_ok(self):
        """Les 9 contrôles sont « ok » sur N et N-1 (BASCULES peut être « info ») ; pas d'avertissement d'affectation."""
        for date_from, date_to, results in (("2025-01-01", "2025-12-31", self.n1), ("2026-01-01", "2026-12-31", self.n)):
            checks = {c["code"]: c for c in self.checker.run(self.company, date_from, date_to, results=results)}
            self.assertEqual(set(checks), CHECK_CODES, f"{date_to} : neuf contrôles attendus, sans AFFECTATION")
            for code, check in checks.items():
                if code == "BASCULES":
                    self.assertIn(check["level"], ("ok", "info"), f"{date_to} BASCULES : {check['message']}")
                else:
                    self.assertEqual(check["level"], "ok", f"{date_to} {code} : {check['message']}")
        # Aucun compte reclassé : 4011 créditeur, 4111 débiteur, banque positive (409x hors contrôle)
        bascules = [c for c in self.checker.run(self.company, "2026-01-01", "2026-12-31", results=self.n) if c["code"] == "BASCULES"]
        self.assertEqual(bascules[0]["level"], "ok", bascules[0]["message"])

    # ------------------------------------------------------------------ MIS Builder, exercice N
    def test_n_mis_equals_engine(self):
        """Les quatre modèles MIS donnent, sur 2026, exactement les rubriques du moteur."""
        mis = {}
        for statement in STATEMENTS:
            instance = self.env["mis.report.instance"].create({
                "name": f"recette {statement}", "report_id": self.env.ref(f"aite_syscohada_mis.report_{statement}").id,
                "company_id": self.company.id,
                "period_ids": [Command.create({"name": "N", "mode": "fix", "manual_date_from": "2026-01-01",
                                               "manual_date_to": "2026-12-31"})]})
            mis[statement] = self.mis_values(instance._compute_matrix())
            self.assert_mis_matches_engine(statement, mis[statement], self.n, "2026")
        # Points de repère calculés à la main, lus directement dans MIS
        self.assertEqual(mis["flux"][kpi_name("flux", "ZH")]["value"], 23689000)
        self.assertEqual(mis["resultat"][kpi_name("resultat", "XI")]["value"], 150000)
        # BZ brut = AM 6 000 000 + BB 2 000 000 + BH 150 000 + BI 357 750 + BJ 2 002 000 + BR 1 155 000 + BS 22 534 000
        #         = 34 198 750 ; amortissements 600 000 ; net 33 598 750
        self.assertEqual(mis["actif"][kpi_name("actif", "BZ")], {"brut": 34198750, "amort": 600000, "net": 33598750})

    # ------------------------------------------------------------------ MIS Builder, colonne « Exercice N-1 »
    def test_n1_mis_column_equals_engine(self):
        """L'instance « États en un clic » : sa colonne « Exercice N-1 » (2025) égale le moteur sur 2025,
        et sa colonne « Exercice N » (2026) égale le moteur sur 2026."""
        Instance = self.env["mis.report.instance"]
        for statement in STATEMENTS:
            instance = Instance._aite_syscohada_instance(statement, company=self.company)
            instance.date = date(2026, 6, 30)  # date de base fixée : N = 2026, N-1 = 2025, quel que soit le jour du test
            self.assertEqual(instance.period_ids.mapped("name"), ["Exercice N", "Exercice N-1"])
            n1 = instance.period_ids.filtered(lambda p: p.name == "Exercice N-1")
            n = instance.period_ids - n1
            self.assertEqual((n1.date_from, n1.date_to), (date(2025, 1, 1), date(2025, 12, 31)))
            self.assertEqual((n.date_from, n.date_to), (date(2026, 1, 1), date(2026, 12, 31)))
            matrix = instance._compute_matrix()
            self.assert_mis_matches_engine(statement, self.mis_values(matrix, n1.id), self.n1, "colonne N-1")
            self.assert_mis_matches_engine(statement, self.mis_values(matrix, n.id), self.n, "colonne N")
            if statement == "resultat":
                mis_n1 = self.mis_values(matrix, n1.id)
                # XI 2025 = 4 500 000 − 3 000 000 + 1 500 000
                self.assertEqual(mis_n1[kpi_name("resultat", "XI")]["value"], 3000000)
            if statement == "passif":
                mis_n1 = self.mis_values(matrix, n1.id)
                # DZ 2025 = CA 20 000 000 + CJ 3 000 000
                self.assertEqual(mis_n1[kpi_name("passif", "DZ")]["value"], 23000000)
