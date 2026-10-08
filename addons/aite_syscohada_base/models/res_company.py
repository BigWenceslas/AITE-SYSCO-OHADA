# -*- coding: utf-8 -*-
import logging

from odoo import Command, _, api, fields, models

_logger = logging.getLogger(__name__)

# Libellés français corrigés (code du modèle SYSCOHADA d'Odoo -> libellé)
ACCOUNT_LABELS = {
    "109": "Apporteurs, capital souscrit, non appelé",
    "121": "Report à nouveau créditeur",
    "129": "Report à nouveau débiteur",
    "1301": "Résultat en instance d'affectation : bénéfice",
    "1309": "Résultat en instance d'affectation : perte",
    "131": "Résultat net : bénéfice",
    "139": "Résultat net : perte",
    "162": "Emprunts et dettes auprès des établissements de crédit",
    "2441": "Matériel de bureau",
    "4011": "Fournisseurs",
    "4081": "Fournisseurs, factures non parvenues",
    "4091": "Fournisseurs, avances et acomptes versés",
    "4094": "Fournisseurs, créances pour emballages et matériels à rendre",
    "4098": "Fournisseurs, rabais, remises, ristournes et autres avoirs à obtenir",
    "4111": "Clients",
    "4113": "Clients, point de vente",
    "4181": "Clients, factures à établir",
    "4191": "Clients, avances et acomptes reçus",
    "4194": "Clients, dettes pour emballages et matériels consignés",
    "422": "Personnel, rémunérations dues",
    "4281": "Dettes provisionnées pour congés à payer",
    "4421": "État, impôts et taxes d'État",
    "4422": "État, impôts et taxes pour les collectivités publiques",
    "4431": "État, TVA facturée sur ventes",
    "4432": "État, TVA facturée sur prestations de services",
    "4435": "État, TVA sur factures à établir",
    "4441": "État, TVA due",
    "4449": "État, crédit de TVA à reporter",
    "4451": "État, TVA récupérable sur immobilisations",
    "4452": "État, TVA récupérable sur achats",
    "4454": "État, TVA récupérable sur services extérieurs et autres charges",
    "4455": "État, TVA récupérable sur factures non parvenues",
    "4471": "État, impôt général sur le revenu retenu à la source",
    "4472": "État, impôts sur salaires retenus à la source",
    "4492": "État, avances et acomptes versés sur impôts",
    "465": "Associés, dividendes à payer",
    "476": "Charges constatées d'avance",
    "477": "Produits constatés d'avance",
    "4811": "Fournisseurs d'investissements, immobilisations incorporelles",
    "4812": "Fournisseurs d'investissements, immobilisations corporelles",
    "552": "Monnaie électronique, téléphone portable",
    "585": "Virements de fonds",
    "6019": "Rabais, remises et ristournes obtenus (non ventilés)",
    "6613": "Congés payés",
    "7019": "Rabais, remises et ristournes accordés (non ventilés)",
}

# (préfixe, type Odoo, lettrable ou None) : types cohérents avec le sens du solde
ACCOUNT_TYPES = [
    ("4451", "asset_current", None), ("4452", "asset_current", None), ("4453", "asset_current", None),
    ("4454", "asset_current", None), ("4455", "asset_current", None), ("4456", "asset_current", None),
    ("4492", "asset_current", None), ("4493", "asset_current", None), ("4494", "asset_current", None),
    ("4495", "asset_current", None), ("4496", "asset_current", None),
    ("4811", "liability_payable", True), ("4812", "liability_payable", True),
]
NON_CURRENT_PREFIXES = ("16", "17")
NON_CURRENT_EXCLUDED = ("166", "176")

# Sous-comptes créés par société : code, libellé, type, lettrable
SUB_ACCOUNTS = [
    ("281810", "Amortissements des frais de prospection et d'évaluation de ressources minérales", "asset_fixed", False),
    ("291810", "Dépréciations des frais de prospection et d'évaluation de ressources minérales", "asset_fixed", False),
    ("291910", "Dépréciations des frais de développement en cours", "asset_fixed", False),
    ("291930", "Dépréciations des logiciels et sites internet en cours", "asset_fixed", False),
    ("293910", "Dépréciations des bâtiments en cours", "asset_fixed", False),
    ("293930", "Dépréciations des ouvrages d'infrastructure en cours", "asset_fixed", False),
    ("294950", "Dépréciations du matériel de transport en cours", "asset_fixed", False),
    ("443800", "État, TVA facturée sur prestations non encore exigible", "liability_current", True),
    ("552100", "Monnaie électronique, Orange Money", "asset_cash", False),
    ("552200", "Monnaie électronique, MTN Mobile Money", "asset_cash", False),
    # Lot 2 : un compte par ligne de la déclaration mensuelle I/TVA-IR
    ("441100", "État, acomptes d'impôt sur le résultat à payer", "liability_current", False),
    ("447110", "État, IRCM retenu à la source", "liability_current", False),
    ("447120", "État, taxe spéciale sur le revenu retenue (TSR)", "liability_current", False),
    ("447130", "État, précomptes retenus sur loyers", "liability_current", False),
    ("447140", "État, retenues sur rémunérations et honoraires", "liability_current", False),
    ("447150", "État, IRNC retenu à la source", "liability_current", False),
    ("447160", "État, TVA retenue à la source", "liability_current", False),
    ("447161", "État, TVA autoliquidée sur prestations étrangères", "liability_current", False),
    ("447170", "État, acomptes sur chiffre d'affaires retenus à la source", "liability_current", False),
    ("447180", "État, précomptes sur achats retenus", "liability_current", False),
    ("447210", "État, IRPP retenu sur salaires", "liability_current", False),
    ("447215", "État, centimes additionnels communaux sur IRPP", "liability_current", False),
    ("447220", "État, Crédit foncier du Cameroun, part salariale", "liability_current", False),
    ("447230", "État, Crédit foncier du Cameroun, part patronale", "liability_current", False),
    ("447240", "État, Fonds national de l'emploi", "liability_current", False),
    ("447250", "État, redevance audiovisuelle", "liability_current", False),
    ("447260", "État, taxe de développement local", "liability_current", False),
    ("449210", "État, précomptes sur achats subis", "asset_current", False),
    ("449220", "État, acomptes sur chiffre d'affaires retenus par les clients", "asset_current", False),
    ("449230", "État, précomptes sur loyers subis", "asset_current", False),
    ("449240", "État, retenues sur honoraires subies", "asset_current", False),
    ("449250", "État, acomptes d'impôt sur le résultat versés", "asset_current", False),
]

# Taxes de retenue à la source (lot 2) : clé, libellé, usage, taux, compte, étiquette de facture, étiquette d'avoir
WITHHOLDING_TAXES = [
    ("retenue_loyers", "Précompte sur loyers retenu (taux à valider)", "purchase", -15.0, "447130"),
    ("retenue_honoraires", "Retenue sur honoraires (taux à valider)", "purchase", -5.0, "447140"),
    ("retenue_tsr", "TSR sur rémunérations versées à l'étranger (taux à valider)", "purchase", -15.0, "447120"),
    ("retenue_tva", "TVA retenue à la source, entreprise habilitée (taux à valider)", "purchase", -19.25, "447160"),
    ("retenue_acompte_ca", "Acompte sur CA retenu à la source (taux à valider)", "purchase", -2.0, "447170"),
    ("subie_acompte_ca", "Acompte sur CA retenu par le client (taux à valider)", "sale", -2.0, "449220"),
    ("subie_loyers", "Précompte sur loyers retenu par le locataire (taux à valider)", "sale", -15.0, "449230"),
    ("subie_honoraires", "Retenue sur honoraires subie (taux à valider)", "sale", -5.0, "449240"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    aite_syscohada_setup_date = fields.Datetime("Paramétrage SYSCOHADA AITE appliqué le", readonly=True, copy=False)

    # ------------------------------------------------------------------ outils
    def _aite_is_syscohada(self):
        self.ensure_one()
        if not self.chart_template:
            return False
        if self.chart_template in ("cm", "syscohada"):
            return True
        mapping = self.env["account.chart.template"]._get_chart_template_mapping()
        return mapping.get(self.chart_template, {}).get("parent") == "syscohada"

    def _aite_account(self, code):
        """Compte de la société dont le code commence par ``code`` complété à 6 chiffres."""
        self.ensure_one()
        full = code.ljust(6, "0")
        return self.env["account.account"].with_company(self).search(
            [("code", "=", full), ("company_ids", "in", self.id)], limit=1)

    def _aite_accounts_prefix(self, prefix):
        self.ensure_one()
        return self.env["account.account"].with_company(self).search(
            [("code", "=like", f"{prefix}%"), ("company_ids", "in", self.id)])

    def _aite_has_posted_lines(self, accounts):
        return bool(self.env["account.move.line"].sudo().search_count(
            [("account_id", "in", accounts.ids), ("company_id", "=", self.id), ("parent_state", "=", "posted")], limit=1))

    # ------------------------------------------------------------------ paramétrage
    def _aite_syscohada_setup(self):
        for company in self:
            if not company._aite_is_syscohada():
                continue
            company = company.with_company(company)
            company._aite_fix_account_labels()
            company._aite_fix_account_types()
            company._aite_create_subaccounts()
            company._aite_fix_cash_difference_accounts()
            if company.chart_template == "cm":
                company._aite_setup_taxes()
            company.aite_syscohada_setup_date = fields.Datetime.now()
        return True

    def action_aite_syscohada_setup(self):
        self._aite_syscohada_setup()
        return {"type": "ir.actions.client", "tag": "display_notification",
                "params": {"title": _("SYSCOHADA"), "message": _("Paramétrage appliqué."), "type": "success"}}

    def _aite_fix_account_labels(self):
        self.ensure_one()
        # langues installées seulement : les paramètres de la comptabilité appellent le paramétrage avec
        # active_test=False, et Odoo refuse d'écrire dans une langue non installée (« Invalid language code »)
        langs = ["en_US"] + [code for code, _name in self.env["res.lang"].get_installed() if code.startswith("fr")]
        for code, label in ACCOUNT_LABELS.items():
            account = self._aite_account(code)
            if not account:
                continue
            for lang in langs:
                if account.with_context(lang=lang).name != label:
                    account.with_context(lang=lang).name = label

    def _aite_fix_account_types(self):
        self.ensure_one()
        for prefix, account_type, reconcile in ACCOUNT_TYPES:
            for account in self._aite_accounts_prefix(prefix):
                vals = {}
                if account.account_type != account_type:
                    vals["account_type"] = account_type
                if reconcile is not None and account.reconcile != reconcile:
                    vals["reconcile"] = reconcile
                self._aite_safe_write(account, vals)
        for prefix in NON_CURRENT_PREFIXES:
            for account in self._aite_accounts_prefix(prefix):
                if account.code.startswith(NON_CURRENT_EXCLUDED) or account.account_type == "liability_non_current":
                    continue
                if account.account_type == "liability_current":
                    self._aite_safe_write(account, {"account_type": "liability_non_current"})

    def _aite_safe_write(self, record, vals):
        if not vals:
            return True
        try:
            with self.env.cr.savepoint():
                record.write(vals)
            return True
        except Exception as e:  # noqa: BLE001 — on journalise et on continue
            _logger.warning("AITE SYSCOHADA : %s %s non modifié (%s)", record._name, record.display_name, e)
            return False

    def _aite_create_subaccounts(self):
        self.ensure_one()
        Account = self.env["account.account"].with_company(self)
        for code, name, account_type, reconcile in SUB_ACCOUNTS:
            if self._aite_account(code):
                continue
            Account.create({"code": code, "name": name, "account_type": account_type,
                            "reconcile": reconcile, "company_ids": [Command.set(self.ids)]})

    def _aite_fix_cash_difference_accounts(self):
        """Écarts de caisse : 658 / 758 au lieu des comptes techniques 999001 / 999002 d'Odoo."""
        self.ensure_one()
        loss = self._aite_accounts_prefix("6588")[:1] or self._aite_accounts_prefix("658")[:1]
        gain = self._aite_accounts_prefix("7588")[:1] or self._aite_accounts_prefix("758")[:1]
        if not (loss and gain):
            return
        self._aite_safe_write(self, {"default_cash_difference_expense_account_id": loss.id,
                                     "default_cash_difference_income_account_id": gain.id})
        journals = self.env["account.journal"].search([("company_id", "=", self.id), ("type", "in", ("cash", "bank"))])
        for journal in journals:
            vals = {}
            if journal.loss_account_id and not journal.loss_account_id.code.startswith("6"):
                vals["loss_account_id"] = loss.id
            if journal.profit_account_id and not journal.profit_account_id.code.startswith("7"):
                vals["profit_account_id"] = gain.id
            self._aite_safe_write(journal, vals)
        technical = self._aite_account("999001") | self._aite_account("999002")
        for account in technical:
            if not self._aite_has_posted_lines(account) and not account.deprecated:
                self._aite_safe_write(account, {"deprecated": True})

    # ------------------------------------------------------------------ taxes (Cameroun)
    def _aite_tax_tags(self, *names):
        country = self.env.ref("base.cm")
        tags = self.env["account.account.tag"].search(
            [("name", "in", list(names)), ("applicability", "=", "taxes"), ("country_id", "=", country.id)])
        return tags

    def _aite_tax_ref(self, key):
        return self.env.ref(f"aite_syscohada_base.{self.id}_{key}", raise_if_not_found=False)

    def _aite_register_tax(self, key, tax):
        self.env["ir.model.data"].create({
            "module": "aite_syscohada_base", "name": f"{self.id}_{key}", "model": tax._name,
            "res_id": tax.id, "noupdate": True})

    def _aite_repartition(self, account, tag_base, tag_tax, refund_tag_base, refund_tag_tax):
        def tags(name):
            return [Command.set(self._aite_tax_tags(name).ids)] if name else []
        return [
            Command.create({"document_type": "invoice", "repartition_type": "base", "tag_ids": tags(tag_base)}),
            Command.create({"document_type": "invoice", "repartition_type": "tax", "account_id": account.id, "tag_ids": tags(tag_tax)}),
            Command.create({"document_type": "refund", "repartition_type": "base", "tag_ids": tags(refund_tag_base)}),
            Command.create({"document_type": "refund", "repartition_type": "tax", "account_id": account.id, "tag_ids": tags(refund_tag_tax)}),
        ]

    def _aite_other_tax_group(self):
        """Groupe de taxes distinct de la TVA : retenues, précomptes, taxe de séjour."""
        group = self.env.ref(f"aite_syscohada_base.{self.id}_tax_group_other", raise_if_not_found=False)
        if not group:
            group = self.env["account.tax.group"].create({
                "name": "Retenues, précomptes et autres taxes", "company_id": self.id,
                "country_id": self.env.ref("base.cm").id, "sequence": 90})
            self.env["ir.model.data"].create({"module": "aite_syscohada_base", "name": f"{self.id}_tax_group_other",
                                              "model": group._name, "res_id": group.id, "noupdate": True})
        return group

    def _aite_setup_taxes(self):
        self.ensure_one()
        chart = self.env["account.chart.template"].with_company(self)
        Tax = self.env["account.tax"].with_company(self)
        group = chart.ref("tax_group_19_25", raise_if_not_found=False)
        acc = self._aite_account
        if not self.tax_exigibility:
            self.tax_exigibility = True
        # 1. TVA collectée sur prestations, exigible à l'encaissement (4432 via compte d'attente 4438)
        if not self._aite_tax_ref("tva_prestations_encaissement") and acc("4432") and acc("4438"):
            tax = Tax.create({
                "name": "19,25 % S (encaissement)",
                "description": "TVA 19,25 % sur prestations de services, exigible à l'encaissement",
                "invoice_label": "TVA 19,25 %",
                "amount": 19.25, "amount_type": "percent", "type_tax_use": "sale",
                "tax_exigibility": "on_payment", "cash_basis_transition_account_id": acc("4438").id,
                "tax_group_id": group.id if group else False, "company_id": self.id,
                "repartition_line_ids": self._aite_repartition(acc("4432"), "+CM_10_base", "+CM_10_tax", "-CM_10_base", "-CM_10_tax"),
            })
            self._aite_register_tax("tva_prestations_encaissement", tax)
        # 2. TVA récupérable sur immobilisations (4451)
        if not self._aite_tax_ref("tva_immobilisations") and acc("4451"):
            tax = Tax.create({
                "name": "19,25 % I", "description": "TVA 19,25 % récupérable sur immobilisations",
                "invoice_label": "TVA 19,25 %",
                "amount": 19.25, "amount_type": "percent", "type_tax_use": "purchase",
                "tax_group_id": group.id if group else False, "company_id": self.id,
                "repartition_line_ids": self._aite_repartition(acc("4451"), None, "+CM_18", None, "-CM_18"),
            })
            self._aite_register_tax("tva_immobilisations", tax)
        # 3. Taxe de séjour (communale), barème à paramétrer : inactive par défaut
        if not self._aite_tax_ref("taxe_sejour") and acc("4422"):
            tax = Tax.create({
                "name": "Taxe de séjour (à paramétrer)",
                "description": "Taxe de séjour collectée pour la commune, montant par nuitée selon le barème",
                "amount": 0.0, "amount_type": "fixed", "type_tax_use": "sale", "active": False,
                "company_id": self.id,
                "repartition_line_ids": self._aite_repartition(acc("4422"), None, None, None, None),
            })
            self._aite_register_tax("taxe_sejour", tax)
        # 4. Précompte sur achats subi : avance d'impôt (449210), taux à valider : inactive par défaut
        if not self._aite_tax_ref("precompte_achats") and acc("449210"):
            tax = Tax.create({
                "name": "Précompte sur achats (taux à valider)",
                "description": "Précompte sur achats facturé par le fournisseur, avance sur l'impôt sur le revenu",
                "amount": 2.0, "amount_type": "percent", "type_tax_use": "purchase", "active": False,
                "company_id": self.id,
                "repartition_line_ids": self._aite_repartition(acc("449210"), None, None, None, None),
            })
            self._aite_register_tax("precompte_achats", tax)
        else:
            tax = self._aite_tax_ref("precompte_achats")
            lines = tax.repartition_line_ids.filtered(lambda l: l.repartition_type == "tax") if tax else False
            if lines and acc("449210") and lines.account_id != acc("449210") and not self.env["account.move.line"].sudo().search_count(
                    [("tax_line_id", "=", tax.id)], limit=1):
                self._aite_safe_write(lines, {"account_id": acc("449210").id})
        # 4 bis. Retenues à la source (lot 2), inactives tant que les taux ne sont pas validés
        other_group = self._aite_other_tax_group()
        for key, name, use, amount, code in WITHHOLDING_TAXES:
            if self._aite_tax_ref(key) or not acc(code):
                continue
            tax = Tax.create({
                "name": name, "amount": amount, "amount_type": "percent", "type_tax_use": use, "active": False,
                "company_id": self.id, "description": name, "tax_group_id": other_group.id,
                "repartition_line_ids": self._aite_repartition(acc(code), None, None, None, None)})
            self._aite_register_tax(key, tax)
        for key in ("taxe_sejour", "precompte_achats"):
            tax = self._aite_tax_ref(key)
            if tax and tax.tax_group_id != other_group:
                self._aite_safe_write(tax, {"tax_group_id": other_group.id})
        # 4 ter. Autoliquidation de la TVA sur prestations étrangères : déductible (L21) et due (L38)
        if not self._aite_tax_ref("autoliquidation_services") and acc("4454") and acc("447161"):
            tags21 = [Command.set(self._aite_tax_tags("+CM_21").ids)]
            tags21r = [Command.set(self._aite_tax_tags("-CM_21").ids)]
            lines = []
            for doc, tags in (("invoice", tags21), ("refund", tags21r)):
                lines += [
                    Command.create({"document_type": doc, "repartition_type": "base"}),
                    Command.create({"document_type": doc, "repartition_type": "tax", "account_id": acc("4454").id,
                                    "factor_percent": 100, "tag_ids": tags}),
                    Command.create({"document_type": doc, "repartition_type": "tax", "account_id": acc("447161").id,
                                    "factor_percent": -100}),
                ]
            tax = Tax.create({
                "name": "TVA 19,25 % autoliquidée, services étrangers (à valider)", "amount": 19.25,
                "amount_type": "percent", "type_tax_use": "purchase", "active": False, "company_id": self.id,
                "tax_group_id": group.id if group else False, "repartition_line_ids": lines})
            self._aite_register_tax("autoliquidation_services", tax)
        # 5. TVA sur services achetés : 4454 au lieu de 4452 (si la taxe n'a encore servi à rien)
        services = chart.ref("tva_purchase_services_19_25", raise_if_not_found=False)
        if services and acc("4454"):
            lines = services.repartition_line_ids.filtered(lambda l: l.repartition_type == "tax")
            if lines.filtered(lambda l: l.account_id != acc("4454")):
                used = self.env["account.move.line"].sudo().search_count(
                    [("tax_line_id", "=", services.id), ("parent_state", "=", "posted")], limit=1)
                if not used:
                    self._aite_safe_write(lines, {"account_id": acc("4454").id})
                else:
                    _logger.warning("AITE SYSCOHADA : taxe %s déjà utilisée, compte 4452 conservé", services.name)
