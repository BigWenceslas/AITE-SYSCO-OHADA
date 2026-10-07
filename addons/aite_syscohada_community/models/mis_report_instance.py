# -*- coding: utf-8 -*-
from odoo import Command, api, models

LABELS = {
    "actif": "Bilan actif", "passif": "Bilan passif",
    "resultat": "Compte de résultat", "flux": "Tableau des flux de trésorerie",
}


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    @api.model
    def _aite_syscohada_instance(self, statement, company=None):
        """Instance MIS de la société, colonnes « Exercice N » et « Exercice N-1 » (années civiles glissantes)."""
        company = company or self.env.company
        report = self.env.ref(f"aite_syscohada_mis.report_{statement}")
        instance = self.search([("report_id", "=", report.id), ("company_id", "=", company.id),
                                ("name", "=", f"SYSCOHADA – {LABELS[statement]}")], limit=1)
        if not instance:
            instance = self.create({
                "name": f"SYSCOHADA – {LABELS[statement]}", "report_id": report.id, "company_id": company.id,
                "period_ids": [
                    Command.create({"name": "Exercice N", "mode": "relative", "type": "y", "offset": 0, "duration": 1, "sequence": 1}),
                    Command.create({"name": "Exercice N-1", "mode": "relative", "type": "y", "offset": -1, "duration": 1, "sequence": 2}),
                ],
            })
        return instance

    @api.model
    def _aite_syscohada_open(self, statement):
        """Aperçu de l'état. Le widget de MIS Builder 18 lit l'instance dans ``active_id`` du contexte (le bouton
        « Aperçu » de la liste l'y met) : une action de menu doit l'y mettre aussi, sinon l'écran plante."""
        instance = self._aite_syscohada_instance(statement)
        return instance.with_context(
            active_model=instance._name, active_id=instance.id, active_ids=instance.ids).preview()
