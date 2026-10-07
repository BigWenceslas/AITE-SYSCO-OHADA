# -*- coding: utf-8 -*-
from odoo.tests import tagged

from odoo.addons.aite_syscohada_base.tests.common import SyscohadaCommon


@tagged("post_install", "-at_install", "aite_syscohada")
class TestMisMenus(SyscohadaCommon):
    """États en un clic : instance MIS par société, colonnes N et N-1, rouverte à l'identique."""

    def test_open_statements(self):
        Instance = self.env["mis.report.instance"].with_company(self.company)
        for statement in ("actif", "passif", "resultat", "flux"):
            action = Instance._aite_syscohada_open(statement)
            self.assertEqual(action["res_model"], "mis.report.instance")
            instance = Instance.browse(action["res_id"])
            self.assertEqual(instance.company_id, self.company)
            self.assertEqual(instance.period_ids.mapped("name"), ["Exercice N", "Exercice N-1"])
            # le widget MIS retrouve l'instance par le contexte (sans quoi : « Invalid ids list » à l'écran)
            self.assertEqual(action["context"]["active_model"], "mis.report.instance")
            self.assertEqual(action["context"]["active_id"], instance.id)
            self.assertEqual(Instance._aite_syscohada_open(statement)["res_id"], instance.id)
            matrix = instance._compute_matrix()
            self.assertTrue(list(matrix.iter_rows()))

    def test_server_actions_and_menus(self):
        for statement in ("actif", "passif", "resultat", "flux"):
            self.assertTrue(self.env.ref(f"aite_syscohada_community.menu_open_{statement}"))
            action = self.env.ref(f"aite_syscohada_community.action_open_{statement}").with_company(self.company).run()
            self.assertEqual(action["res_model"], "mis.report.instance")
            self.assertEqual(action["context"]["active_id"], action["res_id"])
