# -*- coding: utf-8 -*-
"""Contrôles de cohérence SYSCOHADA (rattachement des comptes, équilibres, comptes d'attente, caisse, TFT)."""
from datetime import timedelta

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero

PL_CLASSES = ("6", "7", "8")


class AiteSyscohadaCheck(models.AbstractModel):
    _name = "aite.syscohada.check"
    _description = "Contrôles SYSCOHADA"

    # ------------------------------------------------------------------ rattachement (statique)
    @api.model
    def _mapping_terms(self):
        engine = self.env["aite.syscohada.engine"]
        Rub = self.env["aite.syscohada.rubrique"]
        bilan, resultat = [], []
        for rub in Rub.search([("statement", "=", "actif"), ("line_type", "=", "detail")]):
            for formula in (rub.formula_brut, rub.formula_amort):
                if formula:
                    bilan += [(rub.code, t) for t in engine._parse_account_formula(formula)]
        for rub in Rub.search([("statement", "=", "passif"), ("line_type", "=", "detail")]):
            bilan += [(rub.code, t) for t in engine._parse_account_formula(rub.formula)]
        for rub in Rub.search([("statement", "=", "resultat"), ("line_type", "=", "detail")]):
            resultat += [(rub.code, t) for t in engine._parse_account_formula(rub.formula)]
        return bilan, resultat

    @api.model
    def coverage(self, company, accounts=None):
        """Pour chaque compte : rubriques de bilan captant un solde débiteur, un solde créditeur,
        et rubriques du compte de résultat. Retourne la liste des anomalies."""
        bilan, resultat = self._mapping_terms()
        if accounts is None:
            Account = self.env["account.account"].with_company(company)
            accounts = Account.search([("company_ids", "in", company.id), ("account_type", "!=", "off_balance"),
                                       ("deprecated", "=", False)])
            moved = self._accounts_with_lines(company, None)
            accounts |= Account.browse(moved).filtered(lambda a: a.account_type != "off_balance")
        problems = []
        for account in accounts.with_company(company):
            code = account.code
            debit_hits = sorted({rub for rub, t in bilan if t.matches(code) and t.balance_character in ("", "D")})
            credit_hits = sorted({rub for rub, t in bilan if t.matches(code) and t.balance_character in ("", "C")})
            debit_count = sum(1 for _rub, t in bilan if t.matches(code) and t.balance_character in ("", "D"))
            credit_count = sum(1 for _rub, t in bilan if t.matches(code) and t.balance_character in ("", "C"))
            cr_count = sum(1 for _rub, t in resultat if t.matches(code))
            is_pl = code.startswith(PL_CLASSES)
            issue = []
            if debit_count != 1:
                issue.append(f"solde débiteur capté {debit_count} fois {debit_hits}")
            if credit_count != 1:
                issue.append(f"solde créditeur capté {credit_count} fois {credit_hits}")
            if is_pl and cr_count != 1:
                issue.append(f"compte de résultat : capté {cr_count} fois")
            if not is_pl and cr_count:
                issue.append("compte de bilan capté par le compte de résultat")
            if issue:
                problems.append({"account": account, "code": code, "message": " ; ".join(issue)})
        return problems

    # ------------------------------------------------------------------ contrôles d'une période
    @api.model
    def run(self, company, date_from, date_to, results=None):
        date_from, date_to = fields.Date.to_date(date_from), fields.Date.to_date(date_to)
        engine = self.env["aite.syscohada.engine"]
        digits = company.currency_id.decimal_places
        res = results or engine.compute(company, date_from, date_to)
        checks = []

        def add(code, name, level, message):
            checks.append({"code": code, "name": name, "level": level, "message": message})

        def amount(v):
            return f"{v:,.{digits}f}".replace(",", " ")

        # 1. Rattachement des comptes
        problems = self.coverage(company)
        moved = self._accounts_with_lines(company, date_to)
        blocking = [p for p in problems if p["account"].id in moved]
        if blocking:
            add("RATTACHEMENT", "Comptes mouvementés non rattachés", "error",
                "; ".join(f"{p['code']} ({p['message']})" for p in blocking[:20]))
        elif problems:
            add("RATTACHEMENT", "Comptes non rattachés (sans mouvement)", "warning",
                "; ".join(p["code"] for p in problems[:30]))
        else:
            add("RATTACHEMENT", "Rattachement des comptes", "ok", "Tous les comptes sont rattachés une seule fois.")

        # 2. Pièces en brouillon
        drafts = self.env["account.move"].search_count([("company_id", "=", company.id), ("state", "=", "draft"),
                                                        ("date", ">=", date_from), ("date", "<=", date_to)])
        add("BROUILLONS", "Pièces non validées sur la période", "warning" if drafts else "ok",
            f"{drafts} pièce(s) en brouillon." if drafts else "Aucune pièce en brouillon.")

        # 3. Équilibre du bilan
        bz, dz = res["actif"]["BZ"]["net"], res["passif"]["DZ"]
        add("EQUILIBRE", "Total actif = total passif (BZ = DZ)",
            "ok" if float_is_zero(bz - dz, precision_digits=digits) else "error",
            f"BZ {amount(bz)} ; DZ {amount(dz)} ; écart {amount(bz - dz)}")

        # 4. Résultat
        prior = self._prior_results(company, date_from, date_to)
        xi, cj = res["resultat"]["XI"], res["passif"]["CJ"]
        ok = float_is_zero(cj - prior - xi, precision_digits=digits)
        add("RESULTAT", "Résultat net : XI = CJ hors résultats antérieurs non affectés", "ok" if ok else "error",
            f"XI {amount(xi)} ; CJ {amount(cj)} ; résultats antérieurs non affectés {amount(prior)}")
        if ok and not float_is_zero(prior, precision_digits=digits):
            add("AFFECTATION", "Résultats antérieurs à affecter", "warning",
                f"{amount(prior)} figurent encore en CJ : passer l'écriture d'affectation (compte 13 puis 11, 12, 465).")

        # 5. Comptes d'attente et de virements internes
        end = engine._balances(company, date_to=date_to)
        waiting = {code: bal for code, bal in end.items()
                   if code.startswith(("471", "585", "588")) and not float_is_zero(bal, precision_digits=digits)}
        for account in (company.account_journal_suspense_account_id | company.transfer_account_id):
            bal = end.get(account.with_company(company).code, 0.0)
            if not float_is_zero(bal, precision_digits=digits):
                waiting[account.with_company(company).code] = bal
        add("ATTENTE", "Comptes d'attente et de virements internes soldés", "warning" if waiting else "ok",
            "; ".join(f"{c} : {amount(b)}" for c, b in sorted(waiting.items())) or "Tous soldés.")

        # 6. Caisses créditrices
        cash = {code: bal for code, bal in end.items() if code.startswith("57") and bal < 0
                and not float_is_zero(bal, precision_digits=digits)}
        add("CAISSE", "Aucune caisse créditrice", "error" if cash else "ok",
            "; ".join(f"{c} : {amount(b)}" for c, b in sorted(cash.items())) or "Aucune caisse créditrice.")

        # 7. Tableau des flux : ZH = trésorerie nette du bilan
        if "flux" in res:
            zh = res["flux"]["ZH"]
            tn = res["actif"]["BT"]["net"] - res["passif"]["DT"]
            add("TFT", "Trésorerie de clôture du TFT (ZH) = BT − DT",
                "ok" if float_is_zero(zh - tn, precision_digits=digits) else "error",
                f"ZH {amount(zh)} ; BT − DT {amount(tn)} ; écart {amount(zh - tn)}")

        # 8. Paiements fournisseurs en espèces au-delà de 100 000 FCFA (TVA non déductible)
        payments = self.env["account.payment"].search([
            ("company_id", "=", company.id), ("state", "not in", ("draft", "canceled")),
            ("payment_type", "=", "outbound"), ("partner_type", "=", "supplier"),
            ("journal_id.type", "=", "cash"), ("date", ">=", date_from), ("date", "<=", date_to)])
        big = payments.filtered(lambda p: float_compare(p.amount, 100000, precision_digits=digits) > 0)
        add("ESPECES", "Paiements fournisseurs en espèces > 100 000 FCFA", "warning" if big else "ok",
            "; ".join(f"{p.name} {p.partner_id.name} {amount(p.amount)}" for p in big[:20])
            or "Aucun : la TVA des factures réglées reste déductible.")

        # 9. Bascules (information)
        flips = []
        for code, bal in end.items():
            if code.startswith("40") and not code.startswith("409") and bal > 0:
                flips.append(f"{code} débiteur")
            elif code.startswith("41") and not code.startswith("419") and bal < 0:
                flips.append(f"{code} créditeur")
            elif code.startswith(("52", "53")) and bal < 0:
                flips.append(f"{code} à découvert")
        add("BASCULES", "Comptes reclassés selon le sens du solde", "info" if flips else "ok",
            "; ".join(flips) or "Aucun.")
        return checks

    def _accounts_with_lines(self, company, date_to):
        domain = [("company_id", "=", company.id), ("parent_state", "=", "posted"), ("account_id", "!=", False)]
        if date_to:
            domain.append(("date", "<=", date_to))
        groups = self.env["account.move.line"].sudo()._read_group(domain, ["account_id"], ["__count"])
        return {account.id for account, _count in groups}

    def _prior_results(self, company, date_from, date_to):
        """Résultats non encore affectés au début de la période : comptes 13, 999999 et résultats antérieurs."""
        engine = self.env["aite.syscohada.engine"]
        end = engine._balances(company, date_to=date_to)
        before = engine._balances(company, date_to=date_from - timedelta(days=1))
        total = sum(bal for code, bal in end.items() if code.startswith(("13", "999999")))
        total += sum(bal for code, bal in before.items() if code.startswith(PL_CLASSES))
        return -total
