# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.addons.base.models.res_users import name_boolean_group


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _remove_reified_groups(self, values):
        """Décocher « Montrer les fonctions de comptabilité complètes » retire aussi les droits qu'elle a donnés.

        Odoo ne retire que le groupe décoché : les groupes qu'il implique (lecture seule, basique), sans case
        dans la fiche, restaient à l'utilisateur, qui gardait les menus Tableau de bord, Comptabilité et
        Syscohada. Ils sont retirés avec lui ; ceux qu'un autre groupe conservé implique encore sont remis par
        Odoo (``UsersImplied.write``).
        """
        full = self.env.ref("account.group_account_user", raise_if_not_found=False)
        unchecked = bool(full) and "groups_id" not in values and not values.get(name_boolean_group(full.id), True)
        values = super()._remove_reified_groups(values)
        if unchecked and values.get("groups_id"):
            commands = values["groups_id"]
            added = self.env["res.groups"].sudo().browse([gid for command, gid in commands if command == 4])
            added |= added.trans_implied_ids
            commands += [(3, group.id) for group in full.implied_ids
                         if group not in added and (3, group.id) not in commands]
        return values
