# -*- coding: utf-8 -*-
from odoo import models


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    def _load(self, template_code, company, install_demo, force_create=True):
        res = super()._load(template_code, company, install_demo, force_create=force_create)
        company = company or self.env.company
        if company._aite_is_syscohada():
            company._aite_syscohada_setup()
        return res
