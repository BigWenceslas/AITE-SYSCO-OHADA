# -*- coding: utf-8 -*-
from odoo import api, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    @api.model
    def get_application_groups(self, domain):
        """Remet la case « Montrer les fonctions de comptabilité complètes » dans la section Technique de la fiche
        utilisateur (mode développeur).

        En Community, le module account retire cette case de la fiche : sans elle, seul le menu Paramètres >
        Utilisateurs & Sociétés > Groupes donne ce droit, que demandent les menus Tableau de bord, Comptabilité et
        Syscohada de Facturation. Les droits « lecture seule » et « Basique » restent masqués : la case les donne
        (groupes impliqués). Avec Enterprise (account_accountant), le groupe quitte la catégorie technique et Odoo
        l'affiche déjà : rien n'est ajouté.
        """
        # copie : la surcharge d'account ajoute ses exclusions à la liste reçue
        groups = super().get_application_groups(list(domain))
        full = self.env.ref("account.group_account_user", raise_if_not_found=False)
        if (full and full.category_id.xml_id == "base.module_category_hidden"
                and full.filtered_domain(list(domain) + [("share", "=", False)])):
            groups |= full
        return groups
