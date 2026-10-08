# -*- coding: utf-8 -*-
from odoo import Command
from odoo.addons.base.models.res_users import name_boolean_group
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "aite_syscohada")
class TestUserRights(TransactionCase):
    """Droit « Montrer les fonctions de comptabilité complètes » : case de la section Technique de la fiche
    utilisateur, que le module account masque en Community."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.full = cls.env.ref("account.group_account_user")
        cls.readonly = cls.env.ref("account.group_account_readonly")
        cls.basic = cls.env.ref("account.group_account_basic")

    def setUp(self):
        super().setUp()
        if self.full.category_id != self.env.ref("base.module_category_hidden"):
            self.skipTest("groupe hors de la catégorie technique (Enterprise) : Odoo affiche déjà la case")

    def test_checkbox_in_technical_section(self):
        groups = self.env["res.groups"].get_application_groups([])
        self.assertIn(self.full, groups, "la case doit figurer dans la fiche utilisateur")
        self.assertNotIn(self.readonly, groups, "le droit lecture seule reste masqué, comme dans Odoo")
        self.assertNotIn(self.basic, groups, "le droit Basique reste masqué, comme dans Odoo")
        hidden = self.env.ref("base.module_category_hidden")
        technical = [gs for app, kind, gs, _name in self.env["res.groups"].get_groups_by_application() if app == hidden]
        self.assertEqual(len(technical), 1)
        self.assertIn(self.full, technical[0], "rangée dans la section Technique")
        # vue générée de la fiche : régénérée à chaque mise à jour de module
        self.env["res.groups"]._update_user_groups_view()
        field = name_boolean_group(self.full.id)
        self.assertIn(f'name="{field}"', self.env.ref("base.user_groups_view").arch)
        self.assertIn(field, self.env["res.users"].fields_get([field]))

    def test_checkbox_shows_accounting_menus(self):
        """Profil de la recette : Facturation « Administrateur » sans le droit complet. Menus de Facturation
        masqués (Tableau de bord, Comptabilité, Syscohada) jusqu'à ce que la case soit cochée."""
        user = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Comptable AITE", "login": "aite_comptable_droits",
            "groups_id": [Command.set([self.env.ref("base.group_user").id,
                                       self.env.ref("account.group_account_manager").id])],
        })
        menus = {xmlid: self.env.ref(xmlid).id for xmlid in (
            "account.menu_board_journal_1",  # Tableau de bord
            "account.menu_finance_entries",  # Comptabilité
            "aite_syscohada_base.menu_aite_syscohada_statements",  # États et contrôles (AITE)
        )}

        def visible():
            self.env.invalidate_all()
            self.env.registry.clear_cache()
            ids = self.env["ir.ui.menu"].with_user(user)._visible_menu_ids()
            return {xmlid for xmlid, menu_id in menus.items() if menu_id in ids}

        self.assertEqual(visible(), set())
        user.write({name_boolean_group(self.full.id): True})
        self.assertTrue(user.has_group("account.group_account_readonly"))
        self.assertTrue(user.has_group("account.group_account_basic"))
        self.assertEqual(visible(), set(menus))
