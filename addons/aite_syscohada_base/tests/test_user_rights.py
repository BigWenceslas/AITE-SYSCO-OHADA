# -*- coding: utf-8 -*-
from odoo import Command
from odoo.addons.base.models.res_users import name_boolean_group
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "aite_syscohada")
class TestUserRights(TransactionCase):
    """Droit « Montrer les fonctions de comptabilité complètes » : case de la section Technique de la fiche
    utilisateur, que le module account masque en Community, et qui, décochée, retire les droits qu'elle a donnés."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.full = cls.env.ref("account.group_account_user")
        cls.readonly = cls.env.ref("account.group_account_readonly")
        cls.basic = cls.env.ref("account.group_account_basic")
        cls.field = name_boolean_group(cls.full.id)
        cls.menus = {xmlid: cls.env.ref(xmlid).id for xmlid in (
            "account.menu_board_journal_1",  # Tableau de bord : account.group_account_basic
            "account.menu_finance_entries",  # Comptabilité : account.group_account_readonly
            "aite_syscohada_base.menu_aite_syscohada_statements",  # États et contrôles (AITE) : lecture seule
        )}

    def setUp(self):
        super().setUp()
        if self.full.category_id != self.env.ref("base.module_category_hidden"):
            self.skipTest("groupe hors de la catégorie technique (Enterprise) : Odoo affiche déjà la case")

    def _accountant(self, extra_groups=None):
        """Profil de la recette : Facturation « Administrateur » sans le droit complet."""
        return self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Comptable AITE", "login": "aite_comptable_droits",
            "groups_id": [Command.set([self.env.ref("base.group_user").id,
                                       self.env.ref("account.group_account_manager").id]
                                      + [g.id for g in (extra_groups or [])])],
        })

    def _visible(self, user):
        self.env.invalidate_all()
        self.env.registry.clear_cache()
        ids = self.env["ir.ui.menu"].with_user(user)._visible_menu_ids()
        return {xmlid for xmlid, menu_id in self.menus.items() if menu_id in ids}

    def _groups(self, user):
        return tuple(user.has_group(x) for x in ("account.group_account_user", "account.group_account_readonly",
                                                 "account.group_account_basic"))

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
        self.assertIn(f'name="{self.field}"', self.env.ref("base.user_groups_view").arch)
        self.assertIn(self.field, self.env["res.users"].fields_get([self.field]))

    def test_checkbox_shows_then_hides_accounting_menus(self):
        """Cochée, la case donne les deux groupes impliqués et les trois menus ; décochée, Odoo seul ne retirait
        que le groupe décoché (l'utilisateur gardait lecture seule, basique et les menus) : le socle retire les trois."""
        user = self._accountant()
        self.assertEqual(self._groups(user), (False, False, False))
        self.assertEqual(self._visible(user), set())
        user.write({self.field: True})
        self.assertEqual(self._groups(user), (True, True, True))
        self.assertEqual(self._visible(user), set(self.menus))
        user.write({self.field: False})
        self.assertEqual(self._groups(user), (False, False, False), "décocher retire aussi lecture seule et basique")
        self.assertEqual(self._visible(user), set())
        self.assertTrue(user.has_group("account.group_account_manager"), "le profil Facturation est intact")

    def test_uncheck_keeps_groups_implied_by_another_group(self):
        """Un groupe « Audit » qui implique la lecture seule : décocher la case retire le droit complet et le
        basique, mais Odoo remet la lecture seule, encore impliquée. Restent Comptabilité et États et contrôles ;
        le Tableau de bord (basique) disparaît."""
        audit = self.env["res.groups"].create({"name": "Audit AITE", "implied_ids": [Command.link(self.readonly.id)]})
        user = self._accountant([audit])
        self.assertEqual(self._groups(user), (False, True, False))
        user.write({self.field: True})
        self.assertEqual(self._groups(user), (True, True, True))
        user.write({self.field: False})
        self.assertEqual(self._groups(user), (False, True, False))
        self.assertEqual(self._visible(user), {"account.menu_finance_entries",
                                               "aite_syscohada_base.menu_aite_syscohada_statements"})

    def test_uncheck_with_explicit_groups_untouched(self):
        """Une écriture qui donne ``groups_id`` en clair ignore les cases réifiées, comme dans Odoo."""
        user = self._accountant()
        user.write({self.field: True})
        user.write({self.field: False, "groups_id": [Command.link(self.env.ref("base.group_partner_manager").id)]})
        self.assertEqual(self._groups(user), (True, True, True))
