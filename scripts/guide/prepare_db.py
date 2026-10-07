# Lancé par prepare_db.sh dans « odoo-bin shell » : utilisateur admin en français, rattaché aux trois sociétés.
admin = env.ref("base.user_admin")
bar = env.ref("aite_syscohada_demo.demo_company")
services = env.ref("aite_syscohada_demo_services.demo_company")
main = env.ref("base.main_company")
main.name = "AITE Consulting"
groups = (env.ref("account.group_account_readonly") | env.ref("account.group_account_user")
          | env.ref("account.group_account_manager"))
# société par défaut inchangée : la changer déplacerait le partenaire de l'administrateur dans la société de
# démonstration (capture.js choisit la société par le cookie « cids »)
admin.write({"lang": "fr_FR", "tz": "Africa/Douala", "company_ids": [(6, 0, (main | bar | services).ids)],
             "groups_id": [(4, g.id) for g in groups]})
admin.password = "admin"
line = env.ref("l10n_cm.account_tax_report_line_cm_turnover_normal").with_context(lang="fr_FR")
declaration = env["aite.cm.vat.declaration"].search([("company_id", "=", bar.id)], limit=1)
print("Libellé L10 :", line.name, "| déclaration :", declaration.line_ids.filtered(lambda l: l.code == "CM_NORMAL").name)
env.cr.commit()
