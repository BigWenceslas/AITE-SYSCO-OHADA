# -*- coding: utf-8 -*-
"""Moteur de calcul des états SYSCOHADA, indépendant de l'édition d'Odoo.

Formules de comptes : syntaxe du moteur « account_codes » d'Odoo Enterprise
    terme = [signe] préfixe [\\(exclusion1,exclusion2)] [D|C]
    D (resp. C) : ne retient que les comptes dont le solde est débiteur (resp. créditeur).
Formules de flux (TFT) : termes signés TYPE:ARGUMENT
    R:XI   rubrique du compte de résultat de la période
    B:BT   rubrique de bilan à la clôture (net pour l'actif)   B0:BT  idem à l'ouverture
    V:BB   variation d'une rubrique de bilan (B - B0)
    P:681  solde de la période (débit - crédit) des comptes      E: / S:  solde de clôture / d'ouverture
    D: / C:   débits / crédits de la période                     DX: / CX:  idem hors virements internes au groupe
    Un argument de comptes peut être une formule entre parenthèses : DX:(21+251).
"""
import re
from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models
from odoo.tools import float_round

ACCOUNT_CODES_SPLIT = re.compile(r"(?=[+-])")
ACCOUNT_CODES_TERM = re.compile(
    r"^(?P<sign>[+-]?)"
    r"(?P<prefix>([A-Za-z\d.]*|tag\([\w.]+\))((?=\\)|(?<=[^CD])))"
    r"(\\\((?P<excluded_prefixes>([A-Za-z\d.]+,)*[A-Za-z\d.]*)\))?"
    r"(?P<balance_character>[DC]?)$"
)
AGGREGATION_TERM = re.compile(r"^(?P<sign>[+-]?)(?P<code>[A-Z][A-Z0-9]{1,3})$")
FLOW_TERM = re.compile(r"^(?P<sign>[+-]?)(?P<kind>B0|DX|CX|R|B|V|P|E|S|D|C):(?P<arg>.+)$")
RUBRIQUE_KINDS = {"R", "B", "B0", "V"}


class AccountTerm:
    __slots__ = ("sign", "prefix", "excluded", "balance_character")

    def __init__(self, sign, prefix, excluded, balance_character):
        self.sign = sign
        self.prefix = prefix
        self.excluded = excluded
        self.balance_character = balance_character

    def matches(self, code):
        return code.startswith(self.prefix) and not any(code.startswith(e) for e in self.excluded)

    def captures(self, code, balance):
        if not self.matches(code):
            return False
        if self.balance_character == "D":
            return balance > 0
        if self.balance_character == "C":
            return balance < 0
        return True

    def __repr__(self):
        return f"AccountTerm({self.sign:+d}, {self.prefix!r}, {self.excluded!r}, {self.balance_character!r})"


def _split_top_level(formula):
    tokens, depth, current = [], 0, ""
    for ch in formula.replace(" ", ""):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("parenthèse fermante en trop")
        if ch in "+-" and depth == 0 and current:
            tokens.append(current)
            current = ch
        else:
            current += ch
    if depth:
        raise ValueError("parenthèse non fermée")
    if current:
        tokens.append(current)
    return tokens


class AiteSyscohadaEngine(models.AbstractModel):
    _name = "aite.syscohada.engine"
    _description = "Moteur de calcul des états SYSCOHADA"

    # ------------------------------------------------------------------ analyse des formules
    @api.model
    def _parse_account_formula(self, formula):
        if not formula or not formula.strip():
            raise ValueError("formule vide")
        terms = []
        for token in ACCOUNT_CODES_SPLIT.split(formula.replace(" ", "")):
            if not token:
                continue
            match = ACCOUNT_CODES_TERM.match(token)
            if not match:
                raise ValueError(f"terme invalide « {token} »")
            prefix = match["prefix"]
            if not prefix or prefix in ("+", "-"):
                raise ValueError(f"préfixe vide dans « {token} »")
            if prefix.startswith("tag("):
                raise ValueError("les étiquettes tag(...) ne sont pas gérées par ce moteur")
            excluded = tuple(e for e in (match["excluded_prefixes"] or "").split(",") if e)
            for e in excluded:
                if not e.startswith(prefix):
                    raise ValueError(f"l'exclusion {e} n'est pas un sous-préfixe de {prefix}")
            terms.append(AccountTerm(-1 if match["sign"] == "-" else 1, prefix, excluded, match["balance_character"] or ""))
        if not terms:
            raise ValueError("formule vide")
        return terms

    @api.model
    def _parse_aggregation(self, formula):
        terms = []
        for token in ACCOUNT_CODES_SPLIT.split(formula.replace(" ", "")):
            if not token:
                continue
            match = AGGREGATION_TERM.match(token)
            if not match:
                raise ValueError(f"terme d'agrégation invalide « {token} »")
            terms.append((-1 if match["sign"] == "-" else 1, match["code"]))
        if not terms:
            raise ValueError("agrégation vide")
        return terms

    @api.model
    def _parse_flow_formula(self, formula):
        terms = []
        for token in _split_top_level(formula):
            match = FLOW_TERM.match(token)
            if not match:
                raise ValueError(f"terme de flux invalide « {token} »")
            sign = -1 if match["sign"] == "-" else 1
            kind, arg = match["kind"], match["arg"]
            if kind in RUBRIQUE_KINDS:
                if not re.match(r"^[A-Z][A-Z0-9]{1,3}$", arg):
                    raise ValueError(f"code de rubrique invalide « {arg} »")
                terms.append((sign, kind, arg, None))
            else:
                inner = arg[1:-1] if arg.startswith("(") and arg.endswith(")") else arg
                account_terms = self._parse_account_formula(inner)
                if any(t.balance_character for t in account_terms):
                    raise ValueError("D/C non autorisé dans un argument de flux")
                terms.append((sign, kind, inner, account_terms))
        if not terms:
            raise ValueError("formule de flux vide")
        return terms

    # ------------------------------------------------------------------ évaluation
    @api.model
    def _eval_account_terms(self, terms, balances):
        """balances : {code: solde}. Retourne la somme signée des comptes capturés."""
        total = 0.0
        for term in terms:
            subtotal = 0.0
            for code, balance in balances.items():
                if term.captures(code, balance):
                    subtotal += balance
            total += term.sign * subtotal
        return total

    @api.model
    def _matching_codes(self, terms, codes):
        return {code for code in codes if any(t.matches(code) for t in terms)}

    # ------------------------------------------------------------------ données
    def _account_codes(self, company):
        accounts = self.env["account.account"].with_company(company).search(
            [("company_ids", "in", company.id)])
        return {account.id: account.code for account in accounts}

    def _aml_domain(self, company, date_to=None, date_from=None):
        domain = [("company_id", "=", company.id), ("parent_state", "=", "posted"), ("account_id", "!=", False)]
        if date_to:
            domain.append(("date", "<=", date_to))
        if date_from:
            domain.append(("date", ">=", date_from))
        return domain

    def _balances(self, company, date_to=None, date_from=None, codes=None):
        codes = codes or self._account_codes(company)
        groups = self.env["account.move.line"].sudo()._read_group(
            self._aml_domain(company, date_to, date_from), ["account_id"], ["balance:sum"])
        result = defaultdict(float)
        for account, balance in groups:
            code = codes.get(account.id)
            if code:
                result[code] += balance
        return dict(result)

    def _debit_credit(self, company, date_from, date_to, codes):
        groups = self.env["account.move.line"].sudo()._read_group(
            self._aml_domain(company, date_to, date_from), ["account_id"], ["debit:sum", "credit:sum"])
        debits, credits = defaultdict(float), defaultdict(float)
        for account, debit, credit in groups:
            code = codes.get(account.id)
            if code:
                debits[code] += debit
                credits[code] += credit
        return dict(debits), dict(credits)

    def _movements_excluding_transfers(self, company, date_from, date_to, codes, terms):
        """Débits et crédits de la période sur un groupe de comptes, hors virements internes au groupe
        (une pièce qui débite et crédite le groupe compte pour le seul excédent)."""
        account_ids = [aid for aid, code in codes.items() if any(t.matches(code) for t in terms)]
        if not account_ids:
            return 0.0, 0.0
        domain = self._aml_domain(company, date_to, date_from) + [("account_id", "in", account_ids)]
        groups = self.env["account.move.line"].sudo()._read_group(domain, ["move_id"], ["debit:sum", "credit:sum"])
        debit_total = credit_total = 0.0
        for _move, debit, credit in groups:
            transfer = min(debit, credit)
            debit_total += debit - transfer
            credit_total += credit - transfer
        return debit_total, credit_total

    # ------------------------------------------------------------------ états
    def _rubriques(self, statement):
        return self.env["aite.syscohada.rubrique"].search([("statement", "=", statement)])

    def _aggregate(self, rubriques, detail_values, value_keys=None):
        """Complète detail_values ({code: valeur ou dict}) avec les sous-totaux et totaux."""
        by_code = {r.code: r for r in rubriques}
        values = dict(detail_values)
        visiting = set()

        def resolve(code):
            if code in values:
                return values[code]
            if code in visiting:
                raise ValueError(f"référence circulaire sur {code}")
            rub = by_code.get(code)
            if not rub or not rub.aggregation:
                raise ValueError(f"rubrique inconnue ou sans agrégation : {code}")
            visiting.add(code)
            terms = self._parse_aggregation(rub.aggregation)
            if value_keys:
                total = {k: 0.0 for k in value_keys}
                for sign, sub in terms:
                    sub_val = resolve(sub)
                    for k in value_keys:
                        total[k] += sign * sub_val[k]
            else:
                total = sum(sign * resolve(sub) for sign, sub in terms)
            visiting.discard(code)
            values[code] = total
            return total

        for rub in rubriques:
            resolve(rub.code)
        return values

    def _compute_actif(self, balances):
        rubriques = self._rubriques("actif")
        details = {}
        for rub in rubriques.filtered(lambda r: r.line_type == "detail"):
            brut = self._eval_account_terms(self._parse_account_formula(rub.formula_brut), balances) if rub.formula_brut else 0.0
            amort = -self._eval_account_terms(self._parse_account_formula(rub.formula_amort), balances) if rub.formula_amort else 0.0
            details[rub.code] = {"brut": brut, "amort": amort, "net": brut - amort}
        return self._aggregate(rubriques, details, value_keys=("brut", "amort", "net"))

    def _compute_simple(self, statement, balances):
        rubriques = self._rubriques(statement)
        details = {}
        for rub in rubriques.filtered(lambda r: r.line_type == "detail"):
            details[rub.code] = self._eval_account_terms(self._parse_account_formula(rub.formula), balances)
        return self._aggregate(rubriques, details)

    def _bilan_values(self, actif, passif):
        values = {code: v["net"] for code, v in actif.items()}
        values.update(passif)
        return values

    def _compute_flux(self, company, date_from, date_to, ctx):
        rubriques = self._rubriques("flux")
        codes = ctx["codes"]
        cache = {}
        details = {}
        for rub in rubriques.filtered(lambda r: r.line_type == "detail"):
            total = 0.0
            for sign, kind, arg, account_terms in self._parse_flow_formula(rub.formula):
                if kind == "R":
                    value = ctx["resultat"][arg]
                elif kind == "B":
                    value = ctx["bilan_end"][arg]
                elif kind == "B0":
                    value = ctx["bilan_start"][arg]
                elif kind == "V":
                    value = ctx["bilan_end"][arg] - ctx["bilan_start"][arg]
                elif kind == "P":
                    value = self._eval_account_terms(account_terms, ctx["period"])
                elif kind == "E":
                    value = self._eval_account_terms(account_terms, ctx["end"])
                elif kind == "S":
                    value = self._eval_account_terms(account_terms, ctx["start"])
                elif kind == "D":
                    value = self._eval_account_terms(account_terms, ctx["debits"])
                elif kind == "C":
                    value = self._eval_account_terms(account_terms, ctx["credits"])
                else:  # DX / CX
                    if arg not in cache:
                        cache[arg] = self._movements_excluding_transfers(company, date_from, date_to, codes, account_terms)
                    value = cache[arg][0] if kind == "DX" else cache[arg][1]
                total += sign * value
            details[rub.code] = total
        return self._aggregate(rubriques, details)

    @api.model
    def compute(self, company, date_from, date_to, statements=("actif", "passif", "resultat", "flux")):
        """Calcule les états SYSCOHADA d'une société.

        Bilan : soldes cumulés au ``date_to``. Compte de résultat et flux : période [date_from, date_to].
        Retourne {'actif': {code: {'brut','amort','net'}}, 'passif': {code: montant},
                  'resultat': {code: montant}, 'flux': {code: montant}}.
        """
        date_from, date_to = fields.Date.to_date(date_from), fields.Date.to_date(date_to)
        codes = self._account_codes(company)
        result = {}
        end = self._balances(company, date_to=date_to, codes=codes)
        if {"actif", "passif", "flux"} & set(statements):
            result["actif"] = self._compute_actif(end)
            result["passif"] = self._compute_simple("passif", end)
        period = self._balances(company, date_to=date_to, date_from=date_from, codes=codes)
        if {"resultat", "flux"} & set(statements):
            result["resultat"] = self._compute_simple("resultat", period)
        if "flux" in statements:
            start = self._balances(company, date_to=date_from - timedelta(days=1), codes=codes)
            actif0, passif0 = self._compute_actif(start), self._compute_simple("passif", start)
            debits, credits = self._debit_credit(company, date_from, date_to, codes)
            ctx = {
                "codes": codes, "resultat": result["resultat"],
                "bilan_end": self._bilan_values(result["actif"], result["passif"]),
                "bilan_start": self._bilan_values(actif0, passif0),
                "period": period, "end": end, "start": start, "debits": debits, "credits": credits,
            }
            result["flux"] = self._compute_flux(company, date_from, date_to, ctx)
        rounding = company.currency_id.decimal_places
        return self._round(result, rounding, statements)

    def _round(self, result, digits, statements):
        out = {}
        for statement, values in result.items():
            if statement not in statements:
                continue
            out[statement] = {
                code: ({k: float_round(v, precision_digits=digits) for k, v in val.items()} if isinstance(val, dict)
                       else float_round(val, precision_digits=digits))
                for code, val in values.items()
            }
        return out
