# -*- coding: utf-8 -*-
"""Test avancé : volume d'un mois chargé (août 2026) et temps de calcul de la déclaration.

Scénario (pièces créées en lot : ``account.move.create`` sur une liste, puis ``action_post`` sur le recordset) :
    - 300 factures clients de 10 lignes, taxe tva_sale_19_25, compte 7011 ;
      prix unitaire de chaque ligne de la facture i (i = 0 à 299) : 1 000 × (i % 7 + 1) ;
    - 100 factures fournisseurs de 5 lignes, taxe tva_purchase_good_19_25, compte 6011 ;
      prix unitaire de chaque ligne de la facture i (i = 0 à 99) : 2 500 × (i % 5 + 1) ;
    - 50 factures de prestations de services sur encaissement de 2 lignes, taxe tva_prestations_encaissement,
      compte 7061 ; prix unitaire de chaque ligne de la facture i (i = 0 à 49) : 3 000 × (i % 4 + 1) ;
      les 25 factures de rang pair sont payées le 25 août 2026, les 25 de rang impair restent impayées.

TVA à 19,25 % = 77/400. Les prix sont choisis pour que l'arrondi XAF (sans décimale) compte : 1 000 × 19,25 % = 192,5,
2 500 × 19,25 % = 481,25, 3 000 × 19,25 % = 577,5. Le total de TVA dépend donc du réglage de la société
``tax_calculation_rounding_method`` : arrondi par ligne (défaut d'Odoo, « round_per_line ») ou arrondi global par
facture (« round_globally »). Le test lit ce réglage et retient l'attendu correspondant ; les deux jeux de montants
sont calculés à la main ci-dessous et recalculés par une boucle Python indépendante (``expected_amounts``), qui ne lit
que les paramètres du scénario, jamais les écritures.

Calcul à la main (arrondi au franc supérieur à partir de 0,5, comme ``currency.round``) :

Ventes de biens — k = i % 7 + 1 ; 300 = 42 × 7 + 6 → k = 1 à 6 : 43 factures chacun, k = 7 : 42 factures.
    Σk = 42 × 28 + (1 + 2 + … + 6) = 1 176 + 21 = 1 197
    Base = 10 lignes × 1 000 × 1 197 = 11 970 000 ; 3 000 lignes sur le compte 7011.
    Par ligne : TVA d'une ligne = arrondi(192,5 × k) = 192,5 × k + 0,5 si k impair ;
                k impairs : 43 × 3 (k = 1, 3, 5) + 42 (k = 7) = 171 factures ;
                TVA = 10 × (192,5 × 1 197 + 0,5 × 171) = 10 × (230 422,5 + 85,5) = 2 305 080
    Global    : TVA d'une facture = arrondi(10 × 192,5 × k) = 1 925 × k (exact) ; TVA = 1 925 × 1 197 = 2 304 225

Achats de biens — m = i % 5 + 1, chaque m sur 20 factures ; base = 5 × 2 500 × 20 × (1 + … + 5) = 3 750 000.
    Par ligne : arrondi(481,25 × m) = 481, 963, 1 444, 1 925, 2 406 ; × 5 lignes = 2 405, 4 815, 7 220, 9 625, 12 030 ;
                somme 36 095 ; TVA = 20 × 36 095 = 721 900
    Global    : arrondi(2 406,25 × m) = 2 406, 4 813, 7 219, 9 625, 12 031 ; somme 36 094 ; TVA = 20 × 36 094 = 721 880

Prestations sur encaissement — n = i % 4 + 1 ; 2 lignes de 3 000 × n.
    Payées (i pair) : i % 4 = 0 → n = 1 (13 factures : 0, 4, …, 48) ; i % 4 = 2 → n = 3 (12 factures : 2, 6, …, 46)
        Base = 2 × 3 000 × (13 × 1 + 12 × 3) = 6 000 × 49 = 294 000
        Par ligne : facture n = 1 : 2 × arrondi(577,5) = 1 156 ; n = 3 : 2 × arrondi(1 732,5) = 3 466 ;
                    TVA = 13 × 1 156 + 12 × 3 466 = 15 028 + 41 592 = 56 620
        Global    : facture n = 1 : 1 155 ; n = 3 : 3 465 ; TVA = 13 × 1 155 + 12 × 3 465 = 15 015 + 41 580 = 56 595
    Impayées (i impair) : n = 2 (13 factures : 1, 5, …, 49) ; n = 4 (12 factures : 3, 7, …, 47)
        Base = 6 000 × (13 × 2 + 12 × 4) = 6 000 × 74 = 444 000
        TVA (identique dans les deux modes, 577,5 × 2 = 1 155 entier) = 13 × 2 310 + 12 × 4 620 = 30 030 + 55 440 = 85 470

Compte de résultat du moteur sur août : TA (701) = 11 970 000 ; TC (706) = 294 000 + 444 000 = 738 000.

Déclaration d'août (aucune déclaration validée avant : L17 = 0 ; ni export ni exonération : L15 = L10) :
                                      par ligne                 global
    L10 base = 11 970 000 + 294 000  = 12 264 000              12 264 000
    L10 taxe = biens + prestations    = 2 305 080 + 56 620       2 304 225 + 56 595
                                      = 2 361 700                = 2 360 820
    L18      = TVA des achats         = 721 900                  721 880
    L28      = L10 taxe               = 2 361 700                2 360 820
    L29      = L17 + L18 = 0 + L18    = 721 900                  721 880
    L32      = max(L28 − L29, 0)      = 1 639 800                1 638 940
    L35      = 0 (pas de crédit)
    Acompte L54 = L50 = 2 % × 12 264 000 = 245 280 + CAC 10 % 24 528 = 269 808

Liquidation : D 4431 (TVA des ventes de biens) ; D 4432 (TVA des prestations encaissées) ; C 4452 (L18) ;
C 4441 (L32) ; D 449250 / C 441100 (acompte). Total des débits = L28 + acompte.
Soldes après liquidation : 4431 = 0 ; 4452 = 0 ; 4432 = 0 ; 4438 = −85 470 (TVA des 25 prestations impayées,
encore en attente) ; 4441 = −L32.

Temps mesurés (``time.perf_counter``) et journalisés : ``action_compute`` < 180 s, ``engine.compute`` < 60 s ;
le test entier doit durer moins de 10 minutes.
"""
import logging
import time

from odoo import Command
from odoo.tests import tagged

from .test_vat_declaration import VatDeclarationCommon

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------- paramètres du scénario
MONTH_FROM, MONTH_TO = "2026-08-01", "2026-08-31"
PAYMENT_DATE = "2026-08-25"
SALES, SALE_LINES = 300, 10
PURCHASES, PURCHASE_LINES = 100, 5
SERVICES, SERVICE_LINES = 50, 2
RATE_NUM, RATE_DEN = 77, 400  # 19,25 % = 77/400
ACOMPTE_RATE, CAC_RATE = 2, 10  # acompte 2 % du chiffre d'affaires, CAC 10 % de l'acompte

# bornes de durée (secondes)
MAX_ACTION_COMPUTE = 180
MAX_ENGINE_COMPUTE = 60
MAX_TEST = 600


def sale_price(i):
    return 1000 * (i % 7 + 1)


def purchase_price(i):
    return 2500 * (i % 5 + 1)


def service_price(i):
    return 3000 * (i % 4 + 1)


def service_paid(i):
    return i % 2 == 0


def round_half_up(numerator, denominator):
    """Arrondi entier au plus proche, 0,5 vers le haut, sur une fraction positive (calcul exact en entiers)."""
    return (2 * numerator + denominator) // (2 * denominator)


def invoice_tax(prices, rounding_method):
    """TVA d'une facture en XAF selon le mode d'arrondi de la société."""
    if rounding_method == "round_globally":
        return round_half_up(sum(prices) * RATE_NUM, RATE_DEN)
    return sum(round_half_up(p * RATE_NUM, RATE_DEN) for p in prices)


def expected_amounts(rounding_method):
    """Recalcul indépendant des attendus depuis les seuls paramètres du scénario."""
    sales_base = sales_tax = purchase_base = purchase_tax = 0
    paid_base = paid_tax = unpaid_base = unpaid_tax = 0
    for i in range(SALES):
        prices = [sale_price(i)] * SALE_LINES
        sales_base += sum(prices)
        sales_tax += invoice_tax(prices, rounding_method)
    for i in range(PURCHASES):
        prices = [purchase_price(i)] * PURCHASE_LINES
        purchase_base += sum(prices)
        purchase_tax += invoice_tax(prices, rounding_method)
    for i in range(SERVICES):
        prices = [service_price(i)] * SERVICE_LINES
        if service_paid(i):
            paid_base += sum(prices)
            paid_tax += invoice_tax(prices, rounding_method)
        else:
            unpaid_base += sum(prices)
            unpaid_tax += invoice_tax(prices, rounding_method)
    l10_base = sales_base + paid_base
    l10_tax = sales_tax + paid_tax
    l28, l29 = l10_tax, purchase_tax  # L17 = 0, ni export ni exonération
    acompte = round_half_up(l10_base * ACOMPTE_RATE, 100)
    acompte += round_half_up(acompte * CAC_RATE, 100)
    return {
        "sales_base": sales_base, "sales_tax": sales_tax, "paid_tax": paid_tax, "unpaid_tax": unpaid_tax,
        "services_base": paid_base + unpaid_base,
        "L10": (l10_base, l10_tax), "L18": purchase_tax, "L28": l28, "L29": l29,
        "L32": max(l28 - l29, 0), "L35": max(l29 - l28, 0), "acompte": acompte,
        "lines_7011": SALES * SALE_LINES,
    }


# attendus calculés à la main (voir le docstring du module), par mode d'arrondi
HAND = {
    "round_per_line": {
        "sales_base": 11970000, "sales_tax": 2305080, "paid_tax": 56620, "unpaid_tax": 85470, "services_base": 738000,
        "L10": (12264000, 2361700), "L18": 721900, "L28": 2361700, "L29": 721900, "L32": 1639800, "L35": 0,
        "acompte": 269808, "lines_7011": 3000,
    },
    "round_globally": {
        "sales_base": 11970000, "sales_tax": 2304225, "paid_tax": 56595, "unpaid_tax": 85470, "services_base": 738000,
        "L10": (12264000, 2360820), "L18": 721880, "L28": 2360820, "L29": 721880, "L32": 1638940, "L35": 0,
        "acompte": 269808, "lines_7011": 3000,
    },
}


@tagged("post_install", "-at_install", "aite_syscohada_volume")
# Étiquette dédiée « aite_syscohada_volume », hors de la suite générale : exécuté après les autres tests
# avancés dans le même processus, ce test peut dépasser 10 minutes. Les insertions annulées des tests
# précédents déclenchent l'autovacuum, qui fausse les statistiques pendant la transaction ; le
# planificateur choisit alors un plan très lent pour la requête de lettrage du paiement groupé.
# Seul, sur une base neuve, il dure moins d'une minute. Lancement :
#   scripts/run_tests.sh <base> aite_syscohada_community aite_syscohada_volume
class TestAdvVolume(VatDeclarationCommon):
    """Mois d'août 2026 à fort volume : 450 factures, 3 550 lignes de produits et charges, déclaration et liquidation."""

    # ------------------------------------------------------------------ outils
    def invoice_vals(self, move_type, day, prices, tax, account):
        return {
            "move_type": move_type, "partner_id": self.partner.id, "invoice_date": day, "date": day,
            "company_id": self.company.id,
            "invoice_line_ids": [Command.create({"name": f"ligne {n + 1}", "quantity": 1, "price_unit": price,
                                                 "account_id": account.id, "tax_ids": [Command.set(tax.ids)]})
                                 for n, price in enumerate(prices)],
        }

    def create_documents(self):
        """Crée et valide en lot les 450 factures du mois, puis paie les 25 prestations de rang pair."""
        acc_7011, acc_6011, acc_7061 = self.acc("7011"), self.acc("6011"), self.acc("7061")
        Move = self.env["account.move"]
        day = lambda i, span: f"2026-08-{i % span + 1:02d}"  # noqa: E731
        sales = Move.create([self.invoice_vals("out_invoice", day(i, 28), [sale_price(i)] * SALE_LINES,
                                               self.t_sale, acc_7011) for i in range(SALES)])
        purchases = Move.create([self.invoice_vals("in_invoice", day(i, 28), [purchase_price(i)] * PURCHASE_LINES,
                                                   self.t_buy, acc_6011) for i in range(PURCHASES)])
        services = Move.create([self.invoice_vals("out_invoice", day(i, 20), [service_price(i)] * SERVICE_LINES,
                                                   self.t_services, acc_7061) for i in range(SERVICES)])
        (sales | purchases | services).action_post()
        paid =services.browse([services.ids[i] for i in range(SERVICES) if service_paid(i)])
        self.env["account.payment.register"].with_context(active_model="account.move", active_ids=paid.ids).create(
            {"payment_date": PAYMENT_DATE, "journal_id": self.journal_bank.id, "group_payment": True})._create_payments()
        return sales, purchases, services, paid

    # ------------------------------------------------------------------ scénario
    def test_august_volume(self):
        """450 factures en août 2026 : lignes L10 à L35, liquidation équilibrée, soldes et temps de calcul."""
        start = time.perf_counter()
        method = self.company.tax_calculation_rounding_method or "round_per_line"
        _logger.info("volume : mode d'arrondi de la TVA de la société = %s", method)
        expected = expected_amounts(method)
        # la boucle indépendante doit retrouver le calcul à la main du docstring
        self.assertEqual(expected, HAND[method], f"recalcul des attendus ({method}) différent du calcul à la main")

        t0 = time.perf_counter()
        sales, purchases, services, paid = self.create_documents()
        _logger.info("volume : création et validation de %s factures en %.1f s",
                     len(sales | purchases | services), time.perf_counter() - t0)
        self.assertEqual((len(sales), len(purchases), len(services), len(paid)), (300, 100, 50, 25))
        self.assertTrue(all(m.state == "posted" for m in sales | purchases | services))
        self.assertTrue(all(m.payment_state in ("paid", "in_payment") for m in paid), "25 prestations payées")
        self.assertTrue(all(m.payment_state == "not_paid" for m in services - paid), "25 prestations impayées")

        # 10 lignes × 300 factures = 3 000 lignes de produits sur le compte 7011 en août
        lines_7011 = self.env["account.move.line"].search_count([
            ("account_id", "=", self.acc("7011").id), ("parent_state", "=", "posted"),
            ("date", ">=", MONTH_FROM), ("date", "<=", MONTH_TO)])
        self.assertEqual(lines_7011, expected["lines_7011"], "nombre de lignes 7011 du mois")
        # contrôle intermédiaire : TVA des ventes de biens portée sur 4431 avant liquidation
        self.assertEqual(-self.balance("4431"), expected["sales_tax"], "TVA collectée sur les ventes de biens (4431)")

        # ---------------------------------------------------------------- déclaration
        decl = self.Decl.create({"company_id": self.company.id, "date_from": MONTH_FROM, "date_to": MONTH_TO})
        t0 = time.perf_counter()
        decl.action_compute()
        duration_compute = time.perf_counter() - t0
        _logger.info("volume : action_compute de la déclaration d'août en %.2f s", duration_compute)

        t0 = time.perf_counter()
        statements = self.compute(MONTH_FROM, MONTH_TO)
        duration_engine = time.perf_counter() - t0
        _logger.info("volume : engine.compute sur août en %.2f s", duration_engine)
        # compte de résultat du mois (comptabilité d'engagement) : TA = 701 = 11 970 000 ;
        # TC = 706 = toutes les prestations facturées, payées ou non = 294 000 + 444 000 = 738 000
        self.assertAmount(statements["resultat"]["TA"], expected["sales_base"], "moteur : TA ventes de marchandises")
        self.assertAmount(statements["resultat"]["TC"], expected["services_base"], "moteur : TC services vendus")

        self.assertLess(duration_compute, MAX_ACTION_COMPUTE, "action_compute trop lent")
        self.assertLess(duration_engine, MAX_ENGINE_COMPUTE, "engine.compute trop lent")

        # L10 : biens + prestations encaissées seulement (12 264 000 de base)
        line10 = self.line(decl, "CM_NORMAL")
        self.assertEqual((line10.base, line10.tax), expected["L10"], "L10 : base et taxe")
        self.assertEqual(self.line(decl, "CM_GLOBAL").base, expected["L10"][0], "L15 = L10 (ni export ni exonération)")
        self.assertEqual(decl.credit_previous, 0, "L17 : aucune déclaration validée avant août")
        self.assertEqual(self.line(decl, "CM_LOCAL_PURCHASE").tax, expected["L18"], "L18 : TVA sur achats de biens")
        self.assertEqual((decl.vat_collected, decl.vat_deductible, decl.vat_to_pay, decl.vat_credit, decl.credit_to_report),
                         (expected["L28"], expected["L29"], expected["L32"], 0, expected["L35"]),
                         "L28, L29, L32, L33, L35")
        self.assertEqual(decl.acompte_to_pay, expected["acompte"], "L54 : 2 % de L15 + CAC 10 %")

        # ---------------------------------------------------------------- liquidation
        move = decl.action_create_closing_entry()
        self.assertEqual(move.state, "posted")
        debit, credit = sum(move.line_ids.mapped("debit")), sum(move.line_ids.mapped("credit"))
        self.assertEqual(debit, credit, "écriture de liquidation équilibrée")
        self.assertEqual(debit, expected["L28"] + expected["acompte"], "débits : TVA collectée + acompte")
        for prefix in ("4431", "4432", "4452"):
            self.assertEqual(self.balance(prefix), 0, f"solde {prefix} après liquidation")
        # 4438 : TVA des 25 prestations impayées encore en attente (crédit)
        self.assertEqual(self.balance("4438"), -expected["unpaid_tax"], "solde 4438 : prestations impayées")
        self.assertEqual(self.balance("4441"), -expected["L32"], "solde 4441 : TVA à payer")

        total = time.perf_counter() - start
        _logger.info("volume : test complet en %.1f s (action_compute %.2f s, engine.compute %.2f s)",
                     total, duration_compute, duration_engine)
        self.assertLess(total, MAX_TEST, "le test doit durer moins de 10 minutes")
