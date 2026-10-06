# -*- coding: utf-8 -*-
import random
from datetime import date, timedelta

from odoo.tests import tagged

from .common import SyscohadaCommon

# Gabarits d'écritures usuelles : fonction(montant) -> lignes (compte, débit, crédit)
TEMPLATES = {
    "vente": lambda x, b: [("4111", round(x * 1.1925), 0), ("7011", 0, x), ("4431", 0, round(x * 1.1925) - x)],
    "encaissement": lambda x, b: [(b, x, 0), ("4111", 0, x)],
    "achat": lambda x, b: [("6011", x, 0), ("4452", round(x * 0.1925), 0), ("4011", 0, x + round(x * 0.1925))],
    "paiement": lambda x, b: [("4011", x, 0), (b, 0, x)],
    "prestation": lambda x, b: [("5711", x, 0), ("7061", 0, x)],
    "stock+": lambda x, b: [("311", x, 0), ("6031", 0, x)],
    "stock-": lambda x, b: [("6031", x, 0), ("311", 0, x)],
    "immo_credit": lambda x, b: [("2441", x, 0), ("4812", 0, x)],
    "immo_paiement": lambda x, b: [("4812", x, 0), (b, 0, x)],
    "logiciel": lambda x, b: [("2131", x, 0), (b, 0, x)],
    "en_cours": lambda x, b: [("2491", x, 0), (b, 0, x)],
    "mise_en_service": lambda x, b: [("2441", x, 0), ("2491", 0, x)],
    "amortissement": lambda x, b: [("6813", x, 0), ("2844", 0, x)],
    "cession": lambda x, b: [("2844", x // 2, 0), ("812", x - x // 2, 0), ("2441", 0, x), ("4852", x, 0), ("822", 0, x)],
    "encaissement_cession": lambda x, b: [(b, x, 0), ("4852", 0, x)],
    "provision": lambda x, b: [("6911", x, 0), ("191", 0, x)],
    "reprise_provision": lambda x, b: [("191", x, 0), ("7911", 0, x)],
    "depreciation_client": lambda x, b: [("6594", x, 0), ("491", 0, x)],
    "reprise_depreciation": lambda x, b: [("491", x, 0), ("759", 0, x)],
    "emprunt": lambda x, b: [(b, x, 0), ("162", 0, x)],
    "remboursement": lambda x, b: [("162", x, 0), (b, 0, x)],
    "interets_courus": lambda x, b: [("6712", x, 0), ("1662", 0, x)],
    "paiement_interets": lambda x, b: [("1662", x, 0), (b, 0, x)],
    "capital_souscrit": lambda x, b: [("4613", x, 0), ("1013", 0, x)],
    "capital_verse": lambda x, b: [(b, x, 0), ("4613", 0, x)],
    "subvention": lambda x, b: [(b, x, 0), ("141", 0, x)],
    "quote_part_subvention": lambda x, b: [("141", x, 0), ("799", 0, x)],
    "resultat_en_13": lambda x, b: [("999999", x, 0), ("131", 0, x)],
    "dividendes": lambda x, b: [("131", x, 0), ("465", 0, x)],
    "paiement_dividendes": lambda x, b: [("465", x, 0), (b, 0, x)],
    "ecart_actif": lambda x, b: [("4781", x, 0), ("4111", 0, x)],
    "ecart_passif": lambda x, b: [("4011", x, 0), ("4791", 0, x)],
    "charge_hao": lambda x, b: [("831", x, 0), (b, 0, x)],
    "produit_hao": lambda x, b: [(b, x, 0), ("841", 0, x)],
    "liquidation_tva": lambda x, b: [("4431", x, 0), ("4441", 0, x)],
    "salaires": lambda x, b: [("6611", x, 0), ("422", 0, x)],
    "paiement_salaires": lambda x, b: [("422", x, 0), (b, 0, x)],
    "charges_sociales": lambda x, b: [("664", x, 0), ("431", 0, x)],
    "pret_accorde": lambda x, b: [("2711", x, 0), (b, 0, x)],
    "pret_rembourse": lambda x, b: [(b, x, 0), ("2711", 0, x)],
    "cession_titres": lambda x, b: [("816", x, 0), ("261", 0, x), (b, x + 1000, 0), ("826", 0, x + 1000)],
    "titres_achetes": lambda x, b: [("261", x, 0), (b, 0, x)],
    "prelevement": lambda x, b: [("1048", x, 0), (b, 0, x)],
    "avance_fournisseur": lambda x, b: [("4091", x, 0), (b, 0, x)],
    "avance_client": lambda x, b: [(b, x, 0), ("4191", 0, x)],
    "virement_caisse": lambda x, b: [("585", x, 0), ("5711", 0, x)],
    "virement_banque": lambda x, b: [(b, x, 0), ("585", 0, x)],
    "decouvert": lambda x, b: [("6011", 3 * x, 0), (b, 0, 3 * x)],
}


@tagged("post_install", "-at_install", "aite_syscohada")
class TestTftProperties(SyscohadaCommon):
    """Propriétés vérifiées sur des centaines d'écritures aléatoires :
    bilan équilibré, résultat cohérent, TFT égal à la variation de trésorerie du bilan."""

    def random_entries(self, seed, count, year):
        rng = random.Random(seed)
        names = sorted(TEMPLATES)
        start = date(year, 1, 1)
        for _i in range(count):
            name = rng.choice(names)
            amount = rng.randrange(1000, 3000000, 500)
            day = start + timedelta(days=rng.randrange(0, 365))
            self.entry(day, TEMPLATES[name](amount, self.bank), name)

    def assert_properties(self, date_from, date_to, label):
        res = self.compute(date_from, date_to)
        a, p, r, f = res["actif"], res["passif"], res["resultat"], res["flux"]
        self.assertEqual(a["BZ"]["net"], p["DZ"], f"{label} : bilan déséquilibré")
        prior = self.checker._prior_results(self.company, __import__("odoo").fields.Date.to_date(date_from),
                                            __import__("odoo").fields.Date.to_date(date_to))
        self.assertAlmostEqual(p["CJ"] - prior, r["XI"], places=2, msg=f"{label} : XI ≠ CJ − antérieurs")
        self.assertAlmostEqual(f["ZH"], a["BT"]["net"] - p["DT"], places=2, msg=f"{label} : TFT ≠ trésorerie du bilan")
        self.assertAlmostEqual(f["ZG"], f["ZB"] + f["ZC"] + f["ZF"], places=2)
        return res

    def test_random_ledgers(self):
        for seed in (7, 2024, 31337):
            with self.subTest(seed=seed):
                self.random_entries(seed, 60, 2025)
                self.random_entries(seed + 1, 60, 2026)
                self.assert_properties("2025-01-01", "2025-12-31", f"graine {seed} N-1")
                self.assert_properties("2026-01-01", "2026-12-31", f"graine {seed} N")
                self.assert_properties("2026-04-01", "2026-09-30", f"graine {seed} période partielle")

    def test_every_template_alone(self):
        """Chaque gabarit, isolé, laisse le TFT égal à la variation de trésorerie."""
        year = 2030
        for name, template in sorted(TEMPLATES.items()):
            with self.subTest(template=name):
                self.entry(f"{year}-06-15", template(100000, self.bank), name)
                self.assert_properties(f"{year}-01-01", f"{year}-12-31", name)
                year += 1
